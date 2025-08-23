import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config import DATA_DIR

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Set up single, comprehensive logger
logger = logging.getLogger('performance_tracker_bot')
logger.setLevel(logging.DEBUG)  # Capture all levels

# Clear any existing handlers
logger.handlers.clear()

# Create a single, detailed formatter
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(funcName)-20s:%(lineno)-4d | %(message)s'
)

# Single rotating log file handler (prevents files from getting too large)
log_file = os.path.join(DATA_DIR, 'bot.log')
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=5*1024*1024,  # 5MB max file size
    backupCount=3,         # Keep 3 backup files (bot.log.1, bot.log.2, bot.log.3)
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)  # Log everything to file

# Console handler for immediate feedback
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)  # Only INFO and above to console

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent duplicate logs from parent loggers
logger.propagate = False

# Log system startup
logger.info("🚀 [STARTUP] Logging system initialized - Single log file approach")
logger.info(f"📁 [CONFIG] Log file location: {log_file}")
logger.info("📊 [CONFIG] All log levels (DEBUG/INFO/WARNING/ERROR) go to single file")
logger.debug("🔧 [DEBUG] Debug logging is active") 