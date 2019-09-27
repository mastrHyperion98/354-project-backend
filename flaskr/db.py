from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db_engine = create_engine(current_app.config['DATABASE_URL'], echo=True)
        g.db_session = sessionmaker(bind=g.db_engine)
    return g.db_session

def init_db():
    db = get_db()

def close_db():
    db_session = g.pop('db_session', None)

    if db_session is not None:
        db_session.close_all_sessions()

    db_engine = g.pop('db_engine', None)

    if db_engine is not None:
        db_engine.close()

def init_app(app):
    app.teardown_appcontext(close_db)