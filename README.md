# SteamAutoFriend
SteamAutoFriend sends friend requests automatically and gives you a good overview to manage the outgoing requests. This is an efficient tool to add users such as st4ck and other high level or well known steam users to your friends list. You can set the program to add multiple users at once, leave it and forget about it until all the users has accepted your request. If the request is denied or expired it will simply renew the request without any input from you.

https://github.com/pebnn/SteamAutoFriend

![SteamAutoFriend](https://i.imgur.com/kIQqjBy.png)

## Download and run without setup (*no python needed, plug and play*)
1. Download and unzip. https://github.com/pebnn/SteamAutoFriend/releases
5. Run SteamAutoFriend.exe

Instructions on how to configure SteamAutoFriend to your preferences are found [here](https://github.com/pebnn/SteamAutoFriend#guide-for-first-time-running-the-bot).



## How to run with python 3
1. Download SteamAutoFriend from https://github.com/pebnn/SteamAutoFriend/archive/refs/heads/SteamAutoFriend.zip
2. install python 3 https://www.python.org/downloads/  
3. Open a cmd window and [CD](https://www.lifewire.com/change-directories-in-command-prompt-5185508) to the SteamAutoFriends folder. Now run this command: 
```
pip install -r requirements.txt
```
4. ~~You have to download the chromedriver.exe version **depending on what version of chrome you got installed** at https://chromedriver.chromium.org/downloads. I bundled version 103.0.5060.53 with this project located in the dependencies folder, Replace this file if it doesnt match your version.~~ **SteamAutoFriend automatically handles ChromeDriver installations if using version 1.2.7 or above.**
5. You can open **config.yml** and change some of the settings to your preferences. But this is not needed
6. Open Start.bat *(or alternatively cd to directory where SteamAutoFriend.py is located and run **python SteamAutoFriend.py**)*

## Guide for first time running the bot

1. Start the bot by following either of the two options represented above.
2. Enter your steam username and steam password
3. When asked for steam ID of the user you wish to add go to the users profile and copy the id from the link. https://steamcommunity.com/id/st4ck > st4ck or https://steamcommunity.com/profiles/76561198023414915 > 76561198023414915
You can put several IDs in by seperating them with spaces. (76561198023414915 benjamun gabelogannewell)
4. Enter how many seconds you want between each friend request. Default is 1 minute
5. If asked for automatic chromedriver install, Press "Y". This installs the required chrome driver to run SteamAutoFriend (chromedriver installs into dependencies folder). You can also download this manually by pressing "N"
6. Now a google chrome window will open up, if you have SteamGuard enabled this is where you'll have to enter your SteamGuard code. When this is done the script will cycle through the accounts you added. SteamAutoFriend can now be left idling.


## How to compile standalone executable file yourself
1. Clone the repository from https://github.com/pebnn/SteamAutoFriend
2. Make sure to install PyInstaller. Instructions can be found at: https://pyinstaller.org/en/stable/
3. Open a cmd window and [CD](https://www.lifewire.com/change-directories-in-command-prompt-5185508) to the SteamAutoFriends folder. Now run this command: 
```
pip install -r requirements.txt
```
4. Open CMD or your console of choice, and cd to SteamAutoFriend folder.
5. run this command:
```
pyinstaller --onefile --icon=dependencies\SAF.ico SteamAutoFriend.py
```
6. SteamAutoFriend.exe will save to SteamAutoFriend\dist. Copy the dependencies folder to the folder named "dist".
7. Also remember to copy **config.yml** to the folder named "dist".
8. Now you can run SteamAutoFriend.exe
9. The folder named "dist" can be renamed and moved anywhere independently from any of the other python files, As long as you keep the file structure inside the folder named "dist" as explained above.


## FAQ
   
Q: Can i run SteamAutoFriend minimized in the background or do i need to keep it open?  
A: You can completely minimize the program while it's running and leave it in the background.  

Q: Does SteamAutoFriend support Linux?  
A: Currently SteamAutoFriend is made for Windows systems. Linux has yet to be tested but should be possible with a bit of tweaking in the config file.  


## Other Questions?
You can leave your questions or comments in the Github Discussions page, or feel free to add me on Discord for any questions or requests.
**Benjamin#5555**


