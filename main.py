import json
from conda.common.serialize import json_dump

from f499_tracker.tracker import Tracker
from f499_tracker.tracker_sql import TrackerSQL
from f499_tracker.utils import write_results_to_json_file


def test_subsession_results():
    tracker = Tracker()
    ss_id = 70678353
    res = tracker.iracing_api_client.result(ss_id)
    write_results_to_json_file(res, f'subsession_{ss_id}')


if __name__ == '__main__':
    tracker = Tracker()
    tracker.generate_challenge_stats()

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