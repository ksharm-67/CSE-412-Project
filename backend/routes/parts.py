from flask import Blueprint, jsonify, request
from models import db, Part

bp = Blueprint("parts", __name__, url_prefix="/api/parts")


@bp.route("/", methods=["GET"])
def list_parts():
    parts = Part.query.all()
    return jsonify([p.to_dict() for p in parts])


@bp.route("/<int:partkey>", methods=["GET"])
def get_part(partkey):
    part = db.get_or_404(Part, partkey)
    return jsonify(part.to_dict())


@bp.route("/", methods=["POST"])
def create_part():
    data = request.get_json()
    required = ("p_partkey", "p_name", "p_serialnum", "p_stockqty", "p_unitprice")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    if db.session.get(Part, data["p_partkey"]):
        return jsonify({"error": "Part with that key already exists"}), 409

    part = Part(
        p_partkey=data["p_partkey"],
        p_name=data["p_name"],
        p_serialnum=data["p_serialnum"],
        p_stockqty=data["p_stockqty"],
        p_unitprice=data["p_unitprice"],
    )
    db.session.add(part)
    db.session.commit()
    return jsonify(part.to_dict()), 201


@bp.route("/<int:partkey>", methods=["PUT"])
def update_part(partkey):
    part = db.get_or_404(Part, partkey)
    data = request.get_json()

    if "p_name" in data:
        part.p_name = data["p_name"]
    if "p_serialnum" in data:
        part.p_serialnum = data["p_serialnum"]
    if "p_stockqty" in data:
        part.p_stockqty = data["p_stockqty"]
    if "p_unitprice" in data:
        part.p_unitprice = data["p_unitprice"]

    db.session.commit()
    return jsonify(part.to_dict())


@bp.route("/<int:partkey>", methods=["DELETE"])
def delete_part(partkey):
    part = db.get_or_404(Part, partkey)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": "Part deleted"})


@bp.route("/<int:partkey>/restock", methods=["POST"])
def restock_part(partkey):
    """Add stock to a part's inventory."""
    part = db.get_or_404(Part, partkey)
    data = request.get_json()
    qty = data.get("quantity")
    if qty is None or not isinstance(qty, int) or qty <= 0:
        return jsonify({"error": "quantity must be a positive integer"}), 400
    part.p_stockqty += qty
    db.session.commit()
    return jsonify(part.to_dict())
