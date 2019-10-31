from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base
from flaskr.models.Section import Section


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