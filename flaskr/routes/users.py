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
from flaskr.db import session_scope
from flaskr.models.User import User
from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('', methods=[ 'GET', 'HEAD' ])
@cross_origin(origin='*', methods=[ 'GET', 'HEAD' ])
@login_required
def listUsers():
    username = request.args.get('username')
    email = request.args.get('email')

    with session_scope() as db_session:
        query = db_session.query(User)
    
        if 'username' in request.args:
            query = query.filter(User.username == request.args.get('username'))
    
        if 'email' in request.args:
            query = query.filter(User.email == request.args.get('email'))
    
        if request.method == 'HEAD':
            if query.count() > 0:
                return '', 200
            else:
                return '', 400
        else:
            users = []
            for user in query.all():
                users.append(user.to_json())

            return {
                "users": users
            }, 400



@bp.route('', methods=['POST'])
@cross_origin(origin='*', methods=['POST'])
def registerUser():
    """Endpoint use to register a user to the system. Sends a welcoming
    
    Returns:
        (str, int) -- Returns a tuple of the JSON object of the newly register user and a http status code.
    """

    # Validate that only the valid User properties from the JSON schema update_self.schema.json
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'registration.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }

    new_user = User(first_name=request.json['firstName'], last_name=request.json['lastName'], username=request.json['username'], email=request.json['email'], password=argon2.hash(request.json['password']))


    try:
        with session_scope() as db_session:
            db_session.add(new_user)
    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

    session["user_id"] = new_user.id

    send(current_app.config['SMTP_USERNAME'], new_user.email, "Welcome to 354TheStars!", "<html><body><p>Welcome to 354TheStars!</p></body></html>" ,"Welcome to 354TheStars!")

    return new_user.toJSON(), 200

@bp.route('/self', methods=['GET'])
@cross_origin(origin='*', methods=['GET'])
@login_required
def showSelf():
    """Endpoint that returns the information of the authenticated user.
    
    Returns:
        str -- Returns a JSON object of the authenticated user.
    """
    return g.user.to_json(), 200

@bp.route('/self', methods=['PATCH'])
@cross_origin(origin='*', methods=['PATCH'])
@login_required
def updateSelf():
    """Endpoints to handle updating an authenticate user.
    
    Returns:
        str -- Returns a refreshed instance of user as a JSON or an JSON containing any error encountered.
    """

    # Validate that only the valid User properties from the JSON schema update_self.schema.json
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'update_self.schema.json')
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
            user = db_session.merge(g.user)

            # Update the values to the current User
            for k, v in request.json.items():
                user.__dict__[k] = v

            db_session.add(user)
            g.user = user
            db_session.expunge(g.user)
    except DBAPIError as db_error:
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }
    return g.user.to_json(), 200