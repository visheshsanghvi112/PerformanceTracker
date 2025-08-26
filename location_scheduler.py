#!/usr/bin/env python3
"""
📍 LOCATION SCHEDULER MODULE
===========================
Handles scheduled tasks for GPS location data cleanup
"""

import asyncio
import datetime
from location_storage import location_storage
from logger import logger

class LocationScheduler:
    def __init__(self):
        self.cleanup_interval = 24 * 60 * 60  # 24 hours in seconds
        self.running = False
    
    async def start_scheduler(self):
        """Start the location cleanup scheduler"""
        if self.running:
            return
        
        self.running = True
        logger.info("📍 Location scheduler started")
        
        while self.running:
            try:
                # Wait for the cleanup interval
                await asyncio.sleep(self.cleanup_interval)
                
                if self.running:  # Check if still running after sleep
                    await self.cleanup_expired_locations()
                    
            except Exception as e:
                logger.error(f"📍 Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def cleanup_expired_locations(self):
        """Clean up expired GPS location data"""
        try:
            cleaned_count = location_storage.cleanup_expired_locations()
            
            if cleaned_count > 0:
                logger.info(f"📍 Cleaned up {cleaned_count} expired GPS location entries")
            else:
                logger.debug("📍 No expired GPS location entries to clean up")
                
        except Exception as e:
            logger.error(f"📍 Error during location cleanup: {e}")
    
    def stop_scheduler(self):
        """Stop the location cleanup scheduler"""
        self.running = False
        logger.info("📍 Location scheduler stopped")

# Global instance
location_scheduler = LocationScheduler()