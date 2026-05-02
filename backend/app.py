from flask import Flask
from config import Config
from models import db
from routes.customers import bp as customers_bp
from routes.devices import bp as devices_bp
from routes.technicians import bp as technicians_bp
from routes.parts import bp as parts_bp
from routes.repair_orders import bp as repair_orders_bp
from flask_cors import CORS

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    if config:
        app.config.update(config)

    db.init_app(app)

    app.register_blueprint(customers_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(technicians_bp)
    app.register_blueprint(parts_bp)
    app.register_blueprint(repair_orders_bp)

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    

