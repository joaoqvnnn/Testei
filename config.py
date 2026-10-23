import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROUP_ID = os.getenv("GROUP_ID", "")
GROUP_URL = os.getenv("GROUP_URL", "")
SUPPORT_URL = os.getenv("SUPPORT_URL", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "larizinhastorebot")
STORE_URL = os.getenv("STORE_URL", f"https://t.me/{BOT_USERNAME}")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").rstrip("/")
PORT = int(os.getenv("PORT", "10000"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")

# Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "")
