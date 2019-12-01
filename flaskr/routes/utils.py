from functools import wraps, update_wrapper
from flask import g, session, make_response, request, current_app
from flaskr.models.User import User
from flaskr.db import session_scope
import os
import base64
import uuid

def not_login(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return {
                'code': 400,
                'message': 'Forbidden Access'
            }, 400
        return func(*args, **kwargs)
    return decorated_function

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user' not in g:
            return {
                'code': 400,
                'message': 'Unauthorized Access'
            }, 400

        return func(*args, **kwargs)
    return decorated_function

def cross_origin(origin=os.environ.get('FLASK_ORIGIN') or '*', methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"], headers=["Origin", "X-Requested-With", "Content-Type", "Accept"]):
    def _cross_origin_factory(func):
        def _cross_origin(*args, **kwargs):
            if request.method != 'OPTIONS':
                response = make_response(func(*args, **kwargs))
            else:
                response = make_response()

            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = ", ".join(headers)
            response.headers["Access-Control-Allow-Methods"] = ", ".join(methods)
            # Tells the browser to expose the response to frontend when cross-origin cookies are transferred.
            response.headers["Access-Control-Allow-Credentials"] = "true"
            # Explicitly allows cross-site cookies. The 'Secure' directive doesn't actually work since we're
            # not on https.
            response.headers.add('Set-Cookie','SameSite=None; Secure')

            return response
        return update_wrapper(_cross_origin, func)
    return _cross_origin_factory

def is_logged_in():
    if 'user' in g:
        return True
    else:
        return False

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user' not in g:
            return {
                'code': 400,
                'message': 'Unauthorized Access'
            }, 400
        if not g.user.is_admin:
            return {
                'code': 400,
                'message': 'Unauthorized Access'
            }

        return func(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def convert_and_save(b64_string):
    imgdata = base64.decodebytes(b64_string.encode())
    fileid = str(uuid.uuid4())
    file_name = os.path.join(current_app.config['UPLOAD_FOLDER'], fileid)

    with open(file_name, "wb") as fh:
        fh.write(imgdata)

    return fileid