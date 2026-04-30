def _new_order_payload(**overrides):
    payload = {
        "ro_repairkey": 600,
        "ro_orderkey": 901,
        "ro_custkey": 1,
        "ro_devicekey": 10,
        "ro_totalcost": 50.00,
        "ro_issuedecription": "Battery swap",
        "ro_datestarted": "2026-04-15",
    }
    payload.update(overrides)
    return payload


def test_list_orders_empty(client):
    resp = client.get("/api/orders/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_orders_filter_by_status(client, seeded):
    resp = client.get("/api/orders/?status=received")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1
    resp = client.get("/api/orders/?status=completed")
    assert resp.get_json() == []


def test_get_order(client, seeded):
    resp = client.get("/api/orders/500")
    assert resp.status_code == 200
    assert resp.get_json()["ro_status"] == "received"


def test_get_order_not_found(client):
    assert client.get("/api/orders/999").status_code == 404


def test_create_order_auto_assigns_technician(client, seeded):
    resp = client.post("/api/orders/", json=_new_order_payload())
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ro_techkey"] == 100  # the only seeded technician
    assert body["ro_status"] == "received"


def test_create_order_explicit_technician(client, seeded):
    resp = client.post("/api/orders/", json=_new_order_payload(ro_techkey=100))
    assert resp.status_code == 201
    assert resp.get_json()["ro_techkey"] == 100


def test_create_order_missing_fields(client, seeded):
    resp = client.post("/api/orders/", json={"ro_repairkey": 601})
    assert resp.status_code == 400


def test_create_order_duplicate_key(client, seeded):
    resp = client.post("/api/orders/", json=_new_order_payload(ro_repairkey=500))
    assert resp.status_code == 409


def test_create_order_unknown_customer(client, seeded):
    resp = client.post("/api/orders/", json=_new_order_payload(ro_custkey=999))
    assert resp.status_code == 404


def test_create_order_unknown_device(client, seeded):
    resp = client.post("/api/orders/", json=_new_order_payload(ro_devicekey=999))
    assert resp.status_code == 404


def test_create_order_unknown_technician(client, seeded):
    resp = client.post("/api/orders/", json=_new_order_payload(ro_techkey=999))
    assert resp.status_code == 404


def test_create_order_no_technicians_available(client):
    # Set up just a customer + device, but no technicians.
    client.post("/api/customers/", json={
        "c_custkey": 1, "c_name": "A", "c_phone": "555-0001",
    })
    client.post("/api/customers/", json={
        "c_custkey": 5, "c_name": "B", "c_phone": "555-0005",
    })
    # Need a device too — uses customer 1.
    from models import db, Device
    db.session.add(Device(
        d_devicekey=10, d_devicetype="Laptop", d_serialnum="x",
        d_custkey=1, d_model="m", d_brand="b",
    ))
    db.session.commit()
    resp = client.post("/api/orders/", json=_new_order_payload())
    assert resp.status_code == 400
    assert "No technicians" in resp.get_json()["error"]


def test_create_order_bad_date(client, seeded):
    resp = client.post("/api/orders/", json=_new_order_payload(ro_datestarted="not-a-date"))
    assert resp.status_code == 400


def test_create_order_bad_finished_date(client, seeded):
    resp = client.post("/api/orders/", json=_new_order_payload(ro_datefinished="bad"))
    assert resp.status_code == 400


def test_create_order_invalid_status(client, seeded):
    resp = client.post("/api/orders/", json=_new_order_payload(ro_status="bogus"))
    assert resp.status_code == 400


def test_update_order_fields(client, seeded):
    resp = client.put("/api/orders/500", json={
        "ro_totalcost": 250.00,
        "ro_issuedecription": "Updated",
        "ro_status": "pending",
        "ro_datestarted": "2026-04-02",
        "ro_datefinished": "2026-04-20",
    })
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ro_totalcost"] == 250.00
    assert body["ro_status"] == "pending"
    assert body["ro_datefinished"] == "2026-04-20"


def test_update_order_invalid_status(client, seeded):
    resp = client.put("/api/orders/500", json={"ro_status": "bogus"})
    assert resp.status_code == 400


def test_update_order_unknown_technician(client, seeded):
    resp = client.put("/api/orders/500", json={"ro_techkey": 999})
    assert resp.status_code == 404


def test_update_order_bad_dates(client, seeded):
    assert client.put("/api/orders/500", json={"ro_datestarted": "x"}).status_code == 400
    assert client.put("/api/orders/500", json={"ro_datefinished": "x"}).status_code == 400


def test_update_order_clear_finished(client, seeded):
    client.put("/api/orders/500", json={"ro_datefinished": "2026-04-10"})
    resp = client.put("/api/orders/500", json={"ro_datefinished": None})
    assert resp.status_code == 200
    assert resp.get_json()["ro_datefinished"] is None


def test_update_order_not_found(client):
    resp = client.put("/api/orders/999", json={"ro_status": "pending"})
    assert resp.status_code == 404


def test_status_transition_received_to_pending(client, seeded):
    resp = client.patch("/api/orders/500/status", json={"status": "pending"})
    assert resp.status_code == 200
    assert resp.get_json()["ro_status"] == "pending"


def test_status_transition_pending_to_completed_sets_date(client, seeded):
    client.patch("/api/orders/500/status", json={"status": "pending"})
    resp = client.patch("/api/orders/500/status", json={"status": "completed"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ro_status"] == "completed"
    assert body["ro_datefinished"] is not None


def test_status_transition_invalid(client, seeded):
    # received -> completed is not allowed
    resp = client.patch("/api/orders/500/status", json={"status": "completed"})
    assert resp.status_code == 400


def test_status_transition_missing_field(client, seeded):
    resp = client.patch("/api/orders/500/status", json={})
    assert resp.status_code == 400


def test_status_transition_invalid_value(client, seeded):
    resp = client.patch("/api/orders/500/status", json={"status": "bogus"})
    assert resp.status_code == 400


def test_status_transition_not_found(client):
    resp = client.patch("/api/orders/999/status", json={"status": "pending"})
    assert resp.status_code == 404


def test_delete_order(client, seeded):
    resp = client.delete("/api/orders/500")
    assert resp.status_code == 200
    assert client.get("/api/orders/500").status_code == 404


def test_delete_order_not_found(client):
    assert client.delete("/api/orders/999").status_code == 404


def test_get_order_parts_empty(client, seeded):
    resp = client.get("/api/orders/500/parts")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_order_parts_not_found(client):
    assert client.get("/api/orders/999/parts").status_code == 404


def test_add_part_to_order(client, seeded):
    resp = client.post("/api/orders/500/parts", json={"p_partkey": 1000, "o_qtyused": 2})
    assert resp.status_code == 201
    assert resp.get_json()["o_qtyused"] == 2
    # Stock decremented from 5 -> 3.
    assert client.get("/api/parts/1000").get_json()["p_stockqty"] == 3


def test_add_part_to_order_increments_existing(client, seeded):
    client.post("/api/orders/500/parts", json={"p_partkey": 1000, "o_qtyused": 2})
    resp = client.post("/api/orders/500/parts", json={"p_partkey": 1000, "o_qtyused": 1})
    assert resp.status_code == 200
    assert resp.get_json()["o_qtyused"] == 3
    assert client.get("/api/parts/1000").get_json()["p_stockqty"] == 2


def test_add_part_missing_fields(client, seeded):
    resp = client.post("/api/orders/500/parts", json={"p_partkey": 1000})
    assert resp.status_code == 400


def test_add_part_unknown_part(client, seeded):
    resp = client.post("/api/orders/500/parts", json={"p_partkey": 9999, "o_qtyused": 1})
    assert resp.status_code == 404


def test_add_part_invalid_qty(client, seeded):
    resp = client.post("/api/orders/500/parts", json={"p_partkey": 1000, "o_qtyused": 0})
    assert resp.status_code == 400


def test_add_part_insufficient_stock(client, seeded):
    resp = client.post("/api/orders/500/parts", json={"p_partkey": 1000, "o_qtyused": 100})
    assert resp.status_code == 400


def test_add_part_order_not_found(client, seeded):
    resp = client.post("/api/orders/999/parts", json={"p_partkey": 1000, "o_qtyused": 1})
    assert resp.status_code == 404


def test_remove_part_from_order_restores_stock(client, seeded):
    client.post("/api/orders/500/parts", json={"p_partkey": 1000, "o_qtyused": 2})
    assert client.get("/api/parts/1000").get_json()["p_stockqty"] == 3
    resp = client.delete("/api/orders/500/parts/1000")
    assert resp.status_code == 200
    assert client.get("/api/parts/1000").get_json()["p_stockqty"] == 5


def test_remove_part_from_order_not_found(client, seeded):
    resp = client.delete("/api/orders/500/parts/9999")
    assert resp.status_code == 404


def test_remove_part_order_not_found(client, seeded):
    resp = client.delete("/api/orders/999/parts/1000")
    assert resp.status_code == 404
