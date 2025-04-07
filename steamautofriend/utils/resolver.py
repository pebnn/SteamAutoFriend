import json
import re
from typing import Optional

from .logging import logger

def resolve_account(account: str, steam_session) -> Optional[str]:
    """Resolve a username, URL, or Steam ID to a Steam ID."""
    if not steam_session or not steam_session.logged_in:
        logger.error("Not logged in")
        return None
        
    # Check if it's already a Steam ID
    if account.isdigit() and len(account) > 10:
        return account
        
    # Check if it's a URL
    if '/' in account:
        # Extract the ID or vanity name from the URL
        if '/profiles/' in account:
            # It's a profile URL, extract the ID
            match = re.search(r'/profiles/(\d+)', account)
            if match:
                return match.group(1)
        elif '/id/' in account:
            # It's a vanity URL, extract the vanity name
            match = re.search(r'/id/([^/]+)', account)
            if match:
                vanity_name = match.group(1)
                return resolve_vanity_url(vanity_name, steam_session)
    else:
        # Assume it's a vanity name
        return resolve_vanity_url(account, steam_session)
        
    return None

def resolve_vanity_url(vanity_url: str, steam_session) -> Optional[str]:
    """Resolve a vanity URL to a Steam ID."""
    if not steam_session or not steam_session.logged_in:
        logger.error("Not logged in")
        return None
        
    try:
        # Clean up input
        vanity_url = vanity_url.strip()
        logger.info(f"Trying to resolve vanity URL: {vanity_url}")
        
        # Get our own Steam ID
        own_steam_id = steam_session.get_own_steam_id()
        
        # Try a direct request to the profile page
        try:
            profile_url = f"https://steamcommunity.com/id/{vanity_url}"
            response = steam_session.session.get(profile_url, allow_redirects=True)
            
            # Check if redirected to a /profiles/ URL (meaning it's a valid vanity URL)
            if '/profiles/' in response.url:
                match = re.search(r'/profiles/(\d+)', response.url)
                if match:
                    steam_id = match.group(1)
                    # Validate that this is not our own Steam ID
                    if own_steam_id and steam_id == own_steam_id:
                        logger.warning(f"Vanity URL '{vanity_url}' resolved to our own Steam ID, likely invalid")
                        return None
                    logger.info(f"Resolved vanity URL via redirect: {vanity_url} -> {steam_id}")
                    return steam_id
            
            # Look for the Steam ID in the page content
            steam_id_match = re.search(r'"steamid":"(\d+)"', response.text)
            if steam_id_match:
                steam_id = steam_id_match.group(1)
                # Validate that this is not our own Steam ID
                if own_steam_id and steam_id == own_steam_id:
                    logger.warning(f"Vanity URL '{vanity_url}' resolved to our own Steam ID, likely invalid")
                    return None
                logger.info(f"Resolved vanity URL via page content: {vanity_url} -> {steam_id}")
                return steam_id
            
            # If we got here, try looking for g_rgProfileData
            profile_data_match = re.search(r'g_rgProfileData\s*=\s*({.+?});', response.text, re.DOTALL)
            if profile_data_match:
                try:
                    profile_data = json.loads(profile_data_match.group(1))
                    if 'steamid' in profile_data:
                        steam_id = profile_data['steamid']
                        # Validate that this is not our own Steam ID
                        if own_steam_id and steam_id == own_steam_id:
                            logger.warning(f"Vanity URL '{vanity_url}' resolved to our own Steam ID, likely invalid")
                            return None
                        logger.info(f"Resolved vanity URL via g_rgProfileData: {vanity_url} -> {steam_id}")
                        return steam_id
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse g_rgProfileData JSON for vanity URL: {vanity_url}")
        
        except Exception as e:
            logger.error(f"Error resolving vanity URL '{vanity_url}' via profile page: {str(e)}")
        
        # Last resort: try looking up by account data, might be a username
        try:
            # Get session ID from cookies
            session_id = steam_session.session.cookies.get('sessionid', '')
            if not session_id:
                logger.error("No session ID found in cookies")
                return None
            
            form_data = {
                'type': 'auto',
                'text': vanity_url,
                'sessionid': session_id
            }
            response = steam_session.session.post('https://steamcommunity.com/search/SearchCommunityAjax', data=form_data)
            search_data = response.json()
            
            if search_data.get('success', 0) == 1 and search_data.get('html'):
                # Extract profile links from the search results
                profile_links = re.findall(r'href="https://steamcommunity\.com/id/([^"/]+)"', search_data['html'])
                profile_ids = re.findall(r'href="https://steamcommunity\.com/profiles/(\d+)"', search_data['html'])
                
                # Check if the vanity URL is in the results
                if vanity_url in profile_links and profile_links.index(vanity_url) < len(profile_ids):
                    idx = profile_links.index(vanity_url)
                    steam_id = profile_ids[idx]
                    # Validate that this is not our own Steam ID
                    if own_steam_id and steam_id == own_steam_id:
                        logger.warning(f"Vanity URL '{vanity_url}' resolved to our own Steam ID, likely invalid")
                        return None
                    logger.info(f"Resolved vanity URL via search: {vanity_url} -> {steam_id}")
                    return steam_id
        except Exception as e:
            logger.error(f"Error resolving vanity URL '{vanity_url}' via search: {str(e)}")
        
        try:
            api_url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
            params = {
                "vanityurl": vanity_url,
                "url_type": 1  # 1 for individual profile
            }
            response = steam_session.session.get(api_url, params=params)
            data = response.json()
            
            if data.get("response", {}).get("success") == 1:
                steam_id = data["response"]["steamid"]
                # Validate that this is not our own Steam ID
                if own_steam_id and steam_id == own_steam_id:
                    logger.warning(f"Vanity URL '{vanity_url}' resolved to our own Steam ID, likely invalid")
                    return None
                logger.info(f"Resolved vanity URL using Steam API: {vanity_url} -> {steam_id}")
                return steam_id
        except Exception as e:
            logger.error(f"Error using Steam API to resolve vanity URL: {str(e)}")
        
        logger.error(f"Failed to resolve vanity URL: {vanity_url}")
        return None
        
    except Exception as e:
        logger.error(f"Error resolving vanity URL: {str(e)}")
        return None 