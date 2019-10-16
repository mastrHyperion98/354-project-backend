from flask import (
    Blueprint, g, session
)

from flaskr.routes.utils import login_required, not_login, cross_origin

bp = Blueprint('auth', __name__, url_prefix="/auth")

@bp.route('/logout', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
def logout():
    if 'user_id' in session:
        session.pop('user_id')

    if len(session) <= 0:
        session.clear()

    if 'user' in g:
        g.pop('user')

    return '', 200