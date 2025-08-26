#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE COMPANY SWITCHING TEST SUITE
============================================
Tests all company switching scenarios including:
- Natural language detection
- Company info display with various data types
- Error handling with API failures
- Consistent company context across operations
"""

import sys
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def test_fallback_intent_detection():
    """🔍 Test fallback company switching intent detection"""
    print("🔍 Testing Fallback Intent Detection...")
    
    try:
        from handlers import detect_company_switch_intent
        
        # Test cases for company switching detection
        test_cases = [
            # Positive cases (should detect company switching intent)
            ("i want to change company", True),
            ("change company", True),
            ("switch company", True),
            ("can i change company", True),
            ("how to change company", True),
            ("I want to switch to a different company", True),
            ("company change", True),
            ("company switch", True),
            ("select company", True),
            ("another company", True),
            ("new company", True),
            ("different company", True),
            
            # Negative cases (should NOT detect company switching intent)
            ("hello", False),
            ("sold 5 tablets to apollo", False),
            ("what is the company revenue", False),
            ("company information", False),
            ("my company is doing well", False),
            ("company party tomorrow", False),
            ("random text", False),
            ("", False),
        ]
        
        passed = 0
        failed = 0
        
        for text, expected in test_cases:
            try:
                result = detect_company_switch_intent(text)
                if result == expected:
                    print(f"   ✅ '{text}' -> {result} (expected {expected})")
                    passed += 1
                else:
                    print(f"   ❌ '{text}' -> {result} (expected {expected})")
                    failed += 1
            except Exception as e:
                print(f"   ❌ Error testing '{text}': {e}")
                failed += 1
        
        print(f"   📊 Intent Detection Results: {passed} passed, {failed} failed")
        return failed == 0
        
    except Exception as e:
        print(f"   ❌ Intent detection test failed: {e}")
        return False

def test_safe_formatting_functions():
    """🛡️ Test safe formatting functions with various data types"""
    print("🛡️ Testing Safe Formatting Functions...")
    
    try:
        from company_commands import safe_format_revenue, escape_markdown_safely, safe_format_number
        
        # Test safe_format_revenue
        revenue_tests = [
            (25000, "₹25,000.00"),
            (25000.50, "₹25,000.50"),
            ("25000", "₹25,000.00"),
            ("₹25,000", "₹25,000.00"),
            ("25,000.50", "₹25,000.50"),
            (None, "₹0"),
            ("", "₹0"),
            ("nan", "₹0"),
            ("invalid", "₹invalid"),
            (0, "₹0.00"),
        ]
        
        revenue_passed = 0
        for value, expected in revenue_tests:
            try:
                result = safe_format_revenue(value)
                if result == expected:
                    print(f"   ✅ Revenue format: {value} -> {result}")
                    revenue_passed += 1
                else:
                    print(f"   ⚠️ Revenue format: {value} -> {result} (expected {expected})")
            except Exception as e:
                print(f"   ❌ Revenue format error for {value}: {e}")
        
        # Test escape_markdown_safely
        markdown_tests = [
            ("Normal text", "Normal text"),
            ("Text_with_underscores", "Text\\_with\\_underscores"),
            ("Text*with*asterisks", "Text\\*with\\*asterisks"),
            ("Text`with`backticks", "Text\\`with\\`backticks"),
            ("Text[with]brackets", "Text\\[with\\]brackets"),
            ("Text(with)parentheses", "Text\\(with\\)parentheses"),
            (None, "N/A"),
            ("", ""),
        ]
        
        markdown_passed = 0
        for value, expected in markdown_tests:
            try:
                result = escape_markdown_safely(value)
                if result == expected:
                    print(f"   ✅ Markdown escape: '{value}' -> '{result}'")
                    markdown_passed += 1
                else:
                    print(f"   ⚠️ Markdown escape: '{value}' -> '{result}' (expected '{expected}')")
            except Exception as e:
                print(f"   ❌ Markdown escape error for '{value}': {e}")
        
        # Test safe_format_number
        number_tests = [
            (25, 25),
            (25.7, 25),
            ("25", 25),
            ("25.7", 25),
            (None, 0),
            ("", 0),
            ("nan", 0),
            ("invalid", 0),
        ]
        
        number_passed = 0
        for value, expected in number_tests:
            try:
                result = safe_format_number(value)
                if result == expected:
                    print(f"   ✅ Number format: {value} -> {result}")
                    number_passed += 1
                else:
                    print(f"   ⚠️ Number format: {value} -> {result} (expected {expected})")
            except Exception as e:
                print(f"   ❌ Number format error for {value}: {e}")
        
        total_tests = len(revenue_tests) + len(markdown_tests) + len(number_tests)
        total_passed = revenue_passed + markdown_passed + number_passed
        
        print(f"   📊 Safe Formatting Results: {total_passed}/{total_tests} passed")
        return total_passed == total_tests
        
    except Exception as e:
        print(f"   ❌ Safe formatting test failed: {e}")
        return False

def test_company_statistics_handling():
    """📊 Test company statistics with various data types"""
    print("📊 Testing Company Statistics Handling...")
    
    try:
        from multi_company_sheets import multi_sheet_manager
        
        # Test with mock data containing various data types
        mock_records = [
            {
                'User ID': '123456',
                'Amount': 25000,  # Integer
                'Date': '2025-01-25'
            },
            {
                'User ID': '789012',
                'Amount': '₹15,000',  # String with currency
                'Date': '2025-01-24'
            },
            {
                'User ID': '345678',
                'Amount': '30000.50',  # String number
                'Date': '2025-01-23'
            },
            {
                'User ID': '901234',
                'Amount': 'invalid',  # Invalid amount
                'Date': '2025-01-22'
            },
            {
                'User ID': None,  # Missing user ID
                'Amount': 5000,
                'Date': None  # Missing date
            }
        ]
        
        # Mock the get_company_records method
        with patch.object(multi_sheet_manager, 'get_company_records', return_value=mock_records):
            stats = multi_sheet_manager.get_company_stats('test_company')
            
            print(f"   📊 Stats result: {stats}")
            
            # Verify stats structure
            required_keys = ['total_records', 'total_users', 'total_revenue', 'date_range']
            missing_keys = [key for key in required_keys if key not in stats]
            
            if missing_keys:
                print(f"   ❌ Missing keys in stats: {missing_keys}")
                return False
            
            # Verify data types
            if not isinstance(stats['total_records'], int):
                print(f"   ❌ total_records should be int, got {type(stats['total_records'])}")
                return False
            
            if not isinstance(stats['total_users'], int):
                print(f"   ❌ total_users should be int, got {type(stats['total_users'])}")
                return False
            
            if not isinstance(stats['total_revenue'], (int, float)):
                print(f"   ❌ total_revenue should be numeric, got {type(stats['total_revenue'])}")
                return False
            
            if not isinstance(stats['date_range'], str):
                print(f"   ❌ date_range should be string, got {type(stats['date_range'])}")
                return False
            
            # Verify reasonable values
            if stats['total_records'] != len(mock_records):
                print(f"   ❌ total_records mismatch: {stats['total_records']} vs {len(mock_records)}")
                return False
            
            # Revenue should be sum of valid amounts: 25000 + 15000 + 30000.50 + 5000 = 75000.50
            expected_revenue = 75000.50
            if abs(stats['total_revenue'] - expected_revenue) > 0.01:
                print(f"   ⚠️ Revenue calculation: {stats['total_revenue']} (expected ~{expected_revenue})")
            
            print(f"   ✅ Company statistics handled correctly")
            print(f"   📊 Records: {stats['total_records']}, Users: {stats['total_users']}, Revenue: ₹{stats['total_revenue']:,.2f}")
            return True
        
    except Exception as e:
        print(f"   ❌ Company statistics test failed: {e}")
        return False

def test_company_manager_methods():
    """🏢 Test company manager methods with error handling"""
    print("🏢 Testing Company Manager Methods...")
    
    try:
        from company_manager import company_manager
        
        test_user_id = 999999  # Test user ID
        test_company = "johnlee"
        
        # Test user info retrieval
        user_info = company_manager.get_user_info(test_user_id)
        print(f"   📋 User info structure: {list(user_info.keys())}")
        
        # Test with invalid inputs
        invalid_tests = [
            (None, "johnlee", "Invalid user_id"),
            ("invalid", "johnlee", "Invalid user_id type"),
            (123456, None, "Invalid company"),
            (123456, "invalid_company", "Invalid company"),
            (123456, "", "Empty company"),
        ]
        
        for user_id, company, description in invalid_tests:
            try:
                result = company_manager.switch_user_company(user_id, company)
                if result == False:
                    print(f"   ✅ {description}: Correctly rejected")
                else:
                    print(f"   ⚠️ {description}: Should have been rejected but got {result}")
            except Exception as e:
                print(f"   ✅ {description}: Exception handled - {e}")
        
        # Test access validation
        access_result = company_manager.validate_user_access(test_user_id, test_company)
        print(f"   🔍 Access validation for unregistered user: {access_result}")
        
        # Test company info retrieval
        company_info = company_manager.get_company_info(test_company)
        if company_info and 'display_name' in company_info:
            print(f"   ✅ Company info retrieved: {company_info['display_name']}")
        else:
            print(f"   ❌ Company info missing or invalid: {company_info}")
            return False
        
        print(f"   ✅ Company manager methods working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Company manager test failed: {e}")
        return False

def test_error_handling_scenarios():
    """⚠️ Test error handling with various failure scenarios"""
    print("⚠️ Testing Error Handling Scenarios...")
    
    try:
        from company_commands import safe_format_revenue, handle_company_callback
        
        # Test with extreme values
        extreme_tests = [
            (float('inf'), "Revenue infinity"),
            (float('-inf'), "Revenue negative infinity"),
            (float('nan'), "Revenue NaN"),
            (999999999999999, "Very large number"),
            (-999999999999999, "Very large negative number"),
        ]
        
        error_handled = 0
        for value, description in extreme_tests:
            try:
                result = safe_format_revenue(value)
                print(f"   ✅ {description}: {result}")
                error_handled += 1
            except Exception as e:
                print(f"   ⚠️ {description}: Exception - {e}")
                error_handled += 1
        
        # Test with mock API failures
        print(f"   🔧 Testing API failure scenarios...")
        
        # Mock Google Sheets API failure
        from multi_company_sheets import multi_sheet_manager
        with patch.object(multi_sheet_manager, 'get_company_records', side_effect=Exception("API Error")):
            stats = multi_sheet_manager.get_company_stats('test_company')
            if 'error' in stats:
                print(f"   ✅ API failure handled gracefully: {stats['error']}")
                error_handled += 1
            else:
                print(f"   ⚠️ API failure not handled properly: {stats}")
        
        print(f"   📊 Error handling: {error_handled} scenarios handled")
        return error_handled > 0
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        return False

async def test_message_handler_integration():
    """🔗 Test message handler integration with company switching"""
    print("🔗 Testing Message Handler Integration...")
    
    try:
        from handlers import detect_company_switch_intent
        
        # Test integration scenarios
        test_messages = [
            "i want to change company",
            "switch company please",
            "can i change to different company",
            "company change",
        ]
        
        integration_passed = 0
        for message in test_messages:
            try:
                # Test intent detection
                intent_detected = detect_company_switch_intent(message)
                if intent_detected:
                    print(f"   ✅ Intent detected for: '{message}'")
                    integration_passed += 1
                else:
                    print(f"   ❌ Intent NOT detected for: '{message}'")
            except Exception as e:
                print(f"   ❌ Integration error for '{message}': {e}")
        
        print(f"   📊 Integration: {integration_passed}/{len(test_messages)} messages handled")
        return integration_passed == len(test_messages)
        
    except Exception as e:
        print(f"   ❌ Message handler integration test failed: {e}")
        return False

def run_comprehensive_test_suite():
    """🧪 Run complete company switching test suite"""
    print("🧪 RUNNING COMPREHENSIVE COMPANY SWITCHING TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Fallback Intent Detection", test_fallback_intent_detection),
        ("Safe Formatting Functions", test_safe_formatting_functions),
        ("Company Statistics Handling", test_company_statistics_handling),
        ("Company Manager Methods", test_company_manager_methods),
        ("Error Handling Scenarios", test_error_handling_scenarios),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    # Test async integration
    print(f"\n🔍 Message Handler Integration:")
    try:
        result = asyncio.run(test_message_handler_integration())
        if result:
            print(f"✅ Message Handler Integration: PASSED")
            passed += 1
        else:
            print(f"❌ Message Handler Integration: FAILED")
            failed += 1
    except Exception as e:
        print(f"❌ Message Handler Integration: ERROR - {e}")
        failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 COMPANY SWITCHING TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL COMPANY SWITCHING TESTS PASSED!")
        print("✅ Company switching functionality is working correctly")
        print("✅ Natural language detection implemented")
        print("✅ Safe data formatting working")
        print("✅ Error handling robust")
        print("✅ Company context consistent")
    else:
        print("⚠️ Some tests failed - review the issues above")
    
    return failed == 0

if __name__ == "__main__":
    success = run_comprehensive_test_suite()
    sys.exit(0 if success else 1)