import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
TIME_ID = int(os.getenv("TIME_ID"))
