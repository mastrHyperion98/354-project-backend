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
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User
from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('carts', __name__, url_prefix='/carts')

@bp.route('', methods=[ 'POST', 'OPTIONS' ])
@cross_origin(methods=[ 'POST' ])
def create_cart():
    try:
        with session_scope() as db_session:
            cart = Cart()

            if is_logged_in():
                user = db_session.merge(g.user)
                cart.user_id = user.id
            else:
                # Carts a valid for a set period of time
                # they are delete afterwards.
                cart.date_created = date.today()

            db_session.add(cart)
            db_session.commit()
            session['cart_id'] = cart.id
            return cart.to_json(), 200
    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400


@bp.route('/mine', methods=[ 'GET', 'OPTIONS' ])
@cross_origin(methods=[ 'GET' ])
def get_mine():
    try:
        with session_scope() as db_session:
            if 'cart_id' in session:
                query = db_session.query(Cart).filter(Cart.id==session.get('cart_id'))

                if query.count() > 0:
                    cart = query.one()

                    if is_logged_in() and cart.user_id is None:
                        user = db_session.merge(g.user)
                        cart.user_id = user.id
                        # Remove the possibility to delete the cart
                        cart.date_created = None
                        db_session.commit()
                        session['cart_id'] = cart.id

                    return cart.to_json(), 200
                else:
                    session.pop('cart_id')
                    return {
                        'code': 400,
                        'message': 'Invalid cart_id'
                    }, 400
            else:
                if is_logged_in():
                    user = db_session.merge(g.user)

                    if user.cart is not None:
                        session['cart_id'] = user.cart.id
                        return user.cart.to_json(), 200

                return {
                    'code': 400,
                    'message': 'User has no cart'
                }, 400
    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

@bp.route('/mine/items', methods=[ 'POST', 'OPTIONS' ])
@cross_origin(methods=[ 'POST', 'PUT' ])
def add_item_to_mine():
    # Validate that only the valid CartLine properties from the JSON schema cart_line.schema.json
    schemas_directory = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_directory, 'cart_line.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }, 400
      
    #if 'cart_id' in session:
    if 'cart_id' in session:
        try:
            with session_scope() as db_session:
                product = db_session.query(Product).filter(Product.id==request.json['productId']).first()

                if product is None:
                    return {
                        'code': 404,
                        'message': "Product not found"
                    }, 404

                if product.quantity < request.json['quantity']:
                    return {
                        'code': 400,
                        'message': "Quantity requested exceeds actual quantity of product"
                    }, 400

                cart_line = CartLine(cart_id=session.get('cart_id'), product_id=request.json['productId'], quantity=request.json['quantity'])
                db_session.add(cart_line)

            return '', 200
        except DBAPIError as db_error:
            # Returns an error in case of a integrity constraint not being followed.
            return {
                'code': 400,
                'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
            }, 400
    else:
        return {
            'code': 400,
            'message': 'User has no cart'
        }, 400

@bp.route('/mine/items/<int:product_id>', methods=[ 'DELETE', 'OPTIONS' ])
@cross_origin(methods=[ 'DELETE' ])
def delete_item_from_mine(product_id):
    if 'cart_id' not in session:
        return {
            'code': 400,
            'message': 'No cart associated with the session'
        }, 400

    try:
        with session_scope() as db_session:
            query = db_session.query(CartLine).filter(CartLine.cart_id==session.get('cart_id')).filter(CartLine.product_id==product_id)

            if query.count() == 1:
                cart_line = query.one()
                db_session.delete(cart_line)
            else:
                session.pop('cart_id')
                return {
                    'code': 400,
                    'message': 'Invalid cart_id'
                }, 400
    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

    return '', 200

@bp.route('/mine/items', methods=[ 'PUT', 'OPTIONS' ])
@cross_origin(methods=[ 'PUT', 'POST' ])
def update_cart_line():
    if 'cart_id' not in session:
        return {
            'code': 400,
            'message': 'No cart associated with the session'
        }, 400

    try:
        with session_scope() as db_session:
            product = db_session.query(Product).filter(Product.id==request.json['productId']).first()

            if product.quantity < request.json['quantity']:
                return {
                    'code': 400,
                    'message': "Quantity requested exceeds actual quantity of product"
                }, 400


            query = db_session.query(CartLine).filter(CartLine.cart_id==session.get('cart_id')).filter(CartLine.product_id==request.json['productId'])
            if query.count() == 1:
                cart_line = query.one()
                cart_line.quantity = request.json['quantity']
                db_session.add(cart_line)
            else:
                cart_line = CartLine(cart_id=session.get('cart_id'), product_id=request.json['productId'], quantity=request.json['quantity'])
                db_session.add(cart_line)

        return '', 200
    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

    return '', 200
