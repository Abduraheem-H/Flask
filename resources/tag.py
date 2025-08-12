from sqlite3 import IntegrityError
from flask_smorest import abort, Blueprint
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TagModel, ItemModel
from schema import TagSchema, ItemAndTagSchema

bp = Blueprint("tags", __name__, description="Operations on tags")


@bp.route("/store/<store_id>/tag")
class TagInStore(MethodView):
    @bp.response(200, TagSchema(many=True))
    def get(self, store_id):
        try:
            all_tags = TagModel.query.filter_by(store_id=store_id).all()
            return all_tags
        except SQLAlchemyError:
            abort(500, message="Error occurred while fetching the Tags")

    @bp.arguments(TagSchema)
    @bp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="Error occurred while creating Tag")
        except IntegrityError:
            abort(400, message="Tag with this name already exists")
        return tag


@bp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @bp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if item.store_id != tag.store_id:
            abort(400, message="Item and Tag do not belong to the same store")
        item.tags.append(tag)
        try:

            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="Error occurred while inserting Tag to Item")
        return tag

    @bp.response(200, ItemAndTagSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if item.store_id != tag.store_id:
            abort(400, message="Item and Tag do not belong to the same store")

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="Error occurred while unlinking Tag from Item")
        return {"message": "Tag unlinked from Item"}


@bp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @bp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, message="Tag not found")
        return tag

    @bp.alt_response(
        202,
        description="Delete a tag if no items are associated",
        example={"message": "Tag deleted"},
    )
    @bp.alt_response(404, description="Tag not found")
    @bp.alt_response(
        400,
        description="Returned if a tag is associated with items. In this case, the tag cannot be deleted.",
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted"}
        abort(400, message="Tag is associated with items and cannot be deleted.")
