from location_storage import LocationStorage

class LivePositionStorage:
    """Adapter class for live position storage using LocationStorage backend"""
    
    def __init__(self):
        self._storage = LocationStorage()
    
    def store_live_position(self, user_id: str, company_id: str, position_data: dict) -> bool:
        """Store live position data"""
        return self._storage.store_location(user_id, company_id, position_data)
    
    def get_live_position(self, user_id: str, company_id: str) -> dict:
        """Get live position data"""
        return self._storage.get_location(user_id, company_id)
    
    def clear_live_position(self, user_id: str, company_id: str) -> bool:
        """Clear live position data"""
        return self._storage.clear_location(user_id, company_id)
    
    def get_live_position_status(self, user_id: str, company_id: str) -> dict:
        """Get live position status with expected format"""
        status = self._storage.get_location_status(user_id, company_id)
        
        # Convert location status format to live position status format
        if 'has_location' in status:
            status['has_position'] = status['has_location']
            if status['has_position']:
                status['position'] = status.get('location', 'Unknown')
            
        return status

live_position_storage = LivePositionStorage()
