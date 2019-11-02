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
            new_product = Product(name = request.json['name'],
                                  description = request.json['description'],
                                  quantity = request.json['stockQuantity'],
                                  category_id = request.json['categoryId'],
                                  user_id = request.json['userId'],
                                  tax_id = request.json['taxId'],
                                  brand_id = request.json['brandId'],
                                  condition = request.json['condition'])
            db_session.add(new_product)

            # Commit new product to database making sure of the integrity of the relations.
            db_session.commit()

            # Add the ID to the end of the permalink.
            new_product.permalink = request.json['permalink'] + '-' + new_product.id

            return new_product.to_json(), 200
    except DBAPIError as db_error:

        # In case that the unvalid user was login remove it from session
        if 'user_id' in session:
            session.pop('user_id')

        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400
