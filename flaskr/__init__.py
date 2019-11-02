from flask import Flask, session, g
from .Config import Config
from flaskr.db import session_scope
from flaskr.models.User import User

def create_app(test_config=None):
    #create and configure app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    @app.before_request
    def before_request():
        if 'user_id' in session:
            with session_scope() as db_session:
                query = db_session.query(User).filter(User.id==session.get('user_id'))
                if query.count() == 1:
                    user = query.one()
                    g.user = user
                    db_session.expunge(g.user)
        

    from flaskr.routes.users import bp as users
    app.register_blueprint(users) 

    from flaskr.routes.carts import bp as carts
    app.register_blueprint(carts)

    from flaskr.routes.checkout import bp as checkout
    app.register_blueprint(checkout)  

    from flaskr.routes.products import bp as products
    app.register_blueprint(products)

    from flaskr.routes.price import bp as price
    app.register_blueprint(price)

    from flaskr.routes.brand import bp as brand
    app.register_blueprint(brand)

    from flaskr.routes.order import bp as order
    app.register_blueprint(order)


    return app