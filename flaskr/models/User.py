import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Sequence
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, Sequence('seq_user_id'), primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    date_joined = Column(Date, default=datetime.datetime.now())
    password = Column(String)
    
    def to_json(self):
        """Returns the instance of user as a JSON
        
        Returns:
            dict -- JSON representation of the user
        """
        return {
            'username': self.username,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'dateJoined': self.date_joined
        }