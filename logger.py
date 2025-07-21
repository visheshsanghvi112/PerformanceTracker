import logging
import os
from config import DATA_DIR

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Set up logger
logger = logging.getLogger('telegram_bot')
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(os.path.join(DATA_DIR, 'bot.log'))
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler) 