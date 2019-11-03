from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base

class Price(Base):
    __tablename__ = 'price'

    id = Column(Integer, Sequence('seq_price_id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    start_date = Column(Date, default=date.today())
    end_date = Column(Date, default=date.today())
    amount = Column(Float)

    product = relationship('Product')

    def to_json(self):
        """Returns the instance of price as a JSON

        Returns:
            dict -- JSON representation of the order
        """
        return {
            'product_id': self.product_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'amount': self.amount
        }