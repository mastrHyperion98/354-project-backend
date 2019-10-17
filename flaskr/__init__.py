from flask import Flask
from .Config import Config
def create_app(test_config=None):
    #create and configure app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    from flaskr.routes.users import bp as users
    app.register_blueprint(users) 

    from flaskr.routes.auth import bp as auth
    app.register_blueprint(auth)
    
    return app