#!/usr/bin/env python3
"""
📍 LOCATION COMMANDS MODULE
==========================
Enhanced command handlers for GPS location functionality with comprehensive
error handling, rate limiting, and location freshness checking.
"""

import datetime
from telegram import Update
from telegram.ext import ContextTypes
from location_handler import location_handler
from location_storage import location_storage
from company_manager import company_manager
from decorators import rate_limit, handle_errors
from logger import logger

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def location_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /location command - request GPS location sharing with validation.
    
    This command initiates the location sharing process with comprehensive
    validation and user guidance.
    """
    user = update.effective_user
    logger.info(f"📍 /location command from user {user.id} ({user.username or user.first_name})")
    
    try:
        # Check if user is registered
        if not company_manager.is_user_registered(user.id):
            await update.message.reply_text(
                "🏢 **Company Registration Required**\n\n"
                "To use location features, you must first select your company.\n\n"
                "💡 Use `/company` to get started!",
                parse_mode='Markdown'
            )
            return
        
        # Check location freshness (24-hour threshold)
        current_company = company_manager.get_user_company(user.id)
        if current_company:
            status = location_storage.get_location_status(str(user.id), current_company)
            
            if status['has_location']:
                # Check if location is fresh (less than 24 hours old)
                if status['days_old'] < 1:
                    await update.message.reply_text(
                        f"📍 **Recent Location Available**\n\n"
                        f"📍 **Current Location:** {status['location']}\n"
                        f"⏰ **Captured:** {status['timestamp']}\n"
                        f"📅 **Age:** {status['hours_old']:.1f} hours old\n\n"
                        f"Your location is still fresh! Use `/location_status` for details "
                        f"or `/location_clear` to remove and share a new location.",
                        parse_mode='Markdown'
                    )
                    return
                else:
                    # Location is older than 24 hours - prompt for update
                    await update.message.reply_text(
                        f"📍 **Location Update Recommended**\n\n"
                        f"📍 **Current Location:** {status['location']}\n"
                        f"📅 **Age:** {status['days_old']} days old\n\n"
                        f"Your location is getting old. Sharing a fresh location will "
                        f"improve the accuracy of your sales tracking.\n\n"
                        f"Continue with location sharing?",
                        parse_mode='Markdown'
                    )
        
        # Proceed with location request
        await location_handler.request_location(update, context)
        
    except Exception as e:
        logger.error(f"📍 Error in location command for user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Location Command Error**\n\n"
            "An error occurred while processing your location request. "
            "Please try again or contact support.\n\n"
            "💡 Use `/location` to try again.",
            parse_mode='Markdown'
        )

@rate_limit(calls_per_minute=20)
@handle_errors(notify_user=True)
async def location_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /location_status command - show comprehensive GPS location status.
    
    This command provides detailed information about stored location data
    including freshness, accuracy, and expiration details.
    """
    user = update.effective_user
    logger.info(f"📍 /location_status command from user {user.id}")
    
    try:
        # Check user registration
        if not company_manager.is_user_registered(user.id):
            await update.message.reply_text(
                "🏢 **Company Registration Required**\n\n"
                "Please select your company first using `/company`",
                parse_mode='Markdown'
            )
            return
        
        current_company = company_manager.get_user_company(user.id)
        if not current_company:
            await update.message.reply_text(
                "❌ **Company Selection Required**\n\n"
                "Please select a company first using `/company`",
                parse_mode='Markdown'
            )
            return
        
        # Get enhanced location status
        status = location_storage.get_location_status(str(user.id), current_company)
        company_info = company_manager.get_company_info(current_company)
        company_name = company_info['display_name'] if company_info else current_company
        
        if status['has_location']:
            # Calculate freshness indicators
            freshness_emoji = "🟢" if status['days_old'] < 1 else "🟡" if status['days_old'] < 7 else "🔴"
            freshness_text = "Fresh" if status['days_old'] < 1 else "Getting Old" if status['days_old'] < 7 else "Stale"
            
            message = (
                f"📍 **GPS Location Status**\n\n"
                f"🏢 **Company:** {company_name}\n"
                f"👤 **User:** {user.full_name or user.first_name}\n\n"
                f"📍 **Location:** {status['location']}\n"
                f"⏰ **Captured:** {status['timestamp']}\n"
                f"📅 **Age:** {status['days_old']} days old ({status.get('hours_old', 0):.1f} hours)\n"
                f"🎯 **Freshness:** {freshness_emoji} {freshness_text}\n"
                f"⏳ **Expires in:** {status['expires_in']} days\n\n"
                f"✅ **Status:** Active - Your sales entries include GPS location data\n\n"
                f"💡 **Actions:**\n"
                f"• `/location_clear` - Remove current location\n"
                f"• `/location` - Update with fresh location\n"
                f"• `/location_analytics` - View territory insights"
            )
            
            # Add freshness recommendation
            if status['days_old'] >= 1:
                message += f"\n\n⚠️ **Recommendation:** Consider updating your location for better accuracy"
                
        else:
            message = (
                f"📍 **GPS Location Status**\n\n"
                f"🏢 **Company:** {company_name}\n"
                f"👤 **User:** {user.full_name or user.first_name}\n\n"
                f"❌ **Status:** No GPS location stored\n\n"
                f"📍 **Benefits of Location Sharing:**\n"
                f"• Automatic location tagging in sales entries\n"
                f"• Territory-based performance analytics\n"
                f"• Enhanced reporting and insights\n"
                f"• Better route planning and coverage analysis\n\n"
                f"💡 **Get Started:** Use `/location` to share your location"
            )
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"📍 Error in location_status command for user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Status Retrieval Error**\n\n"
            "Could not retrieve location status. Please try again.",
            parse_mode='Markdown'
        )

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def location_clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /location_clear command - clear stored GPS location with confirmation.
    
    This command removes stored location data with user confirmation and
    provides guidance for re-sharing location if needed.
    """
    user = update.effective_user
    logger.info(f"📍 /location_clear command from user {user.id}")
    
    try:
        # Check user registration
        if not company_manager.is_user_registered(user.id):
            await update.message.reply_text(
                "🏢 **Company Registration Required**\n\n"
                "Please select your company first using `/company`",
                parse_mode='Markdown'
            )
            return
        
        current_company = company_manager.get_user_company(user.id)
        if not current_company:
            await update.message.reply_text(
                "❌ **Company Selection Required**\n\n"
                "Please select a company first using `/company`",
                parse_mode='Markdown'
            )
            return
        
        # Check if location exists before clearing
        status = location_storage.get_location_status(str(user.id), current_company)
        
        if not status['has_location']:
            company_info = company_manager.get_company_info(current_company)
            company_name = company_info['display_name'] if company_info else current_company
            
            await update.message.reply_text(
                f"📍 **No Location Data Found**\n\n"
                f"🏢 **Company:** {company_name}\n"
                f"👤 **User:** {user.full_name or user.first_name}\n\n"
                f"❌ No GPS location data is currently stored for your account.\n\n"
                f"💡 Use `/location` to share your location for enhanced tracking.",
                parse_mode='Markdown'
            )
            return
        
        # Proceed with clearing
        success = location_storage.clear_location(str(user.id), current_company)
        company_info = company_manager.get_company_info(current_company)
        company_name = company_info['display_name'] if company_info else current_company
        
        if success:
            await update.message.reply_text(
                f"✅ **GPS Location Cleared Successfully**\n\n"
                f"🏢 **Company:** {company_name}\n"
                f"👤 **User:** {user.full_name or user.first_name}\n\n"
                f"🗑️ **Removed:** {status['location']}\n"
                f"📅 **Was:** {status['days_old']} days old\n\n"
                f"📍 **Impact:**\n"
                f"• Future sales entries will not include GPS location\n"
                f"• Location-based analytics will not include new data\n"
                f"• Your privacy is protected - all location data removed\n\n"
                f"💡 **Re-enable Location:** Use `/location` to share your location again",
                parse_mode='Markdown'
            )
            logger.info(f"📍 Location cleared successfully for user {user.id} in company {current_company}")
        else:
            await update.message.reply_text(
                f"❌ **Location Clear Failed**\n\n"
                f"Could not remove location data. This might be due to:\n"
                f"• Temporary storage issue\n"
                f"• Data was already removed\n"
                f"• System maintenance\n\n"
                f"💡 Try `/location_status` to check current status",
                parse_mode='Markdown'
            )
            logger.error(f"📍 Failed to clear location for user {user.id}")
            
    except Exception as e:
        logger.error(f"📍 Error in location_clear command for user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Clear Command Error**\n\n"
            "An error occurred while clearing location data. "
            "Please try again or contact support.",
            parse_mode='Markdown'
        )

@handle_errors(notify_user=True)
async def handle_location_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle location messages sent by users (both regular location and live position).
    
    This handler processes Telegram location messages and routes them to the
    appropriate handler based on the type of location request.
    """
    user = update.effective_user
    user_id = str(user.id)
    logger.info(f"📍 Location message received from user {user.id}")
    
    try:
        # Validate that this is actually a location message
        if not update.message.location:
            logger.warning(f"📍 Non-location message received in location handler from user {user.id}")
            await update.message.reply_text(
                "❌ **Invalid Location Data**\n\n"
                "This doesn't appear to be a valid location message. "
                "Please use `/location` or `/position` to share your GPS location properly.",
                parse_mode='Markdown'
            )
            return
        
        # Check user registration
        if not company_manager.is_user_registered(user.id):
            await update.message.reply_text(
                "🏢 **Company Registration Required**\n\n"
                "To save location data, you must first select your company.\n\n"
                "💡 Use `/company` to get started!",
                parse_mode='Markdown'
            )
            return
        
        # Check if this is a live position request first
        from live_position_handler import live_position_handler
        if user_id in live_position_handler.position_requests:
            # This is a live position share
            logger.info(f"📍 Processing as live position for user {user.id}")
            await live_position_handler.handle_live_position(update, context)
        elif user_id in location_handler.location_requests:
            # This is a regular location share
            logger.info(f"📍 Processing as regular location for user {user.id}")
            await location_handler.handle_location(update, context)
        else:
            # No pending request - treat as regular location
            logger.info(f"📍 Processing as regular location (no pending request) for user {user.id}")
            await location_handler.handle_location(update, context)
        
    except Exception as e:
        logger.error(f"📍 Error handling location message from user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Location Processing Error**\n\n"
            "An error occurred while processing your location. "
            "Please try sharing your location again.\n\n"
            "💡 Use `/location` for regular location or `/position` for live position.",
            parse_mode='Markdown'
        )