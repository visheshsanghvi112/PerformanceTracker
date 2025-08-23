import gspread
from oauth2client.service_account import ServiceAccountCredentials
from decorators import retry, handle_errors, measure_time
from logger import logger

# Google Sheets setup with error handling
try:
    SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    CREDS = ServiceAccountCredentials.from_json_keyfile_name('yugrow-dd1d5-6676a7b2d2ea.json', SCOPE)
    CLIENT = gspread.authorize(CREDS)
    SHEET = CLIENT.open('bot').sheet1
    logger.info("✅ Legacy sheets.py connected to Google Sheets")
except FileNotFoundError:
    logger.warning("⚠️ Google Sheets credentials file not found - legacy sheets disabled")
    CLIENT = None
    SHEET = None
except Exception as e:
    logger.warning(f"⚠️ Legacy Google Sheets connection failed: {e}")
    CLIENT = None
    SHEET = None

# Append a row to the sheet with error handling and retries
@retry(max_attempts=3, delay=1.0, exceptions=(Exception,))
@handle_errors(default_return=False)
@measure_time()
def append_row(row):
    """
    Append a row to the Google Sheet with error handling and retries
    
    Args:
        row: List of values to append
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not SHEET:
        logger.warning("⚠️ Cannot append row - Google Sheets not available (offline mode)")
        return False
        
    try:
        SHEET.append_row(row)
        logger.info(f"Successfully appended row to sheet: {row[0] if row else 'empty'}")
        return True
    except Exception as e:
        logger.error(f"Failed to append row to sheet: {str(e)}")
        raise

# Get all records from the sheet with error handling
@retry(max_attempts=3, delay=1.0, exceptions=(Exception,))
@handle_errors(default_return=[])
@measure_time()
def get_all_records():
    """
    Get all records from the Google Sheet with error handling
    
    Returns:
        list: List of records or empty list if failed
    """
    if not SHEET:
        logger.warning("⚠️ Cannot get records - Google Sheets not available (offline mode)")
        return []
        
    try:
        records = SHEET.get_all_records()
        logger.info(f"Successfully retrieved {len(records)} records from sheet")
        return records
    except Exception as e:
        logger.error(f"Failed to get records from sheet: {str(e)}")
        raise

# Get records with filtering
@retry(max_attempts=3, delay=1.0, exceptions=(Exception,))
@handle_errors(default_return=[])
def get_records_by_filter(filter_func):
    """
    Get filtered records from the sheet
    
    Args:
        filter_func: Function to filter records
        
    Returns:
        list: Filtered records
    """
    try:
        all_records = get_all_records()
        filtered_records = [record for record in all_records if filter_func(record)]
        logger.info(f"Filtered {len(filtered_records)} records from {len(all_records)} total")
        return filtered_records
    except Exception as e:
        logger.error(f"Failed to filter records: {str(e)}")
        raise

# Check if sheet is accessible
@handle_errors(default_return=False)
def check_sheet_connection():
    """
    Check if the Google Sheet is accessible
    
    Returns:
        bool: True if accessible, False otherwise
    """
    if not SHEET:
        logger.warning("⚠️ Google Sheets not available (offline mode)")
        return False
        
    try:
        SHEET.get('A1')  # Try to get a single cell
        return True
    except Exception as e:
        logger.error(f"Sheet connection check failed: {str(e)}")
        return False 