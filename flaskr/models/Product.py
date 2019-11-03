from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base
from flaskr.models.Tax import Tax

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
    brand_id = Column(Integer, ForeignKey('brand.id'))

    brand = relationship('Brand')
    user = relationship('User')
    tax = relationship('Tax')
    category = relationship('Category')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'category_id': self.category_id,
            'user_id': self.user_id,
            'tax_id': self.tax_id,
            'permalink': self.permalink,
            'brand_id': self.brand_id
        }

class Category(Base):

    __tablename__ = 'category'

    id = Column(Integer, Sequence('seq_category_id'), primary_key=True)
    section_id = Column(Integer, ForeignKey('section.id'))
    name = Column(String)
    description = Column(String)
    permalink = Column(String)

    section = relationship('Section')
    
    def to_json(self):
        return {
            'id': self.id,
            'section_id': self.section_id,
            'name': self.name,
            'description': self.description,
            'permalink': self.permalink
        }

class Section(Base):

    __tablename__ = 'section'

    id = Column(Integer, Sequence('seq_section_id'), primary_key=True)
    name = Column(String)
    description = Column(String)
    permalink = Column(String)
    icon = Column(String)

    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permalink': self.permalink,
            'icon': self.icon
        }

