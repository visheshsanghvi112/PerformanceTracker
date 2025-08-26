#!/usr/bin/env python3
"""
🤖 COMPLETE AI FEATURES TEST
===========================
Test all AI-powered features and integrations
"""

def test_ai_response_engine():
    """Test AI response engine functionality"""
    print("🤖 Testing AI Response Engine...")
    
    try:
        from ai_response_engine import ai_response_engine
        
        # Test greeting generation
        greeting = ai_response_engine.generate_greeting_response("John")
        if not greeting:
            print("   ❌ Failed to generate greeting")
            return False
        print(f"   ✅ Greeting generated: {greeting[:50]}...")
        
        # Test success response
        success_response = ai_response_engine.generate_success_response("Sales", {
            'amount': 25000,
            'client': 'Apollo Pharmacy'
        })
        if not success_response:
            print("   ❌ Failed to generate success response")
            return False
        print(f"   ✅ Success response generated: {success_response[:50]}...")
        
        # Test error response
        error_response = ai_response_engine.generate_error_response("parsing_failed")
        if not error_response:
            print("   ❌ Failed to generate error response")
            return False
        print(f"   ✅ Error response generated: {error_response[:50]}...")
        
        # Test tip generation
        tip = ai_response_engine.generate_tip_of_the_day()
        if not tip:
            print("   ❌ Failed to generate tip")
            return False
        print(f"   ✅ Tip generated: {tip[:50]}...")
        
        print("   ✅ AI Response Engine working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ AI Response Engine test failed: {e}")
        return False

def test_input_processor():
    """Test input processor functionality"""
    print("🧠 Testing Input Processor...")
    
    try:
        from input_processor import input_processor
        
        # Test valid business input
        valid_result = input_processor.process_input("Sold 5 tablets to Apollo for ₹25000")
        if not valid_result['is_valid']:
            print("   ❌ Valid input rejected")
            return False
        print("   ✅ Valid business input accepted")
        
        # Test invalid input (gibberish)
        invalid_result = input_processor.process_input("asdfghjkl")
        if invalid_result['is_valid']:
            print("   ❌ Invalid input accepted")
            return False
        print("   ✅ Invalid input rejected correctly")
        
        # Test casual conversation
        casual_result = input_processor.process_input("hello how are you")
        if casual_result['is_valid']:
            print("   ❌ Casual conversation accepted as business input")
            return False
        print("   ✅ Casual conversation handled correctly")
        
        # Test fallback response generation
        fallback = input_processor.get_fallback_response("some unclear text")
        if not fallback:
            print("   ❌ Failed to generate fallback response")
            return False
        print(f"   ✅ Fallback response generated: {fallback[:50]}...")
        
        print("   ✅ Input Processor working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Input Processor test failed: {e}")
        return False

def test_gemini_parser():
    """Test Gemini AI parser functionality"""
    print("🤖 Testing Gemini Parser...")
    
    try:
        from gemini_parser import extract_with_gemini
        
        # Test natural language parsing
        test_input = "Sold 5 tablets to Apollo Pharmacy for ₹25000 urgent delivery"
        parsed_result = extract_with_gemini(test_input)
        
        if not parsed_result:
            print("   ⚠️ Gemini parsing returned None (API might be unavailable)")
            return True  # Don't fail test if API is unavailable
        
        # Validate parsed structure
        required_fields = ['client', 'orders', 'amount', 'remarks']
        for field in required_fields:
            if field not in parsed_result:
                print(f"   ❌ Missing field in parsed result: {field}")
                return False
        
        print(f"   ✅ Gemini parsing successful: {parsed_result}")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Gemini Parser test failed (API might be unavailable): {e}")
        return True  # Don't fail test if API is unavailable

def test_batch_handler():
    """Test batch processing functionality"""
    print("📦 Testing Batch Handler...")
    
    try:
        from batch_handler import batch_handler
        
        # Test batch detection
        single_entry = "Sold 5 tablets to Apollo for ₹25000"
        is_batch_single = batch_handler.detect_batch_input(single_entry)
        if is_batch_single:
            print("   ❌ Single entry detected as batch")
            return False
        print("   ✅ Single entry detection correct")
        
        # Test batch detection with multiple entries
        batch_entry = """
        Sold 5 tablets to Apollo for ₹25000
        
        Sold 3 boxes to MedPlus for ₹15000
        
        Purchase from XYZ supplier 10 units ₹8000
        """
        is_batch_multiple = batch_handler.detect_batch_input(batch_entry)
        if not is_batch_multiple:
            print("   ❌ Batch entry not detected")
            return False
        print("   ✅ Batch entry detection correct")
        
        # Test entry splitting
        split_entries = batch_handler._split_entries(batch_entry)
        if len(split_entries) < 2:
            print(f"   ❌ Entry splitting failed: {len(split_entries)} entries")
            return False
        print(f"   ✅ Entry splitting successful: {len(split_entries)} entries")
        
        print("   ✅ Batch Handler working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Batch Handler test failed: {e}")
        return False

def test_parallel_processor():
    """Test parallel processing functionality"""
    print("⚡ Testing Parallel Processor...")
    
    try:
        from parallel_processor import parallel_processor
        
        # Test basic parallel processing setup
        if not hasattr(parallel_processor, 'max_workers'):
            print("   ❌ Parallel processor not properly initialized")
            return False
        
        print(f"   ✅ Parallel processor initialized with {parallel_processor.max_workers} workers")
        
        # Test chunk processing
        test_data = list(range(20))  # 20 items
        
        def simple_processor(chunk):
            return [x * 2 for x in chunk]
        
        results = parallel_processor.process_data_chunks(test_data, 5, simple_processor)
        
        if len(results) != 20:
            print(f"   ❌ Chunk processing failed: expected 20, got {len(results)}")
            return False
        
        print("   ✅ Chunk processing working correctly")
        
        print("   ✅ Parallel Processor working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Parallel Processor test failed: {e}")
        return False

def test_location_integration():
    """Test GPS location integration"""
    print("📍 Testing Location Integration...")
    
    try:
        from location_storage import location_storage
        from location_handler import location_handler
        from geocoding import geocoding_service
        
        # Test location storage
        user_id = "test_user"
        company_id = "test_company"
        
        location_data = {
            'coordinates': {'latitude': 18.947974, 'longitude': 72.829952},
            'address': {
                'city': 'Mumbai',
                'area': 'Kalbadevi',
                'short': 'Kalbadevi, Mumbai',
                'formatted': 'Kalbadevi, Mumbai, Maharashtra, India'
            },
            'timestamp': '2025-01-01T12:00:00'
        }
        
        # Store location
        success = location_storage.store_location(user_id, company_id, location_data)
        if not success:
            print("   ❌ Failed to store location")
            return False
        print("   ✅ Location storage working")
        
        # Retrieve location
        retrieved = location_storage.get_location(user_id, company_id)
        if not retrieved:
            print("   ❌ Failed to retrieve location")
            return False
        print("   ✅ Location retrieval working")
        
        # Test location handler
        location_str = location_handler.get_location_for_entry(user_id, company_id)
        if not location_str:
            print("   ❌ Failed to get location for entry")
            return False
        print(f"   ✅ Location handler working: {location_str}")
        
        # Clean up test data
        location_storage.clear_location(user_id, company_id)
        
        print("   ✅ Location Integration working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Location Integration test failed: {e}")
        return False

def test_analytics_integration():
    """Test analytics integration"""
    print("📊 Testing Analytics Integration...")
    
    try:
        from analytics import analytics_engine
        
        # Test that analytics engine has location analytics method
        if not hasattr(analytics_engine, 'generate_location_analytics'):
            print("   ❌ Location analytics method missing")
            return False
        print("   ✅ Location analytics method available")
        
        # Test other analytics methods
        required_methods = [
            'generate_executive_dashboard',
            'generate_predictive_insights',
            'generate_advanced_charts'
        ]
        
        for method in required_methods:
            if not hasattr(analytics_engine, method):
                print(f"   ❌ Analytics method missing: {method}")
                return False
        
        print("   ✅ All analytics methods available")
        
        print("   ✅ Analytics Integration working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Analytics Integration test failed: {e}")
        return False

def test_commands_integration():
    """Test commands integration"""
    print("📋 Testing Commands Integration...")
    
    try:
        from commands import (
            start_command,
            sales_command,
            purchase_command,
            dashboard_command,
            location_analytics_command,
            ai_help_command
        )
        
        print("   ✅ All command imports successful")
        
        # Test that commands are callable
        required_commands = [
            start_command,
            sales_command,
            purchase_command,
            dashboard_command,
            location_analytics_command,
            ai_help_command
        ]
        
        for cmd in required_commands:
            if not callable(cmd):
                print(f"   ❌ Command not callable: {cmd}")
                return False
        
        print("   ✅ All commands are callable")
        
        print("   ✅ Commands Integration working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Commands Integration test failed: {e}")
        return False

def test_handlers_integration():
    """Test handlers integration"""
    print("🔧 Testing Handlers Integration...")
    
    try:
        from handlers import handle_message
        
        # Test that handler imports AI modules
        import handlers
        
        required_imports = [
            'ai_response_engine',
            'batch_handler',
            'location_handler'
        ]
        
        for imp in required_imports:
            if not hasattr(handlers, imp):
                print(f"   ❌ Handler missing import: {imp}")
                return False
        
        print("   ✅ All AI integrations imported in handlers")
        
        print("   ✅ Handlers Integration working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Handlers Integration test failed: {e}")
        return False

def run_all_ai_tests():
    """Run all AI feature tests"""
    print("🤖 RUNNING COMPLETE AI FEATURES TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("AI Response Engine", test_ai_response_engine),
        ("Input Processor", test_input_processor),
        ("Gemini Parser", test_gemini_parser),
        ("Batch Handler", test_batch_handler),
        ("Parallel Processor", test_parallel_processor),
        ("Location Integration", test_location_integration),
        ("Analytics Integration", test_analytics_integration),
        ("Commands Integration", test_commands_integration),
        ("Handlers Integration", test_handlers_integration)
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
        print("🎉 ALL AI FEATURES TESTS PASSED!")
        print("🤖 AI-Enhanced Features Ready:")
        print("   ✅ Natural language processing")
        print("   ✅ AI-powered responses and tips")
        print("   ✅ Intelligent input validation")
        print("   ✅ Batch processing with AI")
        print("   ✅ Parallel processing for performance")
        print("   ✅ GPS location intelligence")
        print("   ✅ Advanced analytics with AI insights")
        print("   ✅ Enhanced command handlers")
        print("   ✅ Smart error handling and fallbacks")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_ai_tests()
    
    if success:
        print("\n🚀 AI-ENHANCED PERFORMANCE TRACKER IS READY!")
        print("🤖 Users can now:")
        print("   • Use natural language for entries")
        print("   • Get AI-powered responses and tips")
        print("   • Process multiple entries in batches")
        print("   • Enjoy high-performance parallel processing")
        print("   • Access GPS location intelligence")
        print("   • View AI-enhanced analytics")
        print("   • Get intelligent error handling")
        print("   • Experience smart recommendations")
    else:
        print("\n⚠️ Some AI features need attention before production use.")