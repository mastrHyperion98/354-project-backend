import functools
import re
import os
from jsonschema import validate, draft7_format_checker
import jsonschema.exceptions
import json

from flask import (
    Blueprint, g, request, session, current_app, session
)

from sqlalchemy.exc import DBAPIError
from sqlalchemy import or_
from flaskr.db import session_scope
from flaskr.email import send
from flaskr.models.User import User
from flaskr.routes.utils import login_required, not_login, cross_origin

bp = Blueprint('addresses', __name__, url_prefix='/addresses')
@bp.route('', methods=['PUT', 'OPTIONS'])
@login_required
@cross_origin(methods=['PUT'])
def addAddress():
    """Endpoint use to add a address to the user. Sends a welcoming

     Returns:
         (str, int) -- Returns a tuple of the JSON object of the newly add shipping addresses user and a http status code.
     """
    # Validate that only the valid User properties from the JSON schema update_self.schema.json
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'add_addresses.schema.json')
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
            user = db_session.merge(g.user)
            addresses = request.json
            user.addresses = addresses

            db_session.add(user)
            g.user = user
            db_session.expunge(g.user)
            db_session.merge(g.user)

    except DBAPIError as db_error:
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400

    return g.user.to_json(), 200
