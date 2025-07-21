import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS = ServiceAccountCredentials.from_json_keyfile_name('yugrow-dd1d5-010a6b203565.json', SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET = CLIENT.open('bot').sheet1

# Append a row to the sheet
def append_row(row):
    SHEET.append_row(row)

# Get all records from the sheet
def get_all_records():
    return SHEET.get_all_records() 