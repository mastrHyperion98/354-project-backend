import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from flaskr.validation import required

Base = declarative_base()

class User(Base):
    properties = [
        {
            'key': 'firstName', 
            'name': 'First name',
            'rules': [required]
        }, 
        {
            'key': 'lastName',
            'name': 'Last name',
            'rules': [required]
        }, 
        {
            'key': 'email',
            'name': 'Email',
            'rules': [required]
        },
        {
            'key': 'password',
            'name': 'Password',
            'rules': [required]
        }, 
        {
            'key': 'username',
            'name': 'Username',
            'rules': [required]
        }
    ]

    __tablename__ = 'user'

    id = Column(Integer, Sequence('seq_user_id'), primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    date_joined = Column(Date, default=datetime.datetime.now())
    password = Column(String)
