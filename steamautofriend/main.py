import sys
import time
from typing import List
import argparse
import logging

from .utils.logging import setup_logging, logger
from .utils.session import create_session_file
from .utils.accounts import load_accounts, remove_account as remove_account_util, clean_accounts_file
from .utils.blacklist import load_blacklist
from .config import (
    CHECK_INTERVAL, 
    RETRY_COOLDOWN_MINUTES, 
    MAX_DENIED_REQUESTS
)
from .core.auto_friend import SteamAutoFriend

# Set up logging using utils.py's setup
logger = setup_logging()

def print_help():
    """Print help information."""
    print("\nAvailable commands:")
    print("  session - Create a new Steam session from your browser cookies")
    print("  login - Test if your session is valid")
    print("  add [account] - Add a new account to process (username, URL, or Steam ID)")
    print("  remove [account or number] - Remove an account from the queue")
    print("  list - List all accounts in the queue")
    print("  process - Process all accounts in the queue")
    print("  check - Check the status of sent friend requests")
    print("  help - Show this help message")
    print("  exit - Exit the program")

def show_status(bot):
    """Show the current status of the bot."""
    print("\nCurrent status:")
    print(f"  Running: {bot.running}")
    if bot.logged_in:
        print(f"  Session valid: Yes")
        print(f"  Accounts in queue: {bot.account_queue.qsize()}")
        print(f"  Active friend requests: {len(bot.sent_requests)}")
        print(f"  Blacklisted users: {len(bot.blacklist)}")
    else:
        print(f"  Session valid: No")

def list_accounts(bot):
    """List all accounts in the queue."""
    # First clean the accounts file to remove duplicates
    clean_accounts_file()
    
    # Get the accounts (now without duplicates)
    accounts = load_accounts()
    
    # Get blacklist data to check for accounts in cooldown
    blacklist = load_blacklist()
    current_time = time.time()
    cooldown_seconds = RETRY_COOLDOWN_MINUTES * 60
    
    if accounts:
        print("\nCurrent accounts in queue:")
        for i, account in enumerate(accounts, start=1):
            # Attempt to resolve the account to a Steam ID
            steam_id = None
            if bot.logged_in:
                try:
                    steam_id = bot.resolve_account(account)
                except Exception:
                    # If we can't resolve, just continue without Steam ID
                    pass
                
            # Basic account display
            account_info = f"  {i}. {account}"
            
            # Check if this account is in cooldown
            if steam_id and steam_id in blacklist:
                # Get blacklist info
                bl_entry = blacklist[steam_id]
                denied_count = bl_entry.get('count', 0)
                last_attempt = bl_entry.get('last_attempt', 0)
                
                # Calculate remaining cooldown time
                remaining_cooldown = 0
                if current_time - last_attempt < cooldown_seconds:
                    remaining_cooldown = int((cooldown_seconds - (current_time - last_attempt)) / 60)
                
                # Check if permanently blacklisted
                if MAX_DENIED_REQUESTS > 0 and denied_count >= MAX_DENIED_REQUESTS:
                    account_info += f" [BLACKLISTED: {denied_count} denials]"
                # Check if in cooldown
                elif remaining_cooldown > 0:
                    account_info += f" [COOLDOWN: {remaining_cooldown} min remaining]"
                else:
                    account_info += f" [PROCESSED: {denied_count} attempts]"
            elif steam_id:
                account_info += " [READY]"
            
            print(account_info)
            
        # Show when the next check will occur
        if hasattr(bot, 'last_check_time') and bot.last_check_time:
            next_check_in = CHECK_INTERVAL - (current_time - bot.last_check_time)
            if next_check_in < 0:
                next_check_in = "now"
            else:
                next_check_in = f"~{int(next_check_in)} seconds"
                
            print(f"\nNext friend request check: {next_check_in}")
        else:
            print(f"\nNext friend request check: scheduled every {CHECK_INTERVAL} seconds")
    else:
        print("\nNo accounts in queue")

def process_args(bot, args):
    """Process command-line arguments."""
    # Handle named arguments with their values
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '--add':
            if i + 1 < len(args):
                account = args[i + 1]
                bot.add_account(account)
                i += 2
            else:
                logger.error("--add requires an account name")
                i += 1
        elif arg == '--check':
            bot.check_friend_requests()
            i += 1
        elif arg == '--remove':
            if i + 1 < len(args):
                account = args[i + 1]
                remove_account_util(account)
                i += 2
            else:
                logger.error("--remove requires an account name")
                i += 1
        elif arg == '--list':
            list_accounts(bot)
            i += 1
        elif arg == '--interactive':
            # Skip, handled by main function
            i += 1
        else:
            logger.warning(f"Unknown argument: {arg}")
            i += 1

def process_command(command_args, main_bot=None):
    """Process a command with its arguments."""
    args = command_args
    command = args[0].lower()
    
    # Handle exit command specially
    if command in ['exit', 'quit']:
        print("Exiting program...")
        # If we have a bot instance, stop its background threads
        return 'exit'
        
    if command == 'help':
        print_help()
        return
        
    # For the session command, create a new session file
    if command == 'session':
        steam_login_secure = input("Enter steamLoginSecure cookie: ").strip()
        session_id = input("Enter sessionid cookie: ").strip()
        if create_session_file(steam_login_secure, session_id):
            print("Session file created successfully")
        else:
            print("Failed to create session file")
        return
        
    # If we have a main bot instance passed in, use it
    if main_bot and main_bot.logged_in:
        bot = main_bot
    else:
        # Initialize the bot
        bot = SteamAutoFriend()
        
        # For other commands, try to log in
        if command != 'session':
            if not bot.login():
                print("No valid session found. Please use 'session' command to create one.")
                return
    
    if command == 'login':
        print("Session loaded successfully!")
        
    elif command == 'process':
        # Process all accounts in the accounts.txt file
        logger.info("Processing accounts from accounts.txt")
        if bot.load_accounts():
            bot.process_accounts()
        
    elif command == 'check':
        # Check friend request status
        logger.info("Checking friend request status")
        print("Checking friend request status...")
        
        # Get existing data before check
        friends_before = bot.get_friends()
        pending_before = bot.get_pending_requests()
        blacklist_before = load_blacklist()
        
        # Perform the check
        bot.check_friend_requests()
        
        # Get data after check to compare
        friends_after = bot.get_friends()
        pending_after = bot.get_pending_requests()
        blacklist_after = load_blacklist()
        
        # Calculate changes
        new_friends = [f for f in friends_after if f not in friends_before]
        removed_pending = [p for p in pending_before if p not in pending_after]
        new_blacklist = {k: v for k, v in blacklist_after.items() 
                        if k not in blacklist_before or blacklist_before[k]['count'] != v['count']}
        
        # Print summary
        print("\nCheck completed:")
        if new_friends:
            print(f"- {len(new_friends)} new friends accepted your requests")
        
        if removed_pending:
            print(f"- {len(removed_pending)} pending requests were processed (accepted or denied)")
        
        if new_blacklist:
            print(f"- {len(new_blacklist)} accounts had blacklist entries added or updated")
            
        if not new_friends and not removed_pending and not new_blacklist:
            print("- No changes detected in friend status")
            
        # Show when the next automatic check will occur
        current_time = time.time()
        if hasattr(bot, 'last_check_time') and bot.last_check_time:
            next_check_in = CHECK_INTERVAL - (current_time - bot.last_check_time)
            if next_check_in < 0:
                next_check_time = "now"
            else:
                next_check_time = f"in ~{int(next_check_in)} seconds"
                
            print(f"\nNext automatic check will occur {next_check_time}")
        
        # Get and process any accounts from accounts.txt that are ready
        accounts = load_accounts()
        if accounts:
            cooldown_accounts = []
            blacklisted_accounts = []
            ready_accounts = []
            
            # Check each account status
            for account in accounts:
                try:
                    steam_id = bot.resolve_account(account)
                    if not steam_id:
                        continue
                        
                    # Check if already friends
                    if steam_id in friends_after:
                        continue
                        
                    # Check if already has pending request
                    if steam_id in pending_after:
                        continue
                        
                    # Check blacklist status
                    if steam_id in blacklist_after:
                        bl_entry = blacklist_after[steam_id]
                        denied_count = bl_entry.get('count', 0)
                        last_attempt = bl_entry.get('last_attempt', 0)
                        
                        # Calculate remaining cooldown time
                        if current_time - last_attempt < RETRY_COOLDOWN_MINUTES * 60:
                            cooldown_accounts.append(account)
                        elif MAX_DENIED_REQUESTS > 0 and denied_count >= MAX_DENIED_REQUESTS:
                            blacklisted_accounts.append(account)
                        else:
                            ready_accounts.append(account)
                    else:
                        ready_accounts.append(account)
                except Exception:
                    # Skip accounts that can't be resolved
                    pass
                    
            if ready_accounts:
                print(f"\nFound {len(ready_accounts)} accounts ready for processing")
                print("Use the 'process' command to send friend requests to these accounts")
            else:
                print("\nNo accounts are ready to be processed at this time")
                if cooldown_accounts:
                    print(f"- {len(cooldown_accounts)} accounts are in cooldown")
                if blacklisted_accounts:
                    print(f"- {len(blacklisted_accounts)} accounts are blacklisted")
            
    elif command == 'add':
        if len(args) < 2:
            print("Missing account parameter. Usage: add [account]")
            return
            
        account = args[1]
        logger.info(f"Adding account: {account}")
        
        if bot.add_account(account):
            print(f"Account {account} added and processed successfully")
        else:
            print(f"Failed to add account {account}")
            
    elif command == 'remove':
        if len(args) < 2:
            print("Missing account parameter. Usage: remove [account or number]")
            return
            
        account = args[1]
        remove_account_util(account)
        
    elif command == 'list':
        list_accounts(bot)
            
    else:
        print(f"Unknown command: {command}")
        print_help()

def run_interactive_mode(bot):
    """Run the program in interactive mode."""
    print("\nWelcome to SteamAutoFriend Interactive Mode")
    print("Type 'help' for available commands or 'exit' to quit")
    
    # Check if logged in
    if bot.logged_in:
        print("Session loaded successfully!")
    else:
        print("No valid session found. Use 'session' command to create one.")
    
    # Try to use readline for better input handling if available
    try:
        import readline
        # Enable tab completion if readline is available
        def completer(text, state):
            commands = ['help', 'session', 'login', 'add', 'remove', 'list', 'process', 'check', 'exit', 'quit']
            matches = [cmd for cmd in commands if cmd.startswith(text)]
            if state < len(matches):
                return matches[state]
            else:
                return None
        
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer)
        
        # This helps preserve input line when output occurs
        readline.set_startup_hook(lambda: readline.redisplay())
    except ImportError:
        # Readline not available, continue without it
        pass
        
    # Command processing loop
    while True:
        try:
            # Get command from user with a visible prompt
            # Print a newline first to separate from any background output
            sys.stdout.write("\n> ")
            sys.stdout.flush()
            command_line = input().strip()
            if not command_line:
                continue
                
            # Split into command and arguments
            args = command_line.split()
            command = args[0].lower()
            
            # Check for exit command
            if command in ['exit', 'quit']:
                print("Exiting program...")
                bot.stop()  # Stop any background threads
                break
            
            # Process the command with the main bot instance
            process_command(args, main_bot=bot)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            print(f"Error: {str(e)}")
            
# Modify the logging setup to better handle console output
def setup_custom_logging():
    """
    Set up custom logging to prevent interference with command input.
    This reimports and reconfigures the logger from utils.logging.
    """
    # Import the root logger from utils
    from .utils.logging import setup_logging
    
    # Create our custom logger
    app_logger = setup_logging()
    
    # Override the console handler to use sys.stderr instead of stdout
    # This helps prevent interference with command-line input
    for handler in app_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            # Create a new handler for stderr
            console_handler = logging.StreamHandler(sys.stderr)
            # Copy formatter and level
            console_handler.setFormatter(handler.formatter)
            console_handler.setLevel(handler.level)
            # Remove old handler and add new one
            app_logger.removeHandler(handler)
            app_logger.addHandler(console_handler)
            break
            
    return app_logger

def main():
    """Main entry point."""
    # Import the global logger first to ensure it's available
    from .utils.logging import logger as global_logger
    
    # Check for verbose flag
    verbose = False
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        verbose = True
        import logging
        global_logger.setLevel(logging.DEBUG)
        print("Verbose mode enabled - Debug level logging activated")
    
    # Set up improved logging to avoid interfering with input
    try:
        # Configure logging to use stderr for console output
        setup_custom_logging()
    except Exception as e:
        print(f"Warning: Could not configure custom logging: {e}")
    
    # Create the bot
    auto_friend = SteamAutoFriend(verbose=verbose)
    
    # Try to login
    if not auto_friend.login():
        global_logger.error("Login failed. Please create a session using the 'session' command")
        # Continue to interactive mode even if login fails
        print("Login failed. No valid session found or session has expired.")
        print("Please use the 'session' command to create a new session.")
    
    # Run in interactive mode
    run_interactive_mode(auto_friend)

# Start the program if run directly
if __name__ == "__main__":
    main()
