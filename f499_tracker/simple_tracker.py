# This class should be similar to TrackerSQL but I want to simplify the logic
# not that the tracker can write to a SQLite database. Much of the code to do tracking was
# predicated on the idea the Google Sheets was the persistence layer so it did a lot of fetching and deduping.
# this is no longer necessary.

# The tracker should be able to:
# 1. Get a list of participants from Google Sheets.
# 2. Iterate over the list of participants and look up their current season results.
# 3. Turn the results into a list of RaceData objects.
# 4. Iterate over the list of RaceData objects and do an additional API call to get the detail we need and update the RaceData object.
# 5. Write the RaceData objects to a SQLite database in an upsert fashion.
# 6. Once the database is up to date for this run, update the Google Sheets with the new data.
# This is not much different than what the TrackerSQL class does, but I would like to simplify the logic by rewriting it.
# The TrackerSQL class is a bit of a mess. It does a lot of things and is not very well organized.

import sqlite3
from datetime import datetime

import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread

from f499_tracker.challenge_utils import construct_499_race_data
from f499_tracker.config import Config
from f499_tracker.db_handler import DBHandler, flatten_race_results
from f499_tracker.google_sheets_utils import GoogleSheets
from f499_tracker.iracing_utils import augment_race_data
from f499_tracker.utils import write_results_to_json_file


class SimpleTracker:
    def __init__(self, iracing_api_client, db_path):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(Config.SVC_ACCT_KEY_FILE, scope)
        client = gspread.authorize(creds)
        self.google_sheets_client = client

        self.iracing_api_client = iracing_api_client
        self.db_path = db_path
        self.db_handler = self._init_db_handler()

    def _init_db_handler(self):
        # Initialize the database handler
        return DBHandler(db_name=self.db_path)

    def get_participants(self, update_from_sheet=False):
        # 1. Get a list of participants from Google Sheets.
        if (update_from_sheet):
            try:
                participants = GoogleSheets.get_participants_from_sheet(Config.TRACKER_SHEET_NAME,
                                                                        Config.PARTICIPANT_WORKSHEET_ID)
            except Exception as e:
                print(f"Error fetching participants: {e}")
                return []

            # convert the participants to Participant objects and persist to the database
            participants = self.db_handler.upsert_participants(participants)
        else:
            participants = self.db_handler.get_participants()

        return participants

    def get_season_results(self, participant, desired_season_year, desired_season_quarter):
        try:
            # Extract participant details based on object type
            if isinstance(participant, tuple):
                cust_id = participant[0]
                racer_name = participant[1]
                racer_start_date_time = participant[2]
                racer_end_date_time = participant[3]
            else:
                cust_id = participant.cust_id
                racer_name = participant.preferred_name
                racer_start_date_time = participant.start_date_time if participant.start_date_time else datetime.min
                racer_end_date_time = participant.end_date_time if participant.end_date_time else datetime.max

            # Debug information
            print(f"Processing participant: {racer_name} (ID: {cust_id})")
            print(f"Time window: {racer_start_date_time} to {racer_end_date_time}")

            # Normalize participant datetimes to be timezone-naive
            if racer_start_date_time and racer_start_date_time.tzinfo:
                racer_start_date_time = racer_start_date_time.replace(tzinfo=None)
            if racer_end_date_time and racer_end_date_time.tzinfo:
                racer_end_date_time = racer_end_date_time.replace(tzinfo=None)

            # Fetch results from API
            all_results = self.iracing_api_client.result_search_series(
                cust_id=cust_id,
                official_only=True,
                event_types=[Config.EVENT_TYPE],
                season_year=desired_season_year,
                season_quarter=desired_season_quarter,
                category_ids=[5, 6]
            )

            print(f"Found {len(all_results)} total results from API")

            if not all_results:
                return []

            # Filter results based on time window
            filtered_results = []
            for result in all_results:
                try:
                    # Extract start time and ensure it's timezone-naive for comparison
                    race_start_time_str = result['start_time']
                    race_start_time = datetime.fromisoformat(race_start_time_str)
                    if race_start_time.tzinfo:
                        race_start_time = race_start_time.replace(tzinfo=None)

                    # Check if race is within time window
                    is_in_time_window = True
                    if racer_start_date_time:
                        is_in_time_window = is_in_time_window and race_start_time >= racer_start_date_time
                    if racer_end_date_time:
                        is_in_time_window = is_in_time_window and race_start_time <= racer_end_date_time

                    if is_in_time_window:
                        filtered_results.append(result)
                except Exception as e:
                    print(f"Error processing result {result.get('subsession_id', 'unknown')}: {e}")

            print(f"Filtered to {len(filtered_results)} results within time window")

            # Create race data and check for duplicates
            race_data_list = []
            for result in filtered_results:
                try:
                    race_data = construct_499_race_data(result, racer_name)
                    if not self.db_handler.race_exists(race_data.subsession_id, race_data.cust_id):
                        race_data_list.append(race_data)
                except Exception as e:
                    print(f"Error constructing race data for subsession {result.get('subsession_id', 'unknown')}: {e}")

            print(f"Found {len(race_data_list)} new races to process")
            return race_data_list

        except Exception as e:
            print(f"Error fetching season results for {getattr(participant, 'preferred_name', participant)}: {e}")
            return []

    def update_race_data(self, race_data):
        # 4. Iterate over the list of RaceData objects and do an additional API call to get the detail we need and update the RaceData object.
        # for race in race_data:
        try:
            # the additional data is pulled from the iRacing Data API
            # please reference the TrackerSQL method called augment_race_data
            # for an example of how to do this
            updated_race_data = augment_race_data(self.iracing_api_client, race_data)
        except Exception as e:
            print(f"Error updating race data: {e}")

        return updated_race_data

    def write_to_db(self, race_data):
        # 5. Write the RaceData objects to a SQLite database in an upsert fashion.
        self.db_handler.insert_race_data(race_data)

    def update_google_sheets(self):
        # 6. Once the database is up to date for this run, update the Google Sheets with the new data.
        all_race_results = self.db_handler.get_race_results(None, Config.SEASON_YEAR, Config.SEASON_QUARTER)
        all_race_results = flatten_race_results(all_race_results)

        # # convert all_race_results to a pandas DataFrame
        all_race_results_df = pd.DataFrame([result for result in all_race_results])

        GoogleSheets.clear_and_write_results_to_tracking_sheet(all_race_results_df)

    def get_new_races(self, current_race_data):
        # the current_race_data is a list of dictionaries of races from the API
        # each one of the items in the list is a dictionary with a key of `subsession_id` and `cust_id`
        # The database will have race_results that also contain `subsession_id` and `cust_id`
        # For each item in current_race_data, we need to check if there is a corresponding row in the database
        # If there is, that item can be skipped. If there is not, then add this item to a new list that will be returned
        new_race_data = []
        for race in current_race_data:
            # check the database to see if we have seen this one
            if not self.db_handler.race_exists(race['subsession_id'], race['cust_id']):
                new_race_data.append(race)
        return new_race_data

    def get_first_zero_ex_data(self, series_data):
        results = self.db_handler.first_to_zero_ex(series_data)



        return results

    def run(self):
        # Main method to run the tracker
        update_from_sheet = True
        participants = self.get_participants(update_from_sheet)
        all_race_data = []
        for participant in participants:
            # The season results are a list of RaceData objects
            results = self.get_season_results(participant, Config.SEASON_YEAR, Config.SEASON_QUARTER)
            updated_race_data = self.update_race_data(results)

            all_race_data.extend(updated_race_data)

        self.write_to_db(all_race_data)
        self.update_google_sheets()
        print(all_race_data)
