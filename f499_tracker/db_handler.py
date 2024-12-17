from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from datetime import datetime

from f499_tracker.challenge_utils import challenge_score_v2, challenge_score_v3
from f499_tracker.models import Race, RaceResult
from f499_tracker.models.race import Base


def flatten_race_results(results):
    # Flatten the results
    flattened_results = []
    for result in results:
        result_dict = result.__dict__.copy()
        race_dict = result.race.__dict__.copy()
        # Remove the race property from the result_dict, this contained the associated race
        # object which will be merged into the result_dict
        result_dict.pop('race', None)
        # Remove SQLAlchemy state keys
        result_dict.pop('_sa_instance_state', None)
        race_dict.pop('_sa_instance_state', None)
        # Merge race_dict into result_dict
        flattened_result = {**result_dict, **race_dict}
        flattened_results.append(flattened_result)

    return flattened_results


class DBHandler:
    def __init__(self, db_name='race_data.db'):
        if db_name.endswith('.db'):
            db_name = f'sqlite:///{db_name}'
        self.engine = create_engine(db_name)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def race_exists(self, subsession_id, cust_id):
        session = self.Session()
        exists = session.query(RaceResult).join(Race).filter(
            Race.subsession_id == subsession_id,
            RaceResult.cust_id == cust_id
        ).first() is not None
        session.close()
        return exists

    def insert_race_data(self, race_data):
        session = self.Session()
        for data in race_data:
            self.upsert_race_information(data, session)

        session.commit()
        session.close()

    def upsert_race_information(self, data, session):
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

        # add a sort order to the query
        query = query.order_by(Race.start_time.desc())

        results = query.all()
        session.close()
        return results

    def update_all_results(self):
        # This method should iterate through all the race results in the database
        # and update the challenge_points_v2 by recalculating the score based on the
        # current data in the database.
        session = self.Session()

        results = session.query(RaceResult).options(joinedload(RaceResult.race)).all()
        for result in results:
            result.challenge_points_v3 = challenge_score_v3(
                result.average_lap * result.laps_complete,
                result.race.num_entries,
                result.incident_count,
                result.start_position,
                result.finish_position,
                result.new_sub_level,
                result.laps_complete
            )
        session.commit()
        session.close()

    def close(self):
        self.engine.dispose()
