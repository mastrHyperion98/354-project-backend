import functools

from flask import (
    Blueprint, g, request, session, current_app, session
)

from sqlalchemy.exc import DBAPIError
from flaskr.db import session_scope
from flaskr.models.Brand import Brand
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in

bp = Blueprint('brands', __name__, url_prefix="/brands")

@bp.route('', methods=[ 'GET', 'OPTIONS' ])
@cross_origin(methods=[ 'GET' ])
def get_brands():
    with session_scope() as db_session:
        brands = db_session.query(Brand).all()
        if len(brands) > 0:
            return {
                'brands': [ brand.to_json() for brand in brands ]
            }, 200
        else:
            return {
                'brands': []
            }, 200