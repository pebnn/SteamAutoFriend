from selenium import webdriver
import time
from datetime import datetime
import os
import warnings

#disable clutter in console (SET DEBUG TO TRUE TO VIEW POTENTIAL ERRORS)
debug = False
if debug == False:
    warnings.filterwarnings("ignore")

#information
def Information():
    os.system("title SteamAutoFriend1.1 by pebnn")
    os.system("cls")
    print("Made by https://steamcommunity.com/id/benjamun / Benjamin#5555 / https://github.com/pebnn")
    print("Dependencies: https://pypi.org/project/selenium/")
    print("Version: 1.1\n")
def Logo():
    print("   _____ _                                     _        ______    _                _ ")
    print("  / ____| |                         /\        | |      |  ____|  (_)              | |")
    print(" | (___ | |_ ___  __ _ _ __ ___    /  \  _   _| |_ ___ | |__ _ __ _  ___ _ __   __| |")
    print("  \___ \| __/ _ \/ _` | '_ ` _ \  / /\ \| | | | __/ _ \|  __| '__| |/ _ \ '_ \ / _` |")
    print("  ____) | ||  __/ (_| | | | | | |/ ____ \ |_| | || (_) | |  | |  | |  __/ | | | (_| |")
    print(" |_____/ \__\___|\__,_|_| |_| |_/_/    \_\__,_|\__\___/|_|  |_|  |_|\___|_| |_|\__,_|\n")
Information()

#Gather information
username = input("Steamcommunity username: ")
password = input("Steamcommunity password: ")
os.system("cls")
Information()
username, password = username.strip(), password.strip()
account = input("\nSteam ID of account you want to add. Seperate with spaces (NOT FULL LINK! only custom ID or profile ID): ")
account = account.split()
print(account)
firstacc = account[0]

friendinterval = input("How many seconds between each friend request? (leave blank for 10 minutes): ")
friendinterval = friendinterval.strip()
if str(friendinterval) == "":
    friendinterval = 600

steamguard = input("Do you wish to enter a steam guard code? Y/N: ").upper()
if steamguard == "Y" or steamguard == "YES":
    steamguard = True
    steamguardcode = input("Enter your steam guard APP code: ")
elif steamguard != "Y" or steamguard != "YES":
    pass

if firstacc.isnumeric() and len(firstacc) > 16:
    steamurl = "https://steamcommunity.com/profiles/"
else:
    #custom url
    steamurl = "https://steamcommunity.com/id/"

fakefriend = steamurl + firstacc
print("Steam account url set to " + fakefriend)
url = "https://steamcommunity.com/login/home"

#Open google chrome
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome("dependencies\chromedriver.exe", options=options)
driver.maximize_window()
#go to url
driver.get(url)

#Log in
driver.find_element_by_name("username").send_keys(username)
driver.find_element_by_name("password").send_keys(password)
login = driver.find_element_by_css_selector(".btn_blue_steamui")
login.click()

#steamguard
if steamguard == True:
    time.sleep(1)
    auth = driver.find_element_by_id("twofactorcode_entry")
    auth.send_keys(steamguardcode)
    auth.submit()

#Wait for user to be logged in
while driver.current_url == url:
    time.sleep(1)
else:
    pass

os.system("cls")
Logo()
print("Steam Auto Friend started!")

message_lang = ["Send en besked", "Skicka meddelande", "Message", "Melding", "Enviar un mensaje", "Poslat zprávu", "Nachricht senden", "Mensaje", "Μήνυμα", "Envoyer un message", "Messaggio", "Üzenet", "Bericht", "Wyślij wiadomość", "Enviar mensagem", "Trimite un mesaj", "Написать", "Lähetä viesti", "İleti Gönder", "Nhắn tin", "Повідомлення", ""] #Message button languages

def find_by_css(selector, text=''):
    return [element for element in driver.find_elements_by_css_selector(selector) if text in element.text][0]

#Main loop
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
    try:
        driver.find_element_by_css_selector(".btn_profile_action").click() #Click friend button
        try:
            message = find_by_css('.btn_profile_action')  # search only by CSS-selector
            #print(message.text)
            for i in message_lang:
                if i == message.text: #check if message button exsists in different languages
                    #print(i + " text found!") #TEST FOR MESSAGE BUTTON DETECTION (languages)
                    account.pop(accountindex) #removes the account from loop
                    break

        except:
            print("Code doesnt work")
    except:
        pass
    accountindex += 1
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("[" + current_time + "] Friend request attempt number " + str(attempt) + " (" + link + ")")
    driver.refresh()
    time.sleep(int(friendinterval))
    if accountindex >= (len(account)):
        accountindex = 0
    if len(account) <= 0: #Exit loop when account list is empty
        input("All accounts has added you as a friend. Press ENTER to exit the program...")
        break
print("Quitting...")