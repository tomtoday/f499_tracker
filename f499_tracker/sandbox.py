# create a class I can use to test iracing API calls and write out the results to a json file in the gen directory
# I want to be able to call this from the main.py file
from f499_tracker.tracker import Tracker
from f499_tracker.utils import write_results_to_json_file


class TestAPI:
    def __init__(self):
        self.tracker = Tracker()
        self.iracing_api_client = self.tracker.iracing_api_client

    def test_subsession_results(self, ss_id):
        res = self.iracing_api_client.result(ss_id)
        write_results_to_json_file(res, f'subsession_{ss_id}')

