import functools
import re
import os
from jsonschema import validate, draft7_format_checker
import jsonschema.exceptions
import json

from flask import (
    Blueprint, g, request, session, current_app, session
)

from passlib.hash import argon2
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from flaskr.db import session_scope
from flaskr.models.Order import Order, OrderLine, OrderStatus
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User
from flaskr.models.Product import Product
from flaskr.models.Review import Review

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in, admin_required
from datetime import datetime, timedelta
from flaskr.routes.reviews import viewreview
from flaskr.models.ProductRecord import ProductRecord

bp = Blueprint('trending', __name__, url_prefix='/trending')


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
def view_trending_by_week():
        # Later will add the ability to sort by date and Category
        """Endpoint use to compute the total number of items sold between two dates.

             Returns:
                 (str, int) -- Returns a string with the number of sales.
             """
        try:
            with session_scope() as db_session:
                # Added filters by date
                result = db_session.execute('SELECT product.id, SUM(order_line.quantity) AS sales, AVG(review.score) AS avg_score FROM product JOIN "user" ON "user".id = product.user_id LEFT JOIN review ON review.product_id = product.id JOIN order_line ON order_line.product_id = product.id GROUP BY product.id HAVING AVG(review.score) >= 3.5 OR AVG(review.score) IS NULL ORDER BY avg_score, sales DESC LIMIT 10;')


                products = db_session.query(Product).filter(Product.id.in_((r['id'] for r in result))).all()

                return {'products': [product.to_json() for product in products]}, 200
        except DBAPIError as db_error:
            # Returns an error in case of a integrity constraint not being followed.
            return {
                       'code': 400,
                       'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
                   }, 400
