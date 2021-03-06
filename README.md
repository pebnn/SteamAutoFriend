# SteamAutoFriend
SteamAutoFriend sends friend requests automatically and gives you a good overview to manage the outgoing requests. This is a good tool to add users such as st4ck and other high level or well knows steam users to your friends list. You can set the program to add multiple users at once, leave it and forget about it until all the users has accepted your request. If the request is denied or expired it will simply renew the request without any input from you.

https://github.com/pebnn/SteamAutoFriend

![SteamAutoFriend](https://i.imgur.com/kIQqjBy.png)

## Download and run without setup (*no python needed, plug and play*)
1. Download and unzip. https://github.com/pebnn/SteamAutoFriend/releases
2. Download the chromedriver.exe version **depending on what version of chrome you got installed** at https://chromedriver.chromium.org/downloads.
3. You can find your current Chrome version by going to chrome://settings/help
4. Place the chromedriver.exe in the dependencies folder.
5. Run

Instructions on how to configure SteamAutoFriend to your preferences are found in "How to run with python 3" starting from point 7.



## How to run with python 3 (Recommended)
1. Download SteamAutoFriend from https://github.com/pebnn/SteamAutoFriend  
2. install python 3 https://www.python.org/downloads/  
3. Open **install_dependencies.bat** or alternatively run **pip install selenium**, **pip install win10toast**, **pip install pyyaml**, **pip install pwinput** and **pip install cryptocode**
4. You have to download the chromedriver.exe version **depending on what version of chrome you got installed** at https://chromedriver.chromium.org/downloads. I bundled version 103.0.5060.53 with this project located in the dependencies folder, Replace this file if it doesnt match your version.
5. You can open **config.yml** and change some of the settings to your preferences. But this is not needed
6. Open Start.bat *(or alternatively cd to directory where SteamAutoFriend.py is located and run **python SteamAutoFriend.py**)*
7. Enter your steam username and steam password
8. When asked for steam ID of the user you wish to add go to the users profile and copy the id from the link. https://steamcommunity.com/id/st4ck > st4ck or https://steamcommunity.com/profiles/76561198023414915 > 76561198023414915
You can put several IDs in by seperating them with spaces. (76561198023414915 benjamun gabelogannewell)
6. Enter how many seconds you want between each friend request. Default is 5 minutes
7. If you have steamguard app you can enter your code in at this step and the script will automatically enter this code to the web browser. You can also enter it manually into the login screen.
8. Now a google chrome window will open up and cycle through the accounts you added, or just the one.


## How to compile standalone executable file yourself
1. Clone the repository from https://github.com/pebnn/SteamAutoFriend
2. Make sure to install PyInstaller. instructions can be found at: https://pyinstaller.org/en/stable/
3. Run Install_Dependencies.bat
4. cd to SteamAutoFriend folder
5. run **pyinstaller --onefile --icon=dependencies\SAF.ico SteamAutoFriend.py**
6. SteamAutoFriend.exe will save to SteamAutoFriend\dist. Copy the dependencies folder to the dist folder.
7. Also remember to copy **config.yml** to the dist folder.
8. Now you can run SteamAutoFriend.exe
9. The dist folder can be renamed and moved anywhere independently from any of the other python files, As long as you keep the file structure inside the dist folder as explained above.


## FAQ
Q: Where do i check my chrome version?  
A: To find your chrome version open google chrome and in the navigation field, search: chrome://settings/help  
   
   
Q: Can i run SteamAutoFriend minimized in the background or do i need to keep it open?  
A: You can completely minimize the program while it's running and leave it in the background.  

Q: Does SteamAutoFriend support Linux?  
A: Currently SteamAutoFriend is made for Windows systems. Linux has yet to be tested but should be possible with a bit of tweaking in the config file.  


## Other Questions?
Please feel free to add me on Discord for any of your questions.
**Benjamin#5555**


