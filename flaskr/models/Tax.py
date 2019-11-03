from sqlalchemy.orm import relationship
from flaskr.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Numeric

class Tax(Base):

    __tablename__ = 'tax'

    id = Column(Integer, Sequence('seq_tax_id'), primary_key=True)
    rate = Column(Numeric)

    def to_json(self):
        return {
            'id': self.id,
            'rate': str(self.rate)
        }