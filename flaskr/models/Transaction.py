from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from flaskr.db import Base
from flaskr.models.Product import Product

class Transaction(Base):

    __tablename__ = 'user'

    id = Column(Integer, Sequence('seq_user_id'), primary_key=True)
    cart_id = Column(String, ForeignKey(cart.id))
    date_transation = Column(Date, default=date.today())
    cart = relationship('Cart')

    def to_json(self):
        """Returns the instance of user as a JSON
        
        Returns:    
            dict -- JSON representation of the user
        """
        return {
            'cart_id': self.cart_id,
            'date_transaction': self.date_transaction
        }