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

# Add other configuration constants as needed 