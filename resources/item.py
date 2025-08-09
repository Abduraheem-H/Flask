from flask_smorest import abort, Blueprint
from flask import request
from flask.views import MethodView
import uuid

from db import items, stores
from schema import ItemSchema, ItemUpdateSchema

bp = Blueprint("items", __name__, description="Operations on items")


@bp.route("/item")
class ItemView(MethodView):

    @bp.response(200, ItemSchema(many=True))
    def get(self):
        return items.values()

    @bp.arguments(ItemSchema)
    @bp.response(201, ItemSchema)
    def post(self, item_data):
        for item in items.values():
            if (
                item["name"] == item_data["name"]
                and item["store_id"] == item_data["store_id"]
            ):
                abort(400, message="Item already exists in this store!")
        item_id = uuid.uuid4().hex
        new_item = {**item_data, "id": item_id}
        items[item_id] = new_item
        return new_item


@bp.route("/item/<string:item_id>")
class ItemDetailView(MethodView):

    @bp.response(200, ItemSchema)
    def get(self, item_id):
        item = items.get(item_id)
        if not item:
            abort(404, message="Item not found!")
        return item

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": "Item deleted successfully"}, 200
        except KeyError:
            abort(404, message="Item not found!")

    @bp.arguments(ItemUpdateSchema)
    @bp.response(200, ItemSchema)
    def put(self, updated_item_data, item_id):
        try:
            item = items[item_id]
            item.update(updated_item_data)
            return item
        except KeyError:
            abort(404, message="Item not found!")
