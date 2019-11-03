from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from flaskr.db import Base

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