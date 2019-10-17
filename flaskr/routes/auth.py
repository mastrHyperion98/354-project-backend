from flask import (
    Blueprint, g, session
)

from flaskr.routes.utils import login_required, not_login, cross_origin

bp = Blueprint('auth', __name__, url_prefix="/auth")

@bp.route('/login', methods=[ 'POST', 'OPTIONS' ])
@cross_origin(methods=[ 'POST' ])
def login():
    """Endpoint used to login a user.

    Returns:
        (dict, int) -- User JSON representation with 200 if login was successful, Error otherwise
    """
    
    # Verify content of the request.json sent by the client

    # If email and password not in query return 400 with {'code':400, 'message': 'Email and password do not match'}

    # If email and password matches add user_id to session

    # Send user.to_json() back to the client with 200

    return '', 200

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