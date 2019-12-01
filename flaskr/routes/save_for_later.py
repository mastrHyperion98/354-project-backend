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
from flaskr.models.Order import OrderLine
from flaskr.models.Order import Order
from flaskr.models.Order import OrderStatus
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User
from flaskr.models.Save_For_Later import save_product

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('save_for_later', __name__, url_prefix='/save_for_later')

@bp.route("/add", methods =["POST",'OPTIONS'])
@cross_origin(methods=['POST'])
@login_required
def save():

    # Load json data from json schema to variable user_info.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'save_for_later.schema.json')
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

            # get user_id from json
            # user_id = request.json.get("user_id")
            product_id = request.json.get("product_id")

            savedProduct = save_product(
                                        user_id = session['user_id'],
                                        product_id = product_id,
                                        date_saved = date.today()
                                        )
            db_session.add(savedProduct)
            return {
                "code": 200,
                "message": savedProduct.to_json()
            }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400



@bp.route("/view", methods =["GET",'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
def view():

    try:
        # Check if cart id exists with cart items
        with session_scope() as db_session:

            querySave = db_session.query(save_product)

            array=[]
            for item in querySave:
                if item.user_id == session['user_id']:
                    array.append(item.to_json())

            return {
                "code": 200,
                "message": array
            }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400


