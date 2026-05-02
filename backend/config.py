import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://repairmatrix:password123@localhost:888/repairmatrix"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "pass123"
