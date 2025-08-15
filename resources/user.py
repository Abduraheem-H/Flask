from flask_smorest import Blueprint, abort
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token
from flask import current_app

from db import db
from models.users import UserModel
from schema import UserSchema

bp = Blueprint("users", __name__, description="User management endpoints")


@bp.route("/register", methods=["POST"])
class UserRegister(MethodView):
    @bp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter_by(username=user_data["username"]).first():
            abort(409, message="User already exists")
        user_data["password"] = sha256.hash(user_data["password"])
        user = UserModel(**user_data)
        db.session.add(user)
        db.session.commit()
        return {"message": "User registered successfully"}, 201


@bp.route("/user/<int:user_id>")
class UserDetail(MethodView):
    @bp.response(200, UserSchema)
    def get(self, user_id):
        if not UserModel.query.get(user_id):
            abort(404, message="User not found")
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}, 204


@bp.route("/login", methods=["POST"])
class UserLogin(MethodView):

    @bp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(username=user_data["username"]).first()
        if not user or not sha256.verify(user_data["password"], user.password):
            abort(401, message="Invalid credentials")
        # DEBUG: print secret and token
        print("DEBUG login JWT_SECRET_KEY:", current_app.config.get("JWT_SECRET_KEY"))
        token = create_access_token(identity=user.id)
        print("DEBUG created token:", token)
        access_token = create_access_token(identity=str(user.id))
        return {"access_token": access_token}, 200
