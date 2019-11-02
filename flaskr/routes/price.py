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
from flaskr.models.Price import Price
from flaskr.models.Tax import Tax
from flaskr.models.Brand import Brand
from flaskr.models.Order_Status import Order_Status
from flaskr.models.Promotion_Code import Promotion_Code
from flaskr.models.Order import Order
from flaskr.models.OrderLine import OrderLine
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date
bp = Blueprint('price', __name__, url_prefix='/price')
@bp.route("/getPrice", methods=['POST'])
def getPrice():

    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'price.schema.json')
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
        with session_scope() as db_session:

            price = Price(
                        product_id = request.json.get('product_id'),
                        amount = request.json.get('amount')
                )
            db_session.add(price)

        return {
            'code': 200,
            'message': 'success'
        }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error' + db_error.args[0]
        }, 400


@bp.route("/viewPrice", methods=['GET'])
def viewPrice():

    try:
        with session_scope() as db_session:

            queryProduct = db_session.query(Price)

            totalitem =[]

            for item in queryProduct:
                myitem = {
                    "id": item.id,
                    "product_id": item.product_id,
                    "amount": item.amount
                }
                totalitem.append(myitem)
            totalitem = {
                "allitems": totalitem
            }
            return totalitem

        return {
            'code': 200,
            'message': 'success'
        }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

@bp.route("/delPrice", methods=['POST'])
def delPrice():

    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'delprice.schema.json')
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
        with session_scope() as db_session:

            queryProduct = db_session.query(Price).filter(Price.id == request.json.get('id')).one()

            db_session.delete(queryProduct)

        return {
            'code': 200,
            'message': 'success'
        }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400
