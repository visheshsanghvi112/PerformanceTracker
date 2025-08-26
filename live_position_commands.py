#!/usr/bin/env python3
"""
📍 LIVE POSITION COMMANDS MODULE
===============================
Command handlers for live GPS position tracking
SEPARATE from existing location commands
"""

from telegram import Update
from telegram.ext import ContextTypes
from typing import Dict, Any

from live_position_handler import live_position_handler
from decorators import handle_errors, rate_limit
from logger import logger
from company_manager import company_manager

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def position_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """📍 Request live GPS position sharing"""
    user = update.effective_user
    logger.info(f"📍 /position command called by user {user.id} ({user.username or user.first_name})")
    
    try:
        await live_position_handler.request_live_position(update, context)
        logger.info(f"✅ Live position request completed for user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in /position command for user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Live Position Request Failed**\n\n"
            "An error occurred while processing your live position request. "
            "Please try again or contact support if the problem persists.\n\n"
            "💡 You can try `/position` again in a moment.",
            parse_mode='Markdown'
        )

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def position_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """📊 Show current live position status"""
    user = update.effective_user
    logger.info(f"📊 /position_status command called by user {user.id} ({user.username or user.first_name})")
    
    try:
        await live_position_handler.show_live_position_status(update, context)
        logger.info(f"✅ Live position status shown for user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in /position_status command for user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Error retrieving live position status**\n\n"
            "Please try again or contact support if the problem persists.",
            parse_mode='Markdown'
        )

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def position_clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """🗑️ Clear stored live position data"""
    user = update.effective_user
    logger.info(f"🗑️ /position_clear command called by user {user.id} ({user.username or user.first_name})")
    
    try:
        await live_position_handler.clear_live_position(update, context)
        logger.info(f"✅ Live position clear completed for user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in /position_clear command for user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Error clearing live position data**\n\n"
            "Please try again or contact support if the problem persists.",
            parse_mode='Markdown'
        )

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def position_update_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """🔄 Update/refresh live position data"""
    user = update.effective_user
    logger.info(f"🔄 /position_update command called by user {user.id} ({user.username or user.first_name})")
    
    try:
        await live_position_handler.update_live_position(update, context)
        logger.info(f"✅ Live position update initiated for user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in /position_update command for user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Error updating live position**\n\n"
            "Please try again or contact support if the problem persists.",
            parse_mode='Markdown'
        )

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def position_analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """📊 Show live position analytics and insights"""
    user = update.effective_user
    logger.info(f"📊 /position_analytics command called by user {user.id} ({user.username or user.first_name})")
    
    try:
        # Check if user is registered
        if not company_manager.is_user_registered(user.id):
            await update.message.reply_text(
                "🏢 **Company Registration Required**\n\n"
                "Please register with a company first using `/company`"
            )
            return
        
        company_id = company_manager.get_user_company(user.id)
        position_summary = live_position_handler.get_live_position_summary(str(user.id), company_id)
        
        if not position_summary['has_position']:
            await update.message.reply_text(
                "📍 **No Live Position Data for Analytics**\n\n"
                "🔴 You need to share your live position first to view analytics.\n\n"
                "📊 **Available Analytics (after sharing position):**\n"
                "• Real-time territory coverage\n"
                "• Field movement patterns\n"
                "• Position-based performance metrics\n"
                "• Live sales distribution analysis\n\n"
                "💡 Use `/position` to share your live position and unlock analytics!\n\n"
                "⚡ **Note:** Live position analytics are separate from regular location analytics."
            )
            return
        
        # For now, show basic analytics - will be enhanced in later tasks
        company_info = company_manager.get_company_info(company_id)
        company_name = company_info['display_name'] if company_info else company_id
        
        analytics_text = (
            f"📊 **Live Position Analytics**\n\n"
            f"🏢 **Company:** {company_name}\n"
            f"📍 **Current Position:** {position_summary['short_address']}\n"
            f"{position_summary['status_emoji']} **Status:** {position_summary['status_message']}\n"
            f"🎯 **Accuracy:** {position_summary['accuracy_level'].title()}\n\n"
            f"📈 **Quick Insights:**\n"
            f"• Position Age: {position_summary.get('age_hours', 0):.1f} hours\n"
            f"• Data Quality: {position_summary['accuracy_level'].title()}\n"
            f"• Active Status: {'✅ Active' if position_summary['is_fresh'] else '❌ Expired'}\n\n"
            f"🔄 **Advanced Analytics:**\n"
            f"• Territory coverage analysis\n"
            f"• Field movement tracking\n"
            f"• Position-based performance metrics\n"
            f"• Real-time sales distribution\n\n"
            f"💡 **Coming Soon:** Detailed territory analytics, movement patterns, and performance insights!\n\n"
            f"⚡ **Note:** This is separate from regular location analytics."
        )
        
        await update.message.reply_text(analytics_text, parse_mode='Markdown')
        logger.info(f"✅ Live position analytics shown for user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in /position_analytics command for user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Error retrieving live position analytics**\n\n"
            "Please try again or contact support if the problem persists.",
            parse_mode='Markdown'
        )

async def handle_live_position_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """📍 Handle incoming live position location messages"""
    user = update.effective_user
    logger.info(f"📍 Live position location message received from user {user.id}")
    
    try:
        # Check if this is a live position request (user has pending request)
        user_id = str(user.id)
        if user_id in live_position_handler.position_requests:
            # This is a live position share
            await live_position_handler.handle_live_position(update, context)
        else:
            # This might be a regular location share - let the regular location handler deal with it
            logger.debug(f"📍 Location message from user {user.id} not recognized as live position request")
            # Don't handle it here - let the regular location handler process it
            pass
            
    except Exception as e:
        logger.error(f"❌ Error handling live position message from user {user.id}: {e}")
        await update.message.reply_text(
            "❌ **Error processing live position**\n\n"
            "Please try again or contact support if the problem persists.",
            parse_mode='Markdown'
        )