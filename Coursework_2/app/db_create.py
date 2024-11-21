from config import SQLALCHEMY_DATABASE_URI  # noqa: F401
from app import db
import os.path  # noqa: F401

db.create_all()
