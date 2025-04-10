import json
import random
import re
import time
import requests
import traceback
from typing import List, Dict, Optional, Any

from ..config import (
    MIN_DELAY_BETWEEN_REQUESTS, 
    MAX_DELAY_BETWEEN_REQUESTS,
    MAX_DENIED_REQUESTS,
    RETRY_COOLDOWN_MINUTES
)
from .logging import logger
from .blacklist import should_retry, add_to_blacklist, load_blacklist, save_blacklist

def random_delay(interactive=False) -> None:
    """
    Add a random delay between requests.
    
    Args:
        interactive (bool): If True, use a shorter delay for interactive commands.
    """
    if interactive:
        # Use a shorter delay for interactive operations
        delay = random.uniform(1, 3)  # Use 1-3 seconds for interactive operations
    else:
        # Use the standard delay for background operations
        delay = random.uniform(MIN_DELAY_BETWEEN_REQUESTS, MAX_DELAY_BETWEEN_REQUESTS)
        
    time.sleep(delay)

def get_friends(steam_session) -> List[str]:
    """Get the list of friends for the logged-in account."""
    if not steam_session or not steam_session.logged_in:
        logger.error("Not logged in")
        return []
        
    try:
        # Get our own Steam ID
        own_steam_id = None
        own_miniprofile_id = None
        steam_login_secure = steam_session.session.cookies.get('steamLoginSecure', '')
        
        if steam_login_secure:
            parts = steam_login_secure.split('%7C')
            if parts and len(parts) >= 1:
                own_steam_id = parts[0]
                # Calculate our own miniprofile ID for filtering
                try:
                    own_miniprofile_id = str(int(own_steam_id) - 76561197960265728)
                    logger.debug(f"Calculated own miniprofile ID: {own_miniprofile_id}")
                except (ValueError, TypeError):
                    logger.warning("Could not calculate own miniprofile ID")
                    
        if not own_steam_id:
            logger.error("Could not determine own Steam ID")
            return []
                
        # Get friends list
        friends_url = f"https://steamcommunity.com/profiles/{own_steam_id}/friends"
        response = steam_session.session.get(friends_url)
        
        # Extract miniprofile IDs from the HTML (this is a reliable way to get profileIDs)
        miniprofile_pattern = re.findall(r'data-miniprofile="(\d+)"', response.text)
        if miniprofile_pattern:
            # Convert miniprofile IDs to Steam IDs
            # The formula is: steamID64 = miniprofile + 76561197960265728
            steam_ids = []
            for miniprofile in miniprofile_pattern:
                if miniprofile:
                    try:
                        # Skip the current user's profile that appears in the header
                        if own_miniprofile_id and miniprofile == own_miniprofile_id:
                            logger.debug(f"Skipping own miniprofile ID: {miniprofile}")
                            continue
                        
                        steam_id = str(int(miniprofile) + 76561197960265728)
                        steam_ids.append(steam_id)
                    except ValueError:
                        continue
            
            if steam_ids:
                # Remove duplicates and sort
                steam_ids = sorted(list(set(steam_ids)))
                logger.debug(f"Found {len(steam_ids)} friends from miniprofile IDs")
                return steam_ids
        
        # Try the JavaScript variable patterns as a fallback
        friends_data_match = None
        
        patterns = [
            r'g_rgFriends\s*=\s*(\[.*?\]);',
            r'InitFriendsList\s*\(\s*(\[.*?\])',
            r'"friends":\s*(\[.*?\])',
            r'var\s+friendsList\s*=\s*(\[.*?\]);'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text, re.DOTALL)
            if match:
                friends_data_match = match
                break
        
        if friends_data_match:
            try:
                friends_data = json.loads(friends_data_match.group(1))
                logger.debug(f"Found {len(friends_data)} friends from JavaScript")
                
                # Extract Steam IDs
                steam_ids = []
                for friend in friends_data:
                    if isinstance(friend, dict) and 'steamid' in friend:
                        steam_ids.append(friend['steamid'])
                    elif isinstance(friend, str) and friend.isdigit():
                        steam_ids.append(friend)
                        
                return steam_ids
            except json.JSONDecodeError:
                logger.error("Failed to parse friends data JSON")
        
        # If we get here, try to extract from direct profile links
        profile_links = re.findall(r'href="https://steamcommunity\.com/profiles/(\d+)"', response.text)
        if profile_links:
            # Remove duplicates and sort
            steam_ids = sorted(list(set(profile_links)))
            logger.debug(f"Found {len(steam_ids)} friends from profile links")
            return steam_ids
        
        logger.error("Failed to find friends data in page content")
        return []
        
    except Exception as e:
        logger.error(f"Error getting friends list: {str(e)}")
        return []

def get_pending_requests(steam_session) -> List[str]:
    """Get the list of pending friend requests.
    
    This function checks multiple sources to find pending friend requests:
    1. The pending invites page
    2. The manage friends page
    3. Direct profile checks for suspicious cases
    
    Returns:
        List[str]: List of Steam IDs with pending requests
    """
    if not steam_session or not steam_session.logged_in:
        logger.error("Not logged in")
        return []
        
    # Keep track of all found pending requests
    all_pending_requests = set()
    
    try:
        # First get our own Steam ID to find our profile URL
        own_steam_id = steam_session.get_own_steam_id()
        if not own_steam_id:
            logger.error("Could not determine own Steam ID")
            return []
        
        # METHOD 1: Visit pending invites page for our profile
        try:
            pending_url = f'https://steamcommunity.com/profiles/{own_steam_id}/friends/pending'
            response = steam_session.session.get(pending_url)
            
            if response.status_code == 200:
                # Check if we're sent to the login page
                if "You'll need to sign in to see this" in response.text:
                    logger.error("Session expired - redirected to login page")
                else:
                    # Look for pending invites in the HTML
                    # Search for specific divs with pending invites
                    pending_section = re.search(r'<div class="friends_invites_section">(.*?)</div>', response.text, re.DOTALL)
                    
                    # If we can't find the pending invites section, try alternate method
                    if not pending_section:
                        # Try to find the pending invites by looking for miniprofile IDs in specific sections
                        # Look for specific IDs of account we've sent requests to
                        mini_pattern = r'data-miniprofile=["\'](.*?)["\'][^>]*>.*?<span\s+class="friend_blocked_text">Invite\s+Sent'
                        pending_profile_ids = re.findall(mini_pattern, response.text, re.DOTALL | re.IGNORECASE)
                        
                        # Convert miniprofile IDs to Steam IDs
                        if pending_profile_ids:
                            for miniprofile_id in pending_profile_ids:
                                steam_id = convert_miniprofile_id(miniprofile_id)
                                if steam_id:
                                    all_pending_requests.add(steam_id)
                                    
                            logger.debug(f"Found {len(pending_profile_ids)} pending outgoing requests from miniprofile IDs")
                    else:
                        # Get direct Steam IDs from pending friends URLs
                        profile_pattern = r'href="(?:https://steamcommunity\.com)?/profiles/(\d+)"[^>]*>'
                        steam_ids = re.findall(profile_pattern, pending_section.group(1))
                        
                        if steam_ids:
                            # Add all found IDs to our set
                            all_pending_requests.update(steam_ids)
                            logger.debug(f"Found {len(steam_ids)} pending requests by profile URL")
            else:
                logger.error(f"Error accessing pending page: HTTP {response.status_code}")
        except Exception as e:
            logger.warning(f"Error checking pending invites page: {str(e)}")
            
        # METHOD 2: Check "Manage Friends" page which shows outbound requests
        try:
            manage_url = 'https://steamcommunity.com/my/friends/pending'
            manage_resp = steam_session.session.get(manage_url)
            
            if manage_resp.status_code == 200:
                # Check for sent requests pattern
                if 'class="friendInvite_SentRequest' in manage_resp.text:
                    # Extract Steam IDs from sent requests
                    sent_pattern = r'data-steamid="(\d+)"[^>]*>.*?class="friendInvite_SentRequest'
                    sent_ids = re.findall(sent_pattern, manage_resp.text, re.DOTALL)
                    
                    if sent_ids:
                        # Add all found IDs to our set
                        all_pending_requests.update(sent_ids)
                        logger.debug(f"Found {len(sent_ids)} pending sent requests from manage page")
                
                # Also check for the newer UI version
                newer_pattern = r'data-steamid="(\d+)"[^>]*>.*?Pending\.\.\..*?</span>'
                newer_ids = re.findall(newer_pattern, manage_resp.text, re.DOTALL | re.IGNORECASE)
                if newer_ids:
                    all_pending_requests.update(newer_ids)
                    logger.debug(f"Found {len(newer_ids)} pending requests from newer UI")
        except Exception as e:
            logger.warning(f"Error checking manage friends page: {str(e)}")
            
        # METHOD 3: Check the community friends page
        try:
            friends_url = f'https://steamcommunity.com/profiles/{own_steam_id}/friends/'
            friends_resp = steam_session.session.get(friends_url)
            
            if friends_resp.status_code == 200:
                # Look for pending request indicators
                pending_pattern = r'data-steamid="(\d+)"[^>]*>.*?Pending.*?</span>'
                pending_ids = re.findall(pending_pattern, friends_resp.text, re.DOTALL | re.IGNORECASE)
                
                if pending_ids:
                    all_pending_requests.update(pending_ids)
                    logger.debug(f"Found {len(pending_ids)} pending requests from friends page")
        except Exception as e:
            logger.warning(f"Error checking friends page: {str(e)}")
            
        # METHOD 4: Check blacklist for recent additions that might be pending
        # This helps address the race condition where we thought a request was denied
        # but it was just a temporary API glitch
        try:
            blacklist = load_blacklist()
            current_time = time.time()
            for steam_id, data in blacklist.items():
                # If this is a recent addition with a low count and was marked as 
                # potentially denied rather than confirmed, double-check it
                if (data.get('count', 0) <= 1 and 
                    data.get('failure_is_confirmed', True) == False and
                    data.get('reason', '') == 'Friend request potentially denied' and
                    current_time - data.get('last_attempt', 0) < 3600):  # Added in the last hour
                    
                    # Verify by visiting the profile directly
                    try:
                        profile_url = f"https://steamcommunity.com/profiles/{steam_id}"
                        profile_resp = steam_session.session.get(profile_url, timeout=10)
                        
                        if profile_resp.status_code == 200:
                            # Check for pending indicator in profile
                            if "invite_sent" in profile_resp.text or "Pending..." in profile_resp.text:
                                all_pending_requests.add(steam_id)
                                logger.debug(f"Found pending request to {steam_id} via profile verification")
                    except Exception as profile_err:
                        logger.warning(f"Error checking profile for {steam_id}: {str(profile_err)}")
        except Exception as e:
            logger.warning(f"Error checking blacklist for potential pending requests: {str(e)}")
        
        # Return the combined list of pending requests
        result = list(all_pending_requests)
        if result:
            logger.info(f"Found total of {len(result)} pending requests from all sources")
        else:
            logger.info("No pending requests found from any source")
        return result
        
    except Exception as e:
        logger.error(f"Error getting pending requests: {str(e)}")
        traceback.print_exc()
        return []

def send_friend_request(steam_session, steam_id: str, account_name: str = None) -> bool:
    """Send a friend request to a Steam user."""
    # Static variable to track recently successful requests to prevent duplicate messages
    if not hasattr(send_friend_request, "recent_successes"):
        send_friend_request.recent_successes = {}
    
    if not steam_session or not steam_session.logged_in:
        logger.error("Not logged in")
        return False
        
    try:
        # Use account name in messages if provided, otherwise use steam_id
        display_name = account_name or steam_id
        
        # Check if we've recently sent a successful request to this account
        current_time = time.time()
        if steam_id in send_friend_request.recent_successes:
            last_success_time = send_friend_request.recent_successes[steam_id]
            # If we've successfully sent a request to this account in the last 30 minutes,
            # return success without printing duplicate message
            if current_time - last_success_time < 1800:  # 30 minutes in seconds (increased from 10)
                logger.debug(f"Skipping duplicate success message for {display_name} (within 30 min cooldown)")
                return True
        
        # Check if this account is in the blacklist
        if not should_retry(steam_id, MAX_DENIED_REQUESTS, RETRY_COOLDOWN_MINUTES):
            return False
        
        # Track if we've already shown a success message to prevent duplicates 
        # within the same function call
        success_shown = False
        
        # Get own Steam ID for debugging
        own_steam_id = None
        try:
            own_steam_id = steam_session.get_own_steam_id()
            if own_steam_id:
                logger.debug(f"Own Steam ID: {own_steam_id}")
                # Prevent sending friend request to yourself
                if own_steam_id == steam_id:
                    logger.error(f"Cannot send friend request to yourself ({display_name})")
                    print(f"Failed: Cannot send friend request to yourself ({display_name}) (Error code: 40)")
                    return False
        except Exception as e:
            logger.warning(f"Could not retrieve own Steam ID: {str(e)}")
        
        # First check if a request is already pending by checking the pending requests list
        pending_requests = get_pending_requests(steam_session)
        if pending_requests and steam_id in pending_requests:
            logger.info(f"Friend request already pending for {display_name}")
            print(f"Friend request already pending for {display_name} (verified in pending list)")
            # Track this success
            send_friend_request.recent_successes[steam_id] = current_time
            success_shown = True
            return True
            
        # Also check if we're already friends
        friends = get_friends(steam_session)
        if friends and steam_id in friends:
            logger.info(f"Already friends with {display_name}")
            print(f"Already friends with {display_name}")
            # Track this success
            send_friend_request.recent_successes[steam_id] = current_time
            success_shown = True
            return True
            
        # Add random delay before request
        random_delay()
        
        # Get session ID from cookies
        session_id = steam_session.session.cookies.get('sessionid')
        if not session_id:
            logger.error("No session ID found in cookies")
            return False
            
        # First visit the profile page to set up the request and check for friend list status
        profile_url = f"https://steamcommunity.com/profiles/{steam_id}"
        try:
            profile_resp = steam_session.session.get(profile_url, timeout=10)
            logger.debug(f"Profile page status: {profile_resp.status_code}")
            
            # Check if profile page was loaded successfully
            if profile_resp.status_code >= 300:
                logger.error(f"Error accessing profile page for {display_name}: HTTP {profile_resp.status_code}")
                print(f"Failed to load profile page for {display_name}: HTTP {profile_resp.status_code}")
                return False
            
            # Check for full friends list indicators
            if "has reached the maximum number of friends" in profile_resp.text or "friends list is full" in profile_resp.text:
                logger.info(f"User {display_name} has a full friends list")
                print(f"Cannot add {display_name}: Friends list is full")
                return False
                
            # Check if there's a Family View PIN input in the page
            if "familyViewPINForm" in profile_resp.text or "FamilyView" in profile_resp.text:
                logger.error("Family View is enabled and blocking access")
                print(f"Failed: Family View is enabled and blocking access to {display_name}")
                return False
                
            # Check if already friends (from the profile page)
            if "are_friends" in profile_resp.text or 'class="friendRelationship"' in profile_resp.text:
                logger.info(f"Already friends with {display_name} (detected in profile)")
                if not success_shown:
                    print(f"Already friends with {display_name}")
                    success_shown = True
                # Track this success
                send_friend_request.recent_successes[steam_id] = current_time
                return True
                
            # Check if request is already pending (from the profile page)
            if "invite_sent" in profile_resp.text or "Pending..." in profile_resp.text:
                logger.info(f"Friend request already pending for {display_name} (detected in profile)")
                if not success_shown:
                    print(f"Friend request already pending for {display_name}")
                    success_shown = True
                # Track this success
                send_friend_request.recent_successes[steam_id] = current_time
                return True
                
            # Check if the profile has proper friend capabilities
            if "This user has not yet set up their Steam profile" in profile_resp.text:
                logger.warning(f"User {display_name} has not set up their profile")
                print(f"Failed: {display_name} has not set up their profile")
                return False
                
            # Update the session ID from the response cookies if available
            new_session_id = profile_resp.cookies.get('sessionid')
            if new_session_id:
                session_id = new_session_id
                logger.debug(f"Updated session ID from profile page: {session_id}")
        except Exception as e:
            logger.error(f"Error visiting profile page for {display_name}: {str(e)}")
            print(f"Error visiting profile page for {display_name}: {str(e)}")
            return False
        
        # Send friend request
        logger.info(f"Sending friend request to {display_name}")
        
        # Prepare the data payload - include both sessionid and sessionID
        payload = {
            'sessionID': session_id,
            'sessionid': session_id,
            'steamid': steam_id,
            'accept_invite': 0,
            'json': 1  # Request JSON response
        }
        
        logger.debug(f"Request payload: {payload}")
        logger.debug(f"Session cookies: {dict(steam_session.session.cookies)}")
        
        # Using comprehensive headers
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://steamcommunity.com',
            'Referer': profile_url,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Try to send friend request
        try:
            response = steam_session.session.post(
                "https://steamcommunity.com/actions/AddFriendAjax",
                data=payload,
                headers=headers,
                timeout=15
            )
            
            # Log detailed response information for debugging
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Always log the response text
            response_text = response.text
            logger.debug(f"Response text: {response_text}")
            
            logger.info(f"Response status: HTTP {response.status_code}")
            
            # Map error codes to descriptive messages
            error_descriptions = {
                1: "Success",
                2: "Invalid Steam ID",
                8: "User has ignored your request or you have a limited account",
                15: "Friend request already sent or user has a full friends list",
                25: "Too many requests (rate limited)",
                40: "Cannot send friend request to yourself",
                41: "User has rejected request, has privacy settings preventing requests, or has a full friend list"
            }
            
            # Check if we can detect a full friends list directly from the response
            friends_list_full = False
            if "has reached the maximum number of friends" in response_text or "friends list is full" in response_text:
                friends_list_full = True
                logger.info(f"User {display_name} has a full friends list (detected in response)")
                print(f"Cannot add {display_name}: Friends list is full")
                return False
                
            # First check for JSON response with error codes
            if response.headers.get('Content-Type', '').startswith('application/json'):
                try:
                    data = response.json()
                    logger.debug(f"Parsed JSON response: {data}")
                    
                    # Handle success cases
                    if data is True or (isinstance(data, dict) and data.get('success') == 1 and not data.get('failed_invites')):
                        logger.info(f"Successfully sent friend request to {display_name}")
                        if not success_shown:
                            print(f"Friend request sent successfully to {display_name}")
                            success_shown = True
                        # Track this success
                        send_friend_request.recent_successes[steam_id] = current_time
                        return True
                    
                    # Handle error codes in JSON response
                    if isinstance(data, dict) and 'failed_invites_result' in data and len(data['failed_invites_result']) > 0:
                        error_code = data['failed_invites_result'][0]
                        error_description = error_descriptions.get(error_code, f"Unknown error code: {error_code}")
                        
                        # Check if it's actually a full friends list case
                        if error_code == 15 and (friends_list_full or "is full" in response_text.lower() or "reached the maximum number of friends" in response_text.lower()):
                            logger.info(f"Cannot add {display_name}: Friends list is full (error code 15)")
                            print(f"Cannot add {display_name}: Friends list is full")
                            return False
                        
                        # For error code 15 we need to verify if the request is actually pending
                        # by checking the pending list, not just relying on the error code
                        if error_code == 15:
                            # Check for specific text patterns in response that indicate a full friends list
                            if "friend list is full" in response_text.lower() or "reached the maximum number of friends" in response_text.lower():
                                logger.info(f"Cannot add {display_name}: Friends list is full (detected in error code 15 response)")
                                print(f"Cannot add {display_name}: Friends list is full")
                                return False
                                
                            # Refresh the pending requests list to see if our request appears
                            updated_pending = get_pending_requests(steam_session)
                            if steam_id in updated_pending:
                                logger.info(f"Friend request to {display_name} was confirmed in pending list")
                                if not success_shown:
                                    print(f"Friend request sent to {display_name} (verified in pending list)")
                                    success_shown = True
                                # Track this success
                                send_friend_request.recent_successes[steam_id] = current_time
                                return True
                            else:
                                # Error code 15 often means the request is already pending but not visible yet in the pending list
                                # Steam API is often inconsistent in showing pending requests
                                logger.info(f"Friend request likely already sent to {display_name} (error code 15)")
                                if not success_shown:
                                    print(f"Friend request likely already sent to {display_name}")
                                    success_shown = True
                                # Track this as a success to prevent duplicate messages
                                send_friend_request.recent_successes[steam_id] = current_time
                                return True
                        
                        # Code 41 with "invite pending" text is also a success
                        if error_code == 41 and "invite pending" in response_text.lower():
                            logger.info(f"Friend request was already sent to {display_name}")
                            if not success_shown:
                                print(f"Friend request was already sent to {display_name}")
                                success_shown = True
                            # Track this success
                            send_friend_request.recent_successes[steam_id] = current_time
                            return True
                        
                        # Show error message if no success has been shown
                        if not success_shown:
                            print(f"Failed: {error_description} (Error code: {error_code})")
                            success_shown = True
                            
                        return False
                except Exception as json_error:
                    logger.error(f"Failed to parse JSON response: {str(json_error)}")
            
            # Check for success patterns in HTML response
            if "friend invite has been sent" in response_text:
                logger.info(f"Successfully sent friend request to {display_name} (detected in HTML)")
                if not success_shown:
                    print(f"Friend request sent successfully to {display_name}")
                    success_shown = True
                # Track this success
                send_friend_request.recent_successes[steam_id] = current_time
                return True
                
            # Check for error patterns in the response
            if "<html" in response_text:
                # Try to extract error message from HTML
                error_matches = re.search(r'class="error"[^>]*>([^<]+)<', response_text)
                if error_matches:
                    error_message = error_matches.group(1).strip()
                    print(f"Failed: {error_message}")
                    return False
                    
                # Check for common HTML error patterns
                if "family_view_blurb" in response_text:
                    print(f"Failed: Family View is enabled and blocking this request")
                    return False
                elif "You cannot invite this user to be your friend" in response_text:
                    print(f"Failed: {display_name} cannot receive friend requests due to privacy settings")
                    return False
                elif "to add friends on Steam" in response_text:
                    print(f"Failed: Your account is limited and cannot send friend requests")
                    return False
                elif "You'll need to sign in to add a friend" in response_text:
                    print(f"Failed: Authentication required - your session may have expired")
                    return False
                elif "Please verify your humanity" in response_text:
                    print(f"Failed: CAPTCHA verification required - please log into Steam in a browser first")
                    return False
                    
            # If we get a 400 response, it might be a temporary issue - give more details
            if response.status_code == 400:
                # If the response has at least some content, try to parse it
                if len(response_text) > 5:
                    try:
                        # Check if it's a JSON response
                        data = json.loads(response_text)
                        if isinstance(data, dict) and 'failed_invites_result' in data and len(data['failed_invites_result']) > 0:
                            error_code = data['failed_invites_result'][0]
                            error_description = error_descriptions.get(error_code, f"Unknown error code: {error_code}")
                            
                            # Handle specific error codes
                            if error_code == 41:
                                # For error code 41, provide more detailed explanation
                                print(f"Failed: {display_name} has rejected your request, has privacy settings preventing requests, or has a full friend list")
                                # Add to blacklist with reduced retries
                                add_to_blacklist(steam_id, f"Friend request failed with code 41", 2, time.time())
                            else:
                                print(f"Failed with error code {error_code}: {error_description}")
                        else:
                            print(f"Request failed: This may be due to request throttling or server issues")
                    except json.JSONDecodeError:
                        # Not JSON, give generic advice
                        print(f"Request failed: This may be due to request throttling or server issues")
                else:
                    # Empty response
                    print(f"Request failed: Check your connection or try again later")
                    
            # If we get here, it's a general failure with unknown cause
            print(f"Failed to send friend request: HTTP {response.status_code}")
            return False
                
        except Exception as e:
            logger.error(f"Error sending friend request: {str(e)}")
            print(f"Failed: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending friend request to {steam_id}: {str(e)}")
        return False

def convert_miniprofile_id(miniprofile_id: str) -> Optional[str]:
    """Convert a miniprofile ID to a Steam ID."""
    try:
        # The formula is: steamID64 = miniprofile + 76561197960265728
        steam_id = str(int(miniprofile_id) + 76561197960265728)
        return steam_id
    except (ValueError, TypeError):
        logger.error(f"Could not convert miniprofile ID: {miniprofile_id}")
        return None
