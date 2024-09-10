# This method expects full race result JSON data and a customer ID
import math

import pandas as pd

from f499_tracker.challenge_utils import challenge_score_v2

# These are the keys that can only be retrieved from an additional API call for subsession results
DETAIL_DATA_KEYS = [
    'old_irating',
    'old_license_level',
    'old_cpi',
    'old_sub_level',
    'new_irating',
    'new_license_level',
    'new_cpi',
    'new_sub_level',
    'average_lap',
    'laps_complete',
    'num_entries'
]


def extract_values_from_race_result(data, cust_id):
    # Find the first session that matches the criteria
    # team result path:
    # session_results[2].results[15].driver_results[0].oldi_rating
    # individual result path:
    # session_results[2].results[24].oldi_rating

    matching_result = find_result_by_cust_id_simple(data, cust_id)

    # If a matching result is found, extract the required values
    if matching_result:
        cust_car_class_id = matching_result.get('car_class_id')
        field_size = get_number_of_cars_in_class(data, cust_car_class_id)

        augmented_data = {
            'old_irating': matching_result.get('oldi_rating'),
            'old_license_level': matching_result.get('old_license_level'),
            'old_cpi': matching_result.get('old_cpi'),
            'old_sub_level': matching_result.get('old_sub_level'),
            'new_irating': matching_result.get('newi_rating'),
            'new_license_level': matching_result.get('new_license_level'),
            'new_cpi': matching_result.get('new_cpi'),
            'new_sub_level': matching_result.get('new_sub_level'),
            'average_lap': matching_result.get('average_lap'),
            'laps_complete': matching_result.get('laps_complete'),
            'num_entries': field_size,
        }
        return augmented_data

    # Return an empty dictionary if no match is found
    return {}


def get_number_of_cars_in_class(data, car_class_id):
    # data will have a property at a location like this:
    # car_classes[0].num_entries where car_classes.car_class_id == car_class_id
    return next(
        (
            car_class.get('num_entries') for car_class in data.get('car_classes', [])
            if car_class.get('car_class_id') == car_class_id
        ),
        0
    )


def find_result_by_cust_id_simple(data, cust_id):
    matching_result = next(
        (
            result for session in data.get('session_results', [])
            if session.get('simsession_type') == 6
            for result in session.get('results', [])
            if result.get('cust_id') == cust_id
        ),
        None
    )

    # might be a team event so the driver_results are nested
    if matching_result is None:
        matching_result = next(
            (
                result for session in data.get('session_results', [])
                if session.get('simsession_type') == 6
                for res in session.get('results', [])
                for result in res.get('driver_results', [])
                if result.get('cust_id') == cust_id
            ),
            None
        )

    return matching_result


def find_result_by_cust_id(data, cust_id, depth=0):
    # Base case: If we're at the depth where results are stored
    if depth == 2:  # Assuming session_results is at depth 1 and results are at depth 2
        for result in data:
            if result.get('cust_id') == cust_id:
                return result
        return None  # No match found at this depth

    # Recursive case: Dive deeper into the data structure
    if isinstance(data, list):
        for item in data:
            found = find_result_by_cust_id(item, cust_id, depth + 1)
            if found:
                return found
    elif isinstance(data, dict):
        for key in data:
            found = find_result_by_cust_id(data[key], cust_id, depth + 1)
            if found:
                return found

    return None  # No match found in any branch


def augment_race_data(iracing_api_client, race_data):
    # iterate over the race_data
    augmented_race_data = []
    # create a dictionary to cache race results that we retrieve from the API
    race_result_cache = {}

    for i, result in enumerate(race_data, start=1):
        # first check to see if this result has already been augmented
        # you know if it has been augmented if it has valid values for the keys in DETAIL_DATA_KEYS:

        if all(result.get(key) not in [None, ''] and not pd.isna(result.get(key)) for key in DETAIL_DATA_KEYS):
            print(f"Skipping {result['subsession_id']} because it has already been augmented")
            augmented_race_data.append(result)
            continue

        subsession_id = result['subsession_id']

        # if the cache has the result for the subsession_id, use it
        single_result = race_result_cache.get(subsession_id)
        if single_result is None:
            print(f"cache miss for subsession_id: {subsession_id}")
            # get the result for the subsession_id
            single_result = iracing_api_client.result(subsession_id)
            # cache the result using the subsession_id as the key
            race_result_cache[subsession_id] = single_result

        # extract the iracing values from the result
        extracted_data = extract_values_from_race_result(single_result, result['cust_id'])

        # add the extracted data to the race_data
        result.update(extracted_data)

        # calculate the challenge score v2
        racing_time = result['average_lap'] * result['laps_complete']
        result['challenge_points_v2'] = challenge_score_v2(racing_time,
                                                           result['num_entries'],
                                                           result['incident_count'],
                                                           result['start_position'],
                                                           result['finish_position'],
                                                           result['new_sub_level'],
                                                           result['laps_complete']
                                                           )

        augmented_race_data.append(result)
        print(f"Augmented {subsession_id} with fake internet points data")

    return augmented_race_data


def tidy_race_data(race_data_list):
    # race_data_list is a list of lists of dictionaries. It needs to be flattened to a single list of dictionaries
    race_data_list = sum(race_data_list, [])

    # return race_data_list if it is empty
    if not race_data_list:
        return []

    # create a dataframe from the list of dictionaries
    race_data_df = pd.DataFrame(race_data_list)
    # drop duplicates based on subsession_id and cust_id
    race_data_df.drop_duplicates(subset=['subsession_id', 'cust_id'], inplace=True)
    race_data_df.sort_values(by=['start_time', 'cust_id'], ascending=[False, True], inplace=True)
    # Convert the DataFrame to a list of dictionaries
    return race_data_df.to_dict('records')
