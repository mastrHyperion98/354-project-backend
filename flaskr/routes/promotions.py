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
from flaskr.models.Promotions import promotion_code
from flaskr.models.Order import Order
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('promotions', __name__, url_prefix='/promotions')

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
            promotion = promotion_code(
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