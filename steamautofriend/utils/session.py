import json
import time
from pathlib import Path
from typing import Dict, Optional

from ..config import SESSION_FILE, DATE_FORMAT
from .logging import logger

def load_session() -> Optional[Dict]:
    """Load Steam session data from file."""
    if not SESSION_FILE.exists():
        logger.error(f"Session file not found: {SESSION_FILE}")
        return None
    
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
        
        # Ensure the data has the expected structure
        if 'cookies' not in data and 'steamLoginSecure' in data:
            # Convert old format to new format
            data = {
                'cookies': {
                    'steamLoginSecure': data.get('steamLoginSecure', ''),
                    'sessionid': data.get('sessionid', '')
                },
                'timestamp': data.get('timestamp', time.strftime(DATE_FORMAT))
            }
            
        # Log what cookies we have
        if 'cookies' in data:
            cookies = data['cookies']
            steam_login_secure = cookies.get('steamLoginSecure')
            session_id = cookies.get('sessionid')
            
            if not steam_login_secure or not session_id:
                logger.warning("Session is missing required cookies")
                
            logger.debug(f"Loaded session with cookies: {list(cookies.keys())}")
        else:
            logger.warning("No cookies found in session file")
            
        return data
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error loading session file: {str(e)}")
        return None

def save_session(session_data: Dict) -> bool:
    """Save Steam session data to file."""
    try:
        # Ensure cookies are properly formatted
        if 'cookies' in session_data:
            # Make sure both key cookies are present
            cookies = session_data['cookies']
            if 'steamLoginSecure' not in cookies or 'sessionid' not in cookies:
                logger.warning("Missing required cookies for session")
        else:
            logger.warning("No cookies provided in session data")
            
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f, indent=2)
        logger.info("Session saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving session: {str(e)}")
        return False

def clean_cookie_value(value: str, cookie_name: str) -> str:
    """Clean a cookie value by removing the cookie name prefix if present."""
    # Handle format: cookiename:"value" or cookiename:value
    if f'{cookie_name}:' in value:
        # Try to extract value from format like: cookiename:"value" or cookiename:value
        parts = value.split(':', 1)
        if len(parts) > 1:
            value = parts[1].strip()
            # Remove surrounding quotes if present
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            return value
            
    # Handle format: cookiename=value
    prefix = f"{cookie_name}="
    if value.startswith(prefix):
        return value[len(prefix):]
        
    return value

def create_session_file(steam_login_secure: str, session_id: str) -> bool:
    """Create a new session file with provided cookies."""
    try:
        if not steam_login_secure or not session_id:
            logger.error("Both cookies are required")
            return False
            
        # Clean cookie values
        steam_login_secure = clean_cookie_value(steam_login_secure, 'steamLoginSecure')
        session_id = clean_cookie_value(session_id, 'sessionid')
        
        # Create session data
        session_data = {
            'cookies': {
                'steamLoginSecure': steam_login_secure,
                'sessionid': session_id
            },
            'timestamp': time.strftime(DATE_FORMAT)
        }
        
        # Save to file
        return save_session(session_data)
        
    except Exception as e:
        logger.error(f"Error creating session file: {str(e)}")
        return False
