import functools
import re
import os
from jsonschema import validate, draft7_format_checker
import jsonschema.exceptions
import json
from sqlalchemy.orm.exc import NoResultFound

from flask import (
    Blueprint, g, request, session, current_app, session
)

from passlib.hash import argon2
from sqlalchemy.exc import DBAPIError
from sqlalchemy import or_
from sqlalchemy.sql.functions import user

from flaskr.db import session_scope
from flaskr.email import send
from flaskr.models.User import User
from flaskr.models.Review import Review
from flaskr.models.Product import Product
from flaskr.models.Order import Order, OrderLine, OrderStatus
from flaskr.models.Cart import Cart, CartLine
from flaskr.routes.utils import login_required, not_login, cross_origin, admin_required

bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin(methods=['POST'])
@login_required
def review():

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
        }, 400

    try:
        # Check if cart id exists with cart items
        with session_scope() as db_session:
            # check if user has bought this product id
            queryOrder = db_session.query(Order).filter(Order.user_id == g.user.id)

            product = None
            for item in queryOrder:
                queryOrderLine = db_session.query(OrderLine).filter(OrderLine.order_id == item.id)
                for lineitem in queryOrderLine:
                    if lineitem.product.permalink == request.json.get("productPermalink").lower():
                        product = lineitem.product


            if product is not None:
                myreview = Review(user_id = g.user.id,
                        product_id = product.id,
                        comment = request.json.get("comment"),
                        score = request.json.get("score")
                        )
                db_session.add(myreview)
                db_session.commit()
                #db_session.flush()

                return {
                    "code": 200,
                    "message": myreview.to_json()
                }, 200
            else:
                return {
                    "code": 400,
                    "message": "User hasn't bought this product"
                }, 400

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400

@bp.route('/able/<string:permalink>', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
def can_review_product(permalink):
    # Check if cart id exists with cart items
    with session_scope() as db_session:
        # check if user has bought this product id
        queryOrder = db_session.query(Order).filter(Order.user_id == g.user.id)

        for item in queryOrder:
            queryOrderLine = db_session.query(OrderLine).filter(OrderLine.order_id == item.id)
            for lineitem in queryOrderLine:
                if lineitem.product.permalink == permalink.lower():
                    return '', 200

        return '', 400

@bp.route('/reply/<string:username>', methods=['POST', 'OPTIONS'])
@cross_origin(methods=['POST'])
@login_required
def replyreview(username):

    # Load json data from json schema to variable user_info.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'replyreview.schema.json')
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
                rev_id = db_session.query(User).filter(User.username == username).one().id
                myreview = db_session.query(Review).filter(Review.user_id == rev_id, Review.product_id == request.json['product_id']).one()


                if myreview.user_id != session['user_id']:
                    return {
                        'code': 400,
                        'message': 'this user cant reply to this review'
                    }, 400
                else:
                    if myreview.reply is not None or myreview.reply == "":
                        return {
                            'code': 400,
                            'message': 'You have already replied to this review'
                        }, 400
                    else:
                        myreview.reply = request.json.get("reply")
                        return {
                            'code': 200,
                            'message': myreview.to_json()
                        }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400

@bp.route('/view/<string:username>', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
def viewreview(username):

    try:
        # Check if cart id exists with cart items
        with session_scope() as db_session:
            rev_user = db_session.query(User).filter(User.username == username).first()
            myreview = db_session.query(Review)

            if rev_user is None:
                return '', 400
            rev_user_id = rev_user.id

            array=[]
            score = 0
            num_reviews = 0
            for item in myreview:
                if item.product.user_id == rev_user_id:
                    score = score + item.score
                    array.append(item.to_json())
                    num_reviews = num_reviews + 1

            if num_reviews != 0:
                score = "%.2f" % (score / num_reviews)

            return {
                "code": 200,
                "score": score,
                "message": array
            }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400


@bp.route('/view/product/<string:permalink>', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
def viewreview_product(permalink):
    try:
        # Check if cart id exists with cart items
        with session_scope() as db_session:
            product = db_session.query(Product).filter(Product.permalink == permalink).first()

            if product is None:
                return '', 400

            product_id = product.id
            myreview = db_session.query(Review).filter(Review.product_id == product_id)

            array=[]
            score = 0
            num_reviews = len(myreview.all())
            for item in myreview:
                score = score + item.score
                array.append(item.to_json())

            if num_reviews != 0:
                score = "%.2f" % (score / num_reviews)

            return {
                "code": 200,
                "score": score,
                "message": array
            }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400


