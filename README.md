# Ted Music
Lightweight silent music player

![taskmanger.png](https://raw.githubusercontent.com/Prabesh01/ted-music-player/main/taskmanager.PNG)

How about this? Just double click once and you are done for forever. It will play music in the background. No player window pops up, ever. Just music and you. 

If you are one of those people who starts playing songs whenever they start their pc and carry on their work, Ted is just perfect for you.

## Usage
- Visit the [Release page](https://github.com/Prabesh01/ted-music-player/releases) and download suitable exe file from latest release
- After its downloaded, double click and hopefully you are done. 
- Controls:
	**Make sure CAPS LOCK is on**
	- Numpad 5 --> Play/Pause
	- Numpad 4 --> Play Previous Song
	- Numpad 6 --> Next Song
	- Numpad 8 --> Volume Up
	- Numpad 2 --> Volume Down
	- Numpad 0 --> Toogle Loop	

_It will play music you've got in your Music Folder (usually C:\Users\<username>\Music). It will keep playing silently in background without showing any gui to irritate you. It will autostart everytime you turn on your pc._

## Building yourself
- `git clone https://github.com/Prabesh01/ted-music-player.git`
- `cd ted-music-player`
- `pip install -r requirements.txt`
- `pyinstaller --onefile --icon=ted.ico -w ted.py`

_You will get your exe file inside dist folder._


## TO-Do
- maybe a user config file?
- make it more lightweight if possible
- add discord rich presence

## Known Issues
- Antivirus might report false positive trojan. In that case, you can just ignore it (allow it on antiviruses) cuz it really is false positive and certainly is safe or you can also build the exe file yourself instead of using the one in the release page. More info about this on [here](https://stackoverflow.com/questions/43777106/) and [here](https://python.plainenglish.io/pyinstaller-exe-false-positive-trojan-virus-resolved-b33842bd3184)

## Contributions
Contributions are always welcome

# License

[![CC0](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc/4.0/)
