from flask import (
    Blueprint, session
)

from flaskr.routes.utils import cross_origin
from flaskr.db import session_scope
from flaskr.models.Section import Section

bp = Blueprint('sections', __name__, url_prefix="/sections")

@bp.route('', methods=[ 'GET', 'OPTIONS' ])
@cross_origin(methods=[ 'GET' ])
def get_sections():
    with session_scope() as db_session:
        query = db_session.query(Section).all()
        if len(query) > 0:
            return {
                'sections': [ section.to_json() for section in query ]
            }, 200
        else:
            return {
                'sections': []
            }, 200