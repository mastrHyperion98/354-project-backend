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
from sqlalchemy import or_
from flaskr.db import session_scope
from flaskr.models.Order_Status import order_status
from flaskr.models.Order import Order
from flaskr.models.OrderLine import OrderLine
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('orders', __name__, url_prefix='/orders')

@bp.route("/view/<string:type>", methods=['GET'])
@login_required
def view(type):

    try:
        with session_scope() as db_session:

            queryOrder = db_session.query(Order).filter(Order.user_id == session['user_id'])
            #queryOrder = db_session.query(Order).filter(Order.user_id == 1)
            queryOrderLine = db_session.query(OrderLine)
            totalitem =[]

            for item in queryOrder:
                queryLine = queryOrderLine.filter(OrderLine.order_id == item.id)
                myitem = {
                    "id": item.id,
                    #"user_id": session['user_id'],
                    "user_id": item.user_id,
                    "full_name": item.full_name,
                    "line1": item.line1,
                    "line2": item.line2,
                    "city": item.city,
                    "is_express_shipping": item.is_express_shipping,
                    "country": item.country,
                    "total_cost": item.total_cost
                }

                line=[]
                if type=="complete":
                    for itemline in queryLine:
                        if itemline.order_id == item.id and itemline.date_fulfilled != None:
                            myline = {
                                "id": itemline.order_id,
                                "product_id": itemline.product_id,
                                "quantity": itemline.quantity,
                                "fulfilled": itemline.date_fulfilled,
                                "price": float(itemline.cost)
                            }
                            line.append(myline)
                elif type=="pending":
                    for itemline in queryOrderLine:
                        if itemline.order_id == item.id and itemline.date_fulfilled is None:
                            myline = {
                                "id": itemline.order_id,
                                "product_id": itemline.product_id,
                                "quantity": itemline.quantity,
                                "fulfilled": itemline.date_fulfilled,
                                "price": float(itemline.cost)
                            }
                            line.append(myline)
                elif type=="all":
                    for itemline in queryOrderLine:
                        if itemline.order_id == item.id:
                            myline = {
                                "id": itemline.order_id,
                                "product_id": itemline.product_id,
                                "quantity": itemline.quantity,
                                "fulfilled": itemline.date_fulfilled,
                                "price": float(itemline.cost)
                            }
                            line.append(myline)

                
                itemelement={
                    "order": myitem,
                    "order_line": line
                }
                if len(line) > 0:
                    totalitem.append(itemelement)
            totalitem = {
                "allitems": totalitem
            }
            return totalitem

        return {
            'code': 200,
            'message': 'success'
        }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400
