from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base

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
