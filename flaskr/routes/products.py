import functools
import re
import os
from jsonschema import validate, draft7_format_checker
import jsonschema.exceptions
import json
import hashlib
import time
import base64
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
from flaskr.models.Category import Category


bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET', 'POST', 'HEAD'])
def getProducts():
    # Validate that only the valid Query properties from the JSON schema filter_product.schema.json
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'filter_product.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.args, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }, 400

    with session_scope() as db_session:
        products = db_session.query(Product)
        count = None
        if 'category' in request.args:
            category = db_session.query(Category).filter(Category.permalink == request.args['category']).first()
            if category is None:
                return {
                    'code': 404,
                    'message': 'Category not found'
                }, 404

            count = category.products.count()

            products = category.products

        if 'q' in request.args:
            tokens = request.args['q'].strip().split()
            or_instruction = []
            
            for token in tokens:
                or_instruction.append(Product.name.match(token))
                or_instruction.append(Product.description.match(token))

            products = db_session.query(Product).filter(or_(*or_instruction))

            count = products.count()

        if 'priceOrderFilter' in request.args:
            priceOrder = request.args['priceOrderFilter']

            if priceOrder == 'lowToHigh':
                products.order_by(Product.price.first().asc())
            elif priceOrder == 'highToLow':
                products.order_by(Product.price.first().desc())
        
        if count is None:
            count = products.count()

        products = products.limit(request.args['limit']).offset(int(request.args['limit'])*int(request.args['page']))

        return {'products':[ product.to_json() for product in products.all()], 'count': count}

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

@bp.route('/<string:permalink>', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET', 'HEAD'])
@login_required
def get_product_by_permalink(permalink):
    """Endpoint to get a product by permalink

    Returns:
        (str, int) -- Returns a tuple of the JSON object of the found product and a http status
                      code.
    """

    with session_scope() as db_session:
        product = db_session.query(Product).filter(Product.permalink == permalink.lower()).first()

        if product is not None:
            return product.to_json(), 200
        else:
            return '', 404

@bp.route('/uploads/<filename>', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
def uploaded_file(filename):
    """Endpoint for accessing uploaded files
    Returns:
    (str) -- Returns the requested file
    """
    try:
        with open(os.path.join(current_app.config['UPLOAD_FOLDER'], filename),'rb' ) as file:
            try:
                data = file.read()
                encoded_data = base64.encodebytes(data)
                file.close()
                return encoded_data

            except IOError as error:
                file.close()
                return {
                    'code': 400,
                    'message': "An unexpected IO error has occurred"
                }
    except FileNotFoundError as file_error:
        #Returns an error message saying file does not exist
        return{
            'code': 400,
            'message': filename + " does not exist"
        }, 400