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
from flaskr.models.Order import Order
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User
from flaskr.models.Review import review

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('review', __name__, url_prefix='/review')

@bp.route("/add", methods =["POST"])
@login_required
def save():

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
            user_id = request.json.get("user_id")
            product_id = request.json.get("product_id")
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
                            #user_id = user_id,
                            user_id = session['user_id'],
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
                        "message": "Score has to be in range 1 to 5"
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



@bp.route("/view", methods =["GET"])
@login_required
def view():

    try:
        # Check if cart id exists with cart items
        with session_scope() as db_session:

            myreview = db_session.query(review)

            array=[]
            for item in myreview:
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


