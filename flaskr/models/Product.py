from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Numeric
from sqlalchemy.dialects.postgresql import JSON, JSONB

Base = declarative_base()

class Product(Base):

    __tablename__ = 'product'

    product_id = Column(Integer, Sequence('seq_product_id'), primary_key=True)
    product_name = Column(String)
    description = Column(String)
    quantity = Column(Integer)
    category_id = Column(Integer)
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
            'product_id': self.id,
            'product_name': self.name,
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