## SteamAutoFriend

SteamAutoFriend sends friend requests automatically and gives you a clear overview to manage outgoing requests. Point it at one or more Steam profile IDs or custom IDs and let it cycle until the users accept your request.


![SteamAutoFriend](https://i.imgur.com/kIQqjBy.png)

## Download and run without setup (*no python needed, plug and play*)
1. Download and unzip. https://github.com/pebnn/SteamAutoFriend/releases
5. Run SteamAutoFriend.exe

### Installation
Requirements
 - Python 3.8+
 - Google Chrome or Chromium installed
   
1. Download or clone this repository.
2. (Recommended) Create and activate a virtual environment:
   - Linux/macOS:
     ```bash
     python3 -m venv .venv && source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv; .\.venv\Scripts\Activate.ps1
     ```
3. With the venv active, install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running
- Make sure your venv is active in the current shell first.
- Windows:
  ```powershell
  python .\SteamAutoFriend.py
  ```
- Linux/macOS (from an activated shell):
  ```bash
  python SteamAutoFriend.py
  ```

### Guide for first-time use
1. Run the script and enter your Steam credentials.
2. Provide one or more targets (custom IDs like `st4ck` or numeric IDs like `76561198023414915`).
3. Choose the interval (press ENTER to use the default from `config.yml`).
4. Complete the login in the opened Chrome/Chromium window (including Steam Guard if enabled).
5. Leave the program running; it will cycle through targets until they accept you.


### Configuration (`config.yml`)
- `notification`: Windows-only toast notification when a friend is added. On non-Windows systems this setting has no effect beyond console output.
- `defaulttime`: Default seconds between friend requests (used if you press ENTER at the interval prompt).
- `log_file`: If true, appends accepted users to `log.txt`.
- `hidden_password`: Hides the password input in the console.
- `auto_connect_interval`: Seconds to wait before retrying profile loads when connection issues occur.
- `remember_login`: Windows-only. Stores encrypted login in `session.txt` for automatic reuse in future sessions.
- `clear_console`: Clears the console after the given number of printed lines (0 disables).
- `remember_friends`: If true, persists target IDs in `steamIDs.txt` and removes them automatically as users accept you.



### Building a standalone executable (Windows)
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build:
   ```bash
   pyinstaller --onefile --icon=dependencies\SAF.ico SteamAutoFriend.py
   ```
3. Copy `dependencies/` and `config.yml` into the `dist/` folder alongside `SteamAutoFriend.exe`.

### FAQ
- Q: Do I need to manually download ChromeDriver?
  - A: No. It is installed automatically.
- Q: Does it work on Linux?
  - A: Yes, provided Chrome or Chromium is installed. Some features (Windows toast notifications, remember_login) are Windows-only.
- Q: Can I minimize it while it runs?
  - A: Yes. It continues to work in the background.

