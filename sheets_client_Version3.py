import gspread
from google.oauth2.service_account import Credentials
from config import (
    GOOGLE_CREDS_FILE,
    SPREADSHEET_NAME,
    SHEET_SKUS,
    SHEET_DB_PRECIOS,
    SHEET_LOGS_ERRORES,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

class SheetsClient:
    def __init__(self):
        creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        self.spreadsheet = client.open(SPREADSHEET_NAME)
        self.ws_skus = self.spreadsheet.worksheet(SHEET_SKUS)
        self.ws_db = self.spreadsheet.worksheet(SHEET_DB_PRECIOS)
        self.ws_logs = self.spreadsheet.worksheet(SHEET_LOGS_ERRORES)

    def get_skus(self):
        return self.ws_skus.get_all_records()

    def append_precio(self, row):
        self.ws_db.append_row(row, value_input_option="USER_ENTERED")

    def append_error(self, row):
        self.ws_logs.append_row(row, value_input_option="USER_ENTERED")