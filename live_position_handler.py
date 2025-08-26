#!/usr/bin/env python3
"""
📍 LIVE POSITION HANDLER MODULE
==============================
Handles real-time GPS position capture for sales entries
SEPARATE from existing location functionality
"""

import datetime
from typing import Optional, Dict, Any, Tuple
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from live_position_storage import live_position_storage
from geocoding import geocode_service
from company_manager import company_manager
from logger import logger
from error_handler import (
    handle_location_error, handle_geocoding_error, log_location_event
)

class LivePositionHandler:
    """📍 Real-time GPS position capture and processing handler"""
    
    def __init__(self):
        self.position_requests = {}  # Track pending position requests
        self.position_accuracy_threshold = 100  # Meters - minimum accuracy for acceptance
        logger.info("📍 Live Position Handler initialized")
    
    def _validate_position_data(self, location) -> Tuple[bool, str]:
        """✅ Validate incoming live position data"""
        try:
            if not location:
                return False, "No position data provided"
            
            # Check if coordinates exist
            if not hasattr(location, 'latitude') or not hasattr(location, 'longitude'):
                return False, "Missing latitude or longitude"
            
            lat = location.latitude
            lon = location.longitude
            
            # Validate coordinate ranges
            if not (-90 <= lat <= 90):
                return False, f"Invalid latitude: {lat}"
            
            if not (-180 <= lon <= 180):
                return False, f"Invalid longitude: {lon}"
            
            # Check accuracy if available
            if hasattr(location, 'horizontal_accuracy'):
                accuracy = location.horizontal_accuracy
                if accuracy and accuracy > self.position_accuracy_threshold:
                    return False, f"Position accuracy too low: {accuracy}m (required: <{self.position_accuracy_threshold}m)"
            
            return True, "Valid position data"
            
        except Exception as e:
            return False, f"Position validation error: {str(e)}"
    
    async def request_live_position(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """📍 Request user to share their live GPS position"""
        try:
            user = update.effective_user
            user_id = str(user.id)
            
            logger.info(f"📍 Live position request from user {user.id} ({user.username or user.first_name})")
            
            # Validate user registration
            if not company_manager.is_user_registered(user.id):
                await update.message.reply_text(
                    "🏢 **Company Registration Required**\n\n"
                    "To use live position features, you must first select your company.\n\n"
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
            
            # Check if live position already exists
            existing_status = live_position_storage.get_live_position_status(user_id, current_company)
            if existing_status['has_position']:
                await update.message.reply_text(
                    f"📍 **Live Position Already Captured**\n\n"
                    f"📍 **Current Position:** {existing_status['position']}\n"
                    f"⏰ **Captured:** {existing_status['timestamp']}\n"
                    f"📅 **Age:** {existing_status['age_hours']:.1f} hours\n\n"
                    f"💡 Use `/position_clear` to remove current position first, "
                    f"or `/position_update` to refresh your position.",
                    parse_mode='Markdown'
                )
                return
            
            # Get company info for display
            company_info = company_manager.get_company_info(current_company)
            company_name = company_info['display_name'] if company_info else current_company
            
            # Create live position request keyboard
            position_keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Share Live Position", request_location=True)]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
            
            # Track position request with enhanced metadata
            self.position_requests[user_id] = {
                'company_id': current_company,
                'timestamp': datetime.datetime.now().isoformat(),
                'user_name': user.full_name or user.first_name,
                'username': user.username
            }
            
            await update.message.reply_text(
                f"📍 **Share Your Live Position**\n\n"
                f"🏢 **Company:** {company_name}\n"
                f"👤 **User:** {user.full_name or user.first_name}\n\n"
                f"To track your real-time position for sales entries, "
                f"please tap the button below to share your current live position.\n\n"
                f"🔒 **Privacy Features:**\n"
                f"• Live position automatically expires after 24 hours\n"
                f"• Only current area/city stored for entries\n"
                f"• You can clear position data anytime with `/position_clear`\n\n"
                f"💡 **Benefits:**\n"
                f"• Automatic live position in sales entries\n"
                f"• Real-time territory tracking\n"
                f"• Enhanced field analytics\n\n"
                f"⚡ **Note:** This is separate from your regular location data.",
                reply_markup=position_keyboard,
                parse_mode='Markdown'
            )
            
            logger.info(f"📍 Live position request sent to user {user.id} for company {current_company}")
            
        except Exception as e:
            logger.error(f"📍 Error requesting live position from user {update.effective_user.id}: {e}")
            await update.message.reply_text(
                "❌ **Live Position Request Failed**\n\n"
                "An error occurred while setting up live position sharing. "
                "Please try again or contact support if the problem persists.\n\n"
                "💡 You can try `/position` again in a moment.",
                parse_mode='Markdown'
            )
    
    async def handle_live_position(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """📍 Process received live GPS position data"""
        try:
            user = update.effective_user
            user_id = str(user.id)
            location = update.message.location
            
            logger.info(f"📍 Live position received from user {user.id} ({user.username or user.first_name})")
            
            # Validate position data
            is_valid, validation_message = self._validate_position_data(location)
            if not is_valid:
                await update.message.reply_text(
                    f"❌ **Invalid Live Position Data**\n\n"
                    f"Issue: {validation_message}\n\n"
                    f"Please try sharing your live position again with better GPS signal.",
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode='Markdown'
                )
                logger.warning(f"⚠️ Invalid live position from user {user.id}: {validation_message}")
                return
            
            # Get company for this position request
            company_id = None
            request_info = None
            
            if user_id in self.position_requests:
                request_info = self.position_requests[user_id]
                company_id = request_info['company_id']
                del self.position_requests[user_id]  # Clean up request
                logger.info(f"📍 Using company from position request: {company_id}")
            else:
                # Fallback to current company
                company_id = company_manager.get_user_company(user.id)
                logger.info(f"📍 Using current company as fallback: {company_id}")
            
            if not company_id:
                await update.message.reply_text(
                    "❌ **Company Selection Required**\n\n"
                    "Please select a company first using `/company`, then try sharing your live position again.",
                    parse_mode='Markdown'
                )
                return
            
            # Remove keyboard and show processing message
            processing_msg = await update.message.reply_text(
                "🔄 **Processing Your Live Position...**\n\n"
                "📍 Validating coordinates...\n"
                "🌍 Looking up current area...\n"
                "💾 Saving live position data...",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='Markdown'
            )
            
            # Get position information with error handling
            try:
                position_info = geocode_service.get_location_info(
                    location.latitude, 
                    location.longitude
                )
                logger.info(f"📍 Geocoding successful for live position user {user.id}: {position_info.get('short_address', 'Unknown')}")
                
            except Exception as geocoding_error:
                logger.error(f"📍 Live position geocoding failed for user {user.id}: {geocoding_error}")
                # Create fallback position info
                position_info = {
                    'coordinates': {
                        'latitude': location.latitude,
                        'longitude': location.longitude
                    },
                    'address': {
                        'city': 'Unknown City',
                        'area': '',
                        'short': f"Position ({location.latitude:.4f}, {location.longitude:.4f})",
                        'formatted': f"Live Position: {location.latitude:.4f}, {location.longitude:.4f}"
                    },
                    'status': 'geocoding_failed',
                    'accuracy': 'low'
                }
            
            # Prepare live position data for storage
            position_data = {
                'coordinates': {
                    'latitude': location.latitude,
                    'longitude': location.longitude
                },
                'address': position_info.get('address', {}),
                'formatted_address': position_info.get('formatted_address', 'Unknown Position'),
                'short_address': position_info.get('short_address', 'Unknown'),
                'accuracy_level': position_info.get('accuracy', 'medium'),
                'geocoding_status': position_info.get('status', 'unknown'),
                'timestamp': datetime.datetime.now().isoformat(),
                'horizontal_accuracy': getattr(location, 'horizontal_accuracy', None),
                'source': 'telegram_live_position_share',
                'user_info': {
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': user.full_name or user.first_name
                }
            }
            
            # Store live position data
            try:
                success = live_position_storage.store_live_position(user_id, company_id, position_data)
                
                if success:
                    company_info = company_manager.get_company_info(company_id)
                    company_name = company_info['display_name'] if company_info else company_id
                    
                    # Determine accuracy emoji
                    accuracy_emoji = {
                        'high': '🎯',
                        'medium': '📍',
                        'low': '📌',
                        'very_low': '🗺️'
                    }.get(position_data['accuracy_level'], '📍')
                    
                    # Enhanced success message
                    success_text = (
                        f"✅ **Live Position Successfully Captured!**\n\n"
                        f"{accuracy_emoji} **Live Position:** {position_data['short_address']}\n"
                        f"🏢 **Company:** {company_name}\n"
                        f"👤 **User:** {user.full_name or user.first_name}\n"
                        f"🎯 **Accuracy:** {position_data['accuracy_level'].title()}\n\n"
                        f"🎯 **What's Next:**\n"
                        f"• Your sales entries will now include live position data\n"
                        f"• Use `/position_status` to view position details\n"
                        f"• Use `/position_analytics` for real-time territory insights\n\n"
                        f"⏰ **Auto-Expiry:** Live position expires after 24 hours\n\n"
                        f"💡 **Note:** This is separate from your regular location data."
                    )
                    
                    # Update the processing message
                    await processing_msg.edit_text(success_text, parse_mode='Markdown')
                    
                    logger.info(f"✅ Live position saved for user {user.id} in company {company_id} with {position_data['accuracy_level']} accuracy")
                    
                else:
                    await processing_msg.edit_text(
                        "❌ **Failed to Save Live Position**\n\n"
                        "There was an issue storing your live position data.\\n\\n"
                        "**Possible causes:**\n"
                        "• Temporary storage issue\n"
                        "• Network connectivity problem\n\n"
                        "Please try again with `/position`."
                    )
                    logger.error(f"❌ Failed to save live position for user {user.id}")
                    
            except Exception as storage_error:
                logger.error(f"📍 Live position storage error for user {user.id}: {storage_error}")
                await processing_msg.edit_text(
                    "❌ **Storage Error**\n\n"
                    "An error occurred while saving your live position data. "
                    "Please try again or contact support if the problem persists.\n\n"
                    "💡 Use `/position` to try again.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ Critical error handling live position from user {update.effective_user.id}: {e}")
            await update.message.reply_text(
                "❌ **Live Position Processing Error**\n\n"
                "A critical error occurred while processing your live position. "
                "Please try again or contact support.\n\n"
                "💡 Use `/position` to try again.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='Markdown'
            )
    
    def get_live_position_for_entry(self, user_id: str, company_id: str) -> Optional[str]:
        """📍 Get live position string for sales entry"""
        try:
            # Validate inputs
            if not user_id or not company_id:
                logger.warning(f"📍 Invalid parameters for live position retrieval: user_id={user_id}, company_id={company_id}")
                return None
            
            position_data = live_position_storage.get_live_position(user_id, company_id)
            
            if not position_data:
                logger.debug(f"📍 No live position data found for user {user_id} in company {company_id}")
                return None
            
            # Check if position data is still valid (not expired - 24 hours)
            timestamp_str = position_data.get('timestamp')
            if timestamp_str:
                try:
                    position_time = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    age = datetime.datetime.now() - position_time.replace(tzinfo=None)
                    if age > datetime.timedelta(hours=24):
                        logger.debug(f"📍 Live position data for user {user_id} is expired (older than 24h)")
                        return None
                except Exception as e:
                    logger.warning(f"⚠️ Could not parse live position timestamp: {e}")
            
            # Use short_address if available
            if position_data.get('short_address'):
                return position_data['short_address']
            
            # Fallback to building from address components
            address = position_data.get('address', {})
            position_parts = []
            
            if address.get('area'):
                position_parts.append(address['area'])
            
            if address.get('city') and address['city'] != address.get('area'):
                position_parts.append(address['city'])
            
            if position_parts:
                return ', '.join(position_parts)
            else:
                # Final fallback to coordinates
                coords = position_data.get('coordinates', {})
                lat = coords.get('latitude', 0)
                lon = coords.get('longitude', 0)
                return f"Live ({lat:.4f}, {lon:.4f})"
        
        except Exception as e:
            logger.error(f"❌ Error getting live position for entry (user {user_id}, company {company_id}): {e}")
            return None
    
    def get_live_position_summary(self, user_id: str, company_id: str) -> Dict[str, Any]:
        """📊 Get comprehensive live position summary for user"""
        try:
            position_data = live_position_storage.get_live_position(user_id, company_id)
            
            if not position_data:
                return {
                    'has_position': False,
                    'status': 'no_position',
                    'message': 'No live position data available'
                }
            
            # Parse timestamp
            timestamp_str = position_data.get('timestamp')
            position_age = None
            is_fresh = True
            
            if timestamp_str:
                try:
                    position_time = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    position_age = datetime.datetime.now() - position_time.replace(tzinfo=None)
                    is_fresh = position_age <= datetime.timedelta(hours=24)
                except Exception as e:
                    logger.warning(f"⚠️ Could not parse live position timestamp: {e}")
            
            # Determine status
            if not is_fresh:
                status = 'expired'
                status_emoji = '🔴'
                status_message = f"Live position expired ({position_age.days} days old)"
            else:
                status = 'active'
                status_emoji = '🟢'
                hours_old = position_age.total_seconds() / 3600 if position_age else 0
                if hours_old < 1:
                    status_message = "Live position is fresh (less than 1 hour old)"
                else:
                    status_message = f"Live position is {int(hours_old)} hours old"
            
            return {
                'has_position': True,
                'status': status,
                'status_emoji': status_emoji,
                'status_message': status_message,
                'short_address': position_data.get('short_address', 'Unknown'),
                'formatted_address': position_data.get('formatted_address', 'Unknown Position'),
                'accuracy_level': position_data.get('accuracy_level', 'unknown'),
                'coordinates': position_data.get('coordinates', {}),
                'age_hours': position_age.total_seconds() / 3600 if position_age else None,
                'is_fresh': is_fresh,
                'timestamp': timestamp_str
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting live position summary for user {user_id}: {e}")
            return {
                'has_position': False,
                'status': 'error',
                'message': f'Error retrieving live position: {str(e)}'
            }
    
    async def show_live_position_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """📊 Show detailed live position status to user"""
        user = update.effective_user
        
        try:
            # Check if user is registered
            if not company_manager.is_user_registered(user.id):
                await update.message.reply_text(
                    "🏢 **Company Registration Required**\n\n"
                    "Please register with a company first using `/company`"
                )
                return
            
            company_id = company_manager.get_user_company(user.id)
            position_summary = self.get_live_position_summary(str(user.id), company_id)
            
            if not position_summary['has_position']:
                await update.message.reply_text(
                    "📍 **Live Position Status: Not Set**\n\n"
                    "🔴 No live position data available\n\n"
                    "📊 **Missing Benefits:**\n"
                    "• Real-time position in sales entries\n"
                    "• Live territory tracking\n"
                    "• Field movement analytics\n\n"
                    "💡 Use `/position` to share your live position and unlock these features!\n\n"
                    "⚡ **Note:** Live position is separate from regular location data."
                )
                return
            
            # Format detailed status message
            coords = position_summary['coordinates']
            status_text = (
                f"📍 **Live Position Status**\n\n"
                f"{position_summary['status_emoji']} **Status:** {position_summary['status_message']}\n"
                f"📍 **Position:** {position_summary['short_address']}\n"
                f"🎯 **Accuracy:** {position_summary['accuracy_level'].title()}\n"
                f"🏢 **Company:** {company_manager.get_company_display_name(company_id)}\n\n"
                f"📊 **Sales Entry Status:**\n"
            )
            
            if position_summary['is_fresh']:
                status_text += (
                    "✅ Live position included in sales entries\n"
                    "✅ Real-time territory tracking active\n"
                    "✅ Field analytics enabled\n\n"
                )
            else:
                status_text += (
                    "⚠️ Live position expired - not included in entries\n"
                    "⚠️ Territory tracking disabled\n"
                    "⚠️ Field analytics limited\n\n"
                    "💡 Share a fresh live position to reactivate features\n\n"
                )
            
            status_text += (
                f"🗂️ **Technical Details:**\n"
                f"• Coordinates: {coords.get('latitude', 0):.6f}, {coords.get('longitude', 0):.6f}\n"
                f"• Captured: {position_summary.get('timestamp', 'Unknown')}\n"
                f"• Age: {position_summary.get('age_hours', 0):.1f} hours\n\n"
                f"💡 **Commands:**\n"
                f"• `/position_update` - Refresh live position\n"
                f"• `/position_analytics` - View field insights\n"
                f"• `/position_clear` - Remove position data\n\n"
                f"⚡ **Note:** Live position expires after 24 hours automatically."
            )
            
            await update.message.reply_text(status_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error showing live position status for user {user.id}: {e}")
            await update.message.reply_text(
                "❌ **Error retrieving live position status**\n\n"
                "Please try again or contact support."
            )
    
    async def clear_live_position(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """🗑️ Clear stored live position data"""
        user = update.effective_user
        
        try:
            # Check if user is registered
            if not company_manager.is_user_registered(user.id):
                await update.message.reply_text(
                    "🏢 **Company Registration Required**\n\n"
                    "Please register with a company first using `/company`"
                )
                return
            
            company_id = company_manager.get_user_company(user.id)
            
            # Check if user has live position data
            position_summary = self.get_live_position_summary(str(user.id), company_id)
            
            if not position_summary['has_position']:
                await update.message.reply_text(
                    "📍 **No Live Position Data to Clear**\n\n"
                    "🔴 You don't have any live position data stored.\n\n"
                    "💡 Use `/position` to share your live position for field tracking benefits!"
                )
                return
            
            # Clear live position data
            success = live_position_storage.clear_live_position(str(user.id), company_id)
            
            if success:
                await update.message.reply_text(
                    f"✅ **Live Position Data Cleared**\n\n"
                    f"🗑️ Your live position data has been permanently removed.\n\n"
                    f"📊 **Impact:**\n"
                    f"• Live position will no longer appear in sales entries\n"
                    f"• Real-time territory tracking disabled\n"
                    f"• Field analytics will be limited\n\n"
                    f"🔒 **Privacy:** All traces of your live position have been securely deleted.\n\n"
                    f"💡 Use `/position` anytime to share your live position again.\n\n"
                    f"⚡ **Note:** This does not affect your regular location data.",
                    parse_mode='Markdown'
                )
                logger.info(f"🗑️ Live position successfully cleared for user {user.id}")
            else:
                await update.message.reply_text(
                    "❌ **Failed to Clear Live Position Data**\n\n"
                    "There was an issue removing your live position data.\n\n"
                    "Please try `/position_clear` again or contact support."
                )
                logger.error(f"❌ Failed to clear live position for user {user.id}")
                
        except Exception as e:
            logger.error(f"❌ Error clearing live position for user {user.id}: {e}")
            await update.message.reply_text(
                "❌ **Error clearing live position data**\n\n"
                "Please try again or contact support."
            )
    
    async def update_live_position(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """🔄 Update/refresh live position data"""
        user = update.effective_user
        
        try:
            # Check if user is registered
            if not company_manager.is_user_registered(user.id):
                await update.message.reply_text(
                    "🏢 **Company Registration Required**\n\n"
                    "Please register with a company first using `/company`"
                )
                return
            
            company_id = company_manager.get_user_company(user.id)
            
            # Clear existing position first
            live_position_storage.clear_live_position(str(user.id), company_id)
            
            # Request new position
            await self.request_live_position(update, context)
            
        except Exception as e:
            logger.error(f"❌ Error updating live position for user {user.id}: {e}")
            await update.message.reply_text(
                "❌ **Error updating live position**\n\n"
                "Please try again or contact support."
            )


# Global live position handler instance
live_position_handler = LivePositionHandler()