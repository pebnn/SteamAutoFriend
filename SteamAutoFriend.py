from selenium import webdriver
import time
from datetime import datetime
import os
import warnings
import yaml
from win10toast import ToastNotifier
from os.path import exists

#TODO: Automatically install correct chromedriver version and delete old versions if they exist in directory

version = "1.2.1"
# Disable clutter in console (SET DEBUG TO TRUE TO VIEW POTENTIAL ERRORS)
debug = False
if debug == False:
    warnings.filterwarnings("ignore")

yaml_file = open("config.yml", "r")
yaml_config = yaml.full_load(yaml_file)
config = yaml_config
twofactor = bool(config["twofactor"])
notification = bool(config["notification"])
defaulttime = int(config["defaulttime"])
log_file = bool(config["log_file"])

# information
def Information():
    os.system("title SteamAutoFriend v" + version + " by pebnn")
    os.system("cls")
    print("Made by https://steamcommunity.com/id/benjamun / Benjamin#5555 / https://github.com/pebnn")
    print("Dependencies: https://pypi.org/project/selenium/")
    print("Version:" + version + "\n")
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

# Gather information
username = input("Steamcommunity username: ")
password = input("Steamcommunity password: ")
os.system("cls")
Information()
username, password = username.strip(), password.strip()
account = input("\nSteam ID of account you want to add. Seperate with spaces (NOT FULL LINK! only custom ID or profile ID): ")
account = account.split()
print(account)
firstacc = account[0]

friendinterval = input("How many seconds between each friend request? (leave blank for " + str(defaulttime/60) + " minutes): ")
friendinterval = friendinterval.strip()
if str(friendinterval) == "":
    friendinterval = defaulttime

steamguardcode = ""
if twofactor == True:
    steamguard = input("Do you wish to enter a steam guard code? Y/N: ").upper()
    if steamguard == "Y" or steamguard == "YES":
        steamguard = True
        steamguardcode = input("Enter your steam guard APP code: ")
    elif steamguard != "Y" or steamguard != "YES":
        pass

if firstacc.isnumeric() and len(firstacc) > 16:
    steamurl = "https://steamcommunity.com/profiles/"
else:
    # custom url
    steamurl = "https://steamcommunity.com/id/"

fakefriend = steamurl + firstacc
print("Steam account url set to " + fakefriend)
url = "https://steamcommunity.com/login/home"

# Open google chrome
try:
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome("dependencies\chromedriver.exe", options=options)
    driver.maximize_window()
except:
    input("Your chromedriver.exe does not match your currently installed version of Chrome. Please read README.txt for further info!\nPress ENTER to continue...")
# go to url
driver.get(url)

# Log in
driver.find_element_by_name("username").send_keys(username)
driver.find_element_by_name("password").send_keys(password)
login = driver.find_element_by_css_selector(".btn_blue_steamui")
login.click()

# steamguard
if twofactor == True:
    if steamguard == True:
        time.sleep(1)
        auth = driver.find_element_by_id("twofactorcode_entry")
        auth.send_keys(steamguardcode)
        auth.submit()

# Wait for user to be logged in
while driver.current_url == url:
    time.sleep(1)
else:
    pass

os.system("cls")
Logo()
print("Steam Auto Friend started!")

message_lang = ["Send en besked", "Skicka meddelande", "Message", "Melding", "Enviar un mensaje", "Poslat zprávu", "Nachricht senden", "Mensaje", "Μήνυμα", "Envoyer un message", "Messaggio", "Üzenet", "Bericht", "Wyślij wiadomość", "Enviar mensagem", "Trimite un mesaj", "Написать", "Lähetä viesti", "İleti Gönder", "Nhắn tin", "Повідомлення", ""] # Message button languages

def find_by_css(selector, text=''):
    return [element for element in driver.find_elements_by_css_selector(selector) if text in element.text][0]

# Main loop
running = True
attempt = 0
accountindex = 0
while running == True:
    if account[accountindex].isnumeric() and len(account[accountindex]) > 16:
        steamurl = "https://steamcommunity.com/profiles/"
    else:
        # custom url
        steamurl = "https://steamcommunity.com/id/"
    link = steamurl + account[accountindex]
    driver.get(link)
    attempt += 1
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    try:
        driver.find_element_by_css_selector(".btn_profile_action").click() # Click friend button
        try:
            message = find_by_css('.btn_profile_action')  # search only by CSS-selector
            for i in message_lang:
                if i == message.text: # check if message button exsists in different languages
                    account.pop(accountindex) # removes the account from loop if message button is found
                    try:
                        if log_file == True:
                            log_check = exists("log.txt") # Check if log file exsists
                            if log_check == False: # If log file doesnt exist, write to first line in document
                                new_line = ""
                            else:
                                new_line = "\n" # If log file exists write to next line in document
                                
                            log = open("log.txt", "a") # Try to open text file, if file doesnt exsist it will be created
                            log.write(new_line + "[" + current_time + "] " + link + " added you as a friend.")
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
            print("ERROR - Language not recognized. Change to another language to fix this problem!")
    except:
        print("ERROR - Can't find friend button!")
        input("Please log back in again via Chrome. Press ENTER when you're logged back in... ")
    accountindex += 1
    print("[" + current_time + "] Friend request attempt number " + str(attempt) + " (" + link + ")")
    driver.refresh()
    time.sleep(int(friendinterval))
    if accountindex >= (len(account)):
        accountindex = 0
    if len(account) <= 0: # Exit loop when account list is empty
        input("All accounts has added you as a friend. Press ENTER to exit the program...")
        break
print("Quitting...")
