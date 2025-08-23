"""
📊 ENHANCED MULTI-COMPANY GOOGLE SHEETS MANAGER
==============================================
Manages separate sheets for JohnLee, Yugrow, Ambica, Baker & Davis
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from decorators import retry, handle_errors, measure_time
from logger import logger
from company_manager import company_manager
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

class MultiCompanySheetManager:
    """📊 Multi-Company Google Sheets Manager"""
    
    def __init__(self):
        """📊 Initialize Multi-Company Sheet Manager with error handling"""
        logger.info("🔄 Initializing multi-company Google Sheets connection...")
        
        try:
            # Google Sheets setup with error handling
            self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            # Try to load credentials
            try:
                self.creds = ServiceAccountCredentials.from_json_keyfile_name('yugrow-dd1d5-6676a7b2d2ea.json', self.scope)
                logger.info("✅ Google Sheets credentials loaded")
            except FileNotFoundError:
                logger.warning("⚠️ Google Sheets credentials file not found - running in offline mode")
                self.client = None
                self.spreadsheet = None
                self.sheet_cache = {}
                return
            except Exception as cred_error:
                logger.error(f"❌ Credential error: {cred_error}")
                self.client = None
                self.spreadsheet = None
                self.sheet_cache = {}
                return
            
            # Try to authorize and connect
            try:
                self.client = gspread.authorize(self.creds)
                self.spreadsheet = self.client.open('bot')
                logger.info("✅ Connected to Google Sheets")
            except Exception as connect_error:
                logger.error(f"❌ Google Sheets connection error: {connect_error}")
                self.client = None
                self.spreadsheet = None
                self.sheet_cache = {}
                return
            
            # Sheet cache for performance
            self.sheet_cache = {}
            
            # Initialize company sheets
            self._initialize_company_sheets()
            logger.info("📊 Multi-Company Sheet Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize multi-company sheets: {e}")
            self.client = None
            self.spreadsheet = None
            self.sheet_cache = {}
    
    def _initialize_company_sheets(self):
        """🏗️ Initialize sheets for each company"""
        if not self.client or not self.spreadsheet:
            logger.warning("⚠️ Skipping sheet initialization - Google Sheets not available")
            return
            
        try:
            existing_sheets = [sheet.title for sheet in self.spreadsheet.worksheets()]
            logger.info(f"📋 Existing sheets: {existing_sheets}")
            
            for company_key, company_info in company_manager.get_all_companies().items():
                sheet_name = company_info['sheet_name']
                
                if sheet_name not in existing_sheets:
                    # Create new sheet for company
                    logger.info(f"🏗️ Creating sheet for {company_info['display_name']}")
                    sheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=15)
                    
                    # Add headers
                    headers = [
                        "Entry ID", "Date", "User Name", "Type", "Client", 
                        "Location", "Orders", "Amount", "Remarks", "User ID", 
                        "Time", "Company", "Entry Timestamp", "Last Modified"
                    ]
                    sheet.append_row(headers)
                    logger.info(f"✅ Created sheet {sheet_name} with headers")
                else:
                    logger.info(f"✅ Sheet {sheet_name} already exists")
                
                # Cache the sheet
                self.sheet_cache[company_key] = self.spreadsheet.worksheet(sheet_name)
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize company sheets: {e}")
            # Don't raise - allow bot to continue without sheets
    
    def _get_company_sheet(self, company_key: str):
        """📊 Get sheet for specific company"""
        if not self.client or not self.spreadsheet:
            raise Exception("Google Sheets not available (offline mode)")
            
        try:
            if company_key not in self.sheet_cache:
                sheet_name = company_manager.get_company_sheet_name(company_key)
                self.sheet_cache[company_key] = self.spreadsheet.worksheet(sheet_name)
            
            return self.sheet_cache[company_key]
            
        except Exception as e:
            logger.error(f"❌ Failed to get sheet for company {company_key}: {e}")
            raise
    
    @retry(max_attempts=3, delay=1.0, exceptions=(Exception,))
    @handle_errors(default_return=False)
    @measure_time()
    def append_row_to_company(self, company_key: str, row: List) -> bool:
        """📝 Append row to specific company's sheet"""
        if not self.client or not self.spreadsheet:
            logger.warning(f"⚠️ Cannot append row - Google Sheets not available (offline mode)")
            return False
            
        try:
            sheet = self._get_company_sheet(company_key)
            
            # Add company and timestamp info
            enhanced_row = row.copy()
            if len(enhanced_row) < 14:
                enhanced_row.extend([''] * (14 - len(enhanced_row)))
            
            # Ensure company name and timestamp are set
            enhanced_row[11] = company_manager.get_company_display_name(company_key)  # Company
            enhanced_row[12] = enhanced_row[12] if enhanced_row[12] else datetime.now().isoformat()  # Entry Timestamp
            enhanced_row[13] = datetime.now().isoformat()  # Last Modified
            
            sheet.append_row(enhanced_row)
            logger.info(f"📝 Successfully appended row to {company_key} sheet: {enhanced_row[0] if enhanced_row else 'empty'}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to append row to {company_key} sheet: {str(e)}")
            raise
    
    def append_row(self, row: List, company_key: str = None) -> bool:
        """📝 Append row with compatibility for handlers (calls append_row_to_company)"""
        if not company_key:
            logger.error("❌ No company key provided for append_row")
            return False
        return self.append_row_to_company(company_key, row)
    
    @retry(max_attempts=3, delay=1.0, exceptions=(Exception,))
    @handle_errors(default_return=[])
    @measure_time()
    def get_company_records(self, company_key: str, user_id: Optional[int] = None) -> List[Dict]:
        """📊 Get records from specific company's sheet"""
        try:
            sheet = self._get_company_sheet(company_key)
            records = sheet.get_all_records()
            
            # Filter by user ID if provided
            if user_id:
                filtered_records = []
                for record in records:
                    # Check if user ID matches (handle both string and int)
                    record_user_id = str(record.get('User ID', ''))
                    if record_user_id == str(user_id):
                        filtered_records.append(record)
                records = filtered_records
            
            logger.info(f"📊 Retrieved {len(records)} records from {company_key} sheet" + 
                       (f" for user {user_id}" if user_id else ""))
            return records
            
        except Exception as e:
            logger.error(f"❌ Failed to get records from {company_key} sheet: {str(e)}")
            raise
    
    @retry(max_attempts=3, delay=1.0, exceptions=(Exception,))
    @handle_errors(default_return=[])
    @measure_time()
    def get_all_user_records(self, user_id: int) -> List[Dict]:
        """📊 Get all records for a user across all their companies"""
        try:
            all_records = []
            allowed_companies = company_manager.get_user_allowed_companies(user_id)
            
            for company_key in allowed_companies:
                company_records = self.get_company_records(company_key, user_id)
                # Add company context to each record
                for record in company_records:
                    record['_source_company'] = company_key
                all_records.extend(company_records)
            
            logger.info(f"📊 Retrieved {len(all_records)} total records for user {user_id}")
            return all_records
            
        except Exception as e:
            logger.error(f"❌ Failed to get all records for user {user_id}: {str(e)}")
            return []
    
    @handle_errors(default_return=False)
    def check_connection(self) -> bool:
        """🔍 Check if Google Sheets is accessible"""
        try:
            # Try to access the main spreadsheet
            sheets = self.spreadsheet.worksheets()
            logger.info(f"✅ Connection OK - {len(sheets)} sheets accessible")
            return True
        except Exception as e:
            logger.error(f"❌ Connection check failed: {str(e)}")
            return False
    
    @retry(max_attempts=3, delay=1.0, exceptions=(Exception,))
    @handle_errors(default_return=[])
    @measure_time()
    def get_all_records(self, company_key: str = None, user_id: int = None) -> List[Dict]:
        """🔍 Get all records - wrapper method for analytics compatibility"""
        try:
            if user_id and not company_key:
                # Get all records for a user across companies
                return self.get_all_user_records(user_id)
            elif company_key:
                # Get records for a specific company
                return self.get_company_records(company_key, user_id)
            else:
                logger.warning("⚠️ No company or user specified - using default Yugrow")
                return self.get_company_records("yugrow")
        except Exception as e:
            logger.error(f"❌ Failed to get all records: {str(e)}")
            return []
    
    def get_company_stats(self, company_key: str) -> Dict:
        """📈 Get basic stats for a company"""
        try:
            records = self.get_company_records(company_key)
            
            if not records:
                return {"total_records": 0, "total_users": 0, "total_revenue": 0}
            
            import pandas as pd
            df = pd.DataFrame(records)
            
            stats = {
                "total_records": len(df),
                "total_users": df['User ID'].nunique() if 'User ID' in df.columns else 0,
                "total_revenue": df['Amount'].sum() if 'Amount' in df.columns else 0,
                "date_range": f"{df['Date'].min()} to {df['Date'].max()}" if 'Date' in df.columns else "No dates"
            }
            
            logger.info(f"📈 Stats for {company_key}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get stats for {company_key}: {e}")
            return {"error": str(e)}


# Create global instance
multi_sheet_manager = MultiCompanySheetManager()

# ═══════════════════════════════════════════════════════════════
# 🔄 BACKWARD COMPATIBILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def append_row(row: List, company_key: str = None) -> bool:
    """🔄 Backward compatible append_row function"""
    if not company_key:
        logger.warning("⚠️ No company specified for append_row - using default")
        company_key = "yugrow"  # Default fallback
    
    return multi_sheet_manager.append_row_to_company(company_key, row)

def get_all_records(company_key: str = None, user_id: int = None) -> List[Dict]:
    """🔄 Backward compatible get_all_records function"""
    if not company_key:
        if user_id:
            # Get all records for user across companies
            return multi_sheet_manager.get_all_user_records(user_id)
        else:
            logger.warning("⚠️ No company specified for get_all_records - using Yugrow")
            company_key = "yugrow"  # Default fallback
    
    return multi_sheet_manager.get_company_records(company_key, user_id)

def get_records_by_filter(filter_func, company_key: str = None):
    """🔄 Backward compatible filtered records function"""
    try:
        if not company_key:
            company_key = "yugrow"  # Default fallback
        
        all_records = multi_sheet_manager.get_company_records(company_key)
        filtered_records = [record for record in all_records if filter_func(record)]
        logger.info(f"🔍 Filtered {len(filtered_records)} records from {len(all_records)} total")
        return filtered_records
    except Exception as e:
        logger.error(f"❌ Failed to filter records: {str(e)}")
        raise

def check_sheet_connection() -> bool:
    """🔄 Backward compatible connection check"""
    return multi_sheet_manager.check_connection()
