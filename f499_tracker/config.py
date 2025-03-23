import os


class Config:
    DB_NAME = "2025s2_dev.db"
    SEASON_YEAR = 2025
    SEASON_QUARTER = 2

    # F499 Challenge constants
    # This is the list of strings that will be used to search for series in the iRacing API
    F499_SERIES_KEYWORDS = [
        "LMP3",
        "FIA Formula 4",
        "FIA F4",
        "GT4",
        "Sports Car Challenge by Falken Tyre",
    ]

    # iRacing API creds
    IRACING_USERNAME = os.getenv("IRACING_USERNAME")
    IRACING_PASSWORD = os.getenv("IRACING_PASSWORD")

    # Google Sheets service account
    SVC_ACCT_KEY_FILE = os.getenv("F499_SVC_ACCT_KEY_FILE")

    # iRacing API constants
    EVENT_TYPE = 5  # Race

    # Google Sheets constants
    TRACKER_SHEET_NAME = "F499 2025S2 Challenge"

    PARTICIPANT_WORKSHEET_ID = 1419950067
    SERIES_WORKSHEET_ID = 2085237774
    RESULTS_WORKSHEET_ID = 1416763316
    LAST_RUN_SHEET_ID = 1483679123
    FIRST_ZERO_EX_SHEET_ID = 623987881

    SHEET_COLUMN_NAMES = {
        'season_year': 'Year',
        'season_quarter': 'Quarter',
        'season_week_number': 'Week',
        'racer_name': 'Driver',
        'license_category': 'License Category',
        'start_time': 'Start Time',
        'series_name': 'Series',
        'car_name': 'Car',
        'track_name': 'Track',
        'session_link': 'Session URL',
        'start_position': 'Start Position',
        'finish_position': 'Finish Position',
        'incident_count': 'Incident Count',
        'num_entries': 'Number of Entries',
        'laps_complete': 'Laps Completed',
        'challenge_points_v2': 'Challenge Points V2',
        'challenge_points_v3': 'Challenge Points V3',
        'average_lap': 'Average Lap',
        'old_cpi': 'Old CPI',
        'new_cpi': 'New CPI',
        'old_irating': 'Old iRating',
        'new_irating': 'New iRating',
        'old_license_level': 'Old License Level',
        'new_license_level': 'New License Level',
        'old_sub_level': 'Old Sub Level',
        'new_sub_level': 'New Sub Level',
        'series_id': 'Series ID',
        'subsession_id': 'Subsession ID',
        'cust_id': 'Customer ID',
        'series_week_number': 'Series Week',
        'strength_of_field': 'Strength of Field',
    }

    SEASON_INFO = {
        2024: [
            {
                'season_year': 2024,
                'season_number': 1,
                'start_date': '2023-12-12T00:00:00Z',
                'weeks_in_season': 12
            },
            {
                'season_year': 2024,
                'season_number': 2,
                'start_date': '2024-03-12T00:00:00Z',
                'weeks_in_season': 12
            },
            {
                'season_year': 2024,
                'season_number': 3,
                'start_date': '2024-06-11T00:00:00Z',
                'weeks_in_season': 12
            },
            {
                'season_year': 2024,
                'season_number': 4,
                'start_date': '2024-09-10T00:00:00Z',
                'weeks_in_season': 13
            }
        ],
        2025: [
            {
                'season_year': 2025,
                'season_number': 1,
                'start_date': '2024-12-17T00:00:00Z',
                'weeks_in_season': 12
            },
            {
                'season_year': 2025,
                'season_number': 2,
                'start_date': '2025-03-18T00:00:00Z',
                'weeks_in_season': 12
            },
            {
                'season_year': 2025,
                'season_number': 3,
                'start_date': '2025-06-20T00:00:00Z',
                'weeks_in_season': 12
            },
            {
                'season_year': 2025,
                'season_number': 4,
                'start_date': '2025-09-12T00:00:00Z',
                'weeks_in_season': 12
            }
        ]
    }
