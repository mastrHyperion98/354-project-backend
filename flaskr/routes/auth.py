from flask import (
    Blueprint, g, session
)

from flaskr.routes.utils import login_required, not_login, cross_origin
from flaskr.db import session_scope
from flaskr.models.user import User
from passlib.hash import argon2

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
            'code': 400,
            'message': 'Already logged in'
        }, 400

    if 'email' in request.json and 'password' in request.json:
        email = request.json['email']
        password = request.json['password']
    try:
        with session_scope() as db_session:
            query = db_session.query(User).filter(User.email==email).filter(User.password==argon2(password))

            if query.count() == 1:
                user = query.one()
                session['user_id'] = user.id 
                return user.to_json(), 200
            else:
                # error return 400 
                return {
                    'code': 400,
                    'message': 'User not found'
                }
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

    # If the session is empty
    # make sure to remove any
    # data.
    if len(session) <= 0:
        session.clear()

    # If a user is in the global
    # variable remove it
    if 'user' in g:
        g.pop('user')

    return '', 200