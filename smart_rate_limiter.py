#!/usr/bin/env python3
"""
🛡️ SMART RATE LIMITING & RETRY MANAGER
=====================================
Intelligent rate limiting and retry logic for optimal API key usage
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from logger import logger

class SmartRateLimiter:
    """🧠 Intelligent rate limiting for multiple API keys"""
    
    def __init__(self):
        # Conservative limits based on stress test findings
        self.rate_limits = {
            "primary": {
                "requests_per_minute": 12,  # Reduced from 60
                "requests_per_hour": 500,
                "daily_quota": 1000,
                "current_minute_count": 0, 
                "current_hour_count": 0,
                "current_daily_count": 0,
                "reset_time": None
            },
            "secondary": {
                "requests_per_minute": 10,  # Reduced from 60
                "requests_per_hour": 400,
                "daily_quota": 800,
                "current_minute_count": 0,
                "current_hour_count": 0, 
                "current_daily_count": 0,
                "reset_time": None
            },
            "tertiary": {
                "requests_per_minute": 8,   # Reduced from 60
                "requests_per_hour": 300,
                "daily_quota": 600,
                "current_minute_count": 0,
                "current_hour_count": 0,
                "current_daily_count": 0,
                "reset_time": None
            }
        }
        
        # Enhanced key health tracking
        self.key_health = {
            "primary": {
                "healthy": True, 
                "last_error": None, 
                "consecutive_errors": 0,
                "quota_exhausted": False,
                "exhausted_until": None
            },
            "secondary": {
                "healthy": True, 
                "last_error": None, 
                "consecutive_errors": 0,
                "quota_exhausted": False,
                "exhausted_until": None
            },
            "tertiary": {
                "healthy": True, 
                "last_error": None, 
                "consecutive_errors": 0,
                "quota_exhausted": False,
                "exhausted_until": None
            }
        }
        
        self.retry_delays = [2, 5, 10, 30, 60]  # More conservative exponential backoff
        logger.info("🛡️ Enhanced Smart Rate Limiter initialized with conservative limits")
    
    def can_use_key(self, key_type: str) -> bool:
        """Check if API key can be used (not rate limited or quota exhausted)"""
        rate_info = self.rate_limits.get(key_type, {})
        health_info = self.key_health.get(key_type, {})
        
        # Check if quota is exhausted
        if health_info.get("quota_exhausted", False):
            exhausted_until = health_info.get("exhausted_until")
            if exhausted_until and datetime.now() < exhausted_until:
                return False
            else:
                # Reset quota status
                health_info["quota_exhausted"] = False
                health_info["exhausted_until"] = None
                logger.info(f"🔄 Quota reset for {key_type}")
        
        # Check health
        if not health_info.get("healthy", True):
            return False
        
        # Check daily quota
        if rate_info.get("current_daily_count", 0) >= rate_info.get("daily_quota", 1000):
            return False
        
        # Check hourly limit  
        if rate_info.get("current_hour_count", 0) >= rate_info.get("requests_per_hour", 500):
            return False
            
        # Check rate limit (per minute)
        if rate_info.get("reset_time"):
            if datetime.now() > rate_info["reset_time"]:
                # Reset the counter
                rate_info["current_minute_count"] = 0
                rate_info["reset_time"] = None
        
        # Check if we've exceeded per-minute limit
        if rate_info.get("current_minute_count", 0) >= rate_info.get("requests_per_minute", 60):
            return False
            
        return True
    
    def record_request(self, key_type: str, success: bool = True, error_message: str = ""):
        """Record API request and update rate limiting with quota exhaustion detection"""
        if key_type not in self.rate_limits:
            return
        
        # Update all request counts
        self.rate_limits[key_type]["current_minute_count"] += 1
        self.rate_limits[key_type]["current_hour_count"] += 1
        self.rate_limits[key_type]["current_daily_count"] += 1
        
        # Set reset time if first request in this minute
        if not self.rate_limits[key_type]["reset_time"]:
            self.rate_limits[key_type]["reset_time"] = datetime.now() + timedelta(minutes=1)
        
        # Update health status
        if success:
            self.key_health[key_type]["consecutive_errors"] = 0
            self.key_health[key_type]["healthy"] = True
            self.key_health[key_type]["last_error"] = None
        else:
            self.key_health[key_type]["consecutive_errors"] += 1
            self.key_health[key_type]["last_error"] = error_message
            
            # Check if it's a quota error
            if "429" in error_message or "quota" in error_message.lower():
                self.key_health[key_type]["quota_exhausted"] = True
                
                # Extract retry delay if available
                retry_delay = self._extract_retry_delay(error_message)
                self.key_health[key_type]["exhausted_until"] = datetime.now() + timedelta(seconds=retry_delay)
                
                logger.warning(f"🚫 {key_type} quota exhausted, will retry in {retry_delay}s")
            
            # Mark as unhealthy after consecutive errors
            if self.key_health[key_type]["consecutive_errors"] >= 3:
                self.key_health[key_type]["healthy"] = False
                logger.warning(f"🚨 API key {key_type} marked as unhealthy due to consecutive errors")
    
    def _extract_retry_delay(self, error_message: str) -> int:
        """Extract retry delay from Gemini error message"""
        import re
        
        # Look for "retry_delay { seconds: XX }"
        delay_match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', error_message)
        if delay_match:
            return int(delay_match.group(1))
        
        # Default conservative delay
        return 60
    
    def get_available_keys(self) -> List[str]:
        """Get list of currently available (non-rate-limited) keys"""
        available = []
        for key_type in self.rate_limits.keys():
            if self.can_use_key(key_type):
                available.append(key_type)
        return available
    
    async def wait_for_available_key(self, preferred_key: str = None, max_wait: int = 60) -> Optional[str]:
        """Wait for an API key to become available"""
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            # Check preferred key first
            if preferred_key and self.can_use_key(preferred_key):
                return preferred_key
            
            # Check any available key
            available_keys = self.get_available_keys()
            if available_keys:
                return available_keys[0]
            
            # Wait a bit before checking again
            await asyncio.sleep(1)
        
        logger.warning(f"⏰ Timeout waiting for available API key after {max_wait} seconds")
        return None
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get detailed rate limiting status"""
        status = {}
        for key_type, rate_info in self.rate_limits.items():
            health_info = self.key_health[key_type]
            status[key_type] = {
                "available": self.can_use_key(key_type),
                "requests_used": rate_info["current_count"],
                "requests_limit": rate_info["requests_per_minute"],
                "healthy": health_info["healthy"],
                "consecutive_errors": health_info["consecutive_errors"],
                "reset_time": rate_info["reset_time"].isoformat() if rate_info["reset_time"] else None
            }
        
        return {
            "keys": status,
            "available_keys": len(self.get_available_keys()),
            "total_keys": len(self.rate_limits)
        }

# Global rate limiter instance
rate_limiter = SmartRateLimiter()

async def safe_api_call_with_retry(api_func, *args, key_type: str = "primary", max_retries: int = 3, **kwargs):
    """
    🛡️ Safe API call with intelligent retry and rate limiting
    """
    for attempt in range(max_retries):
        try:
            # Check if key is available
            if not rate_limiter.can_use_key(key_type):
                # Try to find alternative key
                available_keys = rate_limiter.get_available_keys()
                if available_keys:
                    key_type = available_keys[0]
                    logger.info(f"🔄 Switching to {key_type} key due to rate limiting")
                else:
                    # Wait for a key to become available
                    logger.info("⏰ All keys rate limited, waiting for availability...")
                    available_key = await rate_limiter.wait_for_available_key(key_type, max_wait=30)
                    if not available_key:
                        raise Exception("All API keys are rate limited")
                    key_type = available_key
            
            # Make the API call
            result = await api_func(*args, **kwargs)
            
            # Record successful request
            rate_limiter.record_request(key_type, success=True)
            
            return result
            
        except Exception as e:
            # Record failed request
            rate_limiter.record_request(key_type, success=False)
            
            error_msg = str(e)
            
            # Handle rate limiting specifically
            if "429" in error_msg or "quota" in error_msg.lower():
                logger.warning(f"⚠️ Rate limit hit for {key_type} key on attempt {attempt + 1}")
                
                # Try different key
                available_keys = rate_limiter.get_available_keys()
                if available_keys and attempt < max_retries - 1:
                    key_type = available_keys[0]
                    logger.info(f"🔄 Retrying with {key_type} key")
                    continue
                
                # Wait before retry
                if attempt < max_retries - 1:
                    wait_time = rate_limiter.retry_delays[min(attempt, len(rate_limiter.retry_delays) - 1)]
                    logger.info(f"⏰ Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                    continue
            
            # Other errors
            if attempt == max_retries - 1:
                logger.error(f"❌ All retry attempts failed for {key_type}: {e}")
                raise e
            
            # Wait before retry
            wait_time = rate_limiter.retry_delays[min(attempt, len(rate_limiter.retry_delays) - 1)]
            await asyncio.sleep(wait_time)
    
    raise Exception(f"Max retries ({max_retries}) exceeded for {key_type}")
