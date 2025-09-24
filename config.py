import os
import logging
from typing import Optional
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
import hmac
import hashlib
from urllib.parse import parse_qsl, unquote

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass

def get_required_env(key: str) -> str:
    """Get a required environment variable or raise ConfigError."""
    value = os.getenv(key)
    if not value:
        raise ConfigError(f"Required environment variable '{key}' is not set")
    return value

def get_optional_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get an optional environment variable with a default value."""
    return os.getenv(key, default)

# --- Load and validate environment variables ---
try:
    # Database configuration (required)
    DB_USER = get_required_env("DB_USER")
    DB_PASSWORD = get_required_env("DB_PASSWORD")
    DB_HOST = get_required_env("DB_HOST")
    DB_PORT = get_required_env("DB_PORT")
    DB_NAME = get_required_env("DB_NAME")
    
    # Application configuration (required)
    URL = get_required_env("URL")
    TOKEN = get_required_env("TOKEN")
    CHANNEL_ID = get_required_env("CHANNEL_ID")
    SADMIN = get_required_env("SADMIN")
    
    # Optional configuration
    ENVIRONMENT = get_optional_env("ENVIRONMENT", "development")
    DEBUG = get_optional_env("DEBUG", "false").lower() == "true"
    SECRET_KEY = get_optional_env("SECRET_KEY", "change-this-in-production")
    
    # File upload configuration
    MAX_FILE_SIZE_MB = int(get_optional_env("MAX_FILE_SIZE_MB", "5"))
    ALLOWED_IMAGE_EXTENSIONS = get_optional_env("ALLOWED_IMAGE_EXTENSIONS", "jpg,jpeg,png,webp").split(",")
    
    logger.info(f"Configuration loaded successfully for environment: {ENVIRONMENT}")
    
except ConfigError as e:
    logger.error(f"Configuration error: {e}")
    raise e
except Exception as e:
    logger.error(f"Unexpected error loading configuration: {e}")
    raise ConfigError(f"Failed to load configuration: {e}")

# --- Directory Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

# Create directories if they don't exist
for directory in [STATIC_DIR, UPLOAD_DIR]:
    os.makedirs(directory, exist_ok=True)

templates = Jinja2Templates(directory="templates")

# --- Security Configuration ---
if ENVIRONMENT == "production" and SECRET_KEY == "change-this-in-production":
    logger.warning("Using default SECRET_KEY in production! Please set a secure SECRET_KEY.")

# --- File Upload Constants ---
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

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