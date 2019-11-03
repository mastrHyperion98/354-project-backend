from datetime import date

from sqlalchemy.orm import relationship
from flaskr.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Numeric

class Price(Base):
    __tablename__ = 'price'

    id = Column(Integer, Sequence('seq_price_id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    start_date = Column(Date, default=date.today())
    end_date = Column(Date)
    amount = Column(Numeric)

    def to_json(self):
        return {
            'id': self.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'amount': str(self.amount)
        }