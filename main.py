# 📁 main.py
# 🚀 Entry point of the Telegram Performance Bot

import os
import sys
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)

# ✅ Configuration and logging
from config import BOT_TOKEN, DATA_DIR
from logger import logger

# ✅ Command functions
from commands import (
    start_command,
    sales_command,
    purchase_command,
    today_command,
    week_command,
    month_command,
    # 🚀 Advanced Analytics Commands
    dashboard_command,
    predictions_command,
    charts_command,
    analytics_help_command,
    top_performers_command,
    location_analytics_command,
    ai_help_command
)

# 🏢 Company management commands
from company_commands import (
    company_select_command,
    handle_company_callback,
    admin_panel_command,
    admin_users_command,
    admin_stats_command,
    admin_assign_command,
    admin_remove_command
)

# 📍 Location management commands
from location_commands import (
    location_command,
    location_status_command,
    location_clear_command,
    handle_location_message
)

# 📍 Live position management commands
from live_position_commands import (
    position_command,
    position_status_command,
    position_clear_command,
    position_update_command,
    position_analytics_command,
    handle_live_position_message
)

# ✅ Message handler for free text entries
from handlers import handle_message

# ✅ Menu system for interactive navigation
from menus import menu_handler

# ✅ Error handling system
from error_handler import handle_error

# ✅ System health checks
from sheets import check_sheet_connection

# ⏰ Optional scheduler for automated tasks
try:
    from scheduler import start_scheduler
except ImportError:
    start_scheduler = None

def check_system_health():
    """Check if all required services are available"""
    logger.info("🔍 Performing system health checks...")
    
    # Check bot token
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment")
        return False
    
    # Check Google Sheets connection
    if not check_sheet_connection():
        logger.warning("⚠️ Google Sheets connection failed - some features may not work")
        # Don't return False here as the bot can still work with limited functionality
    
    # Check if required files exist
    required_files = [
        'yugrow-dd1d5-f97f321827f2.json',  # Google Sheets credentials
        '.env'  # Environment variables
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            logger.warning(f"⚠️ Required file missing: {file}")
    
    logger.info("✅ System health check completed")
    return True

# ✅ Enhanced error handler for the application
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler for the bot"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Try to notify the user if possible
    if isinstance(update, type(update)) and hasattr(update, 'effective_chat'):
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ An unexpected error occurred. The issue has been logged and will be investigated."
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")

# ✅ Main Telegram bot runner
def main():
    """Main function to start the bot"""
    try:
        # 🔍 System health check
        if not check_system_health():
            logger.error("❌ System health check failed. Exiting.")
            sys.exit(1)

        # 🤖 Build app with enhanced configuration
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .build()
        )

        # 🛠 Command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("sales", sales_command))
        application.add_handler(CommandHandler("purchase", purchase_command))
        application.add_handler(CommandHandler("today", today_command))
        application.add_handler(CommandHandler("week", week_command))
        application.add_handler(CommandHandler("month", month_command))
        
        # 🚀 Advanced Analytics Commands
        application.add_handler(CommandHandler("dashboard", dashboard_command))
        application.add_handler(CommandHandler("predictions", predictions_command))
        application.add_handler(CommandHandler("charts", charts_command))
        application.add_handler(CommandHandler("analytics", analytics_help_command))
        application.add_handler(CommandHandler("top", top_performers_command))
        application.add_handler(CommandHandler("location_analytics", location_analytics_command))
        
        # 🤖 AI Help and utility commands
        application.add_handler(CommandHandler("ai_help", ai_help_command))
        application.add_handler(CommandHandler("ai", ai_help_command))
        
        # 🔍 Analytics aliases for easier access
        application.add_handler(CommandHandler("forecast", predictions_command))
        application.add_handler(CommandHandler("trends", charts_command))
        application.add_handler(CommandHandler("help_analytics", analytics_help_command))

        # 🏢 Company Management Commands
        application.add_handler(CommandHandler("company", company_select_command))
        application.add_handler(CommandHandler("admin", admin_panel_command))
        application.add_handler(CommandHandler("admin_users", admin_users_command))
        application.add_handler(CommandHandler("admin_stats", admin_stats_command))
        application.add_handler(CommandHandler("admin_assign", admin_assign_command))
        application.add_handler(CommandHandler("admin_remove", admin_remove_command))

        # 📍 GPS Location Commands
        application.add_handler(CommandHandler("location", location_command))
        application.add_handler(CommandHandler("location_status", location_status_command))
        application.add_handler(CommandHandler("location_clear", location_clear_command))
        
        # 📍 Live Position Commands (SEPARATE from location commands)
        application.add_handler(CommandHandler("position", position_command))
        application.add_handler(CommandHandler("position_status", position_status_command))
        application.add_handler(CommandHandler("position_clear", position_clear_command))
        application.add_handler(CommandHandler("position_update", position_update_command))
        application.add_handler(CommandHandler("position_analytics", position_analytics_command))
        
        # 📍 Location message handler (for GPS coordinates - handles both location and live position)
        application.add_handler(MessageHandler(filters.LOCATION, handle_location_message))

        # 🎛 Interactive menu handlers
        application.add_handler(CallbackQueryHandler(handle_company_callback, pattern=r"^(register_company_|switch_company_|company_info_|close_menu)"))
        application.add_handler(CallbackQueryHandler(menu_handler.handle_callback_query))

        # ✉️ Message handler for unstructured inputs
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # 🚨 Global error handler
        application.add_error_handler(error_handler)

        # ⏱ Optional: Launch scheduler if available
        if start_scheduler:
            try:
                start_scheduler()
                logger.info("⏰ Scheduler initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Scheduler initialization failed: {e}")

        # 🚀 Launch bot
        logger.info("🤖 Performance Tracker Bot is starting...")
        logger.info("📊 Features enabled: Entry logging, AI parsing, Interactive menus, Error handling, Multi-Company Support")
        logger.info(f"🔗 Bot token configured: {BOT_TOKEN[:10]}...{BOT_TOKEN[-4:] if BOT_TOKEN else 'NOT SET'}")
        logger.info("🔗 Bot is running and ready to accept commands!")
        
        # Log system configuration
        logger.debug("🔧 System Configuration:")
        logger.debug(f"   📁 Data directory: {DATA_DIR}")
        logger.debug(f"   🗂️ Log files: bot.log")
        logger.debug(f"   🤖 AI Model: Gemini 2.5 Flash")
        logger.debug(f"   📊 Google Sheets: {'Enabled' if check_sheet_connection() else 'Disabled'}")
        logger.debug(f"   🏢 Multi-Company: Enabled (JohnLee, Yugrow Pharmacy, Ambica Pharma, Baker & Davis)")
        
        # Start polling with error recovery
        logger.info("🔄 Starting bot polling...")
        application.run_polling(
            drop_pending_updates=True,  # Clear any pending updates on restart
            allowed_updates=['message', 'callback_query']  # Only handle these update types
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error starting bot: {e}")
        sys.exit(1)

# ✅ Run main only if called directly
if __name__ == "__main__":
    main()
