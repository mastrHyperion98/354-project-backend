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

    from flaskr.routes.reviews import bp as reviews
    app.register_blueprint(reviews)

    from flaskr.routes.carts import bp as carts
    app.register_blueprint(carts)

    from flaskr.routes.orders import bp as orders
    app.register_blueprint(orders)

    from flaskr.routes.products import bp as products
    app.register_blueprint(products)

    from flaskr.routes.auth import bp as auth
    app.register_blueprint(auth)

    from flaskr.routes.sections import bp as sections
    app.register_blueprint(sections)

    from flaskr.routes.categories import bp as categories
    app.register_blueprint(categories)

    from flaskr.routes.brands import bp as brands
    app.register_blueprint(brands)

    from flaskr.routes.account_recover import bp as recovery
    app.register_blueprint(recovery)

    from flaskr.routes.orders import bp as orders
    app.register_blueprint(orders)

    from flaskr.routes.addresses import bp as addresses
    app.register_blueprint(addresses)

    from flaskr.routes.sales import bp as sales
    app.register_blueprint(sales)

    from flaskr.routes.revenue import bp as revenue
    app.register_blueprint(revenue)
    
    from flaskr.routes.trending import bp as trending
    app.register_blueprint(trending)

    return app
