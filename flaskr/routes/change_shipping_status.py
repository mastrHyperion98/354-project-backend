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
from flaskr.models.Product import Product
from flaskr.models.OrderLine import OrderLine
from flaskr.models.Price import Price
from flaskr.models.Order import Order
from flaskr.models.Order_Status import order_status
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('change_shipping_status', __name__, url_prefix='/change_shipping_status')

@bp.route("", methods =["POST"])
#@login_required
def change_shipping_status():

    # Load json data from json schema to variable user_info.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'change_shipping_status.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }

    try:
        # Check if cart id exists with cart items
        with session_scope() as db_session:

            # get order_id from json
            order_id = request.json.get("order_id")

            # get list of order line for order_id
            queryOrderLine = db_session.query(OrderLine).filter(OrderLine.order_id == order_id)

            productString = ""
            emailBuyer = ""
            shipped = []

            # loop through order line items
            for itemquery in queryOrderLine:
                queryProduct = db_session.query(Product).filter(Product.id == itemquery.product_id).one()

                f=""
                #if queryProduct.user_id == session["user_id"]:
                if f=="":
                    if itemquery.date_fulfilled is None:

                        # email content of shipped items
                        productName = queryProduct.name
                        productString = productString + "<p>" + productName + ", quantity: " + str(itemquery.quantity) + ";  </p>"
                        
                        # specify shipped date
                        itemquery.date_fulfilled = date.today()
                        #db_session.merge(itemquery)

                        # formulate return json
                        productShipped = {
                            "Product Name": productName,
                            "Quantity": itemquery.quantity
                        }
                        shipped.append(productShipped)
            db_session.flush()
            
            if productString!="" and len(shipped)>0:

                # get information of the buyer
                queryOrder = db_session.query(Order).filter(Order.id == order_id).one()
                queryUser = db_session.query(User).filter(User.id == queryOrder.user_id).one()
                emailBuyer = queryUser.email
                firstname = queryUser.first_name
                lastname = queryUser.last_name

                # send email to the buyer
                productString="<p>Ship Date: " + str(date.today()) + "; </p>" + productString
                send(current_app.config['SMTP_USERNAME'], emailBuyer, "Welcome to 354TheStars!", 
                    "<html><body><p>Items shipped!</p>"+productString+"</body></html>" ,
                    "Welcome to 354TheStars!")

                return {
                    "code": 200,
                    "message": "success",
                    "email sent to": emailBuyer,
                    "Shipped": shipped,
                    "Date": str(date.today()),
                    "To": firstname + " " + lastname
                }, 200
            
            else:
                return {
                    "code": 400,
                    "message": "error"
                }, 400


    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': 'error: ' + db_error.args[0]
        }, 400


    


