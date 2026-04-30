def test_list_customers_empty(client):
    resp = client.get("/api/customers/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_customers_seeded(client, seeded):
    resp = client.get("/api/customers/")
    assert resp.status_code == 200
    keys = sorted(c["c_custkey"] for c in resp.get_json())
    assert keys == [1, 2]


def test_get_customer(client, seeded):
    resp = client.get("/api/customers/1")
    assert resp.status_code == 200
    assert resp.get_json()["c_name"] == "Alice"


def test_get_customer_not_found(client):
    resp = client.get("/api/customers/999")
    assert resp.status_code == 404


def test_create_customer(client):
    payload = {"c_custkey": 3, "c_name": "Carol", "c_phone": "555-0003", "c_email": "c@x.com"}
    resp = client.post("/api/customers/", json=payload)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["c_custkey"] == 3
    assert body["c_email"] == "c@x.com"


def test_create_customer_missing_fields(client):
    resp = client.post("/api/customers/", json={"c_custkey": 4})
    assert resp.status_code == 400
    assert "Missing fields" in resp.get_json()["error"]


def test_create_customer_duplicate(client, seeded):
    resp = client.post("/api/customers/", json={
        "c_custkey": 1, "c_name": "Dup", "c_phone": "555-9999",
    })
    assert resp.status_code == 409


def test_update_customer(client, seeded):
    resp = client.put("/api/customers/1", json={"c_name": "Alice Renamed"})
    assert resp.status_code == 200
    assert resp.get_json()["c_name"] == "Alice Renamed"


def test_update_customer_not_found(client):
    resp = client.put("/api/customers/999", json={"c_name": "x"})
    assert resp.status_code == 404


def test_delete_customer(client, seeded):
    resp = client.delete("/api/customers/2")
    assert resp.status_code == 200
    assert client.get("/api/customers/2").status_code == 404


def test_delete_customer_not_found(client):
    resp = client.delete("/api/customers/999")
    assert resp.status_code == 404


def test_get_customer_orders(client, seeded):
    resp = client.get("/api/customers/1/orders")
    assert resp.status_code == 200
    orders = resp.get_json()
    assert len(orders) == 1
    assert orders[0]["ro_repairkey"] == 500


def test_get_customer_orders_not_found(client):
    resp = client.get("/api/customers/999/orders")
    assert resp.status_code == 404


def test_get_customer_devices(client, seeded):
    resp = client.get("/api/customers/1/devices")
    assert resp.status_code == 200
    devices = resp.get_json()
    assert len(devices) == 1
    assert devices[0]["d_devicekey"] == 10


def test_get_customer_devices_empty(client, seeded):
    resp = client.get("/api/customers/2/devices")
    assert resp.status_code == 200
    assert resp.get_json() == []
