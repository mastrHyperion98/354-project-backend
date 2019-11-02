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
from flaskr.models.Order_Status import Order_Status
from flaskr.models.Order import Order

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date
bp = Blueprint('order', __name__, url_prefix='/order')

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