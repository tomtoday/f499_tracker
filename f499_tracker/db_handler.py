from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from f499_tracker.models import Race, RaceResult
from f499_tracker.models.race import Base


class DBHandler:
    def __init__(self, db_name='race_data.db'):
        if db_name.endswith('.db'):
            db_name = f'sqlite:///{db_name}'
        self.engine = create_engine(db_name)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_race_data(self, race_data):
        session = self.Session()
        for data in race_data:
            start_time = datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M:%SZ')
            race = Race(
                season_year=data['season_year'],
                season_quarter=data['season_quarter'],
                week_number=data['week_number'],
                series_name=data['series_name'],
                series_id=data['series_id'],
                start_time=start_time,
                track_name=data['track_name'],
                session_link=data['session_link'],
                subsession_id=data['subsession_id'],
                license_category=data['license_category'],
                num_entries=data['num_entries']
            )
            session.add(race)
            session.flush()  # Ensure race.id is available

            race_result = RaceResult(
                race_id=race.id,
                racer_name=data['racer_name'],
                cust_id=data['cust_id'],
                car_name=data['car_name'],
                start_position=data['start_position'],
                finish_position=data['finish_position'],
                incident_count=data['incident_count'],
                _499_points=data['_499_points'],
                old_irating=data['old_irating'],
                old_license_level=data['old_license_level'],
                old_cpi=data['old_cpi'],
                old_sub_level=data['old_sub_level'],
                new_irating=data['new_irating'],
                new_license_level=data['new_license_level'],
                new_cpi=data['new_cpi'],
                new_sub_level=data['new_sub_level'],
                average_lap=data['average_lap'],
                laps_complete=data['laps_complete'],
                challenge_points_v2=data['challenge_points_v2']
            )
            session.add(race_result)
        session.commit()
        session.close()

    def get_race_data(self):
        session = self.Session()
        races = session.query(Race).all()
        race_results = session.query(RaceResult).all()
        session.close()
        return pd.DataFrame([race.__dict__ for race in races]), pd.DataFrame(
            [result.__dict__ for result in race_results])

    def query_by_start_time_on_or_after(self, start_time):
        session = self.Session()
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')
        races = session.query(Race).filter(Race.start_time >= start_time).all()
        session.close()
        return pd.DataFrame([race.__dict__ for race in races])

    def close(self):
        self.engine.dispose()
