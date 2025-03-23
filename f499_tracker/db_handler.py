from sqlalchemy import create_engine, text, Row
from sqlalchemy.orm import sessionmaker, joinedload
from datetime import datetime

from sqlalchemy.util.preloaded import sql_dml

from f499_tracker.challenge_utils import challenge_score_v2, challenge_score_v3, calculate_week_number, session_link
from f499_tracker.models import Race, RaceResult, Participant
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
        # if data is a RaceData object, convert it to a dictionary
        if hasattr(data, '__dict__'):
            data = data.__dict__

        start_time = datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M:%SZ')
        # Upsert for Race
        race = session.query(Race).filter_by(subsession_id=data['subsession_id']).first()
        if race:
            race.season_year = data['season_year']
            race.season_quarter = data['season_quarter']
            race.series_week_number = data['series_week_number']
            race.season_week_number = data['season_week_number']
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
                series_week_number=data['series_week_number'],
                season_week_number=data['season_week_number'],
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
            race_result.strength_of_field = data['strength_of_field']
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
                challenge_points_v2=data['challenge_points_v2'],
                challenge_points_v3=data['challenge_points_v3'],
                strength_of_field=data['strength_of_field']
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

    def update_all_results_challenge_points_v3(self):
        # This method should iterate through all the race results in the database
        # and update the challenge_points_v3 by recalculating the score based on the
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

    def update_all_season_weeks(self):
        # This method should iterate through all the race results in the database
        # and update the season_week values by calculating them based on the
        # start_time of each race in the database.
        session = self.Session()

        results = session.query(Race).all()
        for result in results:
            start_time = result.start_time
            # convert start_time to a time string in the format like "2025-01-12T00:00:00Z"
            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            season_week_number = calculate_week_number(start_time_str)
            print("Updating season: start time: ", start_time_str, "\n series week number: ", result.series_week_number,
                  "\n calculated week number: ", season_week_number)
            result.season_week_number = season_week_number

        session.commit()
        session.close()

    def update_all_session_links(self):
        # This method should iterate through all the race results in the database
        # and update the season_week values by calculating them based on the
        # start_time of each race in the database.
        session = self.Session()

        results = session.query(Race).all()
        for result in results:
            s_link = session_link(result.subsession_id, True)
            result.session_link = s_link

        session.commit()
        session.close()

    def close(self):
        self.engine.dispose()

    def upsert_participants(self, participants):
        session = self.Session()
        result = []
        for participant in participants:
            cust_id_from_signup = participant[0]
            existing_participant = session.query(Participant).filter_by(cust_id=cust_id_from_signup).first()

            cust_id = cust_id_from_signup
            preferred_name = participant[1]
            start_date_time_str = participant[2]
            end_date_time_str = participant[3]

            start_time = None
            end_time = None
            if start_date_time_str not in [None, '']:
                start_time = datetime.fromisoformat(start_date_time_str)

            if end_date_time_str not in [None, '']:
                 end_time = datetime.fromisoformat(end_date_time_str)

            if existing_participant:
                existing_participant.cust_id = cust_id
                existing_participant.preferred_name = preferred_name
                existing_participant.start_date_time = start_time
                existing_participant.end_date_time = end_time
                db_participant = existing_participant
            else:
                db_participant = Participant(
                    cust_id=cust_id,
                    preferred_name=preferred_name,
                    start_date_time=start_time,
                    end_date_time=end_time
                )
                session.add(db_participant)

            # Create a detached copy of participant attributes
            participant_copy = {
                'id': db_participant.id,
                'cust_id': db_participant.cust_id,
                'preferred_name': db_participant.preferred_name,
                'start_date_time': db_participant.start_date_time,
                'end_date_time': db_participant.end_date_time
            }
            result.append(participant_copy)
        try:
            session.commit()

            # Create new Participant objects that aren't bound to the session
            detached_participants = []
            for p_data in result:
                detached_participant = Participant(
                    id=p_data['id'],
                    cust_id=p_data['cust_id'],
                    preferred_name=p_data['preferred_name'],
                    start_date_time=p_data['start_date_time'],
                    end_date_time=p_data['end_date_time']
                )
                detached_participants.append(detached_participant)

            return detached_participants
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_participants(self):
        session = self.Session()
        return session.query(Participant).order_by(Participant.preferred_name.asc()).all()

    def first_to_zero_ex(self, series_data):
        series_ids = [series[0] for series in series_data]
        series_names = [series[1] for series in series_data]
        # For SQLite, we need to expand the IN clause with individual parameter names
        placeholders = ','.join(f':id{i}' for i in range(len(series_ids)))

        query = f"""
        WITH ranked_results AS (
            SELECT
                rr.racer_name, rr.incident_count,
                r.series_name,
                r.start_time,
                r.season_week_number,
                r.session_link,
                ROW_NUMBER() OVER (PARTITION BY r.series_name, r.season_week_number ORDER BY r.start_time ASC) AS rn
            FROM
                race_results rr
            JOIN
                races r ON rr.race_id = r.id
            WHERE
                rr.incident_count = 0 AND rr.laps_complete > 0 AND r.series_id IN ({placeholders})
        )
        SELECT
            *
        FROM
            ranked_results
        WHERE
            rn = 1
        ORDER BY
            season_week_number, series_name asc, start_time asc;
        """
        session = self.Session()

        # Create a dictionary of named parameters
        params = {f'id{i}': id_val for i, id_val in enumerate(series_ids)}

        # Execute with named parameters
        sql_results = session.execute(text(query), params)
        sql_results = sql_results.fetchall()

        #results are a list of SQLAlchemy Row objects, we need to convert them to a list of dictionaries
        results = [row._mapping for row in sql_results]


        # we need to make sure that we have a result for each series_name in series_names for season_week_number 1
        # if one of the series_names in missing, we need to add a dummy result (kind of a hack)
        series_names_set = set([result.series_name for result in sql_results])
        missing_series_names = set(series_names) - series_names_set

        for series_name in missing_series_names:
            # create a dummy row to insert into the results, since this is a list of SQLAlchemy Row objects
            # and we cannot create a new Row object, I need something that behaves like a Row object
            # I will use a dictionary
            dummy_row = {
                'racer_name': '',
                'incident_count': 0,
                'series_name': series_name,
                'start_time': '',
                'season_week_number': 1,
                'session_link': '',
                'rn': 1
            }
            results.append(dummy_row)

        return results