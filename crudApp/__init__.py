import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .main import main
from .models import *
from .sqlalchemy import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv("MYSQL_USER","user")}:{os.getenv("MYSQL_PASSWORD","user")}@{os.getenv("MYSQL_HOST","localhost")}:3306/{os.getenv("MYSQL_DATABASE","crudApp")}"
    )
    app.secret_key = os.getenv("SECRET_KEY")
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main)

    return app
