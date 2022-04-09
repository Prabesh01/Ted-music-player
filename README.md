# Ted Music
Lightweight silent music player

![taskmanger.png](https://raw.githubusercontent.com/Prabesh01/ted-music-player/main/taskmanager.PNG)

How about this? Just double click once and you are done for ever. It will play musics in background. No player window pops up, just music and you. 

If you are one of those people who starts playing music whenever they start their pc and carry on their work, Ted is just perfect for you.

## Usage
- Visit the [Release page](https://github.com/Prabesh01/ted-music-player/releases) and download suitable exe file from latest release
- After its downloaded, double click and hopefully you are done. 

_It will play musics you've got in your Music Folder (usually C:\Users\<username>\Music). It will keep playing silently in background without showing any gui to irritate you. It will autostart everytime you turn on your pc._

## Building yourself
- `git clone https://github.com/Prabesh01/ted-music-player.git`
- `cd ted-music-player`
- `pip install -r requirements.txt`
- `pyinstaller --onefile --icon=ted.ico -w ted.py`

_You will get your exe file inside dist folder._


## TO-Do
- add playback control shortcuts
- maybe a user config file?
- make it more lightweight if possible
- add discord rich presence

## Known Issues
- Antivirus might report false positive trojan. In that case, you can just ignore it (allow it on antiviruses) cuz it really is false positive and certainly is safe or you can also build the exe file yourself instead of using the one in the release page. More info about this on [here](https://stackoverflow.com/questions/43777106/) and [here](https://python.plainenglish.io/pyinstaller-exe-false-positive-trojan-virus-resolved-b33842bd3184)
- Can't Stop the music? Lol that was intended. Will add keyboard shortcuts to play, stop and other playback controls soon. For now, you will have to kill it from taskmanager. Also, in order to stop app from auto running on startup, open RUN, type `shell:startup` and hit enter. Then delete the ted.exe file in that folder.

## Contributions
Contributions are always welcome

# License

[![CC0](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc/4.0/)
