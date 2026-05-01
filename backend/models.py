from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Customer(db.Model):
    __tablename__ = "customer"

    c_custkey = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.String(25), nullable=False)
    c_phone = db.Column(db.String(15), nullable=False)
    c_email = db.Column(db.String(152))

    devices = db.relationship("Device", backref="customer", lazy=True)
    repair_orders = db.relationship("RepairOrder", backref="customer", lazy=True)

    def to_dict(self):
        return {
            "c_custkey": self.c_custkey,
            "c_name": self.c_name,
            "c_phone": self.c_phone,
            "c_email": self.c_email,
        }


class Device(db.Model):
    __tablename__ = "device"

    d_devicekey = db.Column(db.Integer, primary_key=True)
    d_devicetype = db.Column(db.String(50), nullable=False)
    d_serialnum = db.Column(db.String(150), nullable=False)
    d_custkey = db.Column(db.Integer, db.ForeignKey("customer.c_custkey"), nullable=False)
    d_model = db.Column(db.String(100), nullable=False)
    d_brand = db.Column(db.String(50), nullable=False)

    repair_orders = db.relationship("RepairOrder", backref="device", lazy=True)

    def to_dict(self):
        return {
            "d_devicekey": self.d_devicekey,
            "d_devicetype": self.d_devicetype,
            "d_serialnum": self.d_serialnum,
            "d_custkey": self.d_custkey,
            "d_model": self.d_model,
            "d_brand": self.d_brand,
        }


class Technician(db.Model):
    __tablename__ = "technician"

    t_techkey = db.Column(db.Integer, primary_key=True)
    t_name = db.Column(db.String(25), nullable=False)
    t_specialty = db.Column(db.String(40), nullable=False)
    t_hourlyrate = db.Column(db.Numeric(5, 2), nullable=False)

    repair_orders = db.relationship("RepairOrder", backref="technician", lazy=True)

    def to_dict(self):
        return {
            "t_techkey": self.t_techkey,
            "t_name": self.t_name,
            "t_specialty": self.t_specialty,
            "t_hourlyrate": float(self.t_hourlyrate),
        }


class Part(db.Model):
    __tablename__ = "part"

    p_partkey = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String(55), nullable=False)
    p_serialnum = db.Column(db.String(150), nullable=False)
    p_stockqty = db.Column(db.Integer, nullable=False)
    p_unitprice = db.Column(db.Numeric(6, 2), nullable=False)

    order_parts = db.relationship("OrderParts", backref="part", lazy=True)

    def to_dict(self):
        return {
            "p_partkey": self.p_partkey,
            "p_name": self.p_name,
            "p_serialnum": self.p_serialnum,
            "p_stockqty": self.p_stockqty,
            "p_unitprice": float(self.p_unitprice),
        }


class RepairOrder(db.Model):
    __tablename__ = "repairorder"

    ro_repairkey = db.Column(db.Integer, primary_key=True)
    ro_orderkey = db.Column(db.Integer, nullable=False)
    ro_custkey = db.Column(db.Integer, db.ForeignKey("customer.c_custkey"), nullable=False)
    ro_devicekey = db.Column(db.Integer, db.ForeignKey("device.d_devicekey"), nullable=False)
    ro_techkey = db.Column(db.Integer, db.ForeignKey("technician.t_techkey"), nullable=False)
    ro_totalcost = db.Column(db.Numeric(15, 2), nullable=False)
    ro_issuedecription = db.Column(db.String(500), nullable=False)
    ro_status = db.Column(db.String(10), nullable=False)  # received, pending, completed
    ro_datestarted = db.Column(db.Date, nullable=False)
    ro_datefinished = db.Column(db.Date)

    order_parts = db.relationship("OrderParts", backref="repair_order", lazy=True)

    VALID_STATUSES = ("received", "pending", "completed")

    def to_dict(self):
        return {
            "ro_repairkey": self.ro_repairkey,
            "ro_orderkey": self.ro_orderkey,
            "ro_custkey": self.ro_custkey,
            "ro_devicekey": self.ro_devicekey,
            "ro_techkey": self.ro_techkey,
            "ro_totalcost": float(self.ro_totalcost),
            "ro_issuedecription": self.ro_issuedecription,
            "ro_status": self.ro_status,
            "ro_datestarted": self.ro_datestarted.isoformat() if self.ro_datestarted else None,
            "ro_datefinished": self.ro_datefinished.isoformat() if self.ro_datefinished else None,
        }


class OrderParts(db.Model):
    __tablename__ = "orderparts"

    o_repairkey = db.Column(
        db.Integer,
        db.ForeignKey("repairorder.ro_repairkey"),
        primary_key=True,
    )
    o_partkey = db.Column(
        db.Integer,
        db.ForeignKey("part.p_partkey"),
        primary_key=True,
    )
    o_qtyused = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "o_repairkey": self.o_repairkey,
            "o_partkey": self.o_partkey,
            "o_qtyused": self.o_qtyused,
        }
