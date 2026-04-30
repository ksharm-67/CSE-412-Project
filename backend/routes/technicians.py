from flask import Blueprint, jsonify, request
from models import db, Technician, RepairOrder

bp = Blueprint("technicians", __name__, url_prefix="/api/technicians")


@bp.route("/", methods=["GET"])
def list_technicians():
    technicians = Technician.query.all()
    return jsonify([t.to_dict() for t in technicians])


@bp.route("/<int:techkey>", methods=["GET"])
def get_technician(techkey):
    tech = db.get_or_404(Technician, techkey)
    return jsonify(tech.to_dict())


@bp.route("/", methods=["POST"])
def create_technician():
    data = request.get_json()
    required = ("t_techkey", "t_name", "t_specialty", "t_hourlyrate")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    if db.session.get(Technician, data["t_techkey"]):
        return jsonify({"error": "Technician with that key already exists"}), 409

    tech = Technician(
        t_techkey=data["t_techkey"],
        t_name=data["t_name"],
        t_specialty=data["t_specialty"],
        t_hourlyrate=data["t_hourlyrate"],
    )
    db.session.add(tech)
    db.session.commit()
    return jsonify(tech.to_dict()), 201


@bp.route("/<int:techkey>", methods=["PUT"])
def update_technician(techkey):
    tech = db.get_or_404(Technician, techkey)
    data = request.get_json()

    if "t_name" in data:
        tech.t_name = data["t_name"]
    if "t_specialty" in data:
        tech.t_specialty = data["t_specialty"]
    if "t_hourlyrate" in data:
        tech.t_hourlyrate = data["t_hourlyrate"]

    db.session.commit()
    return jsonify(tech.to_dict())


@bp.route("/<int:techkey>", methods=["DELETE"])
def delete_technician(techkey):
    tech = db.get_or_404(Technician, techkey)
    db.session.delete(tech)
    db.session.commit()
    return jsonify({"message": "Technician deleted"})


@bp.route("/<int:techkey>/orders", methods=["GET"])
def get_technician_orders(techkey):
    tech = db.get_or_404(Technician, techkey)
    return jsonify([ro.to_dict() for ro in tech.repair_orders])


@bp.route("/busiest", methods=["GET"])
def get_technician_workload():
    """Return all technicians with their active order count, sorted ascending."""
    technicians = Technician.query.all()
    result = []
    for t in technicians:
        active = sum(
            1 for ro in t.repair_orders if ro.ro_status in ("received", "pending")
        )
        entry = t.to_dict()
        entry["active_orders"] = active
        result.append(entry)
    result.sort(key=lambda x: x["active_orders"])
    return jsonify(result)
