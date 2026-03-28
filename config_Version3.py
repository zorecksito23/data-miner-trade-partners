import os

SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Data Miner Home Depot")
SHEET_SKUS = os.getenv("SHEET_SKUS", "SKUS")
SHEET_DB_PRECIOS = os.getenv("SHEET_DB_PRECIOS", "DB Precios")
SHEET_LOGS_ERRORES = os.getenv("SHEET_LOGS_ERRORES", "LOGS Errores")
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "service_account.json")
TIMEZONE = os.getenv("TIMEZONE", "America/Mexico_City")