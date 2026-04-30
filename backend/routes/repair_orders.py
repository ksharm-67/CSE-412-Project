import random
from datetime import date
from flask import Blueprint, jsonify, request
from models import db, RepairOrder, Technician, Customer, Device, OrderParts, Part

bp = Blueprint("repair_orders", __name__, url_prefix="/api/orders")


def _assign_technician():
    """Return the technician with the fewest active orders; break ties randomly."""
    technicians = Technician.query.all()
    if not technicians:
        return None

    counts = {}
    for tech in technicians:
        counts[tech.t_techkey] = sum(
            1 for ro in tech.repair_orders if ro.ro_status in ("received", "pending")
        )

    min_count = min(counts.values())
    candidates = [t for t in technicians if counts[t.t_techkey] == min_count]
    return random.choice(candidates)


@bp.route("/", methods=["GET"])
def list_orders():
    status = request.args.get("status")
    query = RepairOrder.query
    if status:
        query = query.filter_by(ro_status=status)
    orders = query.all()
    return jsonify([o.to_dict() for o in orders])


@bp.route("/<int:repairkey>", methods=["GET"])
def get_order(repairkey):
    order = db.get_or_404(RepairOrder, repairkey)
    return jsonify(order.to_dict())


@bp.route("/", methods=["POST"])
def create_order():
    """Create a new repair order. Auto-assigns technician with fewest active orders."""
    data = request.get_json()
    required = ("ro_repairkey", "ro_orderkey", "ro_custkey", "ro_devicekey",
                "ro_totalcost", "ro_issuedecription", "ro_datestarted")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    if db.session.get(RepairOrder, data["ro_repairkey"]):
        return jsonify({"error": "Repair order with that key already exists"}), 409

    if not db.session.get(Customer, data["ro_custkey"]):
        return jsonify({"error": "Customer not found"}), 404

    if not db.session.get(Device, data["ro_devicekey"]):
        return jsonify({"error": "Device not found"}), 404

    # Auto-assign technician unless one is provided
    if "ro_techkey" in data:
        tech = db.session.get(Technician, data["ro_techkey"])
        if not tech:
            return jsonify({"error": "Technician not found"}), 404
    else:
        tech = _assign_technician()
        if not tech:
            return jsonify({"error": "No technicians available"}), 400

    try:
        date_started = date.fromisoformat(data["ro_datestarted"])
    except ValueError:
        return jsonify({"error": "ro_datestarted must be YYYY-MM-DD"}), 400

    date_finished = None
    if data.get("ro_datefinished"):
        try:
            date_finished = date.fromisoformat(data["ro_datefinished"])
        except ValueError:
            return jsonify({"error": "ro_datefinished must be YYYY-MM-DD"}), 400

    status = data.get("ro_status", "received")
    if status not in RepairOrder.VALID_STATUSES:
        return jsonify({"error": f"Invalid status. Must be one of: {RepairOrder.VALID_STATUSES}"}), 400

    order = RepairOrder(
        ro_repairkey=data["ro_repairkey"],
        ro_orderkey=data["ro_orderkey"],
        ro_custkey=data["ro_custkey"],
        ro_devicekey=data["ro_devicekey"],
        ro_techkey=tech.t_techkey,
        ro_totalcost=data["ro_totalcost"],
        ro_issuedecription=data["ro_issuedecription"],
        ro_status=status,
        ro_datestarted=date_started,
        ro_datefinished=date_finished,
    )
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@bp.route("/<int:repairkey>", methods=["PUT"])
def update_order(repairkey):
    order = db.get_or_404(RepairOrder, repairkey)
    data = request.get_json()

    if "ro_status" in data:
        if data["ro_status"] not in RepairOrder.VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of: {RepairOrder.VALID_STATUSES}"}), 400
        order.ro_status = data["ro_status"]

    if "ro_totalcost" in data:
        order.ro_totalcost = data["ro_totalcost"]

    if "ro_issuedecription" in data:
        order.ro_issuedecription = data["ro_issuedecription"]

    if "ro_techkey" in data:
        if not db.session.get(Technician, data["ro_techkey"]):
            return jsonify({"error": "Technician not found"}), 404
        order.ro_techkey = data["ro_techkey"]

    if "ro_datestarted" in data:
        try:
            order.ro_datestarted = date.fromisoformat(data["ro_datestarted"])
        except ValueError:
            return jsonify({"error": "ro_datestarted must be YYYY-MM-DD"}), 400

    if "ro_datefinished" in data:
        if data["ro_datefinished"]:
            try:
                order.ro_datefinished = date.fromisoformat(data["ro_datefinished"])
            except ValueError:
                return jsonify({"error": "ro_datefinished must be YYYY-MM-DD"}), 400
        else:
            order.ro_datefinished = None

    db.session.commit()
    return jsonify(order.to_dict())


@bp.route("/<int:repairkey>/status", methods=["PATCH"])
def update_status(repairkey):
    """Dedicated endpoint for status transitions: received → pending → completed."""
    order = db.get_or_404(RepairOrder, repairkey)
    data = request.get_json()
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "status field required"}), 400

    if new_status not in RepairOrder.VALID_STATUSES:
        return jsonify({"error": f"Invalid status. Must be one of: {RepairOrder.VALID_STATUSES}"}), 400

    valid_transitions = {
        "received": ("pending",),
        "pending": ("completed", "received"),
        "completed": ("pending",),
    }
    allowed = valid_transitions.get(order.ro_status, ())
    if new_status not in allowed:
        return jsonify({
            "error": f"Cannot transition from '{order.ro_status}' to '{new_status}'"
        }), 400

    if new_status == "completed":
        order.ro_datefinished = date.today()

    order.ro_status = new_status
    db.session.commit()
    return jsonify(order.to_dict())


@bp.route("/<int:repairkey>", methods=["DELETE"])
def delete_order(repairkey):
    order = db.get_or_404(RepairOrder, repairkey)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Repair order deleted"})


@bp.route("/<int:repairkey>/parts", methods=["GET"])
def get_order_parts(repairkey):
    db.get_or_404(RepairOrder, repairkey)
    entries = OrderParts.query.filter_by(o_repairkey=repairkey).all()
    return jsonify([e.to_dict() for e in entries])


@bp.route("/<int:repairkey>/parts", methods=["POST"])
def add_part_to_order(repairkey):
    """Add a part to a repair order and decrement inventory."""
    order = db.get_or_404(RepairOrder, repairkey)
    data = request.get_json()

    if "p_partkey" not in data or "o_qtyused" not in data:
        return jsonify({"error": "p_partkey and o_qtyused required"}), 400

    part = db.session.get(Part, data["p_partkey"])
    if not part:
        return jsonify({"error": "Part not found"}), 404

    qty = data["o_qtyused"]
    if not isinstance(qty, int) or qty <= 0:
        return jsonify({"error": "o_qtyused must be a positive integer"}), 400

    if part.p_stockqty < qty:
        return jsonify({"error": f"Insufficient stock. Available: {part.p_stockqty}"}), 400

    existing = OrderParts.query.filter_by(
        o_repairkey=repairkey, o_partkey=data["p_partkey"]
    ).first()
    if existing:
        # Add to existing quantity
        part.p_stockqty -= qty
        existing.o_qtyused += qty
        db.session.commit()
        return jsonify(existing.to_dict())

    entry = OrderParts(
        o_repairkey=repairkey,
        o_partkey=data["p_partkey"],
        o_qtyused=qty,
    )
    part.p_stockqty -= qty
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201


@bp.route("/<int:repairkey>/parts/<int:partkey>", methods=["DELETE"])
def remove_part_from_order(repairkey, partkey):
    """Remove a part from a repair order and restore inventory."""
    db.get_or_404(RepairOrder, repairkey)
    entry = OrderParts.query.filter_by(
        o_repairkey=repairkey, o_partkey=partkey
    ).first_or_404()

    part = db.session.get(Part, partkey)
    if part:
        part.p_stockqty += entry.o_qtyused

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Part removed from order"})
