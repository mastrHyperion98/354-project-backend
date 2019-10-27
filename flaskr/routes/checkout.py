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
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User
from flaskr.models.Order import Order
from flaskr.models.OrderLine import OrderLine
from flaskr.models.price import price

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('checkout', __name__, url_prefix='/checkout')

bp.route("/getorder")
@login_required
def getOrder():

    # Load json data from json schema to variable checkout.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['flaskr/schemas'])
    schema_filepath = os.path.join(schemas_direcotry, 'checkout.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=checkout.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }

    # Load json data from json schema to variable user_info.json 'SCHEMA_FOLDER'
    schema_filepath = os.path.join(schemas_direcotry, 'user_info.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=user_info.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }

    try:
        # Check if cart id exists with cart items
        with session_scope() as db_session:
            queryCart = db_session.query(Cart)
            queryCart = queryCart.filter(Cart.id == checkout.json.get('cart_id'))
            queryItem = db_session.query(CartLine)
            queryItem = queryItem.filter(CartLine.cart_id == checkout.json.get('cart_id'))

            total_price = 0
            for item in queryItem:
                cartID = item.data['cart_id']
                productID = item.data['product_id']
                quantity = item.data['quantity']

                # Get product price
                queryPrice = db_session.query(price).filter(price.product_id == productID).one()
                productPrice = float(queryPrice.data['amount'])

                # Create order line object
                order_line = OrderLine(order_id = cartID, product_id = productID, 
                                        quantity = quantity, price = productPrice)
                # Add to database
                db_session.add(order_line)

                # Calculate total price
                total_price = total_price + productPrice

            # Get json data from json object
            user_id = queryCart.one().data['user_id']
            date_fulfilled = user_info.json.get('date_fulfilled')
            status_id = user_info.json.get('status_id')
            fullname = user_info.json.get('fullname')
            line1 = user_info.json.get('line1')
            line2 = user_info.json.get('line2')
            city = user_info.json.get('city')
            country = user_info.json.get('country')
            phone = user_info.json.get('phone')
            
            # Create order object
            my_order = Order(
                            user_id = user_id,
                            date_fulfilled = date_fulfilled,
                            status_id = status_id,
                            fullname = fullname,
                            line1 = line1,
                            line2 = line2,
                            city = city,
                            country = country,
                            phone = phone,
                            total_cost = total_price
                            )
            # Add to database
            db_session.add(my_order)

            # Prepare to clear cart
            queryCart = db_session.query(Cart)
            queryCart = queryCart.filter(Cart.id == request.json.get('cart_id')).one()
            queryItem = db_session.query(CartLine)
            queryItem = queryItem.filter(CartLine.cart_id == request.json.get('cart_id'))

            # CLEAR CART
            db_session.delete(queryCart)
            db_session.delete(queryItem)


    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

bp.route("/checkout")
@login_required
def checkOut():

    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['flaskr/schemas'])
    schema_filepath = os.path.join(schemas_direcotry, 'checkout.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }

    productList=[]
    item_tmp=[]
    stringList=""

    try:    

    # Check if cart id exists with cart items
        with session_scope() as db_session:
            queryCart = db_session.query(Cart)
            queryCart = queryCart.filter(Cart.id == request.json.get('cart_id'))
            queryItem = db_session.query(CartLine)
            queryItem = queryItem.filter(CartLine.cart_id == request.json.get('cart_id'))

            if queryCart.count() > 0 and queryItem.count() > 0:
                queryCart = queryCart.one()

                # Get buyer's ID from Cart
                userID = queryCart.data['user_ID']

                # Find buyer with user ID
                queryUser = db_session.query(User).filter(User.id == userID)
                queryUser = queryUser.one()

                # Get buyer's email
                emailBuyer = queryUser.data['email']
                
                # iterate through list of items
                for item in queryItem:

                    # Get product by product ID
                    queryProduct = db_session.query(Product).filter(Product.id == item.data['product_ID'])

                    # Get Seller id
                    sellerID = queryProduct.one().data['user_ID']
                    # Get seller ID by user ID
                    sellerQuery = db_session.query(User).filter(User.id == sellerID).one()
                    # Get seller email
                    emailSeller = sellerQuery.data['email']
                    
                    # Get total quantity
                    total_quantity = int(queryProduct.one().data['quantity'])
                    # Get quantity purchased
                    purchased_quantity = int(item.data['quantity'])
                    # Get quantity left
                    left = total_quantity - purchased_quantity

                    # Get name of the product sold
                    productsold=str(queryProduct.one().data['name'])

                    # If quantity left is bigger than 0
                    if left > 0:

                        # SEND EMAIL to seller
                        send(current_app.config['SMTP_USERNAME'], emailSeller, "Welcome to 354TheStars!", "<html><body><p>"+productsold+":"+str(purchased_quantity)+" SOLD </p></body></html>" ,"Welcome to 354TheStars!")

                        # Update list of products sold with quantity
                        item_tmp=[]
                        item_tmp.append(productsold)
                        item_tmp.append(purchased_quantity)
                        productList.append(item_tmp)
                        stringList=stringList+"<p>"+ productsold + " has been purchased with quantity " + str(purchased_quantity) + "</p>"

                        # UPDATE QUANTITY in product table
                        data = queryProduct.data
                        data['quantity'] = left
                        queryProduct.data = data
                        db_session.merge(queryProduct)
                        db_session.flush()
                        db_session.commit()

                    # If quantity left is 0
                    elif left == 0:

                        # SEND EMAIL to seller
                        send(current_app.config['SMTP_USERNAME'], emailSeller, "Welcome to 354TheStars!", "<html><body><p>"+productsold+":"+str(purchased_quantity)+" SOLD </p></body></html>" ,"Welcome to 354TheStars!")

                        # Update list of products sold with quantity
                        item_tmp=[]
                        item_tmp.append(productsold)
                        item_tmp.append(purchased_quantity)
                        productList.append(item_tmp)
                        stringList=stringList+"<p>"+ productsold + " has been purchased with quantity " + str(purchased_quantity) + "</p>"


                        # REMOVE PRODUCT from product table
                        queryProduct=queryProduct.one() 
                        db_session.delete(queryProduct)
                        db_session.flush()
                        db_session.commit()

                    # If quantity left is less than 0 
                    elif left < 0:
                        return {
                            'code': 400,
                            'message': 'Quantity for product '+productsold+' is not sufficient to sell'
                        }, 400

                # SEND EMAIL to the buyer
                send(current_app.config['SMTP_USERNAME'], emailBuyer, "Welcome to 354TheStars!", "<html><body><p>Check out!</p>"+stringList+"</body></html>" ,"Welcome to 354TheStars!")

                return {
                    'cartID': request.json.get('cart_id')
                }, 200 

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

    


