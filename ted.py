# for accessing files and for exiting on errors
import os
import sys

# for gui window, error windows
from tkinter import Tk, messagebox

# for path related stuffs
from pathlib import Path

# for copying files
import shutil

# to see running process and not run if one instance of ted player is already running
import psutil

# for shuffling songs
import random

# player
from pygame import mixer
mixer.init()

# for listening to playback shortcuts on different thread
import threading
import pythoncom
from pynput import keyboard
from win32api import GetKeyState
from win32con import VK_CAPITAL

# for sleeping
import time

# handles ffmpeg binary
from imageio_ffmpeg import get_ffmpeg_exe

# to run shell commands
import subprocess as sp

# get ffmpeg exe file
try:
    FFMPEG_BINARY = get_ffmpeg_exe()
except:
    messagebox.showinfo('FFMPEG not found', 'Please install it to use ted player', parent=gui)
    gui.destroy()
    sys.exit()

# make a temp folder
try:
    home = str(Path.home())
    temp_dir = home+'\\AppData\\Local\\Temp\\tedx'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
except:
    messagebox.showinfo('Cant create temp folder', 'Make sure ted has required permissions', parent=gui)
    gui.destroy()
    sys.exit()

# convert videos file to audio and save in the temp folder    
def conv(toconv):
    cmd = [
        FFMPEG_BINARY,
        "-vn",
        "-sn",
        "-i",
        "%s" % (toconv),
        "-codec:a", 
        "libmp3lame", 
        "-qscale:a", 
        "4",
        "%s\%s.mp3" % (temp_dir,os.path.basename(toconv))
    ]
    sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)

# creating main window object
gui=Tk()
gui.title('TED')
gui.geometry("0x0")

# copying exe file to starup folder for auto run on pc reboot
try:
    spath=home+'\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    if os.path.dirname(sys.argv[0]) != spath:
        shutil.copy(sys.argv[0],spath)
except Exception as e:
    messagebox.showwarning("Couldn't enable autostart on PC startup", str(e), parent=gui)
    pass
del spath

# checking if music folder is accesible and there is atleast one song to be played
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
del home
del song_count
del ext

# check if player is already running.
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
del ted_count

shuffle=[] # add previously played songs to this list to avoid a song being played repeatedly to make shuffling work well
songtracks=[] # add songs to be played in this list. aka playlist
supportedfiles=['mp3','wav','ogg','ogv', 'mp4', 'mpeg', 'avi', 'mov'] # playable media file extensions
videofiles=['mp4', 'mpeg', 'avi', 'mov'] # video file extensions
audiofiles=['mp3','wav','ogg'] # audio file extensions

# adding music files to playlist.
def pl():
    global shuffle
    global songtracks
    
    loop_count=0 # make sure loop doesn't keep running infinitely and the loop breaks after reaching certain number
    
    # recursively get all files in music folder
    kk=[os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(".")) for f in fn]
    
    for i in range(1,20):
        while True:
            play_next=random.choice(kk)
            # avoid adding already added songs to the playlist
            if play_next in songtracks:
                loop_count += 1
                if loop_count > 10:
                    loop_count=0
                    break
            # avoid previously played song to be played again
            elif play_next in shuffle:
                loop_count += 1
                if loop_count > 20:
                    loop_count=0
                    shuffle=[]
                    break
            else:
                # check if the file is a playable media file
                ext=play_next.split(".")[-1]
                if any(vf in ext for vf in supportedfiles):
                    # avaoid adding large files as they compromise performance
                    if os.stat(play_next).st_size/1024>50000:
                        loop_count += 1
                        if loop_count > 10:
                            loop_count=0
                            break                    
                        continue
                    songtracks.append(play_next)
                    loop_count=0
                    break
                else:
                    loop_count += 1
                    if loop_count > 10:
                        loop_count=0
                        break                    
    del kk
    del loop_count
    del play_next
            
# this variable tells weather the user has paused song by pressing 5 
# this is listened by OnKeyboardEvent()
isPaused=False

# play given track
def play(track):
    try:
        global isPaused
        mixer.music.load(track)
        mixer.music.play()
        while isPaused or mixer.music.get_busy():
            time.sleep(1)
    except:
        pass
            
# bool variables. changes when user presses num4 for previous song or num0 to loop the song
loop=False
prev=False
            
#main stuff happens here
def ted():
    err_count=0
    global shuffle
    global songtracks
    global loop
    global prev
    #add first 20 songs tothe playlist
    pl()
    
    while True:
        try:
            #play the first song in the playlist and if it hit error, try to fix playlist and if again error persists, exit
            try:
                track=songtracks[1]                            
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
            
            #check if its video or audio file to decide weather to run it directly or convert it to audio file if it isn't in temp folder 

            if track.split(".")[-1] in videofiles:
                trackk=temp_dir+'\\'+os.path.basename(track)+'.mp3'
                if os.path.exists(trackk):
                    play(trackk)  
                else:
                    conv(track)
                    play(trackk)   
            else:
                play(track)   
            
            # handling loop and prev
            
            songs_count=len(songtracks)
            if not loop and not prev:
                songtracks.pop(0)

            if prev:
                songtracks[0],songtracks[1]=songtracks[1],songtracks[0]
                prev=False
                
            #once the playlist almost gets empty, add more 20 songs to playlist
            if songs_count<=2:
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

#handling keypress events only if caps lock is on
def OnKeyboardEvent(event):
    if GetKeyState(VK_CAPITAL)!=1:
        return True
    try:
        ERR=event.vk    
    except:
        return True
    global player
    global isPaused
    global loop
    global prev
    if event.vk==101:    
        if mixer.music.get_busy():
            isPaused=True            
            mixer.music.pause()
            return True
        else:
            mixer.music.unpause()
            return True
    elif event.vk==102:
        loop=False
        if mixer.music.get_busy():
            mixer.music.stop()
            return True
        else:
            isPaused=False
            return True
    elif event.vk==96:
        if loop==True:
            loop=False
        else:
            loop=True
        return True
    elif event.vk==100:
        loop=False
        if mixer.music.get_busy():
            mixer.music.stop()
        else:
            isPaused=False
        prev=True
        return True
    elif event.vk==104:
        mixer.music.set_volume(mixer.music.get_volume()+0.1)
        return True
    elif event.vk==98:
        mixer.music.set_volume(mixer.music.get_volume()-0.1)
        return True
    return True

#listening to key press 
def shortcut():
    listener = keyboard.Listener(on_press=OnKeyboardEvent)
    listener.start()
    pythoncom.PumpMessages()

#start everything 
def start():
   gui.withdraw()
   threading.Thread(target=shortcut).start()
   ted()

start()

gui.mainloop()