import os
import sys
from datetime import date

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db, Customer, Device, Technician, Part, RepairOrder, OrderParts


@pytest.fixture
def app():
    flask_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded(app):
    """Populate the DB with a small, deterministic dataset for tests that need it."""
    customer = Customer(c_custkey=1, c_name="Alice", c_phone="555-0001", c_email="alice@example.com")
    customer2 = Customer(c_custkey=2, c_name="Bob", c_phone="555-0002", c_email=None)
    db.session.add_all([customer, customer2])

    device = Device(
        d_devicekey=10, d_devicetype="Laptop", d_serialnum="SN-LAP-1",
        d_custkey=1, d_model="X1", d_brand="Lenovo",
    )
    db.session.add(device)

    tech = Technician(t_techkey=100, t_name="Tina", t_specialty="Hardware", t_hourlyrate=50.00)
    db.session.add(tech)

    part = Part(p_partkey=1000, p_name="Battery", p_serialnum="BAT-001",
                p_stockqty=5, p_unitprice=29.99)
    db.session.add(part)

    order = RepairOrder(
        ro_repairkey=500, ro_orderkey=900, ro_custkey=1, ro_devicekey=10,
        ro_techkey=100, ro_totalcost=199.99, ro_issuedecription="Won't boot",
        ro_status="received", ro_datestarted=date(2026, 4, 1),
    )
    db.session.add(order)
    db.session.commit()

    return {
        "customer": customer,
        "customer2": customer2,
        "device": device,
        "technician": tech,
        "part": part,
        "order": order,
    }
