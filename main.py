import cProfile
import json
from datetime import datetime

import pytz

from f499_tracker.config import Config
from f499_tracker.google_sheets_utils import GoogleSheets
from f499_tracker.tracker import Tracker
from f499_tracker.tracker_sql import TrackerSQL
from f499_tracker.utils import write_results_to_json_file


def test_subsession_results():
    tracker = Tracker()
    ss_id = 70678353
    res = tracker.iracing_api_client.result(ss_id)
    write_results_to_json_file(res, f'subsession_{ss_id}')


if __name__ == '__main__':
    # Start a timer or a benchmark so that we can see how long it takes to run the script
    start_time = datetime.now()
    print(f"start_time: {start_time}")

    tracker = Tracker()

    # tracker.generate_challenge_stats(2024, 3, 12)
    # tracker.generate_challenge_stats(2024, 3, None)

    # Top Dentist
    tracker.generate_challenge_stats(2024, 3, 12)

    # results_from('2023-08-08T00:00Z', '2023-08-15T23:59Z')
    # test_subsession_results()

    # tracker_sql = TrackerSQL()
    # # tracker_sql.generate_challenge_stats()
    #
    # week_9 = tracker_sql.db_handler.get_race_results(cust_id=929408, season_year=2024, season_quarter=3, season_week=9)
    #
    # # Serialize week_9 to JSON and include related race data
    # week_9_json = json.dumps([{
    #     'race_result': result.__dict__,
    #     'race': result.race.__dict__
    # } for result in week_9], default=str, indent=2)
    #
    # print(week_9_json)
    # End the timer or benchmark
    end_time = datetime.now()

    if Config.LAST_RUN_SHEET_ID:
        end_time_utc = end_time.astimezone(pytz.utc)
        time_string = end_time_utc.strftime('%Y-%m-%d %H:%M:%S %Z')
        last_updated_data = ["Last updated:",f"{time_string}"]
        GoogleSheets.simple_write_to_sheet(Config.TRACKER_SHEET_NAME, Config.LAST_RUN_SHEET_ID, last_updated_data)


    # Print out how long it took to run the script
    elapsed_time = end_time - start_time
    print(f"end_time: {end_time}")
    print(f"Script execution time: {elapsed_time.total_seconds():.2f} seconds")
    print("================================\n\n")
