#!/usr/bin/env python3
"""
📊 ADD LIVE_POSITION COLUMN TO GOOGLE SHEETS
============================================
Script to add "Live_Position" column to all company sheets
This is SEPARATE from existing Location column
"""

import sys
import os
from typing import List, Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_company_sheets import multi_sheet_manager
from company_manager import company_manager
from logger import logger

def get_sheet_headers(company_id: str) -> List[str]:
    """Get current headers from a company sheet"""
    try:
        # Get all records to see current structure
        records = multi_sheet_manager.get_all_records(company_id)
        if records and len(records) > 0:
            # Return the keys from the first record (these are the headers)
            return list(records[0].keys())
        else:
            # Return default headers if no records exist
            return [
                'ID', 'Date', 'Name', 'Type', 'Client', 'Location', 
                'Orders', 'Amount', 'Remarks', 'User_ID', 'Timestamp'
            ]
    except Exception as e:
        logger.error(f"❌ Error getting headers for {company_id}: {e}")
        return []

def add_live_position_column_to_sheet(company_id: str) -> bool:
    """Add Live_Position column to a specific company sheet"""
    try:
        logger.info(f"📊 Adding Live_Position column to {company_id} sheet...")
        
        # Get current headers
        current_headers = get_sheet_headers(company_id)
        
        if not current_headers:
            logger.error(f"❌ Could not get headers for {company_id}")
            return False
        
        # Check if Live_Position column already exists
        if 'Live_Position' in current_headers:
            logger.info(f"✅ Live_Position column already exists in {company_id} sheet")
            return True
        
        # Get the worksheet
        worksheet = multi_sheet_manager.get_worksheet(company_id)
        if not worksheet:
            logger.error(f"❌ Could not get worksheet for {company_id}")
            return False
        
        # Determine where to add the column (after existing columns)
        new_column_index = len(current_headers) + 1  # +1 because sheets are 1-indexed
        
        # Insert the new column header
        worksheet.insert_cols(new_column_index, number=1)
        
        # Set the header for the new column
        worksheet.update_cell(1, new_column_index, 'Live_Position')
        
        logger.info(f"✅ Successfully added Live_Position column to {company_id} sheet at column {new_column_index}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding Live_Position column to {company_id}: {e}")
        return False

def add_live_position_column_to_all_sheets() -> Dict[str, bool]:
    """Add Live_Position column to all company sheets"""
    results = {}
    
    try:
        # Get all registered companies
        companies = company_manager.get_all_companies()
        
        if not companies:
            logger.warning("⚠️ No companies found in company manager")
            return results
        
        logger.info(f"📊 Adding Live_Position column to {len(companies)} company sheets...")
        
        for company_id in companies:
            try:
                company_info = company_manager.get_company_info(company_id)
                company_name = company_info['display_name'] if company_info else company_id
                
                logger.info(f"🔄 Processing {company_name} ({company_id})...")
                
                success = add_live_position_column_to_sheet(company_id)
                results[company_id] = success
                
                if success:
                    logger.info(f"✅ {company_name}: Live_Position column added successfully")
                else:
                    logger.error(f"❌ {company_name}: Failed to add Live_Position column")
                    
            except Exception as e:
                logger.error(f"❌ Error processing company {company_id}: {e}")
                results[company_id] = False
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Critical error in add_live_position_column_to_all_sheets: {e}")
        return results

def verify_live_position_columns() -> Dict[str, bool]:
    """Verify that Live_Position columns exist in all company sheets"""
    verification_results = {}
    
    try:
        companies = company_manager.get_all_companies()
        
        logger.info(f"🔍 Verifying Live_Position columns in {len(companies)} company sheets...")
        
        for company_id in companies:
            try:
                headers = get_sheet_headers(company_id)
                has_live_position = 'Live_Position' in headers
                verification_results[company_id] = has_live_position
                
                company_info = company_manager.get_company_info(company_id)
                company_name = company_info['display_name'] if company_info else company_id
                
                if has_live_position:
                    logger.info(f"✅ {company_name}: Live_Position column verified")
                else:
                    logger.warning(f"❌ {company_name}: Live_Position column missing")
                    
            except Exception as e:
                logger.error(f"❌ Error verifying {company_id}: {e}")
                verification_results[company_id] = False
        
        return verification_results
        
    except Exception as e:
        logger.error(f"❌ Critical error in verify_live_position_columns: {e}")
        return verification_results

def print_column_summary():
    """Print a summary of all company sheet columns"""
    try:
        companies = company_manager.get_all_companies()
        
        print("\n📊 COMPANY SHEET COLUMN SUMMARY")
        print("=" * 50)
        
        for company_id in companies:
            try:
                company_info = company_manager.get_company_info(company_id)
                company_name = company_info['display_name'] if company_info else company_id
                
                headers = get_sheet_headers(company_id)
                
                print(f"\n🏢 {company_name} ({company_id}):")
                print(f"   Columns ({len(headers)}): {', '.join(headers)}")
                
                # Check for key columns
                has_location = 'Location' in headers
                has_live_position = 'Live_Position' in headers
                
                print(f"   Location column: {'✅' if has_location else '❌'}")
                print(f"   Live_Position column: {'✅' if has_live_position else '❌'}")
                
            except Exception as e:
                print(f"   ❌ Error getting info for {company_id}: {e}")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error in print_column_summary: {e}")

def main():
    """Main function to add Live_Position columns"""
    print("📊 LIVE POSITION COLUMN SETUP")
    print("=" * 40)
    print("This script will add 'Live_Position' column to all company sheets.")
    print("This is SEPARATE from the existing 'Location' column.")
    print()
    
    try:
        # Step 1: Show current column summary
        print("📋 Step 1: Current Column Summary")
        print_column_summary()
        
        # Step 2: Add Live_Position columns
        print("\n🔄 Step 2: Adding Live_Position Columns")
        results = add_live_position_column_to_all_sheets()
        
        # Step 3: Verify additions
        print("\n🔍 Step 3: Verifying Additions")
        verification = verify_live_position_columns()
        
        # Step 4: Summary
        print("\n📊 Step 4: Final Summary")
        print("=" * 40)
        
        total_companies = len(results)
        successful_additions = sum(1 for success in results.values() if success)
        verified_columns = sum(1 for verified in verification.values() if verified)
        
        print(f"Total companies processed: {total_companies}")
        print(f"Successful additions: {successful_additions}")
        print(f"Verified columns: {verified_columns}")
        
        if verified_columns == total_companies:
            print("\n✅ SUCCESS: All company sheets now have Live_Position column!")
        else:
            print(f"\n⚠️ WARNING: {total_companies - verified_columns} sheets missing Live_Position column")
        
        # Step 5: Final column summary
        print("\n📋 Step 5: Updated Column Summary")
        print_column_summary()
        
        print("\n🎯 SETUP COMPLETE!")
        print("Live_Position columns are now ready for live position tracking.")
        print("This is separate from existing Location columns.")
        
    except Exception as e:
        logger.error(f"❌ Critical error in main: {e}")
        print(f"\n❌ SETUP FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()