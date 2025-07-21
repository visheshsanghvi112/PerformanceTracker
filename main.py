# 📁 main.py
# 🚀 Entry point of the Telegram Performance Bot

import os
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ✅ Configuration and logging
from config import BOT_TOKEN
from logger import logger

# ✅ Command functions
from commands import (
    start_command,
    sales_command,
    purchase_command,
    today_command,
    week_command,
    month_command
)

# ✅ Message handler for free text entries
from handlers import handle_message

# ⏰ Optional scheduler for automated tasks
try:
    from scheduler import start_scheduler
except ImportError:
    start_scheduler = None

# ✅ Main Telegram bot runner
def main():
    # 🔐 Check bot token
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment. Please check your .env file.")
        return

    # 🤖 Build app
    application = Application.builder().token(BOT_TOKEN).build()

    # 🛠 Slash command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("sales", sales_command))
    application.add_handler(CommandHandler("purchase", purchase_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("week", week_command))
    application.add_handler(CommandHandler("month", month_command))

    # ✉️ Message handler for unstructured inputs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ⏱ Optional: Launch scheduler if available
    if start_scheduler:
        start_scheduler()
        logger.info("⏰ Scheduler initialized.")

    # 🚀 Launch bot
    logger.info("🤖 Bot is running... Listening for commands and messages.")
    application.run_polling()

# ✅ Run main only if called directly
if __name__ == "__main__":
    main()
