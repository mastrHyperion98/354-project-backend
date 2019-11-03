from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base

class Tax(Base):
    __tablename__ = 'tax'

    id = Column(Integer, Sequence('seq_tax_id'), primary_key=True)
    rate = Column(Float)

    def to_json(self):
        return {
            'id': self.id,
            'rate': self.rate

        }