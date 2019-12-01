from sqlalchemy.orm import relationship
from flaskr.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Sequence

class Brand(Base):
    __tablename__ = 'brand'

    id = Column(Integer, Sequence('seq_brand_id'), primary_key=True)
    name = Column(String)
    permalink = Column(String)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'permalink': self.permalink
        }