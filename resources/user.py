import datetime
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
    create_refresh_token,
    get_jwt_identity,
)


from blocklist import add_to_blocklist
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

        access_token = create_access_token(identity=str(user.id), fresh=True)
        refresh_token = create_refresh_token(identity=str(user.id))
        return {"access_token": access_token, "refresh_token": refresh_token}, 200


@bp.route("/refresh", methods=["POST"])
class UserRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user, fresh=False)
        blocklist_jti = get_jwt().get("jti")
        add_to_blocklist(
            blocklist_jti,
            int(
                get_jwt().get("exp")
                - datetime.datetime.now(datetime.timezone.utc).timestamp()
            ),
        )
        return {"access_token": access_token}, 200


@bp.route("/logout", methods=["POST"])
class UserLogout(MethodView):
    @jwt_required()
    @bp.response(200, description="Successfully logged out")
    def post(self):
        jti = get_jwt().get("jti")
        expires_in = (
            get_jwt().get("exp")
            - datetime.datetime.now(datetime.timezone.utc).timestamp()
        )
        add_to_blocklist(jti, int(expires_in))
        return {"message": "Successfully logged out"}, 200
