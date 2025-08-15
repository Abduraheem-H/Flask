from flask_smorest import abort, Blueprint
from flask_jwt_extended import jwt_required
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError


from db import db
from models.item import ItemModel
from schema import ItemSchema, ItemUpdateSchema

bp = Blueprint("items", __name__, description="Operations on items")


@bp.route("/item")
class ItemView(MethodView):

    @bp.response(200, ItemSchema(many=True))
    @jwt_required()
    def get(self):
        try:
            items = ItemModel.query.all()
            return items
        except SQLAlchemyError:
            abort(500, message="Error occurred while fetching items")

    @jwt_required()
    @bp.arguments(ItemSchema)
    @bp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="Error occured while creating item")
        return item


@bp.route("/item/<string:item_id>")
class ItemDetailView(MethodView):

    @jwt_required(fresh=True)
    @bp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            item = ItemModel.query.get(item_id)
            if not item:
                abort(404, message="Item not found!")
            return item
        except SQLAlchemyError:
            abort(500, message="Error occurred while fetching item")

    @jwt_required(fresh=True)
    def delete(self, item_id):
        try:
            item = ItemModel.query.get(item_id)
            if not item:
                abort(404, message="Item not found!")
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item deleted successfully"}, 200
        except SQLAlchemyError:
            abort(500, message="Error occurred while deleting item")

    @jwt_required(fresh=True)
    @bp.arguments(ItemUpdateSchema)
    @bp.response(200, ItemSchema)
    def put(self, updated_item_data, item_id):
        try:
            item = ItemModel.query.get(item_id)
            if not item:
                item = ItemModel(id=item_id, **updated_item_data)
                db.session.add(item)
            else:
                for key, value in updated_item_data.items():
                    setattr(item, key, value)
            db.session.commit()
            return item
        except SQLAlchemyError:
            abort(500, message="Error occurred while updating item")
