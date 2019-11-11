import functools
import random
import string
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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from flaskr.db import session_scope
from flaskr.models.User import User
from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin

bp = Blueprint('account_recovery', __name__, url_prefix='/recover')

@bp.route("",methods=['POST'])
def recoverAccount():
    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'account_recover.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)

    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }, 400

    try:
        with session_scope() as db_session:
            # Check if the user is logged in, if so log the user out.
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
                
            tmp_password = ''
            # create a random sequence of length 32. A mix of letters and digits.
            for x in range(32):
                if random.randint(0,11) <= 5:
                    tmp_password = tmp_password + random.choice(string.ascii_letters)
                else:
                    tmp_password= tmp_password + random.choice(string.digits)
            #Fetch the provided email address
            email = request.json.get("email")
            # fetch the user account to whom the email belongs
            query_user = db_session.query(User).filter(User.email == email).one()
            query_user.password = argon2.hash(tmp_password)
            query_user.reset_password = True
            #Apply changes to the database
            db_session.commit()
            #send(current_app.config['SMTP_USERNAME'], email, "354TheStarts Account Password Recovery"
              #   , "<html><body><p> You have been provided a temporary password: "+tmp_password+"</p></body></html>",
              #   "Thank you for using our platform and remember to login and change your password!")

        return{
            'code':200,
            "message": "success"
        }, 200

    except DBAPIError as db_error:
         # Returns an error in case of a integrity constraint not being followed.
            return {
                   'code': 400,
                   'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
                }, 400
    # return an error if the email does not match anything in the database
    except NoResultFound:
        # Returns an error in case of a integrity constraint not being followed.
        return {
                   'code': 400,
                   'message':"There exists no users with the email: " + email
               }, 400