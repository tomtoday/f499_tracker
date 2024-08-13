from f499_tracker.iracing_client import IRacingAPIHandler
from oauth2client.service_account import ServiceAccountCredentials
from f499_tracker.config import Config
from f499_tracker.challenge_utils import construct_499_race_data
from f499_tracker.google_sheets_utils import GoogleSheets
from f499_tracker.iracing_utils import augment_race_data, tidy_race_data
from f499_tracker.utils import write_results_to_csv_file
from f499_tracker.db_handler import DBHandler

import time
import gspread
import pandas as pd


class TrackerSQL:
    def __init__(self, db_name='race_data.db'):
        self.api = IRacingAPIHandler()
        self.iracing_api_client = self.api.client

        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(Config.SVC_ACCT_KEY_FILE, scope)
        client = gspread.authorize(creds)
        self.gspread_client = client

        # Initialize DBHandler with the provided database name
        self.db_handler = DBHandler(db_name=db_name)

    def calculate_first_zero_ex(self, week_number, source_sheet_name, source_worksheet_id=None):
        if source_worksheet_id is not None:
            sheet = self.gspread_client.open(source_sheet_name).get_worksheet_by_id(source_worksheet_id)
        else:
            sheet = self.gspread_client.open(source_sheet_name).sheet1

        data = pd.DataFrame(sheet.get_all_records())

        # Filter data for 0 incidents
        filtered_data = data[data['incident_count'] == 0]

        # Initialize a list to hold the first race of each series for each week with 0 incidents
        first_races = []

        # Group by week_number and series_id
        grouped = filtered_data.groupby(['week_number', 'series_id'])

        for name, group in grouped:
            # Sort by start_time to find the earliest race
            sorted_group = group.sort_values(by='start_time')
            # Select the first row as the earliest race with 0 incidents for that series in that week
            first_race = sorted_group.iloc[0].to_dict()
            first_races.append(first_race)

        return first_races

    def gather_data(self, desired_season_year, desired_season_quarter, desired_season_week, limit_series=False):
        # this is the aggregate list for all drivers
        race_data_list = []

        participants = GoogleSheets.get_participants_from_sheet(Config.TRACKER_SHEET_NAME,
                                                                Config.PARTICIPANT_WORKSHEET_ID)
        # iterate over the participants
        for cust_id, driver_name in participants:
            title = f"{desired_season_year}S{desired_season_quarter} Week {desired_season_week} CustID {cust_id}"
            print(f"{driver_name} - Customer ID: {cust_id}, {title}")

            # raw results hold results for a single driver
            raw_results = []

            if limit_series:
                series_of_interest = GoogleSheets.get_series_from_sheet(Config.TRACKER_SHEET_NAME,
                                                                        Config.SERIES_WORKSHEET_ID)
                # Get results for a driver for a specific series in the defined list
                for series in series_of_interest:
                    # pause to avoid hitting the API rate limit
                    series_id = series['series_id']
                    series_name = series['series_name']
                    allowed_car_classes = series['allowed_car_classes']
                    # allowed_car_classes might be an int or it might be a string
                    # if it is a string, it is a pipe-delimited list of car class ids
                    # if it is an int, it is a single car class id
                    if isinstance(allowed_car_classes, str):
                        allowed_car_classes = [int(car_class_id) for car_class_id in allowed_car_classes.split('|')]
                    elif isinstance(allowed_car_classes, int):
                        allowed_car_classes = [allowed_car_classes]

                    try:
                        time.sleep(0.1)
                        series_results = self.iracing_api_client.result_search_series(cust_id=cust_id,
                                                                                      series_id=series_id,
                                                                                      official_only=True,
                                                                                      event_types=[Config.EVENT_TYPE],
                                                                                      season_year=desired_season_year,
                                                                                      season_quarter=desired_season_quarter)

                        print(f"Series: {series_name}")
                        print(f"{len(series_results)} Races")

                        for i, result in enumerate(series_results, start=1):
                            # this is where we can filter out results that do not have the proper car class
                            # check if result['car_class_id'] is in allowed_car_classes
                            if result['car_class_id'] not in allowed_car_classes:
                                print(f"Skipping car class {result['car_class_id']}")
                                continue

                            raw_results.append(result)

                            race_data = construct_499_race_data(result, driver_name)
                            race_data_list.append(race_data)

                    except Exception as e:
                        print(f"Error: {e}")
                        continue
            else:
                # Get all results for a driver regardless of series
                try:
                    time.sleep(0.1)
                    all_results = self.iracing_api_client.result_search_series(cust_id=cust_id,
                                                                               official_only=True,
                                                                               event_types=[Config.EVENT_TYPE],
                                                                               season_year=desired_season_year,
                                                                               season_quarter=desired_season_quarter,
                                                                               category_ids=[5, 6])

                    print("All Series")
                    print(f"{len(all_results)} Races")
                    for i, result in enumerate(all_results, start=1):
                        raw_results.append(result)

                        race_data = construct_499_race_data(result, driver_name)
                        race_data_list.append(race_data)

                except Exception as e:
                    print(f"Error: {e}")
                    continue

        # sort race_data_list by start_time, descending
        race_data_list.sort(key=lambda x: x['start_time'])

        print("Done gathering data")
        return race_data_list

    @staticmethod
    def merge_race_data_with_csv_data(race_data, csv_file_name):
        # convert race_data to a DataFrame
        new_race_data_frame = pd.DataFrame(race_data)

        # read the existing data from the CSV file
        try:
            existing_race_data_frame = pd.read_csv(f"{csv_file_name}_data.csv")
        except (FileNotFoundError, pd.errors.EmptyDataError):
            existing_race_data_frame = pd.DataFrame()

        # convert the race_data list to a DataFrame
        return GoogleSheets.merge_api_race_data_with_existing_data(new_race_data_frame, existing_race_data_frame)

    def generate_challenge_stats(self):
        desired_season_year = 2024
        desired_season_quarter = 3
        desired_season_week = 12

        filename_prefix = f'{desired_season_year}S{desired_season_quarter}'
        race_data_list = []

        # get the data from the API
        api_data = self.gather_data(desired_season_year, desired_season_quarter, desired_season_week, False)
        race_data_list.append(api_data)
        # tidy up the data, sorting it properly
        race_data = tidy_race_data(race_data_list)

        # merge the data from the API with existing data from a Google Sheet or a CSV file
        # race_data = Tracker.merge_race_data_with_gspread_data(race_data)
        race_data = TrackerSQL.merge_race_data_with_csv_data(race_data, filename_prefix)

        # Make additional API calls to fill out more detail on each race
        race_data = augment_race_data(self.iracing_api_client, race_data)

        # write all the data to a local CSV and use that to upload to the Google Sheet
        write_results_to_csv_file(race_data, filename_prefix)

        # now write the data to the database
        # first convert each item in race_data to a race and race result object
        self.db_handler.insert_race_data(race_data)

        # write to the gspread sheet
        # GoogleSheets.append_to_gspread(Config.TRACKER_SHEET_NAME, Config.RESULTS_WORKSHEET_ID, filename_prefix)
