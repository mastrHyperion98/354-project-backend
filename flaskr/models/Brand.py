from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base

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