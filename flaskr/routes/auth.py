from flask import (
    Blueprint, g, session
)

from flaskr.routes.utils import login_required, not_login, cross_origin

bp = Blueprint('auth', __name__, url_prefix="/auth")

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