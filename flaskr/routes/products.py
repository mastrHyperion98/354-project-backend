import functools
import re
import os
from jsonschema import validate, draft7_format_checker
import jsonschema.exceptions
import json
import hashlib
import time

from flask import (
    Blueprint, g, request, session, current_app, session
)

from passlib.hash import argon2
from sqlalchemy.exc import DBAPIError
from sqlalchemy import or_
from flaskr.db import session_scope
from flaskr.models.Product import Product
from flaskr.models.Price import Price
from flaskr.routes.utils import login_required, not_login, cross_origin

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin(methods=['GET', 'POST', 'HEAD'])
@login_required
def createProduct():
    """Endpoint to add a new product to the system

    Returns:
        (str, int) -- Returns a tuple of the JSON object of the newly created product and a http status
                      code.
    """

    # Validate that only the valid Product properties from the JSON schema new_product.schema.json
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'new_product.schema.json')
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
            # Create a md5 of the time of insertion to be appended to the permalink
            md5 = hashlib.md5()
            md5.update(str(time.time()).encode('utf-8'))
            new_product = Product(name = request.json['name'],
                                  description = request.json['description'],
                                  quantity = request.json['stockQuantity'],
                                  category_id = request.json['categoryId'],
                                  user_id = session.get('user_id'),
                                  tax_id = request.json['taxId'],
                                  brand_id = request.json['brandId'],
                                  condition = request.json['condition'],
                                  permalink = request.json['name'].lower().translate(Product.permalink_translation_tab) + '-' + md5.hexdigest()[:5])

            # Adds the price to the product
            new_product.price.append(Price(amount=request.json['price']))
            
            db_session.add(new_product)

            # Commit new product to database making sure of the integrity of the relations.
            db_session.commit()

            return new_product.to_json(), 200
    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400
    
@bp.route("/<int:product_id>/addreview", methods =["POST"])
@login_required
def save(product_id):

    # Load json data from json schema to variable user_info.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'review.schema.json')
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
            #user_id = request.json.get("user_id")
            user_id = session['user_id']
            #product_id = request.json.get("product_id")

            comment = request.json.get("comment")
            score = request.json.get("score")

            # check if user has bought this product id
            queryOrder = db_session.query(Order).filter(Order.user_id == user_id)
            count = 0
            for item in queryOrder:
                queryOrderLine = db_session.query(OrderLine).filter(OrderLine.order_id == item.id)
                for lineitem in queryOrderLine:
                    if lineitem.product_id == product_id:
                        count = count + 1

            if count > 0:
                if score <= 5 and score >= 0:
                    myreview = review(
                            user_id = user_id,
                            #user_id = session['user_id'],
                            product_id = product_id,
                            comment = comment,
                            score = score
                            )
                    db_session.add(myreview)
                    #db_session.flush()

                    return {
                        "code": 200,
                        "message": myreview.to_json()
                    }, 200
                else:
                    return {
                        "code": 400,
                        "message": "Score has to be in range 0 to 5"
                    }, 400
            else:
                return {
                    "code": 400,
                    "message": "This user can't post review because he hasn't bought any of these products"
                }, 400

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400



@bp.route("/<int:product_id>/viewreview", methods =["GET"])
@login_required
def view(product_id):

    try:
        # Check if cart id exists with cart items
        with session_scope() as db_session:

            myreview = db_session.query(review)

            array=[]
            for item in myreview:
                if item.product_id == product_id:
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
