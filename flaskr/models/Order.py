from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Numeric, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, Sequence('seq_order_id'), primary_key=True)
    user_id = Column(String, ForeignKey('user.id'))
    date = Column(Date, default=date.today())
    date_fulfilled = Column(Date, default=None)
    status_id = Column(Integer, ForeignKey('order_status.id'),  default=1)
    full_name = Column(String)
    line1 = Column(String)
    line2 = Column(String)
    is_express_shipping = Column(Boolean, default=False)
    city = Column(String)
    country = Column(String)
    total_cost = Column(Numeric)
    user = relationship('User')

    order_lines = relationship('OrderLine')
    order_status = relationship('OrderStatus')

    def to_json(self):
        """Returns the instance of order as a JSON

        Returns:
            dict -- JSON representation of the order
        """
        return {
            'id': self.id,
            'date': self.date,
            'dateFulfilled': str(self.date_fulfilled),
            'status': self.order_status.to_json(),
            'fullName': self.full_name,
            'line1': self.line1,
            'line2': self.line2,
            'city': self.city,
            'country': self.country,
            'total_cost': str(self.total_cost),
            'orderLines': [ line.to_json() for line in self.order_lines]
        }


class OrderLine(Base):
    __tablename__ = 'order_line'

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    date_fulfilled = Column(Date)
    quantity = Column(Integer)
    cost = Column(Numeric)
    product = relationship('Product')

    order = relationship('Order')

    @hybrid_property
    def buyer(self):
        return self.order.user


    def to_json(self):
        """Returns the instance of order line as a JSON

        Returns:
            dict -- JSON representation of the order
        """
        return {
            'product': {
                'name': self.product.name,
                'permalink': self.product.permalink
            },
            'quantity': self.quantity,
            'cost': str(self.cost)
        }


class OrderStatus(Base):
    __tablename__ = 'order_status'

    id = Column(Integer, Sequence('seq_order_status_id'), primary_key=True)
    status = Column(String)

    def to_json(self):
        """Returns the instance of status as a JSON

        Returns:
            dict -- JSON representation of the order
        """
        return {
            'status': self.status
        }