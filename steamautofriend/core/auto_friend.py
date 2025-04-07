import queue
import threading
import time
from typing import List, Optional, Set, Dict, Any
import traceback

import requests

from ..config import CHECK_INTERVAL
from ..utils.logging import logger
from ..utils.blacklist import load_blacklist, save_blacklist, is_blacklisted
from ..utils.accounts import load_accounts, add_account as add_account_util
from ..utils.friends import send_friend_request, get_friends, get_pending_requests
from ..utils.resolver import resolve_account, resolve_vanity_url
from .steam_session import SteamSession

class SteamAutoFriend:
    """Main class for managing Steam friend requests."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the SteamAutoFriend class."""
        self.steam = None
        self.logged_in = False
        self.blacklist = {}
        self.processing_accounts = set()  # Track accounts being processed
        self.account_queue = queue.Queue()
        self.running = True
        self.sent_requests = set()
        self.last_check_time = 0
        self.verbose = verbose
        
        # Cache for frequently accessed data to reduce duplicate logging
        self._friends_cache = None
        self._friends_cache_time = 0
        self._pending_cache = None
        self._pending_cache_time = 0
        self._cache_ttl = 60  # Cache valid for 60 seconds
        
        # Friend request checker
        self.check_thread = None
        self.check_interval = CHECK_INTERVAL  # Use the value from config
    
    def login(self) -> bool:
        """Log in to Steam."""
        try:
            self.steam = SteamSession()
            if self.steam.load_session():
                logger.info("Session loaded successfully")
                self.logged_in = True  # Make sure to set logged_in state
                # Load blacklist after successful login
                self.blacklist = load_blacklist()
                # Start periodic check after successful login
                self.start_periodic_check()
                return True
            else:
                logger.error("Failed to load session")
                return False
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False

    def load_accounts(self) -> bool:
        """Load accounts from the accounts.txt file."""
        if not self.logged_in:
            logger.error("Not logged in")
            return False
            
        accounts = load_accounts()
        if not accounts:
            logger.info("No accounts found to process")
            return False
            
        # Clear the queue if it has items
        while not self.account_queue.empty():
            self.account_queue.get()
            
        # Add each account to the queue
        for account in accounts:
            self.account_queue.put(account)
            
        logger.info(f"Loaded {len(accounts)} accounts")
        return True
    
    def add_account(self, account: str) -> bool:
        """Add an account to process."""
        # Check format - could be a username, vanity URL, or full profile URL
        account = account.strip()
        
        # Resolve to Steam ID if possible
        steam_id = self.resolve_account(account)
        if steam_id:
            logger.info(f"Resolved account {account} to Steam ID: {steam_id}")
            
            # Add to the accounts file
            add_account_util(account)
            
            # Also add to the queue for processing
            self.account_queue.put(account)
            
            # Process the request in the background
            if steam_id not in self.processing_accounts:
                self.processing_accounts.add(steam_id)
                threading.Thread(target=self.process_account_in_background, 
                                args=(steam_id, account), 
                                daemon=True).start()
            
            return True
        else:
            logger.error(f"Could not resolve account {account} to a Steam ID")
            return False
    
    def resolve_account(self, account: str) -> Optional[str]:
        """Resolve a username, URL, or Steam ID to a Steam ID."""
        return resolve_account(account, self.steam)
    
    def resolve_vanity_url(self, vanity_url: str) -> Optional[str]:
        """Resolve a vanity URL to a Steam ID."""
        return resolve_vanity_url(vanity_url, self.steam)

    def get_steam_id(self, account: str) -> Optional[str]:
        """Get the Steam ID for an account."""
        return self.resolve_account(account)

    def verify_session(self) -> bool:
        """Verify that the session is valid."""
        if not self.steam:
            return False
        return self.steam.verify_session()

    def get_friends(self) -> List[str]:
        """Get the list of friends."""
        current_time = time.time()
        # Return cached result if available and not expired
        if self._friends_cache and (current_time - self._friends_cache_time) < self._cache_ttl:
            return self._friends_cache
            
        # Get fresh data and update cache
        self._friends_cache = get_friends(self.steam)
        self._friends_cache_time = current_time
        return self._friends_cache
        
    def get_pending_requests(self) -> List[str]:
        """Get the list of pending friend requests."""
        current_time = time.time()
        # Return cached result if available and not expired
        if self._pending_cache and (current_time - self._pending_cache_time) < self._cache_ttl:
            return self._pending_cache
            
        # Get fresh data and update cache
        self._pending_cache = get_pending_requests(self.steam)
        self._pending_cache_time = current_time
        return self._pending_cache

    def send_friend_request(self, steam_id: str, account_name: str = None) -> bool:
        """Send a friend request to a Steam user."""
        if not self.steam or not self.logged_in:
            logger.error("Not logged in")
            return False
            
        # Attempt to send the friend request
        success = send_friend_request(self.steam, steam_id, account_name)
        if success:
            self.sent_requests.add(steam_id)
        return success

    def process_account(self, steam_id: str, account_name: str = None) -> None:
        """Process a single account."""
        try:
            display_name = account_name or steam_id
            logger.info(f"Processing account {display_name}")
            
            # Check if already friends
            logger.info(f"Checking if already friends with {display_name}...")
            friends = self.get_friends()
            if steam_id in friends:
                logger.info(f"Already friends with {display_name}")
                print(f"  [✓] Already friends with {display_name}")
                return
            
            # Check if request is already pending
            logger.info(f"Checking if request is already pending for {display_name}...")
            pending = self.get_pending_requests()
            if steam_id in pending:
                logger.info(f"Friend request already pending for {display_name}")
                print(f"  [✓] Friend request already pending for {display_name}")
                return
                
            # Check if blacklisted
            if is_blacklisted(steam_id):
                logger.info(f"{display_name} is blacklisted")
                print(f"  [❌] {display_name} is blacklisted - won't send friend request")
                return
                
            # Send friend request
            result = self.send_friend_request(steam_id, display_name)
            logger.info(f"Friend request to {display_name}: {'Succeeded' if result else 'Failed'}")
            
        except Exception as e:
            logger.error(f"Error processing account {steam_id}: {str(e)}")
            traceback.print_exc()
        finally:
            if steam_id in self.processing_accounts:
                self.processing_accounts.remove(steam_id)
            
    def process_accounts(self, accounts: List[str] = None) -> None:
        """Process a list of accounts or accounts from the queue."""
        if not self.logged_in:
            logger.error("Not logged in")
            return
            
        try:
            # If we don't have accounts provided, load from file
            if accounts is None or len(accounts) == 0:
                # Process from queue
                if self.account_queue.empty():
                    # Try to load accounts from file
                    if self.load_accounts():
                        logger.info("Loaded accounts from file")
                    else:
                        logger.info("No accounts in queue to process")
                        return
                
                count = self.account_queue.qsize()
                logger.info(f"Found {count} accounts to process")
                
                # Process each account directly without using threads
                accounts_to_process = []
                while not self.account_queue.empty():
                    accounts_to_process.append(self.account_queue.get())
                
                # Track how many accounts were processed and how many succeeded
                processed_count = 0
                success_count = 0
                
                for account in accounts_to_process:
                    if not self.running:
                        logger.info("Stopping account processing")
                        break
                        
                    processed_count += 1
                    logger.info(f"Processing account {processed_count} of {len(accounts_to_process)}: {account}")
                    
                    try:
                        steam_id = self.resolve_account(account)
                        if steam_id:
                            logger.info(f"Resolved account {account} to Steam ID: {steam_id}")
                            try:
                                # Process the account but catch any exceptions so we can continue
                                self.process_account(steam_id, account)
                                success_count += 1
                            except Exception as e:
                                logger.error(f"Error processing account {account}: {str(e)}")
                                traceback.print_exc()
                                # Continue with next account despite errors
                                continue
                        else:
                            logger.error(f"Could not resolve account {account}")
                    except Exception as e:
                        logger.error(f"Error resolving account {account}: {str(e)}")
                        traceback.print_exc()
                        continue
                
                logger.info(f"Finished processing {processed_count} accounts. Successful: {success_count}, Failed: {processed_count - success_count}")
            else:
                # Process provided accounts
                logger.info(f"Processing {len(accounts)} provided accounts")
                
                # Track how many accounts were processed and how many succeeded
                processed_count = 0
                success_count = 0
                
                for account in accounts:
                    if not self.running:
                        logger.info("Stopping account processing")
                        break
                    
                    processed_count += 1
                    logger.info(f"Processing account {processed_count} of {len(accounts)}: {account}")
                    
                    try:    
                        steam_id = self.resolve_account(account)
                        if steam_id:
                            logger.info(f"Resolved account {account} to Steam ID: {steam_id}")
                            try:
                                # Process the account but catch any exceptions so we can continue
                                self.process_account(steam_id, account)
                                success_count += 1
                            except Exception as e:
                                logger.error(f"Error processing account {account}: {str(e)}")
                                traceback.print_exc()
                                # Continue with next account despite errors
                                continue
                        else:
                            logger.error(f"Could not resolve account {account}")
                    except Exception as e:
                        logger.error(f"Error resolving account {account}: {str(e)}")
                        traceback.print_exc()
                        continue
                
                logger.info(f"Finished processing {processed_count} accounts. Successful: {success_count}, Failed: {processed_count - success_count}")
            
        except Exception as e:
            logger.error(f"Error processing accounts: {str(e)}")
            traceback.print_exc()
            
    def process_account_in_background(self, steam_id: str, account_name: str = None) -> None:
        """Process a single account in a background thread."""
        try:
            # Process the account
            self.process_account(steam_id, account_name)
        except Exception as e:
            logger.error(f"Error processing account {account_name or steam_id}: {str(e)}")
        finally:
            # Remove the account from the processing set
            self.processing_accounts.discard(steam_id)
            
    def check_friend_requests(self) -> None:
        """Check the status of sent friend requests and process ready accounts."""
        if not self.logged_in:
            logger.warning("Not logged in, cannot check friend requests")
            return
            
        current_time = time.time()
        self.last_check_time = current_time  # Update the last check time
        
        try:
            friends = self.get_friends()
            pending_requests = self.get_pending_requests()
            
            # Check each sent request
            for steam_id in list(self.sent_requests):
                # If request was accepted
                if steam_id in friends:
                    logger.info(f"Friend request to {steam_id} was accepted")
                    self.sent_requests.remove(steam_id)
                    continue
                    
                # If request is still pending
                if steam_id in pending_requests:
                    logger.info(f"Friend request to {steam_id} is still pending")
                    continue
                    
                # Request was denied or ignored
                logger.info(f"Friend request to {steam_id} was denied or ignored")
                self.sent_requests.remove(steam_id)
                
                # Check if enough time has passed for a retry
                if steam_id in self.blacklist:
                    # Update the blacklist entry
                    self.blacklist[steam_id]['count'] += 1
                    self.blacklist[steam_id]['last_attempt'] = current_time
                    save_blacklist(self.blacklist)
                else:
                    # Add a new entry to the blacklist
                    self.blacklist[steam_id] = {
                        'reason': 'Friend request denied',
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'count': 1,
                        'last_attempt': current_time
                    }
                    save_blacklist(self.blacklist)
                    
                # Retry sending the request if we should
                if not is_blacklisted(steam_id):
                    logger.info(f"Retrying friend request to {steam_id}")
                    if self.send_friend_request(steam_id):
                        self.sent_requests.add(steam_id)
            
            # ENHANCEMENT: Process accounts from accounts.txt that are ready
            try:
                # Load accounts from accounts.txt
                from ..utils.accounts import load_accounts
                accounts = load_accounts()
                
                if accounts:
                    logger.info(f"Found {len(accounts)} accounts to check")
                    processed_count = 0
                    
                    for account in accounts:
                        # Skip if we've already processed too many accounts in this check
                        if processed_count >= 2:  # Limit to 2 accounts per check to avoid rate limiting
                            logger.info(f"Rate limiting: Will process remaining accounts in next check")
                            break
                        
                        # Resolve the account to a Steam ID
                        steam_id = self.resolve_account(account)
                        if not steam_id:
                            logger.warning(f"Could not resolve account: {account}")
                            continue
                        
                        # Skip if we're already processing this account
                        if steam_id in self.processing_accounts:
                            logger.debug(f"Already processing {account}")
                            continue
                        
                        # Skip if already friends
                        if steam_id in friends:
                            logger.debug(f"Already friends with {account}")
                            continue
                        
                        # Skip if request already pending
                        if steam_id in pending_requests:
                            logger.debug(f"Friend request already pending for {account}")
                            continue
                        
                        # Skip if blacklisted and should not retry
                        from ..utils.blacklist import should_retry
                        from ..config import MAX_DENIED_REQUESTS, RETRY_COOLDOWN_MINUTES
                        if not should_retry(steam_id, MAX_DENIED_REQUESTS, RETRY_COOLDOWN_MINUTES):
                            logger.debug(f"Account {account} is blacklisted or in cooldown")
                            continue
                        
                        # Process the account
                        logger.info(f"Sending friend request to {account}")
                        if self.send_friend_request(steam_id, account):
                            processed_count += 1
                            self.sent_requests.add(steam_id)
                    
                    if processed_count > 0:
                        logger.info(f"Automatically processed {processed_count} accounts")
            
            except Exception as e:
                logger.error(f"Error processing accounts: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error checking friend requests: {str(e)}")
            
    def start_periodic_check(self) -> None:
        """Start periodic checking of friend requests."""
        def check_loop():
            while self.running:
                try:
                    if not self.logged_in:
                        logger.warning("Not logged in, waiting before next check...")
                        time.sleep(60)  # Wait a minute before retrying
                        continue
                        
                    logger.debug("Checking friend requests...")
                    self.check_friend_requests()
                    # Note: last_check_time is now updated in check_friend_requests
                    time.sleep(CHECK_INTERVAL)
                except Exception as e:
                    logger.error(f"Error in periodic check: {str(e)}")
                    time.sleep(CHECK_INTERVAL)
        
        # Set initial last_check_time to current time
        self.last_check_time = time.time()
        
        # Start the check loop in a background thread
        threading.Thread(target=check_loop, daemon=True).start()
        logger.info("Started periodic friend request check")
        
    def stop(self) -> None:
        """Stop all background processing."""
        self.running = False
        logger.info("Stopping SteamAutoFriend")
