#!/usr/bin/env python3
"""
📍 LOCATION STORAGE MODULE
=========================
Handles GPS location data storage and retrieval with privacy protection
"""

import json
import os
import datetime
from typing import Dict, Optional, Any
from logger import logger

class LocationStorage:
    def __init__(self):
        self.storage_file = "data/location_storage.json"
        self.ensure_storage_file()
    
    def ensure_storage_file(self):
        """Ensure the location storage file exists"""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump({}, f)
    
    def store_location(self, user_id: str, company_id: str, location_data: Dict[str, Any]) -> bool:
        """Store GPS location data for a user in a specific company"""
        try:
            # Load existing data
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            # Create user entry if doesn't exist
            if user_id not in data:
                data[user_id] = {}
            
            # Store location data for the company
            data[user_id][company_id] = {
                'coordinates': location_data.get('coordinates', {}),
                'address': location_data.get('address', {}),
                'timestamp': location_data.get('timestamp', datetime.datetime.now().isoformat()),
                'last_updated': datetime.datetime.now().isoformat()
            }
            
            # Save data
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"📍 Location stored for user {user_id} in company {company_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing location: {e}")
            return False
    
    def get_location(self, user_id: str, company_id: str) -> Optional[Dict[str, Any]]:
        """Get GPS location data for a user in a specific company"""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            if user_id in data and company_id in data[user_id]:
                location_data = data[user_id][company_id]
                
                # Check if location is still valid (within 30 days)
                timestamp = datetime.datetime.fromisoformat(location_data['timestamp'])
                if (datetime.datetime.now() - timestamp).days > 30:
                    logger.info(f"📍 Location data expired for user {user_id}")
                    self.clear_location(user_id, company_id)
                    return None
                
                return location_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving location: {e}")
            return None
    
    def clear_location(self, user_id: str, company_id: str) -> bool:
        """Clear GPS location data for a user in a specific company"""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            if user_id in data and company_id in data[user_id]:
                del data[user_id][company_id]
                
                # Remove user entry if no companies left
                if not data[user_id]:
                    del data[user_id]
                
                with open(self.storage_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"📍 Location cleared for user {user_id} in company {company_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error clearing location: {e}")
            return False
    
    def get_location_status(self, user_id: str, company_id: str) -> Dict[str, Any]:
        """Get enhanced location status for a user in a specific company"""
        location_data = self.get_location(user_id, company_id)
        
        if not location_data:
            return {
                'has_location': False,
                'message': "📍 No GPS location stored. Use /location to share your location."
            }
        
        timestamp = datetime.datetime.fromisoformat(location_data['timestamp'])
        time_diff = datetime.datetime.now() - timestamp
        days_old = time_diff.days
        hours_old = time_diff.total_seconds() / 3600
        
        return {
            'has_location': True,
            'location': location_data['address'].get('short', 'Unknown location'),
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'days_old': days_old,
            'hours_old': hours_old,
            'expires_in': max(0, 30 - days_old),
            'coordinates': location_data['coordinates'],
            'accuracy': location_data.get('accuracy', 'medium'),
            'expired': days_old >= 30
        }
    
    def cleanup_expired_locations(self) -> int:
        """Clean up expired location data (older than 30 days)"""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            cleaned_count = 0
            users_to_remove = []
            
            for user_id, user_data in data.items():
                companies_to_remove = []
                
                for company_id, location_data in user_data.items():
                    timestamp = datetime.datetime.fromisoformat(location_data['timestamp'])
                    if (datetime.datetime.now() - timestamp).days > 30:
                        companies_to_remove.append(company_id)
                        cleaned_count += 1
                
                # Remove expired companies
                for company_id in companies_to_remove:
                    del user_data[company_id]
                
                # Mark user for removal if no companies left
                if not user_data:
                    users_to_remove.append(user_id)
            
            # Remove users with no companies
            for user_id in users_to_remove:
                del data[user_id]
            
            # Save cleaned data
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            if cleaned_count > 0:
                logger.info(f"📍 Cleaned up {cleaned_count} expired location entries")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up locations: {e}")
            return 0

# Global instance
location_storage = LocationStorage()