#!/usr/bin/env python3
"""
📍 LOCATION HANDLER MODULE
=========================
Handles Telegram location messages and GPS data processing
"""

import datetime
from typing import Optional, Dict, Any
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from location_storage import location_storage
from geocoding import geocoding_service
from company_manager import company_manager
from logger import logger
from error_handler import (
    handle_location_error, handle_geocoding_error, handle_gps_accuracy_warning,
    handle_location_permission_denied, log_location_event
)

class LocationHandler:
    def __init__(self):
        self.location_requests = {}  # Track pending location requests
    
    async def request_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Request user to share their GPS location with enhanced validation.
        
        This method creates a custom keyboard with location sharing button
        and handles user registration validation.
        """
        try:
            user = update.effective_user
            user_id = str(user.id)
            
            logger.info(f"📍 Location request from user {user.id} ({user.username or user.first_name})")
            
            # Validate user registration
            if not company_manager.is_user_registered(user.id):
                await update.message.reply_text(
                    "🏢 **Company Registration Required**\n\n"
                    "To use location features, you must first select your company.\n\n"
                    "💡 Use `/company` to get started!",
                    parse_mode='Markdown'
                )
                return
            
            # Get current company
            current_company = company_manager.get_user_company(user.id)
            if not current_company:
                await update.message.reply_text(
                    "❌ **Company Selection Required**\n\n"
                    "Please select a company first using `/company`",
                    parse_mode='Markdown'
                )
                return
            
            # Check if location already exists
            existing_status = location_storage.get_location_status(user_id, current_company)
            if existing_status['has_location']:
                await update.message.reply_text(
                    f"📍 **Location Already Captured**\n\n"
                    f"📍 **Current Location:** {existing_status['location']}\n"
                    f"⏰ **Captured:** {existing_status['timestamp']}\n"
                    f"📅 **Expires in:** {existing_status['expires_in']} days\n\n"
                    f"💡 Use `/location_clear` to remove current location first, "
                    f"or `/location_status` to view details.",
                    parse_mode='Markdown'
                )
                return
            
            # Get company info for display
            company_info = company_manager.get_company_info(current_company)
            company_name = company_info['display_name'] if company_info else current_company
            
            # Create location request keyboard
            location_keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Share Location", request_location=True)]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
            
            # Track location request with enhanced metadata
            self.location_requests[user_id] = {
                'company_id': current_company,
                'timestamp': datetime.datetime.now().isoformat(),
                'user_name': user.full_name or user.first_name,
                'username': user.username
            }
            
            await update.message.reply_text(
                f"📍 **Share Your Location**\n\n"
                f"🏢 **Company:** {company_name}\n"
                f"👤 **User:** {user.full_name or user.first_name}\n\n"
                f"To enhance your sales tracking with GPS location data, "
                f"please tap the button below to share your current location.\n\n"
                f"🔒 **Privacy Features:**\n"
                f"• Coordinates automatically removed after 30 days\n"
                f"• Only general area (city/district) stored long-term\n"
                f"• You can clear location data anytime with `/location_clear`\n\n"
                f"💡 **Benefits:**\n"
                f"• Automatic location tagging in sales entries\n"
                f"• Territory-based performance analytics\n"
                f"• Enhanced reporting and insights",
                reply_markup=location_keyboard,
                parse_mode='Markdown'
            )
            
            logger.info(f"📍 Location request sent to user {user.id} for company {current_company}")
            
        except Exception as e:
            logger.error(f"📍 Error requesting location from user {update.effective_user.id}: {e}")
            await update.message.reply_text(
                "❌ **Location Request Failed**\n\n"
                "An error occurred while setting up location sharing. "
                "Please try again or contact support if the problem persists.\n\n"
                "💡 You can try `/location` again in a moment.",
                parse_mode='Markdown'
            )
    
    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle received GPS location data with comprehensive validation and error handling.
        
        This method processes Telegram location messages, validates coordinates,
        performs geocoding, and stores location data securely.
        """
        try:
            user = update.effective_user
            user_id = str(user.id)
            location = update.message.location
            
            logger.info(f"📍 Location received from user {user.id} ({user.username or user.first_name})")
            
            # Validate location data
            if not location:
                await update.message.reply_text(
                    "❌ **No Location Data**\n\n"
                    "No location data was received. Please try sharing your location again.\n\n"
                    "💡 Use `/location` to try again.",
                    parse_mode='Markdown'
                )
                return
            
            # Validate coordinates
            if not (-90 <= location.latitude <= 90) or not (-180 <= location.longitude <= 180):
                logger.error(f"📍 Invalid coordinates from user {user.id}: {location.latitude}, {location.longitude}")
                await update.message.reply_text(
                    "❌ **Invalid Location Data**\n\n"
                    "The location coordinates appear to be invalid. Please try again.\n\n"
                    "💡 Use `/location` to share your location again.",
                    parse_mode='Markdown'
                )
                return
            
            # Get company for this location request
            company_id = None
            request_info = None
            
            if user_id in self.location_requests:
                request_info = self.location_requests[user_id]
                company_id = request_info['company_id']
                del self.location_requests[user_id]  # Clean up request
                logger.info(f"📍 Using company from location request: {company_id}")
            else:
                # Fallback to current company
                company_id = company_manager.get_user_company(user.id)
                logger.info(f"📍 Using current company as fallback: {company_id}")
            
            if not company_id:
                await update.message.reply_text(
                    "❌ **Company Selection Required**\n\n"
                    "Please select a company first using `/company`, then try sharing your location again.",
                    parse_mode='Markdown'
                )
                return
            
            # Remove keyboard and show processing message
            await update.message.reply_text(
                "🔄 **Processing Your Location...**\n\n"
                "📍 Validating coordinates...\n"
                "🌍 Looking up address information...\n"
                "💾 Preparing to save location data...",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='Markdown'
            )
            
            # Get location information with error handling
            try:
                location_info = geocoding_service.get_location_info(
                    location.latitude, 
                    location.longitude
                )
                logger.info(f"📍 Geocoding successful for user {user.id}: {location_info['address']['short']}")
                
            except Exception as geocoding_error:
                logger.error(f"📍 Geocoding failed for user {user.id}: {geocoding_error}")
                # Create fallback location info
                location_info = {
                    'coordinates': {
                        'latitude': location.latitude,
                        'longitude': location.longitude
                    },
                    'address': {
                        'city': 'Unknown City',
                        'area': '',
                        'short': f"Location ({location.latitude:.4f}, {location.longitude:.4f})",
                        'formatted': f"GPS Location: {location.latitude:.4f}, {location.longitude:.4f}"
                    },
                    'timestamp': datetime.datetime.now().timestamp(),
                    'accuracy': 'low'
                }
            
            # Prepare location data for storage
            location_data = {
                'coordinates': location_info['coordinates'],
                'address': location_info['address'],
                'timestamp': datetime.datetime.now().isoformat(),
                'accuracy': location_info.get('accuracy', 'medium'),
                'user_info': {
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': user.full_name or user.first_name
                }
            }
            
            # Store location data with error handling
            try:
                success = location_storage.store_location(user_id, company_id, location_data)
                
                if success:
                    company_info = company_manager.get_company_info(company_id)
                    company_name = company_info['display_name'] if company_info else company_id
                    
                    # Create success message with location details
                    success_message = (
                        f"✅ **Location Successfully Captured!**\n\n"
                        f"📍 **Location:** {location_info['address']['short']}\n"
                        f"🏢 **Company:** {company_name}\n"
                        f"👤 **User:** {user.full_name or user.first_name}\n"
                        f"📊 **Accuracy:** {location_info.get('accuracy', 'medium').title()}\n\n"
                        f"🎯 **What's Next:**\n"
                        f"• Your sales entries will now include GPS location data\n"
                        f"• Use `/location_status` to view location details\n"
                        f"• Use `/location_analytics` for territory insights\n\n"
                        f"🔒 **Privacy:** Location data expires automatically after 30 days"
                    )
                    
                    await update.message.reply_text(success_message, parse_mode='Markdown')
                    logger.info(f"📍 Location successfully stored for user {user.id} in company {company_id}")
                    
                else:
                    await update.message.reply_text(
                        "❌ **Location Storage Failed**\n\n"
                        "Failed to save your location data. This could be due to:\n"
                        "• Temporary storage issue\n"
                        "• Company access permissions\n"
                        "• System maintenance\n\n"
                        "💡 Please try again with `/location`",
                        parse_mode='Markdown'
                    )
                    logger.error(f"📍 Failed to store location for user {user.id}")
                    
            except Exception as storage_error:
                logger.error(f"📍 Location storage error for user {user.id}: {storage_error}")
                await update.message.reply_text(
                    "❌ **Storage Error**\n\n"
                    "An error occurred while saving your location data. "
                    "Please try again or contact support if the problem persists.\n\n"
                    "💡 Use `/location` to try again.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"📍 Critical error handling location from user {update.effective_user.id}: {e}")
            await update.message.reply_text(
                "❌ **Location Processing Error**\n\n"
                "A critical error occurred while processing your location. "
                "Please try again or contact support.\n\n"
                "💡 Use `/location` to try again.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='Markdown'
            )
    
    def get_location_for_entry(self, user_id: str, company_id: str) -> Optional[str]:
        """
        Get location string for sales entry with validation and fallback.
        
        Args:
            user_id (str): User identifier
            company_id (str): Company identifier
            
        Returns:
            Optional[str]: Location string for entry or None if not available
        """
        try:
            # Validate inputs
            if not user_id or not company_id:
                logger.warning(f"📍 Invalid parameters for location retrieval: user_id={user_id}, company_id={company_id}")
                return None
            
            location_data = location_storage.get_location(user_id, company_id)
            
            if not location_data:
                logger.debug(f"📍 No location data found for user {user_id} in company {company_id}")
                return None
            
            # Check if location data is still valid (not expired)
            if location_data.get('expired', False):
                logger.info(f"📍 Location data expired for user {user_id}")
                return None
            
            # Extract location string
            address = location_data.get('address', {})
            if address:
                location_str = address.get('short', '')
                if location_str and location_str != 'Unknown Location':
                    logger.debug(f"📍 Location retrieved for entry: {location_str}")
                    return location_str
            
            # Fallback to coordinates if address not available
            coordinates = location_data.get('coordinates', {})
            if coordinates.get('latitude') and coordinates.get('longitude'):
                lat = coordinates['latitude']
                lon = coordinates['longitude']
                fallback_str = f"GPS ({lat:.4f}, {lon:.4f})"
                logger.debug(f"📍 Using coordinate fallback for entry: {fallback_str}")
                return fallback_str
            
            return None
            
        except Exception as e:
            logger.error(f"📍 Error getting location for entry (user: {user_id}, company: {company_id}): {e}")
            return None
    
    def validate_location_data(self, location_data: Dict[str, Any]) -> bool:
        """
        Validate location data structure and content.
        
        Args:
            location_data (Dict[str, Any]): Location data to validate
            
        Returns:
            bool: True if location data is valid
        """
        try:
            # Check required fields
            if not isinstance(location_data, dict):
                return False
            
            # Check coordinates
            coordinates = location_data.get('coordinates', {})
            if not isinstance(coordinates, dict):
                return False
            
            lat = coordinates.get('latitude')
            lon = coordinates.get('longitude')
            
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                return False
            
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return False
            
            # Check address
            address = location_data.get('address', {})
            if not isinstance(address, dict):
                return False
            
            # Check timestamp
            timestamp = location_data.get('timestamp')
            if not timestamp:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"📍 Error validating location data: {e}")
            return False
    
    async def show_location_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show current GPS location status"""
        try:
            user_id = str(update.effective_user.id)
            current_company = company_manager.get_user_company(user_id)
            
            if not current_company:
                await update.message.reply_text(
                    "❌ Please select a company first using /company"
                )
                return
            
            status = location_storage.get_location_status(user_id, current_company)
            company_info = company_manager.get_company_info(current_company)
            company_name = company_info['display_name'] if company_info else current_company
            
            if status['has_location']:
                message = f"📍 **GPS Location Status**\n\n"
                message += f"🏢 **Company:** {company_name}\n"
                message += f"📍 **Location:** {status['location']}\n"
                message += f"⏰ **Captured:** {status['timestamp']}\n"
                message += f"📅 **Age:** {status['days_old']} days old\n"
                message += f"⏳ **Expires in:** {status['expires_in']} days\n\n"
                message += f"✅ Your sales entries include GPS location data."
            else:
                message = f"📍 **GPS Location Status**\n\n"
                message += f"🏢 **Company:** {company_name}\n"
                message += f"❌ **Status:** No GPS location stored\n\n"
                message += f"Use /location to share your location and enhance sales tracking."
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"📍 Error showing location status: {e}")
            await update.message.reply_text(
                "❌ Error retrieving location status."
            )
    
    async def clear_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Clear stored GPS location data"""
        try:
            user_id = str(update.effective_user.id)
            current_company = company_manager.get_user_company(user_id)
            
            if not current_company:
                await update.message.reply_text(
                    "❌ Please select a company first using /company"
                )
                return
            
            success = location_storage.clear_location(user_id, current_company)
            company_info = company_manager.get_company_info(current_company)
            company_name = company_info['display_name'] if company_info else current_company
            
            if success:
                await update.message.reply_text(
                    f"✅ **GPS Location Cleared**\n\n"
                    f"🏢 **Company:** {company_name}\n"
                    f"📍 Your GPS location data has been removed.\n\n"
                    f"Use /location to share your location again if needed.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"📍 **No GPS Location Data**\n\n"
                    f"🏢 **Company:** {company_name}\n"
                    f"No GPS location data was found to clear.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"📍 Error clearing location: {e}")
            await update.message.reply_text(
                "❌ Error clearing location data."
            )

# Global instance
location_handler = LocationHandler()