import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from blocklist import is_token_revoked
from db import db
from resources import item, store, tag, user


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

    app.config["JWT_SECRET_KEY"] = "super-secret"
    jwt = JWTManager(app)

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The access token is not fresh",
                    "error": "Fresh token required",
                }
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired", "error": "token_expired"})

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token",
                    "error": "Authorization required",
                }
            ),
            401,
        )

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return is_token_revoked(jti)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"message": "The token has been revoked", "error": "token_revoked"}
            ),
            401,
        )

    with app.app_context():
        db.create_all()

    api = Api(app)
    api.register_blueprint(store.bp)
    api.register_blueprint(item.bp)
    api.register_blueprint(tag.bp)
    api.register_blueprint(user.bp)
    return app
