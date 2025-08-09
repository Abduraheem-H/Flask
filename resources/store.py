from flask_smorest import abort, Blueprint
from flask import request
from flask.views import MethodView
import uuid

from db import items, stores
from schema import StoreSchema

bp = Blueprint("stores", __name__, description="Operations on stores")


@bp.route("/store")
class StoreView(MethodView):

    @bp.response(200, StoreSchema(many=True))
    def get(self):
        return stores.values()

    @bp.arguments(StoreSchema)
    @bp.response(201, StoreSchema)
    def post(self, store_data):
        for store in stores.values():
            if store["name"] == store_data["name"]:
                abort(400, message="Store already exists!")
        store_id = uuid.uuid4().hex
        new_store = {**store_data, "id": store_id}
        stores[store_id] = new_store
        return new_store


@bp.route("/store/<string:store_id>")
class StoreDetailView(MethodView):

    @bp.response(200, StoreSchema)
    def get(self, store_id):
        store = stores.get(store_id)
        if not store:
            abort(404, message="Store not found!")
        return store

    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "Store deleted successfully"}, 200
        except KeyError:
            abort(404, message="Store not found!")
