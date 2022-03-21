# SteamAutoFriend
SteamAutoFriend allows you to add any other users to your friends list until they either accept or block you. This is a good tool to add users such as st4ck and other high level or well knows steam users to your account.

# Download and run without setup
https://github.com/pebnn/SteamAutoFriend/releases/tag/SteamAutoFriend


# How to run with python 3
1. install python 3 https://www.python.org/downloads/
2. Run Install_Dependencies.bat
This step will run "pip install selenium"
3.Run Start.bat
4.Enter your steam username and steam password
5.When asked for steam ID of the user you wish to add go to the users profile and copy the id from the link. https://steamcommunity.com/id/st4ck > st4ck or https://steamcommunity.com/profiles/76561198023414915 > 76561198023414915
You can put several IDs in by seperating them with spaces. (76561198023414915 st4ck gabelogannewell)
6. Enter how many seconds you want between each friend request. Default is 10 minutes
7. If you have steamguard app you can enter your code in at this step and the script will automatically enter this code to the web browser. You can also enter it manually into the login screen.
8. Now a google chrome window will open up and cycle through the accounts you added, or just the one.


# How to compile yourself
1.Clone the repository
2.cd to SteamAutoFriend folder
3.run pyinstaller --onefile --icon=dependencies\SAF.ico SteamAutoFriend.py
4.SteamAutoFriend will save to SteamAutoFriend\dist. Copy the dependencies folder to \dist
5.Now you can run SteamAutoFriend.exe
