from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.dialects.postgresql import JSONB
import datetime

Base = declarative_base()

class User(Base):
    required_properties = [
        {
            'property_key': 'firstName', 
            'property_name': 'First name', 
        }, 
        {
            'property_key': 'lastName',
            'property_name': 'Last name'
        }, 
        {
            'property_key': 'email',
            'property_name': 'Email'
        },
        {
            'property_key': 'password',
            'property_name': 'Password'
        }, 
        {
            'property_key': 'username',
            'property_name': 'Username'
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
