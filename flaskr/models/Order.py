from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base
from flaskr.models.Promotions import promotion_code

class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, Sequence('seq_order_id'), primary_key=True)
    user_id = Column(String, ForeignKey('user.id'))
    date = Column(Date, default=date.today())
    date_fulfilled = Column(Date)
    status_id = Column(Integer, ForeignKey('order_status.id'))
    full_name = Column(String)
    line1 = Column(String)
    line2 = Column(String)
    is_express_shipping = Column(Boolean)
    city = Column(String)
    country = Column(String)
    phone = Column(String)
    total_cost = Column(Float)
    promotion_code_id = Column(Integer, ForeignKey('promotion_code.id'))
    user = relationship('User')

    order_line = relationship('OrderLine')
    order_status = relationship('order_status')
    promotion_code = relationship('promotion_code')

    def to_json(self):
        """Returns the instance of order as a JSON

        Returns:
            dict -- JSON representation of the order
        """
        return {
            'id': self.cart_id,
            'user_id': self.user_id,
            'date': self.date,
            'date_fulfilled': self.date_fulfilled,
            'status_id': self.status_id,
            'full_name': self.full_name,
            'line1': self.line1,
            'line2': self.line2,
            'city': self.city,
            'country': self.country,
            'phone': self.phone,
            'promotion_code_id': self.promotion_code_id
        }
