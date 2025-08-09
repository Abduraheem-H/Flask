from flask_smorest import abort, Blueprint
from flask import request
from flask.views import MethodView
import uuid

from db import items, stores

bp = Blueprint("stores", __name__, description="Operations on stores")


@bp.route("/store")
class StoreView(MethodView):
    def get(self):
        return {"stores": list(stores.values())}, 200

    def post(self):
        store_data = request.get_json()
        if "name" not in store_data:
            abort(400, message="Missing required fields!")
        for store in stores.values():
            if store["name"] == store_data["name"]:
                abort(400, message="Store already exists!")
        store_id = uuid.uuid4().hex
        new_store = {**store_data, "id": store_id}
        stores[store_id] = new_store
        return new_store, 201


@bp.route("/store/<string:store_id>")
class StoreDetailView(MethodView):
    def get(self, store_id):
        store = stores.get(store_id)
        if not store:
            abort(404, message="Store not found!")
        return store, 200

    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "Store deleted successfully"}, 200
        except KeyError:
            abort(404, message="Store not found!")
