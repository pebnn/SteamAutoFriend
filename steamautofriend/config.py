import os
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent.parent
ACCOUNTS_FILE = BASE_DIR / "accounts.txt"
BLACKLIST_FILE = BASE_DIR / "blacklist.txt"
LOG_FILE = BASE_DIR / "steam_auto_friend.log"
SESSION_FILE = BASE_DIR / "steam_session.json"

# Request settings
MAX_DENIED_REQUESTS = 3  # How many times a user can deny a request before being blacklisted
CHECK_INTERVAL = 60  # How often to check friend request status (in seconds)
RETRY_COOLDOWN_MINUTES = 120  # How long to wait before retrying a denied friend request (in minutes)

# Rate limiting
MIN_DELAY_BETWEEN_REQUESTS = 2  # Minimum delay between friend requests in seconds
MAX_DELAY_BETWEEN_REQUESTS = 10  # Maximum delay between friend requests in seconds

# Logging configuration
LOG_LEVEL = "WARNING"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S" 