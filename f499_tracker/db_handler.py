from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
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

            # Upsert for Race
            race = session.query(Race).filter_by(subsession_id=data['subsession_id']).first()
            if race:
                race.season_year = data['season_year']
                race.season_quarter = data['season_quarter']
                race.week_number = data['week_number']
                race.series_name = data['series_name']
                race.series_id = data['series_id']
                race.start_time = start_time
                race.track_name = data['track_name']
                race.session_link = data['session_link']
                race.license_category = data['license_category']
                race.num_entries = data['num_entries']
            else:
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

            # Upsert for RaceResult
            race_result = session.query(RaceResult).filter_by(race_id=race.id, cust_id=data['cust_id']).first()
            if race_result:
                race_result.racer_name = data['racer_name']
                race_result.car_name = data['car_name']
                race_result.start_position = data['start_position']
                race_result.finish_position = data['finish_position']
                race_result.incident_count = data['incident_count']
                race_result._499_points = data['_499_points']
                race_result.old_irating = data['old_irating']
                race_result.old_license_level = data['old_license_level']
                race_result.old_cpi = data['old_cpi']
                race_result.old_sub_level = data['old_sub_level']
                race_result.new_irating = data['new_irating']
                race_result.new_license_level = data['new_license_level']
                race_result.new_cpi = data['new_cpi']
                race_result.new_sub_level = data['new_sub_level']
                race_result.average_lap = data['average_lap']
                race_result.laps_complete = data['laps_complete']
                race_result.challenge_points_v2 = data['challenge_points_v2']
            else:
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

    def get_race_results(self, cust_id=None, season_year=None, season_quarter=None, season_week=None):
        session = self.Session()
        query = session.query(RaceResult).join(Race).options(joinedload(RaceResult.race))

        if cust_id is not None:
            query = query.filter(RaceResult.cust_id == cust_id)
        if season_year is not None:
            query = query.filter(Race.season_year == season_year)
        if season_quarter is not None:
            query = query.filter(Race.season_quarter == season_quarter)
        if season_week is not None:
            query = query.filter(Race.week_number == season_week)

        results = query.all()
        session.close()
        return results

    def close(self):
        self.engine.dispose()
