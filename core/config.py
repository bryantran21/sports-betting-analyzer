import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

ODDS_API_KEY = os.getenv('ODDS_API_KEY')
CFBD_API_KEY = os.getenv('CFBD_API_KEY')

# Safety check
if not ODDS_API_KEY or not CFBD_API_KEY:
    print("⚠️ Warning: One or more API keys are missing from your .env file!")