import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot token from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Admin IDs as a list of integers
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '1201911108').split(',')]

# 🔑 Multi-API Key Configuration for Parallel Processing
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_KEY_2 = os.getenv('GEMINI_API_KEY_2')  # Add this to .env for 2x speedup
GEMINI_API_KEY_3 = os.getenv('GEMINI_API_KEY_3')  # Add this to .env for 3x speedup

# Parallel processing configuration
PARALLEL_PROCESSING_CONFIG = {
    'enabled': bool(GEMINI_API_KEY_2 or GEMINI_API_KEY_3),
    'max_parallel_requests': 3,  # Maximum concurrent API calls
    'batch_size_threshold': 2,   # Minimum entries to trigger parallel processing
}

# Data directory for exports, charts, etc.
DATA_DIR = os.getenv('DATA_DIR', 'data')

# Add other configuration constants as needed 