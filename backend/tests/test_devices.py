def _new_device_payload(**overrides):
    payload = {
        "d_devicekey": 20,
        "d_devicetype": "Phone",
        "d_serialnum": "SN-PHN-1",
        "d_custkey": 1,
        "d_model": "Pixel 8",
        "d_brand": "Google",
    }
    payload.update(overrides)
    return payload


def test_list_devices_empty(client):
    resp = client.get("/api/devices/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_devices_seeded(client, seeded):
    resp = client.get("/api/devices/")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_get_device(client, seeded):
    resp = client.get("/api/devices/10")
    assert resp.status_code == 200
    assert resp.get_json()["d_brand"] == "Lenovo"


def test_get_device_not_found(client):
    assert client.get("/api/devices/999").status_code == 404


def test_create_device(client, seeded):
    resp = client.post("/api/devices/", json=_new_device_payload())
    assert resp.status_code == 201
    assert resp.get_json()["d_devicekey"] == 20


def test_create_device_missing_fields(client):
    resp = client.post("/api/devices/", json={"d_devicekey": 21})
    assert resp.status_code == 400


def test_create_device_duplicate_key(client, seeded):
    resp = client.post("/api/devices/", json=_new_device_payload(d_devicekey=10))
    assert resp.status_code == 409


def test_create_device_unknown_customer(client, seeded):
    resp = client.post("/api/devices/", json=_new_device_payload(d_custkey=999))
    assert resp.status_code == 404


def test_update_device(client, seeded):
    resp = client.put("/api/devices/10", json={"d_model": "X1 Carbon"})
    assert resp.status_code == 200
    assert resp.get_json()["d_model"] == "X1 Carbon"


def test_update_device_change_customer(client, seeded):
    resp = client.put("/api/devices/10", json={"d_custkey": 2})
    assert resp.status_code == 200
    assert resp.get_json()["d_custkey"] == 2


def test_update_device_unknown_customer(client, seeded):
    resp = client.put("/api/devices/10", json={"d_custkey": 999})
    assert resp.status_code == 404


def test_update_device_not_found(client):
    resp = client.put("/api/devices/999", json={"d_model": "x"})
    assert resp.status_code == 404


def test_delete_device(client, seeded):
    # Need to delete dependent order first since FK constraints may apply.
    client.delete("/api/orders/500")
    resp = client.delete("/api/devices/10")
    assert resp.status_code == 200


def test_delete_device_not_found(client):
    assert client.delete("/api/devices/999").status_code == 404
