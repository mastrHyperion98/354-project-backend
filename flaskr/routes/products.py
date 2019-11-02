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
bp = Blueprint('products', __name__, url_prefix='/products')
@bp.route("/getBrand", methods=['POST'])
def getBrand():

    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'brand.schema.json')
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

            brand = Brand(
                            name = request.json.get('name'),
                            description = request.json.get('description'),
                            logo = request.json.get('logo')
                )
            db_session.add(brand)

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

@bp.route("/viewProduct", methods=['GET'])
def viewProduct():

    try:
        with session_scope() as db_session:

            queryProduct = db_session.query(Product)

            totalitem =[]

            for item in queryProduct:
                myitem = {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "quantity": item.quantity
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

@bp.route("/viewPromotion", methods=['GET'])
def viewPromotion():

    try:
        with session_scope() as db_session:

            queryPromotion = db_session.query(promotion_code)

            totalitem =[]

            for item in queryPromotion:
                myitem = {
                    "id": item.id,
                    "code": item.code,
                    "start_date": item.start_date,
                    "end_date": item.end_date
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

@bp.route("/viewOrder", methods=['GET'])
def viewOrder():

    try:
        with session_scope() as db_session:

            queryOrder = db_session.query(Order)

            totalitem =[]

            for item in queryOrder:
                myitem = {
                    "id": item.id,
                    "user_id": item.user_id,
                    "full_name": item.full_name,
                    "line1": item.line1,
                    "line2": item.line2,
                    "city": item.city,
                    "country": item.country,
                    "total_cost": item.total_cost
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


@bp.route("/getProduct", methods=['POST'])
def getProduct():

    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'product.schema.json')
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

            name = request.json.get('name')
            description = request.json.get('description')
            quantity = request.json.get('quantity')
            category_id = request.json.get('category_id')
            user_id = request.json.get('user_id')
            tax_id = request.json.get('tax_id')
            permalink = request.json.get('permalink')
            brand_id = request.json.get('brand_id')

            # Create order object
            product = Product(
                                name = name,
                                description = description,
                                quantity = quantity,
                                category_id = category_id,
                                user_id = user_id,
                                tax_id = tax_id,
                                permalink = permalink,
                                brand_id = brand_id
                            )
            # Add to database
            db_session.add(product)

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

@bp.route("/getTax", methods=['POST'])
def getTax():

    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'tax.schema.json')
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

            rate = request.json.get('rate')

            # Create tax object
            tax = Tax(
                        rate = rate,
            )
            # Add to database
            db_session.add(tax)

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

@bp.route("/getStatus", methods=['POST'])
def getStatus():

    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'getstatus.schema.json')
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

            status = request.json.get('status')

            # Create order status object
            od = Order_Status(
                status = status
            )
            # Add to database
            db_session.add(od)

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

@bp.route("/getPromotion", methods=['POST'])
def getPromotion():

    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'promotion.schema.json')
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

            code = request.json.get('code')

            # Create order status object
            promotion = Promotion_Code(
                code = code
            )
            # Add to database
            db_session.add(promotion)

        return {
            'code': 200,
            'message': 'success'
        }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400

    


