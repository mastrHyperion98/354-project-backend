from datetime import date

from sqlalchemy import update
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from flaskr.models.User import User
from flaskr.models.Product import Product
from flaskr.db import Base


class Cart(Base):
    __tablename__ = 'cart'

    id = Column(Integer, Sequence('seq_cart_id'), primary_key=True)
    date_created = Column(Date)
    user_id = Column(Integer, ForeignKey('user.id'))
    cart_lines = relationship('CartLine')

    user = relationship('User', back_populates='cart')

    def to_json(self):
        return {
            'id': self.id,
            'date_crated': self.date_created,
            'lines': [line.to_json() for line in self.cart_lines]
        }

class CartLine(Base):
    __tablename__ = 'cart_line'

    cart_id = Column(Integer, ForeignKey('cart.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    quantity = Column(Integer)
    product = relationship('Product')

    def to_json(self):
        return {
            'quantity': self.quantity,
            'product': {
                'name': self.product.name,
                'id': self.product.id,
                'price': self.product.price.first().to_json(),
                'permalink': self.product.permalink,
                'categoryPermalink': self.product.category.permalink
            }
        }
