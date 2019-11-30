from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy.orm import relationship
from flaskr.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Numeric
from sqlalchemy.dialects.postgresql import JSON, JSONB
import flaskr.models.Brand
import flaskr.models.Tax

class Product(Base):

    __tablename__ = 'product'

    id = Column(Integer, Sequence('seq_product_id'), primary_key=True)
    name = Column(String)
    description = Column(String)
    quantity = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    tax_id = Column(Integer, ForeignKey('tax.id'))
    date_added = Column(Date, default=date.today())
    permalink = Column(String)
    specifications = Column(JSONB)
    photos = Column(JSON)
    brand = relationship('Brand')
    category = relationship('Category')
    brand_id = Column(Integer, ForeignKey('brand.id'))
    user = relationship('User')
    tax = relationship('Tax')
    condition = Column(String)
    price = Column(Numeric)

    permalink_translation_tab = str.maketrans(' ()/_.~', '-------')

    def to_json(self):
        """Returns the instance of product as a JSON

        Returns:
            dict -- JSON representation of the product
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'category': self.category.to_json(),
            'price': str(self.price),
            'condition': self.condition,
            'sellerInfo': {
                'username': self.user.username,
                'email': self.user.email
            },
            'tax': self.tax.to_json(),
            'dateAdded': str(self.date_added),
            'permalink': self.permalink,
            'specifications': self.specifications,
            'photos': self.photos,
            'brand': self.brand.to_json()
        }
