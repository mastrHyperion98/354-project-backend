from datetime import date

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from flaskr.db import Base
from flaskr.models.Product import Product

class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, Sequence('seq_user_id'), primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    reset_password = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    email = Column(String)
    is_admin = Column(Boolean, default=False)
    reset_password = Column(Boolean, default=False)
    date_joined = Column(Date, default=date.today())
    password = Column(String)
    addresses = Column(JSONB)
    cart = relationship('Cart', uselist=False)


    def to_json(self):
        """Returns the instance of user as a JSON

        Returns:
            dict -- JSON representation of the user
        """
        return {
            'username': self.username,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'dateJoined': self.date_joined,
            'resetPassword': self.reset_password,
            'addresses': self.addresses,
            'isAdmin' : self.is_admin
        }

