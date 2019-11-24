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

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in, admin_required
from datetime import date

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route("/sales", methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
@admin_required
def view_total_sales():
    # Later will add the ability to sort by date
    try:
        with session_scope() as db_session:

            orders = db_session.query(Order)

            if orders.count() < 1:
                return {
                    'code': 404,
                    'message': 'User has no orders'
                }, 404

            sum = 0
            #TO-DO-- ADD filtering by date
            for i in orders:
                sum = sum + i.total_cost

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400
    except NoResultFound:
        # Returns an error in case of a integrity constraint not being followed.
        return {
                   'code': 400,
                   'message': "No sales have been registered"
               }, 400
    return {
        'totalSales': sum,
           }, 200

