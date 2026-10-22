import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
CHANNEL_URL = os.getenv("CHANNEL_URL", "")
SUPPORT_URL = os.getenv("SUPPORT_URL", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "larizinhastorebot")
STORE_URL = os.getenv("STORE_URL", f"https://t.me/{BOT_USERNAME}")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").rstrip("/")
PORT = int(os.getenv("PORT", "8080"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")
PURINCASH_API_KEY = os.getenv("PURINCASH_API_KEY", "")
PURINCASH_API_URL = os.getenv("PURINCASH_API_URL", "")
