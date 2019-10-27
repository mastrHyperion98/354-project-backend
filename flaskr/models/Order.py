from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from flaskr.db import Base
from flaskr.models.User import User
from flaskr.models.order_status import order_status


class Order(Base):

    __tablename__ = 'order'

    id = Column(Integer, Sequence('seq_user_id'), primary_key=True)
    user_id = Column(String, ForeignKey(user.id))
    date = Column(Date, default=date.today())
    date_fulfilled = Column(Date)
    status_id = Column(Integer, ForeignKey(order_status.id))
    fullname = Column(String)
    line1 = Column(String)
    line2 = Column(String)
    city = Column(String)
    country = Column(String)
    phone = Column(String)
    user = relationship('User')
    order_status = relationship('order_status')

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
            'fullname': self.fullname,
            'line1': self.line1,
            'line2': self.line2,
            'city': self.city,
            'country': self.country,
            'phone': self.phone
        }