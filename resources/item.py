from flask_smorest import abort, Blueprint
from flask import request
from flask.views import MethodView
import uuid

from db import items, stores

bp = Blueprint("items", __name__, description="Operations on items")


@bp.route("/item")
class ItemView(MethodView):
    def get(self):
        return {"items": list(items.values())}, 200

    def post(self):
        item_data = request.get_json()
        if item_data["store_id"] not in stores:
            abort(404, message="Store not found!")
        if (
            "name" not in item_data
            or "price" not in item_data
            or "store_id" not in item_data
        ):
            abort(400, message="Missing required fields!")
        for item in items.values():
            if (
                item["name"] == item_data["name"]
                and item["store_id"] == item_data["store_id"]
            ):
                abort(400, message="Item already exists in this store!")
        item_id = uuid.uuid4().hex
        new_item = {**item_data, "id": item_id}
        items[item_id] = new_item
        return new_item, 201


@bp.route("/item/<string:item_id>")
class ItemDetailView(MethodView):
    def get(self, item_id):
        item = items.get(item_id)
        if not item:
            abort(404, message="Item not found!")
        return item, 200

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": "Item deleted successfully"}, 200
        except KeyError:
            abort(404, message="Item not found!")

    def put(self, item_id):
        updated_item_data = request.get_json()
        if item_id not in items:
            abort(404, message="Item not found!")
        if "name" not in updated_item_data or "price" not in updated_item_data:
            abort(400, message="Missing required fields!")
        items[item_id].update(updated_item_data)
        return {"Updated Item": items[item_id]}, 200
