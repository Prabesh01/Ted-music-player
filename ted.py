#for accessing files and for exiting on errors
import os
import sys

#for gui window, error windows
from tkinter import Tk, messagebox

#for path related stuffs
from pathlib import Path

#for copying files
import shutil

#to see running process and not run if one instance of ted player is already running
import psutil

#for shuffling songs
import random

# players
from pygame import mixer # for audio files cuz cant pause resume audio files in ffpyplayer
mixer.init()
from ffpyplayer.player import MediaPlayer # for video files cuz pygame doesn't play them

#for listening to playback shortcuts on different thread
import threading
import pythoncom, pyWinhook

#for sleeping
import time

#creating main window object
gui=Tk()
gui.title('TED')
gui.geometry("0x0")

#copying exe file to starup folder for auto run on pc reboot
try:
    home = str(Path.home())
    spath=home+'\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    file_name =  os.path.basename(sys.argv[0])
    if os.path.dirname(sys.argv[0]) != spath:
        shutil.copy(sys.argv[0],spath)
except Exception as e:
    messagebox.showwarning("Couldn't enable autostart on PC startup", str(e), parent=gui)
    pass

#checking if music folder is accesible and there is atleast one song to be played
try:
    os.chdir(home+"\Music")
    song_count=0
    supportedfiles=['mp3','wav','ogg','ogv', 'mp4', 'mpeg', 'avi', 'mov']
    for dp, dn, fn in os.walk(os.path.expanduser(".")):
        if song_count==1:
            break
        for song in fn:
            ext=song.split(".")[-1]
            if any(vf in ext for vf in supportedfiles):
                song_count=1
                break
    if song_count==0:
        messagebox.showinfo('Nothing to play', 'No music files found in music folder', parent=gui)
        gui.destroy()
        sys.exit()        
except Exception as e:
    messagebox.showerror("Couldn't read Music folder", str(e), parent=gui)
    gui.destroy()
    sys.exit()

#check if player is already running.
try:
    ted_count=0
    for proc in psutil.process_iter():
        if proc.name().lower()==os.path.basename(sys.argv[0]).lower():
            ted_count += 1
            # since the exe is built from pyinstaller, 2 process runs when running one instance. 
            # if there's more than 2 process, that means more than one instance 
            # which will cause multiple songs being played at once by those instances
            if ted_count>2:
                messagebox.showerror('Error', "One instance of TED music player already seems to be running", parent=gui)
                gui.destroy()
                sys.exit()
except:
    pass

shuffle=[] # add previously played songs to this list to avoid a song being played repeatedly to make shuffling work well
songtracks=[] # add songs to be played in this list. aka playlist

#adding music files to playlist.
def pl():
    global shuffle
    global songtracks
    
    loop_count=0 # make sure loop doesn't keep running infinitely and the loop breaks after reaching certain number
    supportedfiles=['mp3','wav','ogg','ogv', 'mp4', 'mpeg', 'avi', 'mov'] #playable media file extensions
    
    #recursively get all files in music folder
    kk=[os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(".")) for f in fn]
    
    for i in range(1,20):
        while True:
            play_next=random.choice(kk)
            #avoid adding already added songs to the playlist
            if play_next in songtracks:
                loop_count += 1
                if loop_count > 10:
                    loop_count=0
                    break
            #avoid previously played song to be played again
            elif play_next in shuffle:
                loop_count += 1
                if loop_count > 20:
                    loop_count=0
                    shuffle=[]
                    break
            else:
                #check if the file is a playable media file
                ext=play_next.split(".")[-1]
                if any(vf in ext for vf in supportedfiles):
                    songtracks.append(play_next)
                    loop_count=0
                    break
                else:
                    loop_count += 1
                    if loop_count > 10:
                        loop_count=0
                        break                    
    del kk

ff_opts = {'vn': True, 'sn': True}  # ffmpeg audio only option
            
# this variable tells weather the user has paused song by pressing 5 
# this is listened by OnKeyboardEvent()
p5=False

# see if p5 is True. if it is, stop anything playing and wait till it gets false. if it is false, continue playing
def play(typ,track):
        global p5
        if p5:
            while True:
                if p5==False:
                    break
                time.sleep(1)
        if typ==1:
            player = MediaPlayer(track,ff_opts=ff_opts)
            val=''
            while val != 'eof':
                if p5:
                    break
                audio_frame, val = player.get_frame()
                if val != 'eof' and audio_frame is not None:
                    if p5:
                        break
                    img, t = audio_frame
            player.close_player()
        else:
            mixer.music.load(track)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(1)
            
#main stuff happens here
def ted():
    err_count=0
    global shuffle
    global songtracks
    #add first 20 songs tothe playlist
    pl()
    
    while True:
        try:
            #play the first song in the playlist and if it hit error, try to fix playlist and if again error persists, exit
            try:
                track=songtracks[0]                            
            except:
                shuffle=[]
                pl()
                try:
                    track=songtracks[0]
                except:
                    messagebox.showinfo('Nothing to play', 'No music files found in music folder', parent=gui)
                    gui.destroy()
                    sys.exit()                        
            shuffle.append(track)
            
            #check if its video or audio file to decide weather ffpyplayer or pygame should run it 
            videofiles=['mp4', 'mpeg', 'avi', 'mov']
            audiofiles=['mp3','wav','ogg']
            
            if track.split(".")[-1] in videofiles:
                play(1,track)
            else:
                play(0,track)
            
            songtracks.pop(0)
            #once the playlist almost gets empty, add more 20 songs to playlist
            if len(songtracks)<=2:
                pl()
            err_count=0
        except Exception as e:
            songtracks.pop(0)
            # keep trying till it get 6 continuous exceptions. then exit
            if err_count>6:
                messagebox.showerror('Dang it!', str(e), parent=gui)
                gui.destroy()
                sys.exit()
            err_count += 1 

#handling keypress events and when num5 is pressed, alter the value of p5 variable. stop playing song if playing
def OnKeyboardEvent(event):
    global p5
    if event.Key=='Numpad5':
        if mixer.music.get_busy():
            mixer.music.stop()
        if p5:
            p5=False
        else:
            p5=True
    return True

#listening to key press 
def shortcut():
    hm = pyWinhook.HookManager()
    hm.KeyDown = OnKeyboardEvent
    hm.HookKeyboard()
    pythoncom.PumpMessages()

#start everything 
def start():
   gui.withdraw()
   threading.Thread(target=shortcut).start()
   ted()

start()

gui.mainloop()
