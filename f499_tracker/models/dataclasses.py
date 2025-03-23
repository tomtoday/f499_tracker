from dataclasses import dataclass, asdict
from typing import Optional
import json

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
    event_strength_of_field: Optional[int] = None

    def update_with_details(self, detailed_data):
        self.old_irating = detailed_data['old_irating']
        self.old_license_level = detailed_data['old_license_level']
        self.old_cpi = detailed_data['old_cpi']
        self.old_sub_level = detailed_data['old_sub_level']
        self.new_irating = detailed_data['new_irating']
        self.new_license_level = detailed_data['new_license_level']
        self.new_cpi = detailed_data['new_cpi']
        self.new_sub_level = detailed_data['new_sub_level']
        self.average_lap = detailed_data['average_lap']
        self.num_entries = detailed_data['num_entries']

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())