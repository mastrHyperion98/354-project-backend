from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Numeric
from flaskr.db import Base

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, Sequence('seq_category_id'), primary_key=True)
    name = Column(String)
    description = Column(String)
    permalink = Column(String)
    icon = Column(String)
    section_id = Column(Integer, ForeignKey('section.id'))
    products = relationship('Product', order_by='desc(Product.name)', lazy='dynamic')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'imageUrl': self.icon,
            'description': self.description,
            'permalink': self.permalink
        }