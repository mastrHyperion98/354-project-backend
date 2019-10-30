from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy.orm import relationship
from flaskr.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Numeric
from sqlalchemy.dialects.postgresql import JSON, JSONB

class Product(Base):

    __tablename__ = 'product'
    
    id = Column(Integer, Sequence('seq_product_id'), primary_key=True)
    name = Column(String)
    description = Column(String)
    quantity = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer)
    tax_id = Column(Integer)
    date_added = Column(Date, default=date.today())
    permalink = Column(String)
    specifications = Column(JSONB)
    photos = Column(JSON)
    brand_id = Column(Integer)

     
    def to_json(self):
        """Returns the instance of product as a JSON
        
        Returns:
            dict -- JSON representation of the product
        """
        return {
            'productId': self.id,
            'productName': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'categoryId': self.category_id,
            'userId': self.user_id,
            'taxId': self.tax_id,
            'dateAdded': self.date_added,
            'permalink': self.permalink,
            'specifications': self.specifications,
            'photos': self.photos,
            'brandId': self.brand_id
        }