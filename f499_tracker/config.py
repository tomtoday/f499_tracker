import os


class Config:
    # iRacing API creds
    IRACING_USERNAME = os.getenv("IRACING_USERNAME")
    IRACING_PASSWORD = os.getenv("IRACING_PASSWORD")

    # Google Sheets service account
    SVC_ACCT_KEY_FILE = os.getenv("F499_SVC_ACCT_KEY_FILE")

    # iRacing API constants
    EVENT_TYPE = 5  # Race

    # Google Sheets constants
    TRACKER_SHEET_NAME = "F499 Tracker v3"
    PARTICIPANT_WORKSHEET_ID = 935466926
    SERIES_WORKSHEET_ID = 2085237774
    RESULTS_WORKSHEET_ID = 1416763316

    # F499 Challenge constants
    # This is the list of strings that will be used to search for series in the iRacing API
    F499_SERIES_KEYWORDS = [
        "LMP3",
        "LMP2",
        "FIA Formula 4",
        "Falken Tyre Sports Car",
        "IMSA iRacing Series",
        "IMSA Endurance"
    ]
