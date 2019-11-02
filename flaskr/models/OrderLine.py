from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base

class OrderLine(Base):
    __tablename__ = 'order_line'

    id = Column(Integer, Sequence('seq_order_id'), primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer)
    cost = Column(Float)
    order = relationship('Order')
    product = relationship('Product')

    def to_json(self):
        """Returns the instance of order line as a JSON

        Returns:
            dict -- JSON representation of the order
        """
        return {
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }