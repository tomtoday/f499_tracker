from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Race(Base):
    __tablename__ = 'races'

    id = Column(Integer, primary_key=True, autoincrement=True)
    season_year = Column(Integer)
    season_quarter = Column(Integer)
    week_number = Column(Integer)
    series_name = Column(String)
    series_id = Column(Integer)
    start_time = Column(DateTime)
    track_name = Column(String)
    session_link = Column(String)
    subsession_id = Column(Integer, unique=True)
    license_category = Column(String)
    num_entries = Column(Integer)

    results = relationship('RaceResult', back_populates='race')
