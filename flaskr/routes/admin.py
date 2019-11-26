import functools
import re
import os
from jsonschema import validate, draft7_format_checker
import strict_rfc3339
import jsonschema.exceptions
import json

from flask import (
    Blueprint, g, request, session, current_app, session
)

from passlib.hash import argon2
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from datetime import datetime, timedelta
from flaskr.db import session_scope
from flaskr.models.Order import Order, OrderLine, OrderStatus
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User
from flaskr.models.Product import Product

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in, admin_required
from datetime import date

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route("/sales/<string:category>", methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
@admin_required
def view_total_sales(category):
    # Later will add the ability to sort by date and Category
    """Endpoint use to add a address to the user. Sends a welcoming

         Returns:
             (str, int) -- Returns a tuple of the JSON object of the newly added addresses and a http status code.
         """

    # Validate that only the valid User properties from the JSON schema update_self.schema.json
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'get_total_sales.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=strict_rfc3339)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
                   'code': 400,
                   'message': validation_error.message
               }, 400
    try:
        with session_scope() as db_session:
            fromDate = datetime.strptime(request.json.get("start_date"), '%Y-%m-%d')
            endDate = datetime.strptime(request.json.get("end_Date"), '%Y-%m-%d') + timedelta(days=1)
            #Added filters by date
            orders = db_session.query(Order).filter(Order.date >= fromDate, Order.date < endDate).all()


            if orders.count() < 1:
                return {
                    'code': 404,
                    'message': 'There are no sales'
                }, 404
            "if all string than fetch all sales data"
            if category == "all":
                sum = 0
                for i in orders:
                    sum = sum + i.total_cost
            #iterate through orderlines and filter by categories


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
