from sqlite3 import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from flask_smorest import abort, Blueprint
from flask import request
from flask.views import MethodView

from db import db
from models.store import StoreModel

from schema import StoreSchema

bp = Blueprint("stores", __name__, description="Operations on stores")


@bp.route("/store")
class StoreView(MethodView):

    @bp.response(200, StoreSchema(many=True))
    def get(self):
        try:
            stores = StoreModel.query.all()
            return stores
        except SQLAlchemyError:
            abort(500, message="Error occurred while fetching stores")

    @bp.arguments(StoreSchema)
    @bp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Store with this name already exists")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="Error occured while creating store")
        return store


@bp.route("/store/<string:store_id>")
class StoreDetailView(MethodView):

    @bp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            store = StoreModel.query.get(store_id)
            if not store:
                abort(404, message="Store not found!")
            return store
        except SQLAlchemyError:
            abort(500, message="Error occurred while fetching store")

    def delete(self, store_id):
        try:
            store = StoreModel.query.get(store_id)
            if not store:
                abort(404, message="Store not found!")
            db.session.delete(store)
            db.session.commit()
            return {"message": "Store deleted successfully"}, 200
        except SQLAlchemyError:
            abort(500, message="Error occurred while deleting store")
