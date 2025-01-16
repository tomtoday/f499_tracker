from dataclasses import dataclass
from typing import Optional

@dataclass
class RaceData:
    start_position: int
    finish_position: int
    incident_count: int
    track_name: str
    subsession_id: int
    start_time: str
    series_week_number: int
    season_week_number: int
    season_year: int
    season_quarter: int
    _499_points: int
    session_link: str
    series_name: str
    series_id: int
    racer_name: str
    cust_id: int
    car_name: str
    license_category: str
    laps_complete: int
    old_irating: Optional[int] = None
    old_license_level: Optional[int] = None
    old_cpi: Optional[float] = None
    old_sub_level: Optional[int] = None
    new_irating: Optional[int] = None
    new_license_level: Optional[int] = None
    new_cpi: Optional[float] = None
    new_sub_level: Optional[int] = None
    average_lap: Optional[int] = None
    num_entries: Optional[int] = None
