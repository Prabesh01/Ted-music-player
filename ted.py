import sys
import os
from tkinter import Tk, messagebox
import shutil
import psutil
from pathlib import Path
import random

# importing * from moviepy.editor gives error when using pyinstaller 
# as per https://github.com/Zulko/moviepy/issues/591
# have to import everything manually

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import AudioClip
from moviepy.editor import concatenate_videoclips,concatenate_audioclips,TextClip,CompositeVideoClip
from moviepy.video.fx.accel_decel import accel_decel
from moviepy.video.fx.blackwhite import blackwhite
from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.freeze_region import freeze_region
from moviepy.video.fx.gamma_corr import gamma_corr
from moviepy.video.fx.headblur import headblur
from moviepy.video.fx.invert_colors import invert_colors
from moviepy.video.fx.loop import loop
from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.video.fx.make_loopable import make_loopable
from moviepy.video.fx.margin import margin
from moviepy.video.fx.mask_and import mask_and
from moviepy.video.fx.mask_color import mask_color
from moviepy.video.fx.mask_or import mask_or
from moviepy.video.fx.mirror_x import mirror_x
from moviepy.video.fx.mirror_y import mirror_y
from moviepy.video.fx.painting import painting
from moviepy.video.fx.resize import resize
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.scroll import scroll
from moviepy.video.fx.speedx import speedx
from moviepy.video.fx.supersample import supersample
from moviepy.video.fx.time_mirror import time_mirror
from moviepy.video.fx.time_symmetrize import time_symmetrize

from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_left_right import audio_left_right
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex

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
                pl()
                try:
                    track=songtracks[0]
                except:
                    messagebox.showinfo('Nothing to play', 'No music files found in music folder', parent=gui)
                    gui.destroy()
                    sys.exit()                        
            shuffle.append(track)
            audioclip = AudioFileClip(track)
            audioclip.preview()
            songtracks.pop(0)
            #once the playlist almost gets empty, add more 20 songs to playlist
            if len(songtracks)<=2:
                pl()
            err_count=0
        except Exception as e:
            # keep trying till it get 6 continuous exceptions. then exit
            if err_count>6:
                messagebox.showerror('Dang it!', str(e), parent=gui)
                gui.destroy()
                sys.exit()
            err_count += 1 

def hide_window():
   gui.withdraw()
   ted()

hide_window()

gui.mainloop()