from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Numeric
from flaskr.db import Base
from flaskr.models.Category import Category

class Section(Base):

    __tablename__ = 'section'

    id = Column(Integer, Sequence('seq_section_id'), primary_key=True)
    name = Column(String)
    description = Column(String)
    permalink = Column(String)
    icon = Column(String)
    categories = relationship('Category')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permalink': self.permalink,
            'icon': self.icon,
            'categories': [ category.to_json() for category in self.categories ]
        }

