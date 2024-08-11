import json
from unittest import TestCase
from unittest.mock import MagicMock
from f499_tracker.iracing_client import IRacingAPIHandler
from f499_tracker.iracing_utils import augment_race_data


class TestIracingUtils(TestCase):
    def test_augment_race_data(self):
        data = [
            {'season_year': 2024, 'season_quarter': 3, 'week_number': 7, 'racer_name': 'Tony Dibden',
             'cust_id': 227267,
             'series_name': 'LMP3 Trophy - Fixed', 'series_id': 525, 'start_time': '2024-07-26T20:30:00Z',
             'track_name': 'Circuit de Barcelona Catalunya',
             'session_link': 'https://members-ng.iracing.com/racing/results-stats/results?subsessionid=70364227',
             'subsession_id': 70364227, 'start_position': 6, 'finish_position': 4, 'incident_count': 5,
             '_499_points': -8, 'old_irating': 3058.0, 'old_cpi': 173.0572, 'old_sub_level': 499.0,
             'new_irating': 3091.0, 'new_cpi': 135.34186, 'new_sub_level': 499.0}
        ]

        # Create a mock for the IRacingAPIHandler
        api = IRacingAPIHandler()
        api.client = MagicMock()

        # Mock the result method of the client
        with open('test_samples/result_70364227_raw_results.json', 'r') as file:
            mocked_result = json.load(file)

        print(f"racer: {data[0]['racer_name']}")
        api.client.result.return_value = mocked_result

        augmented_data = augment_race_data(api.client, data)

        # Assertions to verify the augmented data
        self.assertEqual(len(augmented_data), 1)
        self.assertIn('challenge_points_v2', augmented_data[0])
        self.assertEqual(0.0, augmented_data[0]['challenge_points_v2'])

        print(json.dumps(augmented_data, indent=2))

    def test_augment_race_data_tom(self):
        data = [
            {'season_year': 2024, 'season_quarter': 3, 'week_number': 7, 'racer_name': 'Tom Brice',
             'cust_id': 643506,
             'series_name': 'LMP3 Trophy - Fixed', 'series_id': 525, 'start_time': '2024-07-26T20:30:00Z',
             'track_name': 'Circuit de Barcelona Catalunya',
             'session_link': 'https://members-ng.iracing.com/racing/results-stats/results?subsessionid=70364227',
             'subsession_id': 70364227, 'start_position': 5, 'finish_position': 10, 'incident_count': 0,
             '_499_points': -1, 'old_irating': 2278.0, 'old_cpi': 82.47842, 'old_sub_level': 423.0,
             'new_irating': 2266.0, 'new_cpi': 88.19698, 'new_sub_level': 433.0}
        ]
        # Create a mock for the IRacingAPIHandler
        api = IRacingAPIHandler()
        api.client = MagicMock()

        # Mock the result method of the client
        with open('test_samples/result_70364227_raw_results.json', 'r') as file:
            mocked_result = json.load(file)

        print(f"racer: {data[0]['racer_name']}")
        api.client.result.return_value = mocked_result

        augmented_data = augment_race_data(api.client, data)

        # Assertions to verify the augmented data
        self.assertEqual(len(augmented_data), 1)
        self.assertIn('challenge_points_v2', augmented_data[0])
        self.assertEqual(6.2, augmented_data[0]['challenge_points_v2'])

        print(json.dumps(augmented_data, indent=2))
