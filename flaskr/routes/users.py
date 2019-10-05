import functools
import re

from flask import (
    Blueprint, g, request, session
)

from flaskr.db import get_db

from flaskr.models.User import User

from passlib.hash import argon2

from flaskr.validation import validate

from sqlalchemy.exc import DBAPIError

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('', methods=['GET'])
def listUsers():
    ## TODO implement this endpoint
    return {
        "users": [
            {
                'firstName': 'firstName',
                'lastName': 'lastName',
                'email': 'email'
            },
            {
                'firstName': 'firstName',
                'lastName': 'lastName',
                'email': 'email'
            }
        ]
    }, 200



@bp.route('', methods=['POST'])
def registerUser():
    error = validate(User.properties, request.json)

    if error:
        return error, error["code"]

    new_user = User(first_name=request.json['firstName'], last_name=request.json['lastName'], username=request.json['username'], email=request.json['email'], password=argon2.hash(request.json['password']))
    db = get_db()

    db.add(new_user)

    try:
        db.commit()
    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400
    
    return {}, 200

@bp.route('/<string:username>', methods=['GET'])
def showUserByUsername(username):
    ## TODO implement this endpoint
    return {
        'firstName': 'firstName',
        'lastName': 'lastName',
        'email': 'email'
    }, 200

@bp.route('/self', methods=['GET'])
def showSelf():
    ## TODO implement this endpoint
    return {
        'firstName': 'firstName',
        'lastName': 'lastNme',
        'email': 'email'
    }, 200

@bp.route('/self', methods=['PATCH'])
def updateSelf():
    ## TODO implement this endpoint
        return {
        'firstName': 'firstName',
        'lastName': 'lastNme',
        'email': 'email'
    }, 200