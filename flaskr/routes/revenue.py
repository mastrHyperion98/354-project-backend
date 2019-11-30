import functools
import datetime
from flask import (
    Blueprint, g, request, session, current_app, session
)

from sqlalchemy.exc import DBAPIError
from flaskr.db import session_scope
from flaskr.models.Revenue import Revenue
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in, admin_required

bp = Blueprint('revenue', __name__, url_prefix="/revenue")

@bp.route('', methods=[ 'GET', 'OPTIONS' ])
@cross_origin(methods=[ 'GET' ])
@admin_required
def get_revenue():
    with session_scope() as db_session:
        # TODO check if website owner
        revenue_enteries = db_session.query(Revenue).all()
        if len(revenue_enteries) > 0:
            return {
                'revenue_enteries': [ revenue.to_json() for revenue in revenue_enteries],
                'revenue': calc_revenue(revenue_enteries).__float__()
            }, 200
        else:
            return {
                'revenue_enteries': [],
                'revenue': calc_revenue(revenue_enteries).__float__()
            }, 200

@bp.route('<string:start_date>', methods=[ 'GET', 'OPTIONS' ])
@bp.route('<string:start_date>/<string:end_date>', methods=[ 'GET', 'OPTIONS' ])
@cross_origin(methods=[ 'GET' ])
@admin_required
def get_revenue_by_date(start_date, end_date= None):
    with session_scope() as db_session:
        # TODO check if website owner
        revenue_enteries = []
        if end_date is not None:
            if validate(start_date) and validate(end_date):
                pass
            else:
                return '',404
            revenue_enteries = db_session.query(Revenue).filter(Revenue.purchased_on.between(start_date, end_date)).all()
        else:
            if validate(start_date):
                pass
            else:
                return '',404
            revenue_enteries = db_session.query(Revenue).filter(Revenue.purchased_on == start_date).all()
        if len(revenue_enteries) > 0:
            return {
                'revenue_enteries': [ revenue.to_json() for revenue in revenue_enteries ],
                'revenue': calc_revenue(revenue_enteries).__float__()
            }, 200
        else:
            return {
                'revenue_enteries': [],
                'revenue': 0
            }, 200

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return 0
    return 1

def calc_revenue(revenue_enteries):
    amount = 0
    for revenue in revenue_enteries:
        amount += revenue.profit
    return amount
