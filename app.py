import os

from flask import Flask
from flask_smorest import Api

from db import db
from resources import item, store, tag


def create_app(db_uri=None):
    app = Flask(__name__)

    app.config["API_TITLE"] = "Store and Item API"
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_JSON_PATH"] = "openapi.json"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    api = Api(app)

    api.register_blueprint(store.bp)
    api.register_blueprint(item.bp)
    api.register_blueprint(tag.bp)

    return app
