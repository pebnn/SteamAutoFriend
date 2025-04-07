import time
from typing import Dict, Optional, Any
from pathlib import Path

from ..config import BLACKLIST_FILE, DATE_FORMAT
from .logging import logger

def ensure_blacklist_file() -> None:
    """Create blacklist.txt if it doesn't exist."""
    if not BLACKLIST_FILE.exists():
        BLACKLIST_FILE.touch()
        logger.info("Created new blacklist.txt file")

def load_blacklist() -> Dict[str, Dict[str, Any]]:
    """Load blacklist from file."""
    try:
        ensure_blacklist_file()
            
        blacklist = {}
        with open(BLACKLIST_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    steam_id = parts[0]
                    reason = parts[1]
                    timestamp = parts[2]
                    count = int(parts[3]) if len(parts) > 3 else 1
                    last_attempt = float(parts[4]) if len(parts) > 4 else time.time()
                    blacklist[steam_id] = {
                        'reason': reason,
                        'timestamp': timestamp,
                        'count': count,
                        'last_attempt': last_attempt
                    }
        return blacklist
    except Exception as e:
        logger.error(f"Error loading blacklist: {str(e)}")
        return {}

def save_blacklist(blacklist: Dict[str, Dict[str, Any]]) -> None:
    """Save blacklist to file."""
    try:
        ensure_blacklist_file()
        
        with open(BLACKLIST_FILE, 'w') as f:
            for steam_id, data in blacklist.items():
                f.write(f"{steam_id}|{data['reason']}|{data['timestamp']}|{data['count']}|{data['last_attempt']}\n")
        logger.info("Blacklist saved successfully")
    except Exception as e:
        logger.error(f"Error saving blacklist: {str(e)}")

def add_to_blacklist(steam_id: str, reason: str = "", count: int = 1, last_attempt: float = None) -> None:
    """Add a Steam ID to the blacklist file."""
    try:
        ensure_blacklist_file()
            
        timestamp = time.strftime(DATE_FORMAT)
        last_attempt = last_attempt or time.time()
        
        # Check if already in blacklist
        blacklist = load_blacklist()
        if steam_id in blacklist:
            # Update existing entry
            blacklist[steam_id]['count'] = count
            blacklist[steam_id]['last_attempt'] = last_attempt
            if reason:
                blacklist[steam_id]['reason'] = reason
            save_blacklist(blacklist)
        else:
            # Add new entry
            with open(BLACKLIST_FILE, 'a') as f:
                f.write(f"{steam_id}|{reason}|{timestamp}|{count}|{last_attempt}\n")
                
        logger.info(f"Added/updated {steam_id} in blacklist with count {count}")
    except Exception as e:
        logger.error(f"Error adding to blacklist: {str(e)}")

def is_blacklisted(steam_id: str) -> bool:
    """Check if a Steam ID is in the blacklist."""
    try:
        blacklist = load_blacklist()
        return steam_id in blacklist
    except Exception as e:
        logger.error(f"Error checking blacklist: {str(e)}")
        return False

def should_retry(steam_id: str, max_denied_requests: int, cooldown_minutes: int) -> bool:
    """Check if we should retry a denied friend request."""
    try:
        blacklist = load_blacklist()
        if steam_id not in blacklist:
            return True
            
        # Check if we've reached max denials
        denied_count = blacklist[steam_id].get('count', 0)
        if max_denied_requests > 0 and denied_count >= max_denied_requests:
            logger.info(f"Skipping {steam_id}: Already denied {denied_count} times")
            return False
            
        # Check if cooldown period has passed
        last_attempt = blacklist[steam_id].get('last_attempt', 0)
        cooldown_seconds = cooldown_minutes * 60
        if time.time() - last_attempt < cooldown_seconds:
            remaining_time = cooldown_seconds - (time.time() - last_attempt)
            logger.info(f"Friend request for {steam_id} is on cooldown for {int(remaining_time / 60)} more minutes")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error checking retry status: {str(e)}")
        return False
