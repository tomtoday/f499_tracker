# This is a sample Python script.
import json

import pandas as pd

from f499_tracker.config import Config
from f499_tracker.google_sheets_utils import GoogleSheets
from f499_tracker.iracing_client import IRacingAPIHandler
from f499_tracker.tracker import Tracker
from f499_tracker.utils import (
    flatten_sum,
    write_results_to_csv_file,
    write_results_to_json_file
)
from f499_tracker.iracing_utils import extract_values_from_race_result, augment_race_data


def aggregate_race_data(desired_season_year, desired_season_quarter):
    race_data_list = []
    desired_season_week = 12

    race_data_list.append(tracker.gather_data(desired_season_year, desired_season_quarter, desired_season_week, False))

    # race_data_list is a list of lists of dictionaries. It needs to be flattened to a single list of dictionaries
    race_data_list = sum(race_data_list, [])
    # create a dataframe from the list of dictionaries
    race_data_df = pd.DataFrame(race_data_list)
    # drop duplicates based on subsession_id and cust_id
    race_data_df.drop_duplicates(subset=['subsession_id', 'cust_id'], inplace=True)
    race_data_df.sort_values(by=['start_time', 'cust_id'], ascending=[False, True], inplace=True)
    # Convert the DataFrame to a list of dictionaries
    return race_data_df.to_dict('records')


def data_run():
    desired_season_year = 2024
    desired_season_quarter = 3
    filename_prefix = f'{desired_season_year}S{desired_season_quarter}'

    race_data = aggregate_race_data(2024, 3)
    # race_data = Tracker.merge_race_data_with_gspread_data(race_data)
    race_data = Tracker.merge_race_data_with_csv_data(race_data, filename_prefix)

    race_data = augment_race_data(tracker.iracing_api_client, race_data)

    # write all the data to a local CSV and use that to upload to the Google Sheet
    write_results_to_csv_file(race_data, filename_prefix)

    # write to the gspread sheet
    GoogleSheets.append_to_gspread(Config.TRACKER_SHEET_NAME, Config.RESULTS_WORKSHEET_ID, filename_prefix)


if __name__ == '__main__':
    tracker = Tracker()
    data_run()
