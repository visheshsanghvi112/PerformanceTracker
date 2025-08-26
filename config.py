import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot token from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Admin IDs as a list of integers
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '1201911108').split(',')]

# Data directory for exports, charts, etc.
DATA_DIR = os.getenv('DATA_DIR', 'data')

# Google Sheets credentials file (from environment variable)
GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'yugrow-dd1d5-6676a7b2d2ea.json')

# Add other configuration constants as needed 