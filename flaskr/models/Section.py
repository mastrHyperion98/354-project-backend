from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base

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