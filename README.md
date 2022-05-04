# SteamAutoFriend
SteamAutoFriend sends friend requests automatically and gives you a good overview to manage the outgoing requests. This is a good tool to add users such as st4ck and other high level or well knows steam users to your friends list. You can set the program to add multiple users at once, leave it and forget about it until all the users has accepted your request. If the request is denied or expired it will simply renew the request without any input from you.

![SteamAutoFriend](https://i.imgur.com/kIQqjBy.png)

# Download and run without setup (*no python needed, plug and play*)
1. Download and unzip. https://github.com/pebnn/SteamAutoFriend/releases
2. download the chromedriver.exe version **depending on what version of chrome you got installed** at https://chromedriver.chromium.org/downloads.
3. Place the chromedriver.exe in the dependencies folder.
4. Run



# How to run with python 3 (Recommended)
1. install python 3 https://www.python.org/downloads/
2. Open **install_dependencies.bat** or alternatively run **pip install selenium**, **pip install win10toast** and **pip install pyyaml**
3. You have to download the chromedriver.exe version **depending on what version of chrome you got installed** at https://chromedriver.chromium.org/downloads. I bundled version 99.0.4844.51 with this project located in the dependencies folder, Replace this file if it doesnt match your version.
4. You can open **config.yml** and change some of the settings to your preferences. But this is not needed
5. Run Start.bat *(or alternatively cd to directory where SteamAutoFriend.py is located and run **python SteamAutoFriend.py**)*
6. Enter your steam username and steam password
7. When asked for steam ID of the user you wish to add go to the users profile and copy the id from the link. https://steamcommunity.com/id/st4ck > st4ck or https://steamcommunity.com/profiles/76561198023414915 > 76561198023414915
You can put several IDs in by seperating them with spaces. (76561198023414915 st4ck gabelogannewell)
6. Enter how many seconds you want between each friend request. Default is 10 minutes
7. If you have steamguard app you can enter your code in at this step and the script will automatically enter this code to the web browser. You can also enter it manually into the login screen.
8. Now a google chrome window will open up and cycle through the accounts you added, or just the one.


# How to compile single executable file yourself
1. Clone the repository
2. Make sure to install PyInstaller. instructions can be found at: https://pyinstaller.org/en/stable/
3. cd to SteamAutoFriend folder
4. run **pyinstaller --onefile --icon=dependencies\SAF.ico SteamAutoFriend.py**
5. SteamAutoFriend.exe will save to SteamAutoFriend\dist. Copy the dependencies folder to the dist folder.
6. Also remember to copy **config.yml** to the dist folder.
7. Now you can run SteamAutoFriend.exe
8. The dist folder can be renamed and moved anywhere independently from any of the other python files, As long as you keep the file structure inside the dist folder as explained above.

# Questions?
Please feel free to add me on Discord for any of your questions.
**Benjamin#5555**


