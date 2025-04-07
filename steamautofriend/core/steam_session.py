import requests
from typing import Dict, List, Optional

from ..utils.logging import logger
from ..utils.session import load_session, save_session
from ..utils.friends import get_friends as get_friends_util
from ..utils.friends import get_pending_requests as get_pending_requests_util
from ..utils.accounts import extract_steam_id_from_url

class SteamSession:
    """Class representing a Steam session."""
    
    def __init__(self):
        """Initialize the Steam session."""
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        self.session.headers.update(self.headers)
        self.logged_in = False
    
    def load_session(self) -> bool:
        """Load a saved Steam session."""
        try:
            # Load session from file
            session_data = load_session()
            if not session_data:
                logger.error("Failed to load session data")
                return False
                
            # Add the cookies to the session
            cookies = session_data.get('cookies', {})
            if not cookies:
                logger.error("No cookies in session data")
                return False
                
            # Check for required cookies
            steam_login_secure = cookies.get('steamLoginSecure')
            session_id = cookies.get('sessionid')
            
            if not steam_login_secure:
                logger.error("Missing required cookie: steamLoginSecure")
                return False
                
            if not session_id:
                logger.warning("Missing sessionid cookie - will try to acquire one")
                # Continue anyway, we'll try to get a sessionid
            
            # Set cookies in the session with proper domain
            for name, value in cookies.items():
                self.session.cookies.set(name, value, domain='.steamcommunity.com', path='/')
                
            logger.info(f"Set {len(cookies)} cookies from session file")
            
            # Visit the Steam Community home page to get any missing cookies
            try:
                logger.info("Visiting Steam Community to refresh cookies...")
                home_resp = self.session.get('https://steamcommunity.com/', timeout=10)
                logger.debug(f"Home page status: {home_resp.status_code}")
                
                # Check if we got a sessionid cookie now
                if 'sessionid' not in self.session.cookies and home_resp.status_code == 200:
                    # Try to extract sessionid from the page content
                    import re
                    sessionid_match = re.search(r'g_sessionID\s*=\s*["\']([^"\']+)["\']', home_resp.text)
                    if sessionid_match:
                        sessionid_value = sessionid_match.group(1)
                        logger.info(f"Found sessionid in page: {sessionid_value}")
                        self.session.cookies.set('sessionid', sessionid_value, domain='.steamcommunity.com', path='/')
            except Exception as e:
                logger.warning(f"Error refreshing cookies: {str(e)}")
            
            # Verify that the session is valid
            if self.verify_session():
                # Session is valid
                self.logged_in = True
                logger.info("Session loaded successfully!")
                
                # Save the updated cookies
                self.save_session()
                return True
            else:
                logger.error("Session verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Error loading session: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    def verify_session(self) -> bool:
        """Verify that the session is valid."""
        # Check if we have the required cookies
        cookies = self.session.cookies
        
        steam_login_secure = cookies.get('steamLoginSecure')
        session_id = cookies.get('sessionid')
        
        if not steam_login_secure:
            logger.error("Session is missing required cookie: steamLoginSecure")
            return False
            
        if not session_id:
            logger.warning("Session is missing sessionid cookie")
            # We'll continue anyway since we might be able to get one
            
        # Check if we can access Steam
        try:
            logger.debug("Checking access to Steam profile page...")
            response = self.session.get('https://steamcommunity.com/my', 
                                        allow_redirects=False,
                                        timeout=10)
            
            # Log response details
            logger.debug(f"Profile check response: {response.status_code}")
            if response.status_code == 302:
                logger.debug(f"Redirect location: {response.headers.get('Location', 'None')}")
            
            # If we get redirected to login, the session is invalid
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                if 'login' in redirect_url.lower():
                    logger.error("Session is invalid (redirected to login)")
                    return False
                else:
                    logger.info(f"Unexpected redirect to: {redirect_url}")
                    # Some redirects might be normal, like profile redirects
                    
                    # Try to follow the redirect
                    try:
                        redirect_resp = self.session.get(redirect_url, timeout=10)
                        logger.debug(f"Redirect response: {redirect_resp.status_code}")
                        
                        # If we successfully followed the redirect and didn't get redirected to login
                        if redirect_resp.status_code == 200 and 'login' not in redirect_resp.url.lower():
                            # Check if we can extract our Steam ID from the URL
                            steam_id = extract_steam_id_from_url(redirect_resp.url)
                            if steam_id:
                                logger.info(f"Successfully verified session through redirect, Steam ID: {steam_id}")
                            else:
                                logger.info("Successfully verified session through redirect")
                            return True
                    except Exception as redirect_err:
                        logger.error(f"Error following redirect: {str(redirect_err)}")
                
            # If we get a 200 response, the session is valid
            if response.status_code == 200:
                logger.info("Session is valid")
                return True
                
            logger.error(f"Unknown session validation error: HTTP {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"Error verifying session: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    def save_session(self) -> bool:
        """Save the current Steam session."""
        try:
            # Create a dictionary to store the session data
            data = {
                'cookies': {name: value for name, value in self.session.cookies.items()},
            }
            
            # Save the session data
            return save_session(data)
            
        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")
            return False
            
    def get_friends(self) -> List[str]:
        """Get the list of friends for the logged-in account."""
        return get_friends_util(self)
            
    def get_pending_requests(self) -> List[str]:
        """Get the list of pending friend requests."""
        return get_pending_requests_util(self)
            
    def get_own_steam_id(self) -> Optional[str]:
        """Get the Steam ID of the logged-in account."""
        try:
            steam_login_secure = self.session.cookies.get('steamLoginSecure', '')
            if steam_login_secure:
                parts = steam_login_secure.split('%7C')
                if parts and len(parts) >= 1:
                    return parts[0]
            return None
        except Exception as e:
            logger.error(f"Error getting own Steam ID: {str(e)}")
            return None
