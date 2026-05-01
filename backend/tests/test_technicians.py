def _new_tech_payload(**overrides):
    payload = {
        "t_techkey": 200,
        "t_name": "Tom",
        "t_specialty": "Software",
        "t_hourlyrate": 65.50,
    }
    payload.update(overrides)
    return payload


def test_list_technicians_empty(client):
    resp = client.get("/api/technicians/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_technician(client, seeded):
    resp = client.get("/api/technicians/100")
    assert resp.status_code == 200
    assert resp.get_json()["t_name"] == "Tina"


def test_get_technician_not_found(client):
    assert client.get("/api/technicians/999").status_code == 404


def test_create_technician(client):
    resp = client.post("/api/technicians/", json=_new_tech_payload())
    assert resp.status_code == 201
    assert resp.get_json()["t_techkey"] == 200


def test_create_technician_missing_fields(client):
    resp = client.post("/api/technicians/", json={"t_techkey": 201})
    assert resp.status_code == 400


def test_create_technician_duplicate(client, seeded):
    resp = client.post("/api/technicians/", json=_new_tech_payload(t_techkey=100))
    assert resp.status_code == 409


def test_update_technician(client, seeded):
    resp = client.put("/api/technicians/100", json={"t_hourlyrate": 99.99})
    assert resp.status_code == 200
    assert resp.get_json()["t_hourlyrate"] == 99.99


def test_update_technician_not_found(client):
    resp = client.put("/api/technicians/999", json={"t_name": "x"})
    assert resp.status_code == 404


def test_delete_technician(client):
    # Use a tech without dependent orders to avoid FK issues.
    client.post("/api/technicians/", json=_new_tech_payload(t_techkey=300))
    resp = client.delete("/api/technicians/300")
    assert resp.status_code == 200
    assert client.get("/api/technicians/300").status_code == 404


def test_delete_technician_not_found(client):
    assert client.delete("/api/technicians/999").status_code == 404


def test_technician_orders(client, seeded):
    resp = client.get("/api/technicians/100/orders")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_technician_orders_not_found(client):
    assert client.get("/api/technicians/999/orders").status_code == 404


def test_technician_workload_busiest(client, seeded):
    # Add a second tech with no orders; workload should sort ascending.
    client.post("/api/technicians/", json=_new_tech_payload(t_techkey=200))
    resp = client.get("/api/technicians/busiest")
    assert resp.status_code == 200
    rows = resp.get_json()
    assert [r["active_orders"] for r in rows] == sorted(r["active_orders"] for r in rows)
    by_key = {r["t_techkey"]: r for r in rows}
    assert by_key[200]["active_orders"] == 0
    assert by_key[100]["active_orders"] == 1
