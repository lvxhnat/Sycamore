import os
import pandas as pd

from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleSheetUtility:

    def __init__(self):

        self.credentials_path = os.environ['GOOGLE_SHEET_CREDENTIALS']

    def create_object_gsheets(self, scopes):
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        return sheet

    def get_gsheets(
            self,
            spreadsheet_id: str = "1Hx5OFCtdzisc1B_jpMfYfHBxtw-vyjYLvYa-dcvyvR0",
            sheet=None):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        if(sheet == None):
            sheet = self.create_google_sheet_object(
                self.credentials_path, scopes=SCOPES)

        return [x["properties"]["title"] for x in sheet.get(spreadsheetId=spreadsheet_id).execute()["sheets"]]

    def create_gsheets(
            spreadsheet_id: str,
            sheet_name: str,
            sheet: str = None):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        if(sheet == None):
            sheet = self.create_google_sheet_object(scopes=SCOPES)
        try:
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }

            response = sheet.batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()

            return response
        except Exception as e:
            print(e)

    def read_df_from_gsheets(
            self,
            spreadsheet_id: str,
            sheet_name: str = 'Sheet1',
            sheet_range: str = None,
            first_row_is_header: str = True):
        '''Returns a Pandas DataFrame from Google Sheets, 
        for a given spreadsheet_id and range. Sheet must be shared 
        with the service account, e.g. :
        googlesheet@root-sanctuary-178203.iam.gserviceaccount.com'''

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        sheet = self.create_google_sheet_object(
            self.credentials_path, scopes=SCOPES)

        name_range = sheet_name + '!' + sheet_range if sheet_range else sheet_name
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=name_range).execute()
        df = pd.DataFrame(result['values'])

        if first_row_is_header:
            df.columns = df.loc[0]
            df = df.drop(0)
        return df

    def write_df_to_gsheets(
            self,
            df: pd.DataFrame,
            spreadsheet_id: str,
            sheet_name: str = 'Sheet1',
            start_cell: str = 'A1',
            include_column_names: str = True):
        '''Writes data from Pandas DataFrame to Google Sheets, 
        for a given spreadsheet_id, a sheet name and a start cell. 
        The service account must have write access to the sheet, e.g. :
        googlesheet@root-sanctuary-178203.iam.gserviceaccount.com'''

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
                  'https://www.googleapis.com/auth/drive']

        sheet = self.create_object_gsheets(
            self.credentials_path, scopes=SCOPES)

        if(sheet_name not in self.get_gsheets(spreadsheet_id, sheet=sheet)):
            self.create_gsheets(spreadsheet_id, sheet_name)

        name_range = sheet_name + '!' + start_cell

        values = []
        if include_column_names:
            values.extend([df.columns.values.tolist()])
        values.extend(df.values.tolist())
        data = {'values': values}

        response = sheet.values().update(spreadsheetId=spreadsheet_id,
                                         body=data,
                                         range=name_range,
                                         valueInputOption='RAW').execute()
        return response

    def clear_values_of_gsheet(
            self,
            spreadsheet_id,
            sheet_range,
            sheet_name='Sheet1'):
        '''Clears cells in a Google Sheet, 
        for a given spreadsheet_id, and a sheet range 
        The service account must have write access to the sheet, e.g. :
        googlesheet@root-sanctuary-178203.iam.gserviceaccount.com'''
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        sheet = self.create_object_gsheets(
            self.credentials_path, scopes=SCOPES)
        name_range = sheet_name + '!' + sheet_range
        response = sheet.values().clear(
            spreadsheetId=spreadsheet_id, range=name_range).execute()
        return response
