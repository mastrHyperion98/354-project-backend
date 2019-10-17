from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base

class Product(Base):

    __tablename__ = 'product'

    id = Column(Integer, Sequence('seq_product_id'), primary_key=True)
    name = Column(String)
    description = Column(String)
    quantity = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    #user = relationship("User", back_populates="product")
    tax_id = Column(Integer, ForeignKey('tax.id'))
    date_added = Column(Date, default=date.today())
    permalink = Column(String)
    brand_id = Column(Integer, ForeignKey('brand'))

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity
        }