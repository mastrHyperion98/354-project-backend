from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
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

class Brand(Base):

    __tablename__ = 'brand'

    id = Column(Integer, Sequence('seq_brand_id'), primary_key=True)
    name = Column(String)
    description = Column(String)
    logo = Column(Integer)
    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'logo': self.logo
        }

class Tax(Base):

    __tablename__ = 'tax'

    id = Column(Integer, Sequence('seq_tax_id'), primary_key=True)
    rate = Column(Float)
    
    
    def to_json(self):
        return {
            'id': self.id,
            'rate': self.rate
            
        }

class order_status(Base):

    __tablename__ = 'order_status'

    id = Column(Integer, Sequence('seq_order_status_id'), primary_key=True)
    status = Column(String)
  

    def to_json(self):
        """Returns the instance of status as a JSON
        
        Returns:    
            dict -- JSON representation of the order
        """
        return {
            'id': self.id,
            'status': self.status
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

class promotion_code(Base):

    __tablename__ = 'promotion_code'

    id = Column(Integer, Sequence('seq_user_id'), primary_key=True)
    code = Column(String)
    start_date = Column(Date, default=date.today())
    end_date = Column(Date, default=date.today())


    def to_json(self):
        """Returns the instance of price as a JSON
        
        Returns:    
            dict -- JSON representation of the order
        """
        return {
            'id': self.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'code': self.code
        }

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
    city = Column(String)
    country = Column(String)
    phone = Column(String)
    total_cost = Column(Float)
    promotion_code_id = Column(Integer, ForeignKey('promotion_code.id'))
    user = relationship('User')
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


class OrderLine(Base):

    __tablename__ = 'order_line'

    id = Column(Integer, Sequence('seq_order_id'), primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer)
    cost = Column(Float)
    order = relationship('Order')
    product = relationship('Product')

    def to_json(self):
        """Returns the instance of order line as a JSON
        
        Returns:    
            dict -- JSON representation of the order
        """
        return {
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }