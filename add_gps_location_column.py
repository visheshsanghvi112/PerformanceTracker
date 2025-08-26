#!/usr/bin/env python3
"""
📍 ADD GPS LOCATION COLUMN TO GOOGLE SHEETS
==========================================
Adds GPS_Location column to existing Google Sheets without affecting the original Location column
"""

def add_gps_location_column():
    """Add GPS_Location column to all company sheets"""
    print("📍 Adding GPS_Location column to Google Sheets...")
    
    try:
        from multi_company_sheets import multi_sheet_manager
        
        # Company sheet mapping
        companies = {
            "johnlee": "JohnLee_Data",
            "yugrow": "Yugrow_Data", 
            "ambica": "Ambica_Data",
            "baker": "Baker_Data"
        }
        
        for company_id, sheet_name in companies.items():
            try:
                print(f"\n🔧 Processing {sheet_name}...")
                
                # Get the worksheet
                worksheet = multi_sheet_manager.spreadsheet.worksheet(sheet_name)
                
                # Get current headers (first row)
                headers = worksheet.row_values(1)
                print(f"   📋 Current headers: {len(headers)} columns")
                
                # Check if GPS_Location already exists
                if 'GPS_Location' in headers:
                    print(f"   ✅ GPS_Location column already exists in {sheet_name}")
                    continue
                
                # Add GPS_Location header
                headers.append('GPS_Location')
                
                # Update the header row
                worksheet.update('1:1', [headers])
                print(f"   ✅ Added GPS_Location column to {sheet_name}")
                print(f"   📊 New header count: {len(headers)} columns")
                
                # Show the new headers
                print(f"   📋 Updated headers:")
                for i, header in enumerate(headers[-5:], len(headers)-4):  # Show last 5 headers
                    print(f"      {i}. {header}")
                
            except Exception as e:
                print(f"   ⚠️ Error processing {sheet_name}: {e}")
                continue
        
        print("\n✅ GPS_Location column addition completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding GPS_Location columns: {e}")
        return False

def verify_gps_location_columns():
    """Verify that GPS_Location columns were added successfully"""
    print("\n🔍 Verifying GPS_Location columns...")
    
    try:
        from multi_company_sheets import multi_sheet_manager
        
        companies = {
            "johnlee": "JohnLee_Data",
            "yugrow": "Yugrow_Data", 
            "ambica": "Ambica_Data",
            "baker": "Baker_Data"
        }
        
        for company_id, sheet_name in companies.items():
            try:
                worksheet = multi_sheet_manager.spreadsheet.worksheet(sheet_name)
                headers = worksheet.row_values(1)
                
                if 'GPS_Location' in headers:
                    gps_col_index = headers.index('GPS_Location') + 1
                    print(f"   ✅ {sheet_name}: GPS_Location in column {gps_col_index}")
                else:
                    print(f"   ❌ {sheet_name}: GPS_Location column missing")
                    
            except Exception as e:
                print(f"   ⚠️ {sheet_name}: Error checking - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying columns: {e}")
        return False

if __name__ == "__main__":
    print("📍 ADDING GPS LOCATION COLUMN TO GOOGLE SHEETS")
    print("=" * 55)
    
    print("🎯 Purpose: Add GPS_Location column for live GPS tracking")
    print("📋 Note: This is separate from the existing Location column")
    print("🔧 The existing Location column will remain unchanged")
    
    success = add_gps_location_column()
    
    if success:
        verify_gps_location_columns()
        print("\n🎉 GPS_Location column setup completed!")
        print("📍 The bot will now add GPS location data to the new column")
    else:
        print("\n❌ GPS_Location column setup failed")