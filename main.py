# This is a sample Python script.

from f499_tracker.tracker import Tracker
from f499_tracker.tracker_sql import TrackerSQL
from f499_tracker.utils import write_results_to_json_file


def test_subsession_results():
    tracker = Tracker()
    ss_id = 70678353
    res = tracker.iracing_api_client.result(ss_id)
    write_results_to_json_file(res, f'subsession_{ss_id}')


if __name__ == '__main__':
    # tracker = Tracker()
    # tracker.generate_challenge_stats()
    # test_subsession_results()
    tracker_sql = TrackerSQL()
    tracker_sql.generate_challenge_stats()
