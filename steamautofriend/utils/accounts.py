import re
import json
from typing import List, Optional, Set
from pathlib import Path

from ..config import ACCOUNTS_FILE
from .logging import logger

def ensure_accounts_file() -> None:
    """Create accounts.txt if it doesn't exist."""
    if not ACCOUNTS_FILE.exists():
        ACCOUNTS_FILE.touch()
        logger.info("Created new accounts.txt file")

def load_accounts() -> List[str]:
    """Load accounts from the accounts file."""
    ensure_accounts_file()
    
    try:
        with open(ACCOUNTS_FILE, 'r') as f:
            content = f.read().strip()
            
        if not content:
            logger.info("Accounts file is empty")
            return []
            
        # Try to parse as JSON first (new format)
        try:
            accounts = json.loads(content)
            if isinstance(accounts, list):
                logger.info(f"Loaded {len(accounts)} accounts from JSON format")
                return accounts
        except json.JSONDecodeError:
            # Not JSON, try line-by-line format (old format)
            accounts = [line.strip() for line in content.split('\n') if line.strip()]
            logger.info(f"Loaded {len(accounts)} accounts from text format")
            return accounts
            
    except Exception as e:
        logger.error(f"Error loading accounts: {str(e)}")
        return []

def save_accounts(accounts: List[str]) -> None:
    """Save accounts to the accounts file."""
    ensure_accounts_file()
    
    with open(ACCOUNTS_FILE, 'w') as f:
        for account in accounts:
            f.write(f"{account}\n")
    logger.info(f"Saved {len(accounts)} accounts to file")

def add_account(account: str) -> bool:
    """Add a new account to the accounts file."""
    try:
        # Ensure the account is a string
        account = str(account).strip()
        
        # Check if account already exists
        accounts = load_accounts()
        if account in accounts:
            logger.info(f"Account {account} already exists in the file")
            return False
        
        # Add new account
        with open(ACCOUNTS_FILE, 'a') as f:
            f.write(f"{account}\n")
        logger.info(f"Added new account: {account}")
        return True
    except Exception as e:
        logger.error(f"Error adding account: {str(e)}")
        return False

def remove_account(account_identifier: str) -> bool:
    """Remove an account from the accounts file.
    
    Args:
        account_identifier: Either a number (1-based index) or a string representing 
                           a Steam username/URL/ID
    """
    try:
        # Load the current accounts
        accounts = load_accounts()
        if not accounts:
            logger.warning("No accounts in the queue to remove")
            return False
            
        # Check if the account is a number
        if account_identifier.isdigit():
            # Convert to 0-based index
            index = int(account_identifier) - 1
            if 0 <= index < len(accounts):
                removed = accounts.pop(index)
                save_accounts(accounts)
                logger.info(f"Removed account {index + 1}: {removed}")
                return True
            else:
                logger.error(f"Invalid account number: {account_identifier}")
                return False
        else:
            # Try to find the account by name or URL
            for i, acc in enumerate(accounts):
                if account_identifier.lower() in acc.lower():
                    removed = accounts.pop(i)
                    save_accounts(accounts)
                    logger.info(f"Removed account: {removed}")
                    return True
                    
            logger.error(f"Account not found: {account_identifier}")
            return False
    except Exception as e:
        logger.error(f"Error removing account: {str(e)}")
        return False

def extract_steam_id_from_url(url: str) -> Optional[str]:
    """Extract Steam ID from a Steam profile URL."""
    # Handle profile URLs
    profile_match = re.search(r'steamcommunity\.com/profiles/(\d+)', url)
    if profile_match:
        return profile_match.group(1)
    
    # Handle vanity URLs
    vanity_match = re.search(r'steamcommunity\.com/id/([^/]+)', url)
    if vanity_match:
        return vanity_match.group(1)
    
    return None

def clean_accounts_file() -> None:
    """Remove duplicate accounts from the accounts file."""
    try:
        accounts = load_accounts()
        if not accounts:
            return
            
        # Remove duplicates while preserving order
        seen = set()
        unique_accounts = []
        for account in accounts:
            if account not in seen:
                seen.add(account)
                unique_accounts.append(account)
                
        # Save cleaned list
        save_accounts(unique_accounts)
        logger.info(f"Cleaned accounts file: removed {len(accounts) - len(unique_accounts)} duplicates")
        
    except Exception as e:
        logger.error(f"Error cleaning accounts file: {str(e)}")
