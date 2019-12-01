from datetime import date

from sqlalchemy import update
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
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
            'date_created': self.date_created,
            'user_id': self.user_id,
            'lines': [line.to_json() for line in self.cart_lines]
        }

class CartLine(Base):
    __tablename__ = 'cart_line'

    cart_id = Column(Integer, ForeignKey('cart.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    quantity = Column(Integer)
    product = relationship('Product')

    @hybrid_property
    def cost(self):
        return self.product.price * self.quantity * (self.product.tax.rate + 1)

    def to_json(self):
        return {
            'quantity': self.quantity,
            'product': {
                'name': self.product.name,
                'id': self.product.id,
                'price': str(self.product.price),
                'permalink': self.product.permalink,
                'categoryPermalink': self.product.category.permalink
            }
        }
