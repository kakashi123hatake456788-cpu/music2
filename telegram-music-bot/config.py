import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION_STRING = os.environ["SESSION_STRING"]

_allowed = os.environ.get("ALLOWED_CHATS", "").strip()
ALLOWED_CHATS = {int(c) for c in _allowed.split(",") if c.strip()} if _allowed else None

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
