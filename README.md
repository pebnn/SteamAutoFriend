# SteamAutoFriend
SteamAutoFriend allows you to add users to your friends list until they either accept or block you. This is a good tool to add users such as st4ck and other high level or well knows steam users to your friends list.

![SteamAutoFriend](https://i.imgur.com/kIQqjBy.png)

# Download and run without setup (version 1.1)
1. Download and unzip. https://github.com/pebnn/SteamAutoFriend/releases/tag/SteamAutoFriend
2. download the chromedriver.exe version **depending on what version of chrome you got installed** at https://chromedriver.chromium.org/downloads.
3. Place the chromedriver.exe in the dependencies folder.
4. Run



# How to run with python 3 (Recommended)
1. install python 3 https://www.python.org/downloads/
2. Run **install_dependencies.bat** or alternatively run **pip install selenium**, **pip install win10toast** and ** pip install pyyaml**
3. You have to download the chromedriver.exe version **depending on what version of chrome you got installed** at https://chromedriver.chromium.org/downloads. I bundled version 99.0.4844.51 with this project located in the dependencies folder, Replace this file if it doesnt match your version.
4. Run Start.bat
5. Enter your steam username and steam password
6. When asked for steam ID of the user you wish to add go to the users profile and copy the id from the link. https://steamcommunity.com/id/st4ck > st4ck or https://steamcommunity.com/profiles/76561198023414915 > 76561198023414915
You can put several IDs in by seperating them with spaces. (76561198023414915 st4ck gabelogannewell)
6. Enter how many seconds you want between each friend request. Default is 10 minutes
7. If you have steamguard app you can enter your code in at this step and the script will automatically enter this code to the web browser. You can also enter it manually into the login screen.
8. Now a google chrome window will open up and cycle through the accounts you added, or just the one.


# How to compile yourself  (currently not working with version 1.2)
1. Clone the repository
2. Make sure to install PyInstaller. instructions can be found at: https://pyinstaller.org/en/stable/
3. cd to SteamAutoFriend folder
4. run **pyinstaller --onefile --icon=dependencies\SAF.ico SteamAutoFriend.py**
5. SteamAutoFriend will save to SteamAutoFriend\dist. Copy the dependencies folder to \dist
6. Now you can run SteamAutoFriend.exe

# Questions?
Please feel free to add me on Discord for any of your questions.
**Benjamin#5555**


