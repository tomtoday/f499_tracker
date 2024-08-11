import json
from unittest import TestCase

from f499_tracker.iracing_utils import get_number_of_cars_in_class, find_result_by_cust_id_simple


class TestUtils(TestCase):
    def test_get_number_of_cars_in_class_single_event(self):
        # Read the JSON file
        with open('test_samples/single_result_70017256_raw_results.json', 'r') as file:
            data = json.load(file)

        # Sample car_class_id to test with
        car_class_id = 3188  # F4

        # Expected result
        expected_number_of_cars = 20

        # Call the method and assert the result
        number_of_cars = get_number_of_cars_in_class(data, car_class_id)
        self.assertEqual(expected_number_of_cars, number_of_cars)

    def test_get_number_of_cars_in_class_single_event_bad_class(self):
        # Read the JSON file
        with open('test_samples/single_result_70017256_raw_results.json', 'r') as file:
            data = json.load(file)

        # Sample car_class_id to test with
        car_class_id = 10089111  # Bad car class

        # Expected result
        expected_number_of_cars = 0

        # Call the method and assert the result
        number_of_cars = get_number_of_cars_in_class(data, car_class_id)
        self.assertEqual(expected_number_of_cars, number_of_cars)

    def test_get_number_of_cars_in_class_team_event(self):
        # Read the JSON file
        with open('test_samples/result_70060893_raw_results.json', 'r') as file:
            data = json.load(file)

        # Sample car_class_id to test with
        car_class_id = 2523  # LMP2

        # Expected result
        expected_number_of_cars = 11

        # Call the method and assert the result
        number_of_cars = get_number_of_cars_in_class(data, car_class_id)
        self.assertEqual(expected_number_of_cars, number_of_cars)

    def test_find_result_by_cust_id_simple(self):
        with open('test_samples/result_70060893_raw_results.json', 'r') as file:
            data = json.load(file)
        result = find_result_by_cust_id_simple(data, 818734)
        assert result is not None
        assert result['cust_id'] == 818734
