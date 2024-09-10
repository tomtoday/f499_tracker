import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from f499_tracker.config import Config


class GoogleSheets:
    _client = None

    @staticmethod
    def get_client():
        if GoogleSheets._client is None:
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(Config.SVC_ACCT_KEY_FILE, scope)
            GoogleSheets._client = gspread.authorize(creds)
        return GoogleSheets._client

    @staticmethod
    def get_gspread_sheet(sheet_name, worksheet_id=None):
        client = GoogleSheets.get_client()
        if worksheet_id is not None:
            return client.open(sheet_name).get_worksheet_by_id(worksheet_id)
        else:
            return client.open(sheet_name).sheet1

    @staticmethod
    def get_participants_from_sheet(sheet_name, worksheet_id):
        retrieve_participants = []

        # get participants from the sheet named "F499 Tracker" and worksheet id 1273007515
        sheet = GoogleSheets.get_gspread_sheet(sheet_name, worksheet_id)

        df = pd.DataFrame(sheet.get_all_records())
        for index, row in df.iterrows():
            retrieve_participants.append((row['cust_id'], row['driver_name']))

        return retrieve_participants

    @staticmethod
    def get_series_from_sheet(sheet_name, worksheet_id):
        retrieve_series = []
        # get series from the sheet named "F499 Tracker" and worksheet id 2085237774
        sheet = GoogleSheets.get_gspread_sheet(sheet_name, worksheet_id)

        df = pd.DataFrame(sheet.get_all_records())
        for index, row in df.iterrows():
            retrieve_series.append(row)

        return retrieve_series

    @staticmethod
    def upload_to_gspread(sheet_name, data_csv_filename):
        sheet = GoogleSheets.get_gspread_sheet(sheet_name)
        df = pd.read_csv(data_csv_filename)
        sheet.update([df.columns.values.tolist()] + df.values.tolist())

    @staticmethod
    def append_to_gspread(sheet_name, worksheet_id, data_csv_filename_prefix):
        sheet = GoogleSheets.get_gspread_sheet(sheet_name, worksheet_id)

        # Read existing data from the Google Sheet, skipping the first two rows
        existing_df = pd.DataFrame(sheet.get_all_records())

        # # Load new data from the CSV file  skipping the first row
        new_df = pd.read_csv(f"{data_csv_filename_prefix}_data.csv")

        # Append new data to the existing data using pd.concat
        df = pd.concat([existing_df, new_df], ignore_index=True)

        # drop duplicates based on subsession_id and cust_id
        df.drop_duplicates(subset=['subsession_id', 'cust_id'], inplace=True)
        # sor the df by start_  time, descending and cust_id
        df.sort_values(by=['start_time', 'cust_id'], ascending=[False, True], inplace=True)

        # Clear the sheet so that we can write the now complete new data
        sheet.clear()
        # write df to the sheet, including the header
        sheet.update([df.columns.values.tolist()] + df.values.tolist())

        # batch_format appropriate columns to be numbers with no decimal places
        sheet.batch_format([{'range': 'A:A', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}},
                            {'range': 'B:B', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}},
                            {'range': 'C:C', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}},
                            {'range': 'E:E', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}},
                            {'range': 'G:G', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}},
                            {'range': 'K:K', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}},
                            {'range': 'L:L', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}},
                            {'range': 'M:M', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}},
                            {'range': 'N:N', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}},
                            {'range': 'O:O', 'format': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}}
                            ])

    @staticmethod
    def simple_write_to_sheet(sheet_name, worksheet_id, data):
        sheet = GoogleSheets.get_gspread_sheet(sheet_name, worksheet_id)
        # sheet.clear()
        # the value of data is a two item list. First item is the header and the second item is the data
        # Sets 'Hello world' in 'A2' cell
        # worksheet.update([['Hello world']], 'A2')
        sheet.update([[data[0]]], 'A1')
        sheet.update([[data[1]]], 'A2')
        # sheet.update('A1', data[0])
        # sheet.update('A2', data[1])


    @staticmethod
    def merge_race_data_with_gspread_data(race_data):
        # merge race_data pulled from the API with the data in the google sheet
        # First, we need get the data from the google sheet and put it into a DataFrame
        existing_google_sheet = GoogleSheets.get_gspread_sheet(Config.TRACKER_SHEET_NAME, Config.RESULTS_WORKSHEET_ID)
        existing_df = pd.DataFrame(existing_google_sheet.get_all_records())
        return GoogleSheets.merge_api_race_data_with_existing_data(pd.DataFrame(race_data), existing_df)

    @staticmethod
    def merge_api_race_data_with_existing_data(race_data_frame, existing_data_frame):
        # Append new data to the existing data using pd.concat
        merged_df = pd.concat([existing_data_frame, race_data_frame], ignore_index=True)
        merged_df = merged_df.combine_first(race_data_frame).combine_first(existing_data_frame)
        # Identify columns with float64 dtype
        float_cols = merged_df.select_dtypes(include=['float64']).columns

        # Convert these columns to object dtype
        merged_df[float_cols] = merged_df[float_cols].astype(object)

        # Fill remaining NaN values with an empty string
        merged_df.fillna('', inplace=True)

        # drop duplicates based on subsession_id and cust_id
        merged_df.drop_duplicates(subset=['subsession_id', 'cust_id'], inplace=True)

        if merged_df.empty:
            return []

        # sort the df by start_time, descending and cust_id
        merged_df.sort_values(by=['start_time', 'cust_id'], ascending=[False, True], inplace=True)

        return merged_df.to_dict('records')
