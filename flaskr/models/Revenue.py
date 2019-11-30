from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Numeric, Boolean
from flaskr.db import Base
from datetime import date


class Revenue(Base):
    __tablename__ = 'revenue'

    id = Column(Integer, Sequence('seq_revenue_id'), primary_key=True)
    seller_id = Column(Integer, ForeignKey('user.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    order_id = Column(Integer, ForeignKey('order.id'))
    profit = Column(Numeric)
    purchased_on = Column(Date, default=date.today())
    

    def to_json(self):
        return {
            'seller_id': self.seller_id,
            'product_id': self.product_id,
            'order_id': self.order_id,
            'profit': self.profit.__float__(),
            'purchased_on': str(self.purchased_on)
        }
