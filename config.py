import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
import hmac
import hashlib
from urllib.parse import parse_qsl, unquote

load_dotenv()

# --- Load environment variables ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
URL = os.getenv("URL")
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SADMIN = os.getenv("SADMIN")

# --- Directory Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")

# --- Telegram Data Validation ---
def validate(init_data: str) -> bool:
    """Validates the initData received from the Telegram Web App."""
    try:
        # The init_data is URL-encoded, so it needs to be decoded.
        unquoted_data = unquote(init_data)
        
        # Parse the string into a dictionary.
        parsed_data = dict(parse_qsl(unquoted_data))
        
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            return False

        # The data_check_string is the sorted key-value pairs.
        data_check_string = '\n'.join(
            f"{key}={value}" for key, value in sorted(parsed_data.items())
        )

        # Calculate the secret key.
        secret_key = hmac.new(
            "WebAppData".encode(), TOKEN.encode(), hashlib.sha256
        ).digest()
        
        # Calculate the hash of the data_check_string.
        calculated_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        # Compare the received hash with the calculated hash.
        return received_hash == calculated_hash
    except Exception:
        return False
    
def format_price(price: int) -> str:
    """Formats the price with spaces as thousand separators."""
    return f"{price:,}".replace(",", " ")