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
from flaskr.models.Order import Order, OrderLine, OrderStatus
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User
from flaskr.models.Product import Product
from flaskr.models.Revenue import Revenue
from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('orders', __name__, url_prefix='/orders')

@bp.route("/mine", methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET'])
@login_required
def get_my_orders():

    try:
        with session_scope() as db_session:

            orders = db_session.query(Order).filter(Order.user_id == g.user.id)

            if orders.count() < 1:
                return {
                    'code': 404,
                    'message': 'User has no orders'
                }, 404

            return {'orders': [order.to_json() for order in orders.all()]}, 200

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

@bp.route("/<int:order_id>", methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET', 'PATCH'])
@login_required
def get_order(order_id):

    try:
        with session_scope() as db_session:

            order = db_session.query(Order).filter(Order.id == order_id).first()

            if order is None:
                return {
                    'code': 404,
                    'message': 'Order does not exist'
                }, 404

            if order.user_id != g.user.id:
                return {
                    'code': 403,
                    'message': 'Order does not belong to user.'
                }, 403

            return order.to_json(), 200

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

@bp.route("/<int:order_id>/items/<int:product_id>", methods=[ 'PATCH', 'OPTIONS' ])
@cross_origin(methods=['PATCH'])
@login_required
def update_order_line(order_id, product_id):
    # Validate that only the valid CartLine properties from the JSON schema cart_line.schema.json
    schemas_directory = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_directory, 'update_order_line_shipping_status.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }, 400

    with session_scope() as db_session:
        order_line = db_session.query(OrderLine).filter(OrderLine.order_id == order_id).filter(OrderLine.product_id == product_id).first()

        if order_line is None:
            return {
                'code': 404,
                'message': 'Order does not exist'
            }, 404

        if order_line.product.user_id != g.user.id:
             return {
                'code': 404,
                'message': 'Not products seller'
            }, 404

        order_line.date_fulfilled = request.json['dateFulfilled']

        send(current_app.config['SMTP_USERNAME'], order_line.buyer.email, "Shipping Notification", "<html><body><p>%s x %d has been shipped on %s</p></body></html>"%(order_line.product.name, order_line.quantity, str(order_line.date_fulfilled)) ,"%s x %d has been shipped on %s" % (order_line.product.name, order_line.quantity, str(order_line.date_fulfilled)))

        return '', 200


@bp.route("", methods=[ 'POST', 'OPTIONS' ])
@cross_origin(methods=['POST'])
@login_required
def create_order():
    # Validate that only the valid CartLine properties from the JSON schema cart_line.schema.json
    schemas_directory = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_directory, 'new_order.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }, 400
    # Create the order for the current cart
    try:
        with session_scope() as db_session:
            user = db_session.merge(g.user)
            cart = user.cart

            if cart is None:
                return {
                    'code': 400,
                    'message': 'User has no cart'
                }, 400

            if len(cart.cart_lines) == 0:
                return {
                    'code': 400,
                    'message': 'User cannot checkout an empty cart'
                }, 400

            order = Order(user_id=g.user.id, full_name=request.json['fullName'], line1=request.json['line1'], is_express_shipping=request.json['isExpressShipping'], city=request.json['city'], country=request.json['country'])

            if 'line2' in request.json:
                order.line2 = request.json['line2']

            total_cost = 0

            dict_sellers_items_sold = {}

            db_session.begin_nested()
            #Lock TABLE
            db_session.execute('LOCK TABLE product IN ROW EXCLUSIVE MODE')

            for line in cart.cart_lines:
                product = db_session.query(Product).filter(Product.id == line.product_id).with_for_update().one()

                order.order_lines.append(OrderLine(product_id=product.id, quantity=min(product.quantity, line.quantity), cost=line.cost))
                total_cost += order.order_lines[-1].cost

                dict_seller_items_sold = dict_sellers_items_sold.setdefault(product.user_id, {})
                dict_seller_items_sold['seller'] = line.product.user
                dict_seller_items_sold.setdefault('items', []).append((product, min(product.quantity, line.quantity)))

            order.total_cost = total_cost

            db_session.add(order)
            db_session.commit()

            db_session.query(CartLine).filter(CartLine.cart_id == cart.id).delete()

            items_bought = []
            for v in dict_sellers_items_sold.values():
                items_sold= []
                for item_sold in v['items']:
                    email_line = '%d x %s %.2f' % (item_sold[1], item_sold[0].name, item_sold[0].price)
                    items_sold.append(email_line)
                    items_bought.append(email_line)
                    item_sold[0].quantity -= item_sold[1]
                    # create a revenue entry for this product sold.
                    profits = computeProfit(item_sold[0].price, v['seller'].id)
                    revenue_entry = Revenue(seller_id= v['seller'].id, product_id=item_sold[0].id, order_id=order.id, profit=profits, purchased_on=order.date)
                    db_session.add(revenue_entry)
                    db_session.commit()

                send(current_app.config['SMTP_USERNAME'], v['seller'].email, "Sale Notification", "<html><body><p>Here is an overview of your sale:<ul><li>%s</li></ul></p></body></html>"%'</li><li>'.join(items_sold) ,'Here is an overview of your sale:\n%s'% '\n'.join(items_sold))

            send(current_app.config['SMTP_USERNAME'], g.user.email, "Purchase Notification", "<html><body><p>Here is an overview of your purchase:<ul><li>%s</li></ul></p></body></html>"%'</li><li>'.join(items_bought) ,'Here is an overview of your purchase:\n%s'% '\n'.join(items_bought))
            return order.to_json(), 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

def computeProfit(price, seller_id):
    try:
        with session_scope() as db_session:
            revenue_list = db_session.query(Revenue).filter(Revenue.seller_id == seller_id).all()
            fee_new = 0.03
            fee_normal = 0.08

            if len(revenue_list) <= 10:
                return "%.2f" % (float(price) * float(fee_new))
            else:
                return "%.2f" % (float(price) * float(fee_normal))

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
                   'code': 400,
                   'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
               }, 400

@bp.route("/view/<string:type>", methods=['GET', 'OPTIONS'])
@cross_origin(methods='GET')
@login_required
def view(type):

    try:
        with session_scope() as db_session:

            queryOrder = db_session.query(Order).filter(Order.user_id == session['user_id'])
            queryOrderLine = db_session.query(OrderLine)
            totalitem =[]

            for item in queryOrder:
                queryLine = item.order_lines
                myitem = item.to_json()

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
            return totalitem, 200

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
