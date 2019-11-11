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
from sqlalchemy import or_
from flaskr.db import session_scope
from flaskr.models.Product import Product
from flaskr.models.OrderLine import OrderLine
from flaskr.models.Price import Price
from flaskr.models.Order import Order
from flaskr.models.Order_Status import order_status
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('set_express_shipping', __name__, url_prefix='/set_express_shipping')

@bp.route("", methods =["POST"])
@login_required
def set_express_shipping():

    # Load json data from json schema to variable user_info.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'set_express_shipping.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }

    try:
        # Check if cart id exists with cart items
        with session_scope() as db_session:

            # get order_id from json
            order_id = request.json.get("order_id")

            # get list of order  for order_id
            queryOrder = db_session.query(Order).filter(Order.id == order_id).one()

            if queryOrder.user_id == session['user_id']:
                queryOrder.is_express_shipping = True
            else:
                return {
                    "code": 400,
                    "message": "wrong user_id"
                }, 400

            return {
                "code": 200,
                "message": "success"
            }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400


    


