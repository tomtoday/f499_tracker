# F499 Challenge Tracker

A Python application for tracking iRacing F499 Challenge participation and scoring.

NOTE: this tool has not been updated to use the iRacing oAuth authorization flow. It is useful as a historical record, the most useful part is the scoring algorithm in [f499_tracker/challenge_utils.py](f499_tracker/challenge_utils.py)

## Overview

This project pulls data from the iRacing API to track F499 Challenge participation across multiple racing series including:
- LMP3
- FIA Formula 4
- GT4
- Sports Car Challenge by Falken Tyre

## Features

- Fetches race results from iRacing API
- Calculates custom challenge scoring metrics
- Stores data in SQLite database
- Updates Google Sheets with results
- Tracks "first zero incident" races

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables:
   - `IRACING_USERNAME`: Your iRacing username
   - `IRACING_PASSWORD`: Your iRacing password
   - `F499_SVC_ACCT_KEY_FILE`: Path to Google Sheets service account key file

## Usage

Run the tracker:
```python
python main.py
```

## Architecture

- `SimpleTracker`: Main tracker class (recommended)
- `IRacingAPIHandler`: Handles iRacing API interactions
- `GoogleSheets`: Manages Google Sheets integration
- `DBHandler`: SQLite database operations
- `challenge_utils`: Scoring calculation functions

This was coded by sim dentists.