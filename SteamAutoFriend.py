from selenium import webdriver
import time
from datetime import datetime
import os
import warnings
import yaml
from win10toast import ToastNotifier
from os.path import exists
import pwinput
import cryptocode
import subprocess
import wget
import zipfile
from chromedriver_version import chromedriver_versions

version = "1.3.2"
# Disable clutter in console
debug = False
if debug == False:
    warnings.filterwarnings("ignore")

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
auto_chromedriver = bool(config["auto_chromedriver"])
remember_friends = bool(config["remember_friends"])

# information
def Information():
    os.system("title SteamAutoFriend v" + version + " by pebnn")
    os.system("cls")
    print("Made by https://steamcommunity.com/id/benjamun / Benjamin#5555 / https://github.com/pebnn")
    print("Version: " + version + "\n")
def Logo():
    print("   _____ _                                     _        ______    _                _ ")
    print("  / ____| |                         /\        | |      |  ____|  (_)              | |")
    print(" | (___ | |_ ___  __ _ _ __ ___    /  \  _   _| |_ ___ | |__ _ __ _  ___ _ __   __| |")
    print("  \___ \| __/ _ \/ _` | '_ ` _ \  / /\ \| | | | __/ _ \|  __| '__| |/ _ \ '_ \ / _` |")
    print("  ____) | ||  __/ (_| | | | | | |/ ____ \ |_| | || (_) | |  | |  | |  __/ | | | (_| |")
    print(" |_____/ \__\___|\__,_|_| |_| |_/_/    \_\__,_|\__\___/|_|  |_|  |_|\___|_| |_|\__,_|\n")
toaster = ToastNotifier()
def Notification():
    toaster.show_toast("SteamAutoFriend",
                       "A user has accepted you to their friends list!",
                       icon_path="dependencies/saf.ico",
                       duration=10)
Information()

# Uptime
startTime = time.time()
def getUptime():
    return (time.time() - startTime)

clear_console_enable = True
if clear_console <= 0:
    clear_console_enable = False

try:
    if remember_login == True:
        hwid = str(subprocess.check_output("wmic csproduct get uuid"), "utf-8").split("\n")[1].strip()
except:
    if remember_login == True:
        # Bellow is an experimental hwid command for Linux systems
        #hwid = str(subprocess.Popen('hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid').split())
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


if remember_login == True and exists("session.txt") == True:
    while True:
        remember_login_input = input("Would you like to log in using your currently saved login info? Y/N (N = Delete session.txt): ")
        if remember_login_input.upper() == "N" or remember_login_input.upper() == "Y" or remember_login_input == "":
            break
        else:
            print("\"" + remember_login_input + "\"" + " is not a valid input for this action!")
    if remember_login_input.upper() == "N":
        os.remove("session.txt")
        os.system("cls")
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

os.system("cls")
Information()
username, password = str(username).strip(), str(password).strip()
if remember_login == True and exists("session.txt") == False:
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
        if not exists("steamIDs.txt"):
            steam_ids = open("steamIDs.txt", "a") # Create text file if it doesn't already exist

        steam_ids = open("steamIDs.txt", "r").readlines()
        for steam_id in steam_ids:
            steam_id = steam_id.replace("\n", "")
            if steam_id in account:
                continue
            else:
                account.append(steam_id)

        steam_ids_control = open("SteamIDs.txt", "r").readlines()
        steam_ids_control = [i.replace("\n", "") for i in steam_ids_control] # Remove "\n" from each item in list
        for acc in account:
            if acc in steam_ids_control:
                continue
            elif acc not in steam_ids_control:
                steamids_temp = open("SteamIDs.txt", "a")
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

os.system("cls")

chrome_dir = []
# Get current Chrome version number
if auto_chromedriver == True:

    # Find and scan Chrome Applications folder for version number
    try:
        try:
            for folder in os.scandir("C:\Program Files (x86)\Google\Chrome\Application"):
                    chrome_dir.append(folder)
        except:
            for folder in os.scandir("C:\Program Files\Google\Chrome\Application"):
                    chrome_dir.append(folder)
    except:
        while True:
            custom_dir = input("Enter your Google Chrome install directory (example: C:\Program Files\Google\Chrome): ") + "\Application"
            try:
                for folder in os.scandir(custom_dir):
                    chrome_dir.append(folder)
                break
            except:
                print("Your directory does not contain Google Chrome!")


    for folder in chrome_dir:
        folder = folder.name
        folder_fragment = str(folder[0 : 2])
        if folder_fragment.isdigit():
            chrome_ver = folder

    chromedriver_version_final = []
    chrome_ver_list = chrome_ver.split(".")
    chrome_ver_start = chrome_ver_list[0]

    for version in chromedriver_versions:
        version_split = version.split(".")
        version_start = version_split[0]
        if version_start == chrome_ver_start:
            chromedriver_version_final.append(version)
    chromedriver_url = "https://chromedriver.storage.googleapis.com/index.html?path=" + chromedriver_version_final[0] + "/"
    chromedriver_file_url = "https://chromedriver.storage.googleapis.com/" + chromedriver_version_final[0] + "/chromedriver_win32.zip"

# Open google chrome
dependencies_files = []
try:
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome("dependencies/chromedriver.exe", options=options)
    driver.maximize_window()
except:
    if auto_chromedriver == True:
        print("Chromedriver.exe was not found or does not match your currently installed version of Chrome. Please read README.txt for further info!")
        valid_input = ["Y", "YES", "N", "NO", ""]
        while True:
            chromedriver_input = input("Would you like to automatically download the correct ChromeDriver version? Y/N: ").upper()
            if chromedriver_input in valid_input:
                break
            else:
                print("\"" + chromedriver_input + "\"" + " is not a valid input!")

        if chromedriver_input == "Y" or chromedriver_input == "YES" or chromedriver_input == "":
            # Delete old chromedriver file
            for file in os.listdir("dependencies"):
                dependencies_files.append(file)
            for file in dependencies_files:
                if "chromedriver" in file:
                    os.remove("dependencies/" + file)

            # Download ZIP containing new ChromeDriver file
            print("Downloading ChromeDriver version " + chromedriver_version_final[0])
            wget.download(chromedriver_file_url, out="dependencies")
            print("Download Complete!")

            # Unzip ChromeDriver.exe
            with zipfile.ZipFile("dependencies/chromedriver_win32.zip", 'r') as zip_ref:
                zip_ref.extractall("dependencies")

            # Delete downloaded ZIP file
            os.remove("dependencies/chromedriver_win32.zip")

            # Open Chrome again
            try:
                options = webdriver.ChromeOptions()
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                driver = webdriver.Chrome("dependencies/chromedriver.exe", options=options)
                driver.maximize_window()
            except:
                input("Could not start Chrome. Please read README.txt for more info.")

        elif chromedriver_input == "N" or chromedriver_input == "NO" or chromedriver_input == "":
            print("Currently installed Chrome version: " + chrome_ver)
            print("Required ChromeDriver version: " + chromedriver_version_final[0] + "\nDownload from: " + chromedriver_url)
            input("Press ENTER to continue...")
    else:
        input("Your chromedriver.exe does not match your currently installed version of Chrome. Please read README.txt for further info!\nPress ENTER to continue...")

# Go to url
driver.get(url)

# Log in
try:
    driver.find_element_by_name("username").send_keys(username)
    driver.find_element_by_name("password").send_keys(password)
    login = driver.find_element_by_css_selector(".btn_blue_steamui")
    login.click()
except:
    driver.find_element_by_xpath("//input[@type='text']").send_keys(username)
    driver.find_element_by_xpath("//input[@type='password']").send_keys(password)
    login = driver.find_element_by_class_name("newlogindialog_SubmitButton_2QgFE")
    login.click()


# Wait for user to be logged in
while driver.current_url == url:
    time.sleep(1)

os.system("cls")
Logo()
print("Steam Auto Friend started!")

# Message button languages
message_lang = ["Send en besked", "Skicka meddelande", "Message", "Melding", "Enviar un mensaje",
                "Poslat zprávu", "Nachricht senden", "Mensaje", "Μήνυμα", "Envoyer un message",
                "Messaggio", "Üzenet", "Bericht", "Wyślij wiadomość", "Enviar mensagem",
                "Trimite un mesaj", "Написать", "Lähetä viesti", "İleti Gönder", "Nhắn tin", "Повідомлення"]

def find_by_css(selector, text=''):
    return [element for element in driver.find_elements_by_css_selector(selector) if text in element.text][0]

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
    os.system("title SteamAutoFriend v1.3.2 by pebnn - Uptime: " + str(uptime))

    if count > clear_console and clear_console_enable == True: # Clear console lines after set amount of lines has been printed (clear_console is set in config.yml)
        try:
            os.system("cls")
        except:
            os.system("clear") # run Linux clear command instead of Windows "cls" if OS is Linux based.
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

    link = steamurl + account[accountindex]
    if "https://steamcommunity.com/login" not in driver.current_url:
        driver.get(link)
        attempt += 1
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = datetime.today().strftime('%d-%m-%Y')
    try:
        driver.find_element_by_css_selector(".btn_profile_action").click() # Click friend button
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
                        except:
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
                    except:
                        pass
                    if notification == True:
                        try:
                            Notification()
                        except:
                            print("ERROR - Notification not able to run. (only works on Windows systems")
                    break

        except:
            print("ERROR - Language not recognized. Change Steamcommunity to another language to fix this problem!")
    except:
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

    if remember_friends == True: # Update account list to include new steamIDs.txt entries (will not update removed items from text file)
        if exists("steamIDs.txt"):
            steam_ids = open("steamIDs.txt", "r").readlines()
            for steam_id in steam_ids:
                steam_id = steam_id.replace("\n", "")
                if steam_id in account:
                    continue
                else:
                    account.append(steam_id)

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
