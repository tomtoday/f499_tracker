import cProfile
import json
from datetime import datetime

import pytz

from f499_tracker.config import Config
from f499_tracker.google_sheets_utils import GoogleSheets
from f499_tracker.sandbox import TestAPI
from f499_tracker.tracker import Tracker
from f499_tracker.tracker_sql import TrackerSQL


def season_participant_run():
    start_time = datetime.now()
    print(f"start_time: {start_time}")
    # test_api = TestAPI()
    # test_api.test_subsession_results(70920172)
    tracker = Tracker()
    # # Top Dentist - Week 12 2024S3
    # tracker.generate_challenge_stats(2024, 3, 12)
    ## 2024 Season 4 F499 Challenge
    tracker.generate_challenge_stats(2024, 4)

    end_time = datetime.now()
    mark_last_run(end_time)

    elapsed_time = end_time - start_time
    print(f"end_time: {end_time}")
    print(f"Script execution time: {elapsed_time.total_seconds():.2f} seconds")
    print("================================\n\n")


def league_season_run():
    start_time = datetime.now()
    print(f"start_time: {start_time}")
    tracker = Tracker()
    tracker.generate_challenge_stats_for_league(7919, 109891)
    end_time = datetime.now()
    mark_last_run(end_time)
    elapsed_time = end_time - start_time
    print(f"end_time: {end_time}")
    print(f"Script execution time: {elapsed_time.total_seconds():.2f} seconds")
    print("================================\n\n")


def latest_season_run():
    start_time = datetime.now()
    print(f"start_time: {start_time}")
    tracker = TrackerSQL(Config.DB_NAME)
    tracker.generate_challenge_stats(2025, 1)

    end_time = datetime.now()
    mark_last_run(end_time)

    elapsed_time = end_time - start_time
    print(f"end_time: {end_time}")
    print(f"Script execution time: {elapsed_time.total_seconds():.2f} seconds")
    print("================================\n\n")


def mark_last_run(end_time):
    if Config.LAST_RUN_SHEET_ID:
        end_time_utc = end_time.astimezone(pytz.utc)
        time_string = end_time_utc.strftime('%Y-%m-%d %H:%M:%S %Z')
        last_updated_data = ["Last updated:", f"{time_string}"]
        GoogleSheets.simple_write_to_sheet(Config.TRACKER_SHEET_NAME, Config.LAST_RUN_SHEET_ID, last_updated_data)


def challenge_stats_for_race(subsession_id, cust_id):
    start_time = datetime.now()
    print(f"start_time: {start_time}")
    tracker = TrackerSQL()
    tracker.get_results_for_subsession(subsession_id, cust_id)


if __name__ == '__main__':
    # season_participant_run()
    # league_season_run()

    latest_season_run()

    # tony_cust_id = 227267
    # challenge_stats_for_race(73894739, tony_cust_id)

    # tracker = TrackerSQL(Config.DB_NAME)
    # tracker.db_handler.update_all_session_links()
