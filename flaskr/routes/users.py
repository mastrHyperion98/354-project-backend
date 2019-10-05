import functools

from flask import (
    Blueprint, g, request, session
)

from flaskr.db import get_db

from flaskr.models.User import User

from passlib.hash import argon2

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

def verifyPropertyExists(properties, json, error_code, error_message):
    for property in properties:
        if property["property_key"] not in json:
            return {
                "code": error_code,
                "message": error_message % property["property_name"]
            }

    return None

@bp.route('', methods=['POST'])
def registerUser():
    error = verifyPropertyExists(User.required_properties, request.json, 400, "%s is required")

    if error:
        return error, 400

    new_user = User(first_name=request.json['firstName'], last_name=request.json['lastName'], username=request.json['username'], email=request.json['email'], password=argon2.hash(request.json['password']))
    db = get_db()
    db.add(new_user)
    db.commit()
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