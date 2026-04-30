from flask import Blueprint, jsonify, request
from models import db, Device, Customer

bp = Blueprint("devices", __name__, url_prefix="/api/devices")


@bp.route("/", methods=["GET"])
def list_devices():
    devices = Device.query.all()
    return jsonify([d.to_dict() for d in devices])


@bp.route("/<int:devicekey>", methods=["GET"])
def get_device(devicekey):
    device = db.get_or_404(Device, devicekey)
    return jsonify(device.to_dict())


@bp.route("/", methods=["POST"])
def create_device():
    data = request.get_json()
    required = ("d_devicekey", "d_devicetype", "d_serialnum", "d_custkey", "d_model", "d_brand")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    if db.session.get(Device, data["d_devicekey"]):
        return jsonify({"error": "Device with that key already exists"}), 409

    if not db.session.get(Customer, data["d_custkey"]):
        return jsonify({"error": "Customer not found"}), 404

    device = Device(
        d_devicekey=data["d_devicekey"],
        d_devicetype=data["d_devicetype"],
        d_serialnum=data["d_serialnum"],
        d_custkey=data["d_custkey"],
        d_model=data["d_model"],
        d_brand=data["d_brand"],
    )
    db.session.add(device)
    db.session.commit()
    return jsonify(device.to_dict()), 201


@bp.route("/<int:devicekey>", methods=["PUT"])
def update_device(devicekey):
    device = db.get_or_404(Device, devicekey)
    data = request.get_json()

    if "d_devicetype" in data:
        device.d_devicetype = data["d_devicetype"]
    if "d_serialnum" in data:
        device.d_serialnum = data["d_serialnum"]
    if "d_custkey" in data:
        if not db.session.get(Customer, data["d_custkey"]):
            return jsonify({"error": "Customer not found"}), 404
        device.d_custkey = data["d_custkey"]
    if "d_model" in data:
        device.d_model = data["d_model"]
    if "d_brand" in data:
        device.d_brand = data["d_brand"]

    db.session.commit()
    return jsonify(device.to_dict())


@bp.route("/<int:devicekey>", methods=["DELETE"])
def delete_device(devicekey):
    device = db.get_or_404(Device, devicekey)
    db.session.delete(device)
    db.session.commit()
    return jsonify({"message": "Device deleted"})
