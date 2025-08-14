from selenium import webdriver
import time
from datetime import datetime
import os
import warnings
import yaml
import platform
from os.path import exists
import pwinput
import cryptocode
import subprocess

# Selenium modern imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

version = "1.3.6"
# Disable clutter in console
debug = False
if debug == False:
    warnings.filterwarnings("ignore")

# OS helpers
IS_WINDOWS = platform.system() == "Windows"

def clear_console_cmd():
    try:
        if IS_WINDOWS:
            os.system("cls")
        else:
            os.system("clear")
    except Exception:
        pass

def set_title(text: str):
    if IS_WINDOWS:
        # Only attempt Windows console title
        try:
            os.system("title " + text)
        except Exception:
            pass

# Notifications (Windows only)
try:
    if IS_WINDOWS:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
    else:
        toaster = None
except Exception:
    toaster = None

def Notification():
    if toaster is None:
        return
    try:
        toaster.show_toast(
            "SteamAutoFriend",
            "A user has accepted you to their friends list!",
            icon_path="dependencies/SAF.ico",
            duration=10,
        )
    except Exception:
        pass

yaml_file = open("config.yml", "r")
yaml_config = yaml.full_load(yaml_file)
config = yaml_config
notification = bool(config["notification"])
defaulttime = int(config["defaulttime"])
log_file = bool(config["log_file"])
hidden_password = bool(config["hidden_password"])
auto_connect_interval = int(config["auto_connect_interval"])
remember_login = bool(config["remember_login"])
clear_console = int(config["clear_console"]) 
remember_friends = bool(config["remember_friends"]) 

# Persist newly entered account IDs to steamIDs.txt (no duplicates)

def persist_accounts_to_file(accounts):
    if not remember_friends:
        return
    try:
        if not exists("steamIDs.txt"):
            open("steamIDs.txt", "a").close()
        existing = []
        try:
            with open("steamIDs.txt", "r") as f:
                existing = [line.strip() for line in f.readlines()]
        except Exception:
            existing = []
        with open("steamIDs.txt", "a") as out:
            for acc in accounts:
                if acc and acc not in existing:
                    out.write(acc + "\n")
    except Exception:
        pass

# information
def Information():
    set_title("SteamAutoFriend v" + version + " by pebnn")
    clear_console_cmd()
    print("Made by https://steamcommunity.com/id/benjamun / Benjamin#5555 / https://github.com/pebnn")
    print("Version: " + version + "\n")

def Logo():
    print("   _____ _                                     _        ______    _                _ ")
    print("  / ____| |                         /\\        | |      |  ____|  (_)              | |")
    print(" | (___ | |_ ___  __ _ _ __ ___    /  \\  _   _| |_ ___ | |__ _ __ _  ___ _ __   __| |")
    print("  \\___ \| __/ _ \\/ _` | '_ ` _ \\  / /\\ \\| | | | __/ _ \\|  __| '__| |/ _ \\ '_ \\ / _` |")
    print("  ____) | ||  __/ (_| | | | | | |/ ____ \\ |_| | || (_) | |  | |  | |  __/ | | | (_| |")
    print(" |_____/ \\__\\___|\\__,_|_| |_| |_/_/    \\_\\__,_|\\__\\___/|_|  |_|  |_|\\___|_| |_|\\__,_|\n")

Information()

# Uptime
startTime = time.time()

def getUptime():
    return (time.time() - startTime)

clear_console_enable = True
if clear_console <= 0:
    clear_console_enable = False

try:
    if remember_login == True and IS_WINDOWS:
        # Windows-only HWID
        hwid = str(subprocess.check_output("wmic csproduct get uuid"), "utf-8").split("\n")[1].strip()
except Exception:
    if remember_login == True and not IS_WINDOWS:
        print("Remember_login is only compatible with Windows systems for the time being.")

# Gather information

if remember_login == True and exists("session.txt") == False:
    username = input("Steamcommunity username: ")
    if hidden_password == True:
        password = pwinput.pwinput("Steamcommunity password: ")
    else:
        password = input("Steamcommunity password: ")

elif remember_login == False:
    username = input("Steamcommunity username: ")
    if hidden_password == True:
        password = pwinput.pwinput("Steamcommunity password: ")
    else:
        password = input("Steamcommunity password: ")


if remember_login == True and exists("session.txt") == True and IS_WINDOWS:
    while True:
        remember_login_input = input("Would you like to log in using your currently saved login info? Y/N (N = Delete session.txt): ")
        if remember_login_input.upper() == "N" or remember_login_input.upper() == "Y" or remember_login_input == "":
            break
        else:
            print("\"" + remember_login_input + "\"" + " is not a valid input for this action!")
    if remember_login_input.upper() == "N":
        os.remove("session.txt")
        clear_console_cmd()
        username = input("Steamcommunity username: ")
        if hidden_password == True:
            password = pwinput.pwinput("Steamcommunity password: ")
        else:
            password = input("Steamcommunity password: ")
    else:
        session_file = open("session.txt", "r")
        session_lines = session_file.readlines()
        decrypted_info = cryptocode.decrypt(session_lines[-1], hwid)
        login_list = str(decrypted_info).split()
        username, password = login_list[0], login_list[1]
        session_file.close()

clear_console_cmd()
Information()
username, password = str(username).strip(), str(password).strip()
if remember_login == True and exists("session.txt") == False and IS_WINDOWS:
    if exists("session.txt") == False:
        session = open("session.txt", "a") # Create session.txt if it doesnt exist
        session.close()
    info = "# If you enable remember_login in config.yml your username and password will be stored here as an encrypted string.\n" \
            "# This allows SteamAutoFriend to automatically log you in when you start the program. (do not edit this file, delete the file if login fails)"
    session = open("session.txt", "r") # Open session.txt as readable
    password_encrypted = cryptocode.encrypt(username + " " + password, hwid)
    lines = info + "\n\n" + password_encrypted # Set values for session.txt
    session.close()

    session = open("session.txt", "w") # Open session.txt as writable
    session.write(lines) # Write values to session.txt
    session.close()
elif remember_login == False:
    if exists("session.txt") == True:
        os.remove("session.txt") # Delete session.txt if config setting set to False
while True:
    account = input("Steam ID of account you want to add. Seperate with spaces (NOT FULL LINK! only custom ID or profile ID): ")
    if remember_friends == True and exists("steamIDs.txt") != True and account == "":
        print("You need to enter at least one steam ID!\n")
    elif remember_friends == False and len(account) == 0:
        print("You need to enter at least one steam ID!\n")
    else:
        break

account = account.split()

# Persist initial input accounts to file if enabled
persist_accounts_to_file(account)

# Load previous session ids to account list
if remember_friends == True:
    if exists("steamIDs.txt") == True:
        valid_input = ["Y", "YES", "N", "NO", ""]
        while True:
            load_steamids = input("Would you like to also load steamIDs from previous sessions? Y/N: ").upper()
            if load_steamids in valid_input:
                break
            else:
                print("\"" + load_steamids + "\"" + " is not a valid input!")
    else:
        load_steamids = ""
    if load_steamids == "Y" or load_steamids == "YES" or load_steamids == "":
        load_previous_ids = True
        if not exists("steamIDs.txt"):
            steam_ids = open("steamIDs.txt", "a") # Create text file if it doesn't already exist
            steam_ids.close()

        steam_ids = open("steamIDs.txt", "r").readlines()
        for steam_id in steam_ids:
            steam_id = steam_id.strip()
            if steam_id in account:
                continue
            else:
                account.append(steam_id)
    elif load_steamids == "N" or load_steamids == "NO":
        load_previous_ids = False

        steam_ids_control = open("steamIDs.txt", "r").readlines()
        steam_ids_control = [i.strip() for i in steam_ids_control] # Remove whitespace/newlines
        for acc in account:
            if acc in steam_ids_control:
                continue
            elif acc not in steam_ids_control:
                steamids_temp = open("steamIDs.txt", "a")
                if acc == "":
                    continue
                else:
                    steamids_temp.write(acc + "\n")
                    steamids_temp.close()

steamidtxt_check = exists("steamIDs.txt")
if remember_friends == False and steamidtxt_check == True:
    delete_steamIDs = input("The config option REMEMBER_FRIENDS is disabled but \"steamIDs.txt\" still exists in the directory. Would you like to delete it? Y/N: ").upper()
    if delete_steamIDs == "Y" or delete_steamIDs == "YES":
        os.remove("steamIDs.txt")

while True:
    friendinterval = input("How many seconds between each friend request? (leave blank for " + str(defaulttime/60) + " minute(s)): ")
    if friendinterval.isnumeric() or friendinterval == "":
        break
    else:
        print("Your input has to be numeric!\n")
friendinterval = friendinterval.strip()
if str(friendinterval) == "":
    friendinterval = defaulttime


if account[0].isnumeric() and len(account[0]) > 16:
    steamurl = "https://steamcommunity.com/profiles/"
else:
    # custom url
    steamurl = "https://steamcommunity.com/id/"

fakefriend = steamurl + account[0]
url = "https://steamcommunity.com/login/home"

clear_console_cmd()

# Open google chrome using Selenium Manager (no external driver installer needed)
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Try to locate Chrome/Chromium binary on Linux if default lookup fails
if not IS_WINDOWS:
    possible_bins = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
    ]
    for binary in possible_bins:
        if os.path.exists(binary):
            options.binary_location = binary
            break

try:
    # Selenium Manager will resolve and download the correct driver automatically (Selenium >= 4.6)
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
except Exception as e:
    input(f"Could not start Chrome. Error: {e}\nEnsure Google Chrome/Chromium is installed. Press ENTER to exit...")
    raise

# Helpers: Family View detection and waiting

def is_family_view_prompt() -> bool:
    try:
        src = driver.page_source.lower()
    except Exception:
        return False
    if ("family view" in src) or ("parental" in src):
        selectors = [
            "input[type='password']",
            "input[name*='pin']",
            "input[id*='pin']",
        ]
        for sel in selectors:
            try:
                if driver.find_elements(By.CSS_SELECTOR, sel):
                    return True
            except Exception:
                continue
    return False

def wait_for_family_view_unlock():
    notified = False
    while True:
        if not is_family_view_prompt():
            break
        if not notified:
            print("Family View is enabled. Waiting for you to enter the PIN in the browser...")
            notified = True
        time.sleep(1)

# Generic multi-strategy element finder with wait

def wait_and_find(wait: WebDriverWait, locators, condition=EC.presence_of_element_located):
    last_exc = None
    for by, sel in locators:
        try:
            return wait.until(condition((by, sel)))
        except Exception as exc:
            last_exc = exc
            continue
    raise last_exc if last_exc else TimeoutError("Element not found with provided locators")

# Find element in top-level or in iframes

def find_in_any_context(locators, condition=EC.presence_of_element_located, timeout=60):
    # Try top-level first
    driver.switch_to.default_content()
    try:
        return wait_and_find(WebDriverWait(driver, timeout), locators, condition)
    except Exception:
        pass
    # Try each iframe
    frames = driver.find_elements(By.TAG_NAME, 'iframe')
    for fr in frames:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(fr)
            return wait_and_find(WebDriverWait(driver, 10), locators, condition)
        except Exception:
            continue
    # Not found
    driver.switch_to.default_content()
    raise TimeoutError("Element not found in any context (top-level or iframes)")


# Go to url
driver.get(url)

# Log in
# Define locators
USERNAME_LOCATORS = [
    (By.XPATH, "//div[normalize-space(text())='Sign in with account name']/following::input[@type='text'][1]"),
    (By.CSS_SELECTOR, "form input[type='text']"),
    (By.ID, "input_username"),
    (By.NAME, "username"),
    (By.CSS_SELECTOR, "input[autocomplete='username']"),
    (By.XPATH, "//input[@type='text' or @name='username' or @autocomplete='username']"),
]
PASSWORD_LOCATORS = [
    (By.XPATH, "//div[normalize-space(text())='Password']/following::input[@type='password'][1]"),
    (By.CSS_SELECTOR, "form input[type='password']"),
    (By.ID, "input_password"),
    (By.NAME, "password"),
]
SIGNIN_LOCATORS = [
    (By.XPATH, "//form//button[@type='submit' and contains(., 'Sign in')]"),
    (By.CSS_SELECTOR, "form button[type='submit']"),
    (By.ID, "login_btn_signin"),
    (By.CSS_SELECTOR, "button[type='submit']"),
    (By.XPATH, "//button[contains(., 'Sign in') or contains(., 'Sign In') or contains(., 'Anmelden') or contains(., 'Entrar') or contains(., 'Se connecter')]")
]

# Ensure body is present
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Enter credentials (search across iframes if necessary)
user_el = find_in_any_context(USERNAME_LOCATORS, EC.element_to_be_clickable, timeout=60)
try:
    user_el.clear()
except Exception:
    pass
user_el.send_keys(username)
pass_el = find_in_any_context(PASSWORD_LOCATORS, EC.presence_of_element_located, timeout=60)
try:
    pass_el.clear()
except Exception:
    pass
pass_el.send_keys(password)
find_in_any_context(SIGNIN_LOCATORS, EC.element_to_be_clickable, timeout=60).click()

# Return to top-level before continuing
driver.switch_to.default_content()

# Wait for user to be logged in
while driver.current_url == url:
    time.sleep(1)

# If Family View is enabled, wait for manual PIN entry
wait_for_family_view_unlock()

clear_console_cmd()
Logo()
print("Steam Auto Friend started!")

# Message button languages
message_lang = [
    "Send en besked",
    "Skicka meddelande",
    "Message",
    "Melding",
    "Enviar un mensaje",
    "Poslat zprávu",
    "Nachricht senden",
    "Mensaje",
    "Μήνυμα",
    "Envoyer un message",
    "Messaggio",
    "Üzenet",
    "Bericht",
    "Wyślij wiadomość",
    "Enviar mensagem",
    "Trimite un mesaj",
    "Написать",
    "Lähetä viesti",
    "İleti Gönder",
    "Nhắn tin",
    "Повідомлення",
]

def find_by_css(selector, text=''):
    return [element for element in driver.find_elements(By.CSS_SELECTOR, selector) if text in element.text][0]

# Main loop
running = True
count = 0
attempt = 0
accountindex = 0
add_friend_attempt = 0
while running == True:

    getUptime()
    uptime_minutes = getUptime() // 60
    uptime_hours = uptime_minutes // 60
    uptime = "%02d:%02d" % (uptime_hours, uptime_minutes % 60)
    set_title("SteamAutoFriend v" + version + " by pebnn - Uptime: " + str(uptime))

    if count > clear_console and clear_console_enable == True: # Clear console lines after set amount of lines has been printed (clear_console is set in config.yml)
        try:
            clear_console_cmd()
        except Exception:
            pass
        count = 0
        Logo()
        print("Console cleaned.")
    if clear_console_enable == True:
        count += 1

    if account[accountindex].isnumeric() and len(account[accountindex]) > 16:
        steamurl = "https://steamcommunity.com/profiles/"
    else:
        # custom url
        steamurl = "https://steamcommunity.com/id/"

    # Check if user is logging in, if true it will wait until user is fully logged in
    while "https://steamcommunity.com/login/" in driver.current_url:
        time.sleep(1)

    # If Family View prompts appear at any point, wait for PIN entry
    wait_for_family_view_unlock()

    link = steamurl + account[accountindex]
    if "https://steamcommunity.com/login" not in driver.current_url:
        driver.get(link)
        attempt += 1
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = datetime.today().strftime('%d-%m-%Y')
    try:
        # If Family View gate appears on profile, wait
        wait_for_family_view_unlock()
        driver.find_element(By.CSS_SELECTOR, ".btn_profile_action").click() # Click friend button
        try:
            message = find_by_css('.btn_profile_action')  # search only by CSS-selector
            for i in message_lang:
                if i == message.text: # check if message button exists in different languages
                    account_removed = account[accountindex]
                    account.pop(accountindex) # removes the account from loop if message button is found

                    if remember_friends == True: # Delete steamID from steamID.txt
                        try:
                            steamids = open("steamIDs.txt", "r")
                            lines = steamids.readlines()
                            lines = [i.replace("\n", "") for i in lines]  # Remove "\n" from each item in list
                            for i in lines:
                                if i == account_removed:
                                    lines.remove(i)
                            steamids_rewritte = open("steamIDs.txt", "w")
                            for i in lines:
                                steamids_rewritte.write(i + "\n")
                            steamids_rewritte.close()
                        except Exception:
                            print("Error deleting steamID from steamIDs.txt")

                    try:
                        if log_file == True:
                            log_check = exists("log.txt") # Check if log file exists
                            if log_check == False: # If log file doesnt exsist, write to first line in document
                                new_line = ""
                            else:
                                new_line = "\n" # If log file exists write to next line in document

                            log = open("log.txt", "a") # Try to open text file, if file doesnt exsist it will be created
                            log.write(new_line + "[" + current_time + " - " + current_date + "] " + link + " added you as a friend.")
                            log.close()
                        print(link + " accepted you, and has been removed from SteamAutoFriend!")
                    except Exception:
                        pass
                    if notification == True:
                        try:
                            Notification()
                        except Exception:
                            print("ERROR - Notification not able to run. (Windows only)")
                    break

        except Exception:
            print("ERROR - Language not recognized. Change Steamcommunity to another language to fix this problem!")
    except Exception:
        print("ERROR - Can't find friend button!")
        if add_friend_attempt < 3 and auto_connect_interval == 0:
            print("Attempting to find friend button...")
            driver.get(link)
            add_friend_attempt += 1
        elif auto_connect_interval > 0:
            if "https://steamcommunity.com/login" not in driver.current_url:
                print("Reconnecting in " + str(auto_connect_interval) + " seconds. (You may need to log in through chrome or the targeted profile can't be found.)")
                time.sleep(auto_connect_interval)
            if "https://steamcommunity.com/login" not in driver.current_url:
                print("Reconnecting...")
                driver.get(link)
        else:
            input("Please log back in again via Chrome. Press ENTER when you're logged back in... ")
            add_friend_attempt = 0

    if remember_friends == True and load_previous_ids == True: # Update account list to include new steamIDs.txt entries (will not update removed items from text file)
        if exists("steamIDs.txt"):
            steam_ids = open("steamIDs.txt", "r").readlines()
            for steam_id in steam_ids:
                steam_id = steam_id.strip()
                if steam_id in account:
                    continue
                else:
                    account.append(steam_id)
    # Persist any newly added IDs mid-run
    persist_accounts_to_file(account)

    accountindex += 1
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("[" + current_time + "] Friend request attempt number " + str(attempt) + " (" + link + ")")
    driver.refresh()
    time.sleep(int(friendinterval))
    if accountindex >= (len(account)):
        accountindex = 0
    if len(account) <= 0: # Exit loop when account list is empty
        input("All accounts has added you as a friend. Press ENTER to exit the program...")
        running = False
print("Quitting...")
