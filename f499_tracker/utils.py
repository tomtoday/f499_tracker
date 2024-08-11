import csv
import json
from datetime import timedelta


def write_results_to_json_file(results, filename):
    # Write the raw results to a JSON file
    with open(f"{filename}_raw_results.json", 'w') as jsonfile:
        json.dump(results, jsonfile)


def write_results_to_csv_file(race_data_list, filename):
    # Specify the order of your columns
    fieldnames = ["season_year",
                  "season_quarter",
                  "week_number",
                  "racer_name",
                  "cust_id",
                  "series_name",
                  "series_id",
                  "start_time",
                  "track_name",
                  "session_link",
                  "subsession_id",
                  "car_name",
                  "start_position",
                  "finish_position",
                  "incident_count",
                  "_499_points",
                  "old_irating",
                  "old_license_level",
                  "old_cpi",
                  "old_sub_level",
                  "new_irating",
                  "new_license_level",
                  "new_cpi",
                  "new_sub_level",
                  'average_lap',
                  'laps_complete',
                  'num_entries',
                  'challenge_points_v2'
                  ]

    # Open your CSV file in write mode
    with open(f'{filename}_data.csv', 'w', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header to the CSV file
        writer.writeheader()

        # Write each dictionary in the list to the CSV file
        for race_data_dict in race_data_list:
            writer.writerow(race_data_dict)


def print_race_results(race_data):
    print(f"Race {race_data['start_time']}:")
    print(f"Driver: {race_data['racer_name']} - Customer ID: {race_data['cust_id']}")
    print(f"Session Link: [{race_data['subsession_id']}]({race_data['session_link']})")
    print(f"Series: {race_data['series_name']}")
    print(f"Track: {race_data['track_name']}")
    print(f"Start Position: {race_data['start_position'] if race_data['start_position'] else 'N/A'}")
    print(f"Finish Position: {race_data['finish_position'] if race_data['finish_position'] else 'N/A'}")
    print(f"Number of Incidents: {race_data['incident_count']}")
    print(f"F499 Scoring Points: {race_data['_499_points']}")
    print()


def read_csv_as_dict(file_path):
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data


def convert_ticks_to_timedelta(ticks):
    # Convert ticks to seconds
    total_seconds = ticks / 10000
    return timedelta(seconds=total_seconds)
