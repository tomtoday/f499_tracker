import cProfile
import json
from datetime import datetime

import pytz

from f499_tracker.config import Config
from f499_tracker.google_sheets_utils import GoogleSheets
from f499_tracker.sandbox import TestAPI
from f499_tracker.tracker import Tracker
from f499_tracker.tracker_sql import TrackerSQL


if __name__ == '__main__':
    start_time = datetime.now()
    print(f"start_time: {start_time}")

    test_api = TestAPI()
    test_api.test_subsession_results(70920172)

    # tracker = Tracker()
    # # Top Dentist - Week 12 2024S3
    # tracker.generate_challenge_stats(2024, 3, 12)

    end_time = datetime.now()

    # if Config.LAST_RUN_SHEET_ID:
    #     end_time_utc = end_time.astimezone(pytz.utc)
    #     time_string = end_time_utc.strftime('%Y-%m-%d %H:%M:%S %Z')
    #     last_updated_data = ["Last updated:",f"{time_string}"]
    #     GoogleSheets.simple_write_to_sheet(Config.TRACKER_SHEET_NAME, Config.LAST_RUN_SHEET_ID, last_updated_data)

    elapsed_time = end_time - start_time
    print(f"end_time: {end_time}")
    print(f"Script execution time: {elapsed_time.total_seconds():.2f} seconds")
    print("================================\n\n")
