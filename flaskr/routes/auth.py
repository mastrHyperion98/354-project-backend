import re
from flask import (
    Blueprint, g, session, request, current_app
)

from flaskr.routes.utils import login_required, not_login, cross_origin
from flaskr.db import session_scope
from flaskr.models.User import User
from flaskr.models.Cart import Cart, CartLine
from passlib.hash import argon2
from sqlalchemy.exc import DBAPIError
from jsonschema import validate, draft7_format_checker
import jsonschema.exceptions
import json
import os

bp = Blueprint('auth', __name__, url_prefix="/auth")

@bp.route('/login', methods=[ 'POST', 'OPTIONS' ])
@cross_origin(methods=[ 'POST' ])
def login():
    """Endpoint used to login a user.

    Returns:
        (dict, int) -- User JSON representation with 200 if login was successful, Error otherwise
    """

    # Verify content of the request.json sent by the client
    if 'user_id' in session:
        return {
            'code': 401,
            'message': 'Already logged in'
        }, 401

    # Validate that only the valid User properties from the JSON schema update_self.schema.json
    schemas_directory = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_directory, 'login.schema.json')
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
            query = db_session.query(User).filter(User.email==request.json['email'])

            if query.count() == 1:
                user = query.one()
                if argon2.verify(request.json['password'], user.password):

                    session['user_id'] = user.id

                    if 'cart_id' in session:
                        ephemeral_cart = db_session.query(Cart).filter(Cart.id == session['cart_id']).first()

                        if ephemeral_cart is not None:
                            if user.cart is None:
                                ephemeral_cart.user_id = user.id
                            else:
                                for ephemeral_cart_line in ephemeral_cart.cart_lines:
                                    cart_line = db_session.query(CartLine).filter(CartLine.cart_id == user.cart.id).filter(CartLine.product_id == ephemeral_cart_line.product_id).first()

                                    if cart_line is None:
                                        user.cart.cart_lines.append(CartLine(product_id=ephemeral_cart_line.product_id, quantity=ephemeral_cart_line.quantity))
                                    elif cart_line.product.quantity+ephemeral_cart_line <= cart_line.product.quantity:
                                        cart_line.quantity += ephemeral_cart.quantity

                        session.pop('cart_id')

                    return user.to_json(), 200
                else:
                    return {
                        'code': 400,
                        'message': 'Password is invalid.'
                    }, 400
            else:
                return {
                    'code': 400,
                    'message': 'Email is invalid.'
                }, 400
    except DBAPIError as db_error:

        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

@bp.route('/logout', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
def logout():
    """Endpoint use to logout a login user.

    Returns:
        (str, int) -- Empty string with 200 if logout was successful, Error otherwise
    """
    # Checks whether a user is session
    # if there is remove it
    if 'user_id' in session:
        session.pop('user_id')

    if 'cart_id' in session:
        session.pop('cart_id')

    # If a user is in the global
    # variable remove it
    if 'user' in g:
        g.pop('user')

    return '', 200
