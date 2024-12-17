import os


class Config:
    # F499 Challenge constants
    # This is the list of strings that will be used to search for series in the iRacing API
    F499_SEASON3_SERIES_KEYWORDS = [
        "LMP3",
        "LMP2",
        "FIA Formula 4",
        "Falken Tyre Sports Car",
        "IMSA iRacing Series",
        "IMSA Endurance"
    ]

    # iRacing API creds
    IRACING_USERNAME = os.getenv("IRACING_USERNAME")
    IRACING_PASSWORD = os.getenv("IRACING_PASSWORD")

    # Google Sheets service account
    SVC_ACCT_KEY_FILE = os.getenv("F499_SVC_ACCT_KEY_FILE")

    # iRacing API constants
    EVENT_TYPE = 5  # Race

    # Google Sheets constants
    # TRACKER_SHEET_NAME = "F499 Tracker v3"
    # TRACKER_SHEET_NAME = "Top Dentist 2024S3W12 Tracker"
    # TRACKER_SHEET_NAME = "F499 2024S4 Challenge"
    TRACKER_SHEET_NAME = "F499 2025S1 Challenge"

    # PARTICIPANT_WORKSHEET_ID = 935466926
    PARTICIPANT_WORKSHEET_ID = 1419950067
    SERIES_WORKSHEET_ID = 2085237774
    RESULTS_WORKSHEET_ID = 1416763316
    # LAST_RUN_SHEET_ID = None
    LAST_RUN_SHEET_ID = 1483679123

    SHEET_COLUMN_NAMES = {
        'season_year': 'Year',
        'season_quarter': 'Quarter',
        'week_number': 'Week',
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
        'cust_id': 'Customer ID'
    }
