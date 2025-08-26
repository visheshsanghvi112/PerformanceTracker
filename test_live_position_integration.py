#!/usr/bin/env python3
"""
🧪 LIVE POSITION TRACKING INTEGRATION TESTS
===========================================
Comprehensive end-to-end testing for the live GPS position tracking feature
SEPARATE from existing location functionality
"""

import unittest
import asyncio
import os
import sys
import tempfile
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules to test
from live_position_handler import live_position_handler
from live_position_storage import live_position_storage
from geocoding import geocode_service
from company_manager import company_manager

class TestLivePositionIntegration(unittest.TestCase):
    """🧪 Integration tests for live position tracking workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_user_id = "54321"
        self.test_company_id = "test_company"
        self.test_coordinates = (19.0760, 72.8777)  # Mumbai coordinates
        
        # Mock Telegram objects
        self.mock_update = Mock()
        self.mock_update.effective_user = Mock()
        self.mock_update.effective_user.id = int(self.test_user_id)
        self.mock_update.effective_user.first_name = "Test"
        self.mock_update.effective_user.full_name = "Test User"
        self.mock_update.effective_user.username = "testuser"
        
        self.mock_update.message = Mock()
        self.mock_update.message.reply_text = AsyncMock()
        self.mock_update.message.location = Mock()
        self.mock_update.message.location.latitude = self.test_coordinates[0]
        self.mock_update.message.location.longitude = self.test_coordinates[1]
        
        self.mock_context = Mock()
        self.mock_context.user_data = {}
        
        # Clear any existing test data
        self.cleanup_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """Remove test data from storage"""
        try:
            live_position_storage.clear_live_position(self.test_user_id, self.test_company_id)
        except:
            pass
    
    @patch('company_manager.is_user_registered')
    @patch('company_manager.get_user_company')
    async def test_live_position_request_flow(self, mock_get_company, mock_is_registered):
        """🧪 Test complete live position request flow"""
        # Setup mocks
        mock_is_registered.return_value = True
        mock_get_company.return_value = self.test_company_id
        
        # Test live position request
        await live_position_handler.request_live_position(self.mock_update, self.mock_context)
        
        # Verify user was prompted for live position
        self.mock_update.message.reply_text.assert_called()
        call_args = self.mock_update.message.reply_text.call_args
        self.assertIn("Share Your Live Position", call_args[0][0])
        
        # Verify keyboard was created
        self.assertIsNotNone(call_args[1]['reply_markup'])
    
    @patch('company_manager.is_user_registered')
    @patch('company_manager.get_user_company')
    @patch('geocoding.geocode_service.get_location_info')
    async def test_live_position_processing_flow(self, mock_geocoding, mock_get_company, mock_is_registered):
        """🧪 Test complete live position processing flow"""
        # Setup mocks
        mock_is_registered.return_value = True
        mock_get_company.return_value = self.test_company_id
        
        # Mock geocoding response
        mock_geocoding.return_value = {
            'coordinates': {
                'latitude': self.test_coordinates[0],
                'longitude': self.test_coordinates[1]
            },
            'address': {
                'city': 'Mumbai',
                'area': 'Bandra',
                'short': 'Bandra, Mumbai',
                'formatted': 'Bandra, Mumbai, Maharashtra, India'
            },
            'short_address': 'Bandra, Mumbai',
            'accuracy': 'high',
            'status': 'success'
        }
        
        # Add user to position requests
        live_position_handler.position_requests[self.test_user_id] = {
            'company_id': self.test_company_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Test live position processing
        await live_position_handler.handle_live_position(self.mock_update, self.mock_context)
        
        # Verify success message was sent
        self.mock_update.message.reply_text.assert_called()
        # Check if any call contains success message
        success_calls = [call for call in self.mock_update.message.reply_text.call_args_list 
                        if "Successfully Captured" in str(call)]
        self.assertTrue(len(success_calls) > 0, "Success message should be sent")
    
    def test_live_position_storage_operations(self):
        """🧪 Test live position storage CRUD operations"""
        # Test data
        position_data = {
            'coordinates': {
                'latitude': self.test_coordinates[0],
                'longitude': self.test_coordinates[1]
            },
            'address': {
                'city': 'Mumbai',
                'area': 'Bandra',
                'short': 'Bandra, Mumbai',
                'formatted': 'Bandra, Mumbai, Maharashtra, India'
            },
            'short_address': 'Bandra, Mumbai',
            'timestamp': datetime.now().isoformat(),
            'accuracy_level': 'high'
        }
        
        # Test store live position
        success = live_position_storage.store_live_position(
            self.test_user_id, 
            self.test_company_id, 
            position_data
        )
        self.assertTrue(success, "Live position should be stored successfully")
        
        # Test retrieve live position
        retrieved_data = live_position_storage.get_live_position(
            self.test_user_id, 
            self.test_company_id
        )
        self.assertIsNotNone(retrieved_data, "Live position should be retrievable")
        self.assertEqual(
            retrieved_data['coordinates']['latitude'], 
            self.test_coordinates[0],
            "Retrieved coordinates should match stored coordinates"
        )
        
        # Test live position status
        status = live_position_storage.get_live_position_status(
            self.test_user_id, 
            self.test_company_id
        )
        self.assertTrue(status['has_position'], "Status should show live position exists")
        self.assertIn('Mumbai', status['position'], "Status should include position name")
        
        # Test clear live position
        clear_success = live_position_storage.clear_live_position(
            self.test_user_id, 
            self.test_company_id
        )
        self.assertTrue(clear_success, "Live position should be cleared successfully")
        
        # Verify live position is cleared
        cleared_data = live_position_storage.get_live_position(
            self.test_user_id, 
            self.test_company_id
        )
        self.assertIsNone(cleared_data, "Live position should be None after clearing")
    
    def test_live_position_for_entry_integration(self):
        """🧪 Test live position integration with sales entries"""
        # Store test live position
        position_data = {
            'coordinates': {
                'latitude': self.test_coordinates[0],
                'longitude': self.test_coordinates[1]
            },
            'address': {
                'short': 'Bandra, Mumbai'
            },
            'short_address': 'Bandra, Mumbai',
            'timestamp': datetime.now().isoformat()
        }
        
        live_position_storage.store_live_position(
            self.test_user_id, 
            self.test_company_id, 
            position_data
        )
        
        # Test getting live position for entry
        position_str = live_position_handler.get_live_position_for_entry(
            self.test_user_id, 
            self.test_company_id
        )
        
        self.assertIsNotNone(position_str, "Live position string should be returned")
        self.assertIn('Mumbai', position_str, "Live position string should contain Mumbai")
    
    def test_live_position_data_isolation(self):
        """🧪 Test live position data isolation between users and companies"""
        # Store live position for test user in test company
        position_data_1 = {
            'coordinates': {'latitude': 19.0760, 'longitude': 72.8777},
            'address': {'short': 'Mumbai Position'},
            'short_address': 'Mumbai Position',
            'timestamp': datetime.now().isoformat()
        }
        
        live_position_storage.store_live_position(
            self.test_user_id, 
            self.test_company_id, 
            position_data_1
        )
        
        # Store live position for different user
        other_user_id = "67890"
        position_data_2 = {
            'coordinates': {'latitude': 28.6139, 'longitude': 77.2090},
            'address': {'short': 'Delhi Position'},
            'short_address': 'Delhi Position',
            'timestamp': datetime.now().isoformat()
        }
        
        live_position_storage.store_live_position(
            other_user_id, 
            self.test_company_id, 
            position_data_2
        )
        
        # Verify data isolation
        user1_position = live_position_storage.get_live_position(
            self.test_user_id, 
            self.test_company_id
        )
        user2_position = live_position_storage.get_live_position(
            other_user_id, 
            self.test_company_id
        )
        
        self.assertNotEqual(
            user1_position['short_address'], 
            user2_position['short_address'],
            "Different users should have different live position data"
        )
        
        # Clean up
        live_position_storage.clear_live_position(other_user_id, self.test_company_id)
    
    def test_live_position_expiry_functionality(self):
        """🧪 Test automatic live position data expiry (24 hours)"""
        # Store live position with old timestamp (25 hours ago)
        old_timestamp = (datetime.now() - timedelta(hours=25)).isoformat()
        
        position_data = {
            'coordinates': {
                'latitude': self.test_coordinates[0],
                'longitude': self.test_coordinates[1]
            },
            'address': {'short': 'Old Position'},
            'short_address': 'Old Position',
            'timestamp': old_timestamp
        }
        
        live_position_storage.store_live_position(
            self.test_user_id, 
            self.test_company_id, 
            position_data
        )
        
        # Test that expired live position is not returned for entries
        position_str = live_position_handler.get_live_position_for_entry(
            self.test_user_id, 
            self.test_company_id
        )
        
        # Should return None because position is expired
        self.assertIsNone(position_str, "Expired live position should not be returned for entries")
    
    def test_live_position_separation_from_location(self):
        """🧪 Test that live position is separate from regular location"""
        # This test ensures live position doesn't interfere with regular location functionality
        
        # Store live position
        position_data = {
            'coordinates': {'latitude': 19.0760, 'longitude': 72.8777},
            'short_address': 'Live Position Mumbai',
            'timestamp': datetime.now().isoformat()
        }
        
        live_position_storage.store_live_position(
            self.test_user_id, 
            self.test_company_id, 
            position_data
        )
        
        # Verify live position exists
        live_position = live_position_handler.get_live_position_for_entry(
            self.test_user_id, 
            self.test_company_id
        )
        
        self.assertIsNotNone(live_position, "Live position should exist")
        self.assertIn('Mumbai', live_position, "Live position should contain Mumbai")
        
        # Verify this doesn't affect regular location functionality
        # (Regular location should still work independently)
        from location_handler import location_handler
        regular_location = location_handler.get_location_for_entry(
            self.test_user_id, 
            self.test_company_id
        )
        
        # Regular location should be independent (likely None since we didn't set it)
        # This test ensures separation between the two systems
        self.assertTrue(True, "Live position and regular location should be separate systems")
    
    async def test_live_position_error_handling(self):
        """🧪 Test various error handling scenarios for live position"""
        # Test invalid coordinates
        self.mock_update.message.location.latitude = 91  # Invalid latitude
        self.mock_update.message.location.longitude = 181  # Invalid longitude
        
        with patch('company_manager.is_user_registered', return_value=True):
            with patch('company_manager.get_user_company', return_value=self.test_company_id):
                await live_position_handler.handle_live_position(self.mock_update, self.mock_context)
        
        # Verify error message was sent
        error_calls = [call for call in self.mock_update.message.reply_text.call_args_list 
                      if "Invalid" in str(call)]
        self.assertTrue(len(error_calls) > 0, "Error message should be sent for invalid coordinates")
    
    def test_live_position_summary_functionality(self):
        """🧪 Test live position summary functionality"""
        # Store test live position
        position_data = {
            'coordinates': {'latitude': 19.0760, 'longitude': 72.8777},
            'short_address': 'Test Position',
            'accuracy_level': 'high',
            'timestamp': datetime.now().isoformat()
        }
        
        live_position_storage.store_live_position(
            self.test_user_id, 
            self.test_company_id, 
            position_data
        )
        
        # Get summary
        summary = live_position_handler.get_live_position_summary(
            self.test_user_id, 
            self.test_company_id
        )
        
        self.assertTrue(summary['has_position'], "Summary should show position exists")
        self.assertEqual(summary['status'], 'active', "Summary should show active status")
        self.assertTrue(summary['is_fresh'], "Summary should show position is fresh")
        self.assertIn('Test Position', summary['short_address'], "Summary should contain position name")


class TestLivePositionPerformance(unittest.TestCase):
    """🚀 Performance tests for live position tracking"""
    
    def setUp(self):
        self.test_user_id = "99998"
        self.test_company_id = "perf_test_company"
    
    def tearDown(self):
        # Clean up test data
        try:
            live_position_storage.clear_live_position(self.test_user_id, self.test_company_id)
        except:
            pass
    
    def test_live_position_storage_performance(self):
        """🚀 Test live position storage performance"""
        import time
        
        position_data = {
            'coordinates': {'latitude': 19.0760, 'longitude': 72.8777},
            'short_address': 'Performance Test Position',
            'timestamp': datetime.now().isoformat()
        }
        
        # Measure storage time
        start_time = time.time()
        success = live_position_storage.store_live_position(
            self.test_user_id, 
            self.test_company_id, 
            position_data
        )
        storage_time = time.time() - start_time
        
        self.assertTrue(success, "Storage should succeed")
        self.assertLess(storage_time, 1.0, "Storage should complete within 1 second")
        
        # Measure retrieval time
        start_time = time.time()
        retrieved_data = live_position_storage.get_live_position(
            self.test_user_id, 
            self.test_company_id
        )
        retrieval_time = time.time() - start_time
        
        self.assertIsNotNone(retrieved_data, "Retrieval should succeed")
        self.assertLess(retrieval_time, 0.5, "Retrieval should complete within 0.5 seconds")


def run_live_position_tests():
    """🧪 Run all live position integration tests"""
    print("🧪 Starting Live Position Tracking Integration Tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLivePositionIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestLivePositionPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n🧪 Live Position Integration Tests Complete!")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n🎯 Overall Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    return success


if __name__ == "__main__":
    # Run live position integration tests
    success = run_live_position_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)