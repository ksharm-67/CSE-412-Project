def _new_part_payload(**overrides):
    payload = {
        "p_partkey": 2000,
        "p_name": "Screen",
        "p_serialnum": "SCR-001",
        "p_stockqty": 10,
        "p_unitprice": 149.99,
    }
    payload.update(overrides)
    return payload


def test_list_parts_empty(client):
    resp = client.get("/api/parts/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_part(client, seeded):
    resp = client.get("/api/parts/1000")
    assert resp.status_code == 200
    assert resp.get_json()["p_name"] == "Battery"


def test_get_part_not_found(client):
    assert client.get("/api/parts/999").status_code == 404


def test_create_part(client):
    resp = client.post("/api/parts/", json=_new_part_payload())
    assert resp.status_code == 201
    assert resp.get_json()["p_partkey"] == 2000


def test_create_part_missing_fields(client):
    resp = client.post("/api/parts/", json={"p_partkey": 2001})
    assert resp.status_code == 400


def test_create_part_duplicate(client, seeded):
    resp = client.post("/api/parts/", json=_new_part_payload(p_partkey=1000))
    assert resp.status_code == 409


def test_update_part(client, seeded):
    resp = client.put("/api/parts/1000", json={"p_stockqty": 50})
    assert resp.status_code == 200
    assert resp.get_json()["p_stockqty"] == 50


def test_update_part_not_found(client):
    resp = client.put("/api/parts/999", json={"p_name": "x"})
    assert resp.status_code == 404


def test_delete_part(client):
    client.post("/api/parts/", json=_new_part_payload(p_partkey=2500))
    resp = client.delete("/api/parts/2500")
    assert resp.status_code == 200
    assert client.get("/api/parts/2500").status_code == 404


def test_delete_part_not_found(client):
    assert client.delete("/api/parts/999").status_code == 404


def test_restock_part(client, seeded):
    resp = client.post("/api/parts/1000/restock", json={"quantity": 7})
    assert resp.status_code == 200
    assert resp.get_json()["p_stockqty"] == 12  # was 5, +7


def test_restock_part_invalid_quantity(client, seeded):
    for bad in [0, -1, "many", None]:
        resp = client.post("/api/parts/1000/restock", json={"quantity": bad})
        assert resp.status_code == 400


def test_restock_part_not_found(client):
    resp = client.post("/api/parts/999/restock", json={"quantity": 5})
    assert resp.status_code == 404
