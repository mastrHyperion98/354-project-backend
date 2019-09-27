import functools

from flask import (
    Blueprint, g, request, session
)

from flaskr.db import get_db

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
    ## TODO implement this endpoint
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