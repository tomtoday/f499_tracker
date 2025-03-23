from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from f499_tracker.models.race import Base


class Participant(Base):
    __tablename__ = 'participants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cust_id = Column(Integer, unique=True, nullable=False)
    preferred_name = Column(String, nullable=False)
    start_date_time = Column(DateTime)
    end_date_time = Column(DateTime)

    # Define relationship with results if needed
    # results = relationship('RaceResult', back_populates='participant')