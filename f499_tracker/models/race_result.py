from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .race import Base


class RaceResult(Base):
    __tablename__ = 'race_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.id'))
    racer_name = Column(String)
    cust_id = Column(Integer)
    car_name = Column(String)
    start_position = Column(Integer)
    finish_position = Column(Integer)
    incident_count = Column(Integer)
    _499_points = Column(Float)
    old_irating = Column(Integer)
    old_license_level = Column(Integer)
    old_cpi = Column(Float)
    old_sub_level = Column(Integer)
    new_irating = Column(Integer)
    new_license_level = Column(Integer)
    new_cpi = Column(Float)
    new_sub_level = Column(Integer)
    average_lap = Column(Float)
    laps_complete = Column(Integer)
    challenge_points_v2 = Column(Float)

    race = relationship('Race', back_populates='results')
    __table_args__ = (UniqueConstraint('race_id', 'cust_id', name='_race_cust_uc'),)