#!/usr/bin/env python3
"""
🌍 GEOCODING SERVICE
===================
Converts GPS coordinates to readable addresses using OpenStreetMap
"""

import requests
import time
from typing import Dict, Optional, Any
from logger import logger

class GeocodingService:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/reverse"
        self.headers = {
            'User-Agent': 'PerformanceTracker/1.0 (Telegram Bot)'
        }
        self.rate_limit_delay = 1  # 1 second between requests
        self.last_request_time = 0
        self.fallback_enabled = True
        self.max_retries = 3
        self.timeout = 10
    
    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Convert GPS coordinates to readable address with retry mechanism.
        
        Args:
            latitude (float): GPS latitude coordinate
            longitude (float): GPS longitude coordinate
            
        Returns:
            Optional[Dict[str, Any]]: Parsed address information or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                
                params = {
                    'lat': latitude,
                    'lon': longitude,
                    'format': 'json',
                    'addressdetails': 1,
                    'zoom': 18
                }
                
                logger.debug(f"🌍 Geocoding attempt {attempt + 1} for ({latitude}, {longitude})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and 'address' in data:
                        result = self._parse_address(data)
                        logger.info(f"🌍 Geocoding successful: {result['short']}")
                        return result
                    else:
                        logger.warning(f"🌍 Empty geocoding response for ({latitude}, {longitude})")
                        
                elif response.status_code == 429:  # Rate limited
                    logger.warning(f"🌍 Rate limited, waiting longer...")
                    time.sleep(2 * (attempt + 1))  # Exponential backoff
                    continue
                    
                else:
                    logger.warning(f"🌍 Geocoding API returned status {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"🌍 Geocoding timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(1 * (attempt + 1))  # Wait before retry
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"🌍 Geocoding request failed on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1 * (attempt + 1))  # Wait before retry
                    continue
                    
            except Exception as e:
                logger.error(f"🌍 Geocoding error on attempt {attempt + 1}: {e}")
                break  # Don't retry on unexpected errors
        
        logger.warning(f"🌍 All geocoding attempts failed for ({latitude}, {longitude})")
        return None
    
    def _parse_address(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse geocoding response into structured address"""
        try:
            address = data.get('address', {})
            
            # Extract address components
            city = (address.get('city') or 
                   address.get('town') or 
                   address.get('village') or 
                   address.get('municipality') or
                   'Unknown City')
            
            area = (address.get('suburb') or 
                   address.get('neighbourhood') or 
                   address.get('quarter') or
                   address.get('district') or
                   address.get('subdistrict') or
                   '')
            
            state = (address.get('state') or 
                    address.get('province') or 
                    '')
            
            country = address.get('country', '')
            
            # Create formatted addresses
            short_address = f"{area}, {city}" if area else city
            formatted_address = data.get('display_name', short_address)
            
            return {
                'city': city,
                'area': area,
                'state': state,
                'country': country,
                'short': short_address,
                'formatted': formatted_address,
                'raw': data
            }
            
        except Exception as e:
            logger.error(f"🌍 Error parsing address: {e}")
            return {
                'city': 'Unknown City',
                'area': '',
                'state': '',
                'country': '',
                'short': 'Unknown Location',
                'formatted': 'Unknown Location',
                'raw': data
            }
    
    def get_location_info(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get complete location information from coordinates with comprehensive fallback.
        
        Args:
            latitude (float): GPS latitude coordinate
            longitude (float): GPS longitude coordinate
            
        Returns:
            Dict[str, Any]: Complete location information with coordinates and address
        """
        try:
            # Validate coordinates
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                raise ValueError(f"Invalid coordinates: lat={latitude}, lon={longitude}")
            
            logger.info(f"🌍 Getting location info for ({latitude:.6f}, {longitude:.6f})")
            
            # Get address from coordinates
            address_info = self.reverse_geocode(latitude, longitude)
            
            if not address_info and self.fallback_enabled:
                # Enhanced fallback with coordinate-based location estimation
                address_info = self._create_fallback_address(latitude, longitude)
                logger.info(f"🌍 Using fallback address: {address_info['short']}")
            elif not address_info:
                # Basic fallback
                address_info = {
                    'city': 'Unknown City',
                    'area': '',
                    'state': '',
                    'country': '',
                    'short': f"Location ({latitude:.4f}, {longitude:.4f})",
                    'formatted': f"GPS Location: {latitude:.4f}, {longitude:.4f}"
                }
            
            return {
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'address': address_info,
                'timestamp': time.time(),
                'accuracy': self._estimate_accuracy(address_info)
            }
            
        except Exception as e:
            logger.error(f"🌍 Error getting location info: {e}")
            return {
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'address': {
                    'city': 'Unknown City',
                    'area': '',
                    'state': '',
                    'country': '',
                    'short': 'Location Error',
                    'formatted': 'Unable to determine location'
                },
                'timestamp': time.time(),
                'accuracy': 'low',
                'error': str(e)
            }
    
    def _create_fallback_address(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Create fallback address information when geocoding fails.
        Uses coordinate-based estimation for basic location info.
        """
        try:
            # Basic coordinate-based location estimation
            # This is a simplified approach - in production you might use offline databases
            
            # Determine general region based on coordinates
            region = self._estimate_region(latitude, longitude)
            
            return {
                'city': region.get('city', 'Unknown City'),
                'area': region.get('area', ''),
                'state': region.get('state', ''),
                'country': region.get('country', ''),
                'short': f"{region.get('area', 'Area')}, {region.get('city', 'City')}",
                'formatted': f"Approximate location: {region.get('city', 'Unknown')} ({latitude:.4f}, {longitude:.4f})",
                'fallback': True
            }
            
        except Exception as e:
            logger.error(f"🌍 Fallback address creation failed: {e}")
            return {
                'city': 'Unknown City',
                'area': '',
                'state': '',
                'country': '',
                'short': f"Location ({latitude:.4f}, {longitude:.4f})",
                'formatted': f"GPS Coordinates: {latitude:.4f}, {longitude:.4f}",
                'fallback': True
            }
    
    def _estimate_region(self, latitude: float, longitude: float) -> Dict[str, str]:
        """
        Estimate region based on coordinates.
        This is a basic implementation - could be enhanced with offline databases.
        """
        # Basic region estimation for common areas
        # This is simplified - in production you'd use proper geographic databases
        
        if 18.0 <= latitude <= 20.0 and 72.0 <= longitude <= 73.5:
            return {
                'city': 'Mumbai',
                'area': 'Mumbai Area',
                'state': 'Maharashtra',
                'country': 'India'
            }
        elif 12.8 <= latitude <= 13.2 and 77.4 <= longitude <= 77.8:
            return {
                'city': 'Bangalore',
                'area': 'Bangalore Area',
                'state': 'Karnataka',
                'country': 'India'
            }
        elif 28.4 <= latitude <= 28.8 and 76.8 <= longitude <= 77.5:
            return {
                'city': 'Delhi',
                'area': 'Delhi Area',
                'state': 'Delhi',
                'country': 'India'
            }
        elif 22.4 <= latitude <= 23.2 and 72.4 <= longitude <= 72.8:
            return {
                'city': 'Ahmedabad',
                'area': 'Ahmedabad Area',
                'state': 'Gujarat',
                'country': 'India'
            }
        else:
            # Generic fallback
            return {
                'city': 'Unknown City',
                'area': 'Unknown Area',
                'state': 'Unknown State',
                'country': 'Unknown Country'
            }
    
    def _estimate_accuracy(self, address_info: Dict[str, Any]) -> str:
        """Estimate the accuracy of the address information"""
        if address_info.get('fallback'):
            return 'low'
        elif address_info.get('area') and address_info.get('city'):
            return 'high'
        elif address_info.get('city'):
            return 'medium'
        else:
            return 'low'
    
    def test_connection(self) -> bool:
        """Test geocoding service connection"""
        try:
            # Test with a known location (Mumbai coordinates)
            test_result = self.reverse_geocode(18.9750, 72.8258)
            if test_result:
                logger.info(f"🌍 Geocoding service test successful: {test_result['short']}")
                return True
            else:
                logger.warning("🌍 Geocoding service test returned no results")
                return False
        except Exception as e:
            logger.error(f"🌍 Geocoding service test failed: {e}")
            return False

# Global instance
geocoding_service = GeocodingService()