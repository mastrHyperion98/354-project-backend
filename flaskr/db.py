from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import current_app, g
from flask.cli import with_appcontext
from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def new_session():
    if 'db_engine' not in g:
        g.db_engine = create_engine(current_app.config['DATABASE_URL'], echo=True)
        g.db_sessionmaker = sessionmaker(bind=g.db_engine)
    return g.db_sessionmaker()

def close_db():
    db_engine = g.pop('db_engine', None)

    if db_engine is not None:
        db_engine.close()

def init_app(app):
    app.teardown_appcontext(close_db)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = new_session()

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
