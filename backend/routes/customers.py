from flask import Blueprint, jsonify, request
from models import db, Customer

bp = Blueprint("customers", __name__, url_prefix="/api/customers")


@bp.route("/", methods=["GET"])
def list_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])


@bp.route("/<int:custkey>", methods=["GET"])
def get_customer(custkey):
    customer = db.get_or_404(Customer, custkey)
    return jsonify(customer.to_dict())


@bp.route("/", methods=["POST"])
def create_customer():
    data = request.get_json()
    required = ("c_custkey", "c_name", "c_phone")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    if db.session.get(Customer, data["c_custkey"]):
        return jsonify({"error": "Customer with that key already exists"}), 409

    customer = Customer(
        c_custkey=data["c_custkey"],
        c_name=data["c_name"],
        c_phone=data["c_phone"],
        c_email=data.get("c_email"),
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201


@bp.route("/<int:custkey>", methods=["PUT"])
def update_customer(custkey):
    customer = db.get_or_404(Customer, custkey)
    data = request.get_json()

    if "c_name" in data:
        customer.c_name = data["c_name"]
    if "c_phone" in data:
        customer.c_phone = data["c_phone"]
    if "c_email" in data:
        customer.c_email = data["c_email"]

    db.session.commit()
    return jsonify(customer.to_dict())


@bp.route("/<int:custkey>", methods=["DELETE"])
def delete_customer(custkey):
    customer = db.get_or_404(Customer, custkey)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted"})


@bp.route("/<int:custkey>/orders", methods=["GET"])
def get_customer_orders(custkey):
    customer = db.get_or_404(Customer, custkey)
    return jsonify([ro.to_dict() for ro in customer.repair_orders])


@bp.route("/<int:custkey>/devices", methods=["GET"])
def get_customer_devices(custkey):
    customer = db.get_or_404(Customer, custkey)
    return jsonify([d.to_dict() for d in customer.devices])
