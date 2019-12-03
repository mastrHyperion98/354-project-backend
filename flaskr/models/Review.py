from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base
from flaskr.models.User import User
from flaskr.models.Product import Product

class Review(Base):
    __tablename__ = 'review'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    comment = Column(String)
    score = Column(Float)
    reply = Column(String)
    user = relationship('User')
    product = relationship('Product')

    def to_json(self):
        """Returns the instance of status as a JSON

        Returns:
            dict -- JSON representation of the order
        """
        return {
            'username': self.user.username,
            'comment': self.comment,
            'score': self.score,
            'reply': self.reply
        }
