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
import datetime
from flaskr.models.SellerRecord import SellerRecord

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/sales', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
@admin_required
def view_total_sales():
    # Later will add the ability to sort by date and Category
    """Endpoint use to compute the total number of items sold between two dates.

         Returns:
             (str, int) -- Returns a string with the number of sales.
         """
    try:
        with session_scope() as db_session:
            orders = db_session.query(Order).all()

            if len(orders) < 1:
                return {
                    'code': 404,
                    'message': 'There are no sales'
                }, 404

            nmbr_itm = 0
            for order in orders:
                for items in order.order_lines:
                    nmbr_itm = nmbr_itm + items.quantity

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
        'numberItems': nmbr_itm
           }, 200

@bp.route('/sales/<string:start_date>', methods=['GET', 'OPTIONS'])
@bp.route('/sales/<string:start_date>/<string:end_date>', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
@admin_required
def view_total_sales_by_date(start_date, end_date= None):
    # Later will add the ability to sort by date and Category
    """Endpoint use to compute the total number of items sold between two dates.

         Returns:
             (str, int) -- Returns a string with the number of sales.
         """
    try:
        with session_scope() as db_session:
            if end_date is not None:
                if validate(start_date) and validate(end_date):
                    pass
                else:
                    return '', 404
                orders = db_session.query(Order).filter(Order.date.between(start_date, end_date)).all()
            else:
                if validate(start_date):
                    pass
                else:
                    return '', 404
                orders = db_session.query(Order).filter(Order.date == start_date).all()
            if len(orders) < 1:
                return {
                    'code': 404,
                    'message': 'There are no sales'
                }, 404

            nmbr_itm = 0
            for order in orders:
                for items in order.order_lines:
                    nmbr_itm = nmbr_itm + items.quantity

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
        'numberItems': nmbr_itm
           }, 200

@bp.route('/update/<string:username>', methods=['PATCH', 'OPTIONS'])
@cross_origin(methods=['PATCH', 'GET'])
@login_required
@admin_required
def admin_update_user(username):
    """"Endpoints to handle updating an authenticate user.
    Returns:
        str -- Returns a refreshed instance of user as a JSON or an JSON containing any error encountered.
    """

    # Validate that only the valid User properties from the JSON schema update_self.schema.json
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'admin_update_user.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }, 400

    try:
        with session_scope() as db_session:
            user = db_session.query(User).filter(User.username == username).one()
            db_session.expunge(user)
            email = request.json['email']
            for k, v in request.json.items():
                # if k == password hash password
                if k == "password":
                    user.__dict__[k] = argon2.hash(v)
                    user.reset_password = False
                else:
                    user.__dict__[k] = v
            db_session.merge(user)

        return user.to_json(), 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

@bp.route('/sales/leaderboard', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
@admin_required
def view_sales_leaderboard():
        # Later will add the ability to sort by date and Category
        """Endpoint use to compute the total number of items sold between two dates.

             Returns:
                 (str, int) -- Returns a string with the number of sales.
             """
        try:
            with session_scope() as db_session:
                # Added filters by date
                users = db_session.query(User).all()
                leaderboard = []
                for user in users:
                    username = user.username
                    sales = 0
                    products = db_session.query(Product).filter(Product.user_id == user.id).all()
                    for product in products:
                        order_lines = db_session.query(OrderLine).filter(OrderLine.product_id == product.id)
                        for order_line in order_lines:
                            sales = sales + order_line.quantity
                    seller = SellerRecord(username, sales)
                    leaderboard.append(seller)
                #Sort the entries
                leaderboard.sort()
                first_ten = []
                for i in range(min(10,len(leaderboard))):
                    first_ten.append(leaderboard[i].to_json())

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
        return{
            "top_sellers": first_ten
              }, 200

@bp.route('/sales/leaderboard/<string:start_date>', methods=['GET', 'OPTIONS'])
@bp.route('/sales/leaderboard/<string:start_date>/<string:end_date>', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
@admin_required
def view_sales_leaderboard_by_date(start_date, end_date= None):
        # Later will add the ability to sort by date and Category
        """Endpoint use to compute the total number of items sold between two dates.

             Returns:
                 (str, int) -- Returns a string with the number of sales.
             """
        try:
            with session_scope() as db_session:
                # Added filters by date
                users = db_session.query(User).all()
                leaderboard = []
                for user in users:
                    username = user.username
                    sales = 0
                    products = db_session.query(Product).filter(Product.user_id == user.id).all()
                    for product in products:
                        if end_date is not None:
                            if validate(start_date) and validate(end_date):
                                pass
                            else:
                                return '', 404
                            order_lines = db_session.query(OrderLine).filter(OrderLine.product_id == product.id, OrderLine.date_fulfilled.between(start_date,end_date))
                        else:
                            if validate(start_date):
                                pass
                            else:
                                return '', 404
                            order_lines = db_session.query(OrderLine).filter(OrderLine.product_id == product.id, OrderLine.date_fulfilled == start_date)

                        for order_line in order_lines:
                            sales = sales + order_line.quantity
                    seller = SellerRecord(username, sales)
                    leaderboard.append(seller)
                #Sort the entries
                leaderboard.sort()
                first_ten = []
                for i in range(min(10,len(leaderboard))):
                    first_ten.append(leaderboard[i].to_json())

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
        return{
            "top_sellers": first_ten
              }, 200

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return 0
    return 1
