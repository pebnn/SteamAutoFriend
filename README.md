# SteamAutoFriend

SteamAutoFriend is a powerful, automated tool for managing Steam friend requests through a simple command-line interface. It intelligently handles the entire friend request lifecycle - from sending requests to processing responses and managing rejections. The tool features a sophisticated retry system with configurable cooldown periods, blacklisting for declined requests, and automated periodic checks to maximize acceptance rates. Whether you're rebuilding your friends list or connecting with new players, SteamAutoFriend streamlines the process while respecting Steam's rate limits and user preferences.

## Features

- Automatically sends friend requests to specified Steam users
- Tracks and handles rejected friend requests with configurable retry logic
- Provides a simple command-line interface
- Uses cookie-based authentication for security
- Includes safety features to prevent abuse

## Installation

### Option 1: Install as a Package (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/pebnn/SteamAutoFriend.git
cd SteamAutoFriend
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Now you can run the program from anywhere using:
```bash
steamautofriend
```

### Option 2: Using Python Module Directly

1. Clone the repository:
```bash
git clone https://github.com/pebnn/SteamAutoFriend.git
cd SteamAutoFriend
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the program:
```bash
python -m steamautofriend.main
```

## Configuration

### Cookie Setup

SteamAutoFriend uses your Steam session cookies for authentication. To set this up:

1. Log in to Steam in your web browser
2. Open your browser's developer tools (F12)
3. Go to the "Application" or "Storage" tab
4. Find the cookies for steamcommunity.com
5. Copy the values for:
   - `steamLoginSecure`
   - `sessionid`
6. Run SteamAutoFriend and use the `session` command to input these values

The program accepts cookies in multiple formats:
- Raw value: `abcdefghijklm1234567890`
- With name prefix: `steamLoginSecure=abcdefghijklm1234567890`
- With name and colon: `steamLoginSecure:abcdefghijklm1234567890`
- With name, colon and quotes: `steamLoginSecure:"abcdefghijklm1234567890"`

#### Family View Compatibility

**Important**: This tool cannot handle Steam accounts with Family View PIN protection directly, but there is a workaround:

1. Log in to Steam in your browser
2. Enter your Family View PIN to unlock all features
3. After PIN authentication, export the cookies as described above
4. Use these cookies with SteamAutoFriend

This allows the tool to use your already-authenticated session. Note that you'll need to repeat these steps whenever your PIN session expires in the browser.

### Blacklist Configuration

SteamAutoFriend includes a blacklist feature to prevent repeatedly sending requests to users who deny them. This is controlled by the `MAX_DENIED_REQUESTS` setting in `config.py`:

- A positive number (default: 3) will blacklist users after that many denials
  - For example, setting it to 1 blacklists users immediately after their first denial
- Setting it to 0 disables blacklisting completely, allowing requests to be sent regardless of denials

## Usage

SteamAutoFriend provides several commands for managing the friend request process:

### Commands

- `session` - Create a new Steam session from your browser cookies
- `login` - Test if your session is valid
- `add [account]` - Add a new account to process (username, URL, or Steam ID)
- `remove [account or number]` - Remove an account from the queue
- `list` - List all accounts in the queue
- `process` - Process all accounts in the queue
- `check` - Check the status of sent friend requests
- `status` - Show the current status of the bot
- `help` - Show the help message
- `exit` - Exit the program

### Finding Steam IDs

To add friends, you'll need their Steam ID. You can find this in several ways:

1. From a Steam profile URL:
   - Regular URL: `https://steamcommunity.com/profiles/76561198055930586`
   - Custom URL: `https://steamcommunity.com/id/kisats`

2. Using Steam's search function:
   - Visit https://steamcommunity.com/search
   - Search for the user
   - Copy their profile URL

### Adding Friends

1. Start SteamAutoFriend
2. Use the `add` command with the Steam ID, profile URL, or username
3. SteamAutoFriend will automatically process the request

Example:
```
> add st4ck
```

## Safety Features

SteamAutoFriend includes several safety features:

- Random delays between requests to prevent rate limiting
- Blacklist system to prevent harassment/spam reports
- Automatic retry with configurable cooldown periods
- Detailed logging of all actions

## Logs

SteamAutoFriend maintains detailed logs of all actions in `steam_auto_friend.log`. The log includes:

- Timestamps for all actions
- Success/failure of friend requests
- Blacklist updates
- Error messages and warnings

### Log Level Configuration

SteamAutoFriend provides flexible logging options controlled by the `LOG_LEVEL` setting in `config.py`:

- `DEBUG`: Shows all possible log messages (very verbose) - useful for troubleshooting
- `INFO`: Shows general information messages, warnings, and errors (moderately verbose)
- `WARNING`: Shows only warnings and errors (default) - recommended for normal usage
- `ERROR`: Shows only errors
- `CRITICAL`: Shows only critical errors (least verbose)

The log level affects what you see in the console output, but the program always writes all log levels to the log file (`steam_auto_friend.log`) for troubleshooting. This allows you to keep the console clean while maintaining detailed logs for reference.

To change the log level:
1. Open `config.py`
2. Change `LOG_LEVEL = "WARNING"` to your desired level
3. Restart the program

For normal usage, the default `WARNING` level provides a clean console interface while still showing important messages. If you're troubleshooting issues, you can set it to `INFO` or `DEBUG` for more detailed output.

## Error Codes

When sending friend requests, you may encounter these error codes:

- 1: Success
- 2: Invalid Steam ID
- 8: User has ignored your request or you have a limited account
- 15: Friend request already sent
- 25: Too many requests (rate limited)
- 40: Cannot send friend request to yourself
- 41: User has rejected request, has privacy settings preventing requests, or has a full friend list

Error code 41 is the most common and can mean any of the following:
- The user has rejected your previous friend request
- The user has privacy settings that prevent friend requests
- The user's friend list is full
- The user's account has limitations preventing friend requests

## Disclaimer

SteamAutoFriend is provided as-is and is not affiliated with Valve or Steam. Use it responsibly and in accordance with Steam's terms of service. Excessive friend requests may result in account restrictions. 
