from flask import (
    Blueprint, session
)

from flaskr.routes.utils import cross_origin
from flaskr.db import session_scope
from flaskr.models.Category import Category

bp = Blueprint('categories', __name__, url_prefix="/categories")

@bp.route('', methods=[ 'GET', 'OPTIONS' ])
@cross_origin(methods=[ 'GET' ])
def get_categories():
    with session_scope() as db_session:
        categories = db_session.query(Category).all()

        if len(categories) > 0:
            return {
                'categories': [
                    category.to_json() for category in categories
                ]
            }, 200
        else:
            return {
                'categories': []
            }, 200

@bp.route('/<string:permalink>', methods=[ 'GET', 'OPTIONS' ])
@cross_origin(methods=[ 'GET' ])
def get_category_by_permalink(permalink):
    with session_scope() as db_session:
        category = db_session.query(Category).filter(Category.permalink == permalink.lower()).first()

        if category is not None:
            return category.to_json(), 200
        else:
            return '', 404

@bp.route('/exist/<string:permalink>', methods=[ 'GET', 'OPTIONS' ])
@cross_origin(methods=[ 'GET' ])
def does_category_exist(permalink):
    with session_scope() as db_session:
        category = db_session.query(Category).filter(Category.permalink == permalink.lower()).first()

        status_code = 404
        if category is not None:
            status_code = 200

        return '', status_code

@bp.route('/<string:permalink>/products', methods=[ 'GET', 'OPTIONS' ])
@cross_origin(methods=[ 'GET' ])
def get_products_category_by_permalink(permalink):
    with session_scope() as db_session:
        category = db_session.query(Category).filter(Category.permalink == permalink.lower()).first()

        if category is not None:
            return {
                'products': [ product.to_json() for product in category.products]
            }, 200
        else:
            return '', 404
