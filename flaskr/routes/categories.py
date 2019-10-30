from flask import (
    Blueprint, session
)

from flaskr.routes.utils import cross_origin
from flaskr.db import session_scope
from flaskr.models.Category import Category

bp = Blueprint('categories', __name__, url_prefix="/categories")

@bp.route('/<string:permalink>', methods=[ 'GET' ])
@cross_origin(methods=[ 'GET' ])
def get_category_by_permalink(permalink):
    with session_scope() as db_session:
        category = db_session.query(Category).filter(Category.permalink == permalink).one()

        if category is not None:
            return category.to_json(), 200
        else:
            return '', 404

@bp.route('/<string:permalink>/products', methods=[ 'GET' ])
@cross_origin(methods=[ 'GET' ])
def get_products_category_by_permalink(permalink):
    with session_scope() as db_session:
        category = db_session.query(Category).filter(Category.permalink == permalink).one()

        if category is not None:
            return {
                'products': [ product.to_json() for product in category.products]
            }, 200
        else:
            return '', 404