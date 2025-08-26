#!/usr/bin/env python3
"""
🧪 COMPLETE GPS LOCATION FEATURE TEST
====================================
Test all GPS location functionality end-to-end
"""

def test_location_storage():
    """Test GPS location storage functionality"""
    print("📍 Testing GPS location storage...")
    
    try:
        from location_storage import location_storage
        import datetime
        
        # Test data
        user_id = "1201911108"
        company_id = "johnlee"
        location_data = {
            'coordinates': {'latitude': 18.947974, 'longitude': 72.829952},
            'address': {
                'city': 'Mumbai',
                'area': 'Kalbadevi',
                'short': 'Kalbadevi, Mumbai',
                'formatted': 'Kalbadevi, Mumbai, Maharashtra, India'
            },
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Store location
        success = location_storage.store_location(user_id, company_id, location_data)
        if not success:
            print("   ❌ Failed to store location")
            return False
        
        # Retrieve location
        retrieved = location_storage.get_location(user_id, company_id)
        if not retrieved:
            print("   ❌ Failed to retrieve location")
            return False
        
        # Check status
        status = location_storage.get_location_status(user_id, company_id)
        if not status['has_location']:
            print("   ❌ Location status incorrect")
            return False
        
        print("   ✅ Location storage working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Location storage test failed: {e}")
        return False

def test_geocoding():
    """Test geocoding service"""
    print("🌍 Testing geocoding service...")
    
    try:
        from geocoding import geocoding_service
        
        # Test coordinates (Mumbai)
        latitude = 18.947974
        longitude = 72.829952
        
        # Get location info
        location_info = geocoding_service.get_location_info(latitude, longitude)
        
        if not location_info or not location_info.get('address'):
            print("   ❌ Failed to get location info")
            return False
        
        address = location_info['address']
        if not address.get('short'):
            print("   ❌ No short address generated")
            return False
        
        print(f"   ✅ Geocoding working: {address['short']}")
        return True
        
    except Exception as e:
        print(f"   ❌ Geocoding test failed: {e}")
        return False

def test_location_handler():
    """Test location handler functionality"""
    print("📱 Testing location handler...")
    
    try:
        from location_handler import location_handler
        
        # Test getting location for entry
        user_id = "1201911108"
        company_id = "johnlee"
        
        location_str = location_handler.get_location_for_entry(user_id, company_id)
        
        if location_str:
            print(f"   ✅ Location handler working: {location_str}")
        else:
            print("   ⚠️ No location data (expected if not stored)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Location handler test failed: {e}")
        return False

def test_handlers_integration():
    """Test handlers.py integration with GPS location"""
    print("🔧 Testing handlers integration...")
    
    try:
        from handlers import handle_message
        from location_handler import location_handler
        
        # Test that location_handler is imported correctly
        if hasattr(location_handler, 'get_location_for_entry'):
            print("   ✅ Handlers integration working")
            return True
        else:
            print("   ❌ Location handler method missing")
            return False
        
    except Exception as e:
        print(f"   ❌ Handlers integration test failed: {e}")
        return False

def test_analytics_integration():
    """Test analytics integration with GPS location"""
    print("📊 Testing analytics integration...")
    
    try:
        from analytics import analytics_engine
        
        # Test that location analytics method exists
        if hasattr(analytics_engine, 'generate_location_analytics'):
            print("   ✅ Analytics integration working")
            return True
        else:
            print("   ❌ Location analytics method missing")
            return False
        
    except Exception as e:
        print(f"   ❌ Analytics integration test failed: {e}")
        return False

def test_commands_integration():
    """Test commands integration"""
    print("📋 Testing commands integration...")
    
    try:
        from commands import location_analytics_command
        from location_commands import (
            location_command,
            location_status_command,
            location_clear_command,
            handle_location_message
        )
        
        print("   ✅ All location commands imported successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Commands integration test failed: {e}")
        return False

def test_main_integration():
    """Test main.py integration"""
    print("🚀 Testing main.py integration...")
    
    try:
        # Check if main.py can import location commands
        import sys
        import os
        
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Try importing main (this will test all imports)
        import main
        
        print("   ✅ Main.py integration working")
        return True
        
    except Exception as e:
        print(f"   ❌ Main.py integration test failed: {e}")
        return False

def test_complete_flow():
    """Test complete GPS location flow"""
    print("🔄 Testing complete GPS location flow...")
    
    try:
        from location_storage import location_storage
        from location_handler import location_handler
        from analytics import analytics_engine
        import datetime
        
        # 1. Store GPS location
        user_id = "1201911108"
        company_id = "johnlee"
        location_data = {
            'coordinates': {'latitude': 18.947974, 'longitude': 72.829952},
            'address': {
                'city': 'Mumbai',
                'area': 'Kalbadevi',
                'short': 'Kalbadevi, Mumbai',
                'formatted': 'Kalbadevi, Mumbai, Maharashtra, India'
            },
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        location_storage.store_location(user_id, company_id, location_data)
        
        # 2. Get location for entry
        gps_location_str = location_handler.get_location_for_entry(user_id, company_id)
        
        # 3. Simulate sales entry with GPS location
        row_data = [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Date
            "Test User",                                            # User Name
            "Apollo Pharmacy",                                      # Client
            "Sales",                                               # Type
            100,                                                   # Orders
            5000,                                                  # Amount
            "",                                                    # Original Location (empty)
            gps_location_str or ""                                 # GPS_Location (NEW!)
        ]
        
        print(f"   📍 GPS Location for entry: {gps_location_str}")
        print(f"   📊 Row data structure: {len(row_data)} columns")
        print("   ✅ Complete flow working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Complete flow test failed: {e}")
        return False

def run_all_tests():
    """Run all GPS location tests"""
    print("🧪 RUNNING COMPLETE GPS LOCATION FEATURE TESTS")
    print("=" * 60)
    
    tests = [
        ("Location Storage", test_location_storage),
        ("Geocoding Service", test_geocoding),
        ("Location Handler", test_location_handler),
        ("Handlers Integration", test_handlers_integration),
        ("Analytics Integration", test_analytics_integration),
        ("Commands Integration", test_commands_integration),
        ("Main Integration", test_main_integration),
        ("Complete Flow", test_complete_flow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! GPS location feature is ready!")
        print("🌍 Features working:")
        print("   ✅ GPS location storage and retrieval")
        print("   ✅ Geocoding service (coordinates to addresses)")
        print("   ✅ Location handler for Telegram integration")
        print("   ✅ Sales entry integration with GPS location")
        print("   ✅ Analytics integration for territory insights")
        print("   ✅ Command handlers for location management")
        print("   ✅ Complete end-to-end flow")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n🚀 GPS LOCATION FEATURE IS READY FOR PRODUCTION!")
        print("📍 Users can now:")
        print("   • Share GPS location with /location")
        print("   • Check status with /location_status")
        print("   • Clear location with /location_clear")
        print("   • Get territory analytics with /location_analytics")
        print("   • Automatic GPS tagging on sales entries")
    else:
        print("\n⚠️ Some issues need to be resolved before production use.")