import os
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
import time
import pygame
from mutagen.wave import WAVE

import librosa
import numpy as np

import math

# Modifyable settings

class MusicVisualizer(object):
    def __init__(self):
        # Tkinter GUI initialization
        self.root = Tk()
        self.root.title("Control")

        self.file_button = Button(self.root, text='Open File', command=self.open_file_callback)
        self.file_button.grid(row=0, column=0, sticky="NSEW")

        self.play_button = Button(self.root, text='Play', command=self.play_callback)
        self.play_button.grid(row=0, column=1, sticky="NSEW")

        self.pause_button = Button(self.root, text='Pause', command=self.pause_callback)
        self.pause_button.grid(row=0, column=2, sticky="NSEW")
        
        self.pause_state = False

        self.stop_button = Button(self.root, text='Stop/Reset', command=self.stop_callback)
        self.stop_button.grid(row=0, column=3, sticky="NSEW")
        
        self.cur_song_text = Label(self.root,text="Current Song: ")
        self.cur_song_text.grid(row=1, columnspan=4, sticky="nws")
        
        self.song_progress_text = Label(self.root, text="0:00 / 0:00 ", width=10)
        self.song_progress_text.grid(row=2,column=0,sticky="nws")

        self.song_progress_bar = Progressbar(self.root, orient=HORIZONTAL, maximum=1, value=0, mode = "determinate")
        self.song_progress_bar.grid(row=2, column=1, columnspan=3, sticky="nsew")
        
        self.bar_count_lable = Label(self.root, text="Bar Count: ")
        self.bar_count_lable.grid(row=3, column=0, sticky="news")

        self.bar_count_slider = Scale(self.root, from_=1, to=30, orient=HORIZONTAL)
        self.bar_count_slider.grid(row=3, column=1, columnspan=3, sticky="news")
        self.bar_count_slider.set(30)

        self.freq_min_lable = Label(self.root,text="Min Freq (KHZ): ")
        self.freq_min_lable.grid(row=4, column=0, sticky="news")
        
        self.freq_min_slider = Scale(self.root, from_=0.1, to=10, resolution=0.1, orient=HORIZONTAL)
        self.freq_min_slider.grid(row=4, column=1, columnspan=3, sticky="news")
        self.freq_min_slider.set(0.1)

        self.freq_max_lable = Label(self.root,text="Max Freq (KHZ): ")
        self.freq_max_lable.grid(row=5, column=0, sticky="news")
        
        self.freq_max_slider = Scale(self.root, from_=1, to=10, resolution=0.1, orient=HORIZONTAL)
        self.freq_max_slider.grid(row=5, column=1, columnspan=3, sticky="news")
        self.freq_max_slider.set(10)

        self.r1_lable = Label(self.root,text="Radius 1: ")
        self.r1_lable.grid(row=6, column=0, sticky="news")

        self.r1_slider = Scale(self.root, from_=25, to=300, orient=HORIZONTAL)
        self.r1_slider.grid(row=6, column=1, columnspan=3, sticky="news")
        self.r1_slider.set(50)
        
        self.r2_lable = Label(self.root,text="Radius 2: ")
        self.r2_lable.grid(row=7, column=0, sticky="news")

        self.r2_slider = Scale(self.root, from_=25, to=300, orient=HORIZONTAL)
        self.r2_slider.grid(row=7, column=1, columnspan=3, sticky="news")
        self.r2_slider.set(150)

        self.pad_lable = Label(self.root,text="Ray Padding: ")
        self.pad_lable.grid(row=8, column=0, sticky="news")

        self.pad_slider = Scale(self.root, from_=0, to=15, orient=HORIZONTAL)
        self.pad_slider.grid(row=8, column=1, columnspan=3, sticky="news")
        self.pad_slider.set(2)

        self.dbmin_lable = Label(self.root,text="Min decibels: ")
        self.dbmin_lable.grid(row=9, column=0, sticky="news")

        self.dbmin_slider = Scale(self.root, from_=-100, to=0, orient=HORIZONTAL)
        self.dbmin_slider.grid(row=9, column=1, columnspan=3, sticky="news")
        self.dbmin_slider.set(-80)

        self.dbmax_lable = Label(self.root,text="Max decibels: ")
        self.dbmax_lable.grid(row=10, column=0, sticky="news")

        self.dbmax_slider = Scale(self.root, from_=0, to=100, orient=HORIZONTAL)
        self.dbmax_slider.grid(row=10, column=1, columnspan=3, sticky="news")
        self.dbmax_slider.set(0)

        self.update_button = Button(self.root, text="Update Settings", command=self.update_settings_callback)
        self.update_button.grid(row=11, columnspan=4, sticky="news")

        # Configure grids for resizeability
        Grid.columnconfigure(self.root,0,weight=1)
        Grid.columnconfigure(self.root,1,weight=1)
        Grid.columnconfigure(self.root,2,weight=1)
        Grid.columnconfigure(self.root,3,weight=1)
        
        # Stuff to make Tkinter and Pygame not fight
        os.environ['SDL_WINDOWID'] = str(self.root.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

        self.root.update_idletasks()

        # Pygame init        
        pygame.init()
        self.pygame_screen = pygame.display.set_mode((512,512))
        self.pygame_width, self.pygame_height = pygame.display.get_surface().get_size()
        pygame.display.set_caption('PyMusicVisualizer - Null')
        pygame.mixer.init()

        self.cr1 = 50
        self.cr2 = 150
        self.cpad = 2 * math.pi/180
        self.cdbmin = -80
        self.cdbmax = 0

        self.min = 100
        self.max = 10000
        self.count = 30
        self.frequencies = np.arange(self.min, self.max, (self.max-self.min)/self.count)

        # Call pygame later and run the main loop for tkinter
        self.song_elapsed_time = 0
        self.root.after(1000, self.pygame_update)
        self.root.mainloop()

    def update_settings_callback(self):
        self.cr1 = self.r1_slider.get()
        self.cr2 = self.r2_slider.get()
        self.cpad = self.pad_slider.get() * math.pi/180
        self.cdbmin = self.dbmin_slider.get()
        self.cdbmax = self.dbmax_slider.get()

        self.min = self.freq_min_slider.get() * 1000
        self.max = self.freq_max_slider.get() * 1000
        self.count = self.bar_count_slider.get()
        self.frequencies = np.arange(self.min, self.max, (self.max-self.min)/self.count)
        print("Settings updated")

    def open_file_callback(self):
        file_path = filedialog.askopenfilename(initialdir="./test_music",filetypes=[("wav files","*.wav")])
        self.root.update()
        self.cur_song_path = file_path
        self.cur_song_text.configure(text="Current Song: "+file_path)
        pygame.display.set_caption('PyMusicVisualizer - {}'.format(os.path.basename(file_path)))

        # file_path2 = file_path.split('.')[0] + ".wav"
        
        # At the moment, my understanding of how to use ffts to create spectrograms from audio is nil. So is my general knowledge of digital signal processing in relation to audio.  
        # The following spectrograph code is copied from https://gitlab.com/avirzayev/medium-audio-visualizer-code/-/blob/master/main.py
        # I hope in the future to understand how to do this.

        time_series, sample_rate = librosa.load(file_path)
        stft = np.abs(librosa.stft(time_series, hop_length=512, n_fft=2048*4))
        self.spectrogram = librosa.amplitude_to_db(stft, ref=np.max)
        frequencies = librosa.core.fft_frequencies(n_fft=2048*4)
        times = librosa.core.frames_to_time(np.arange(self.spectrogram.shape[1]), sr=sample_rate, hop_length=512, n_fft=2048*4)
        self.time_index_ratio = len(times)/times[len(times) - 1]
        self.frequencies_index_ratio = len(frequencies)/frequencies[len(frequencies)-1]
        print("Song Setup: "+file_path)

    def get_decibel(self,target_time, freq):
        return self.spectrogram[int(freq * self.frequencies_index_ratio)][int(target_time * self.time_index_ratio)]

    def play_callback(self):
        pygame.mixer.music.load(self.cur_song_path)
        self.song_duration = WAVE(self.cur_song_path).info.length

        self.play_update() 
        pygame.mixer.music.play()
        
    def pause_callback(self):
        self.pause_state = not self.pause_state
        if self.pause_state == True:
            pygame.mixer.music.pause()
        else:         
            pygame.mixer.music.unpause()

    def stop_callback(self):
        pygame.mixer.music.stop()
        
    def play_update(self):
        self.song_progress_text.configure(text="{} / {}".format(time.strftime('%M:%S', time.gmtime(self.song_elapsed_time)),time.strftime('%M:%S', time.gmtime(self.song_duration))))
        self.song_progress_bar.configure(value = self.song_elapsed_time/self.song_duration)
        self.song_progress_text.after(1000, self.play_update)

    def pygame_update(self):
        self.song_elapsed_time = pygame.mixer.music.get_pos() / 1000
        if pygame.mixer.music.get_busy() == True:
            self.pygame_screen.fill((0,0,0))
            for index,freq in enumerate(self.frequencies):
                ang = 2*math.pi*index/self.count - math.pi/2
                offset = (2*math.pi/self.count)/2
                mag = self.get_decibel(self.song_elapsed_time,freq)
                r1 = self.cr1
                r2 = self.cr2 + mag * (self.cr2-self.cr1)/(self.cdbmax-self.cdbmin)
                c1 = math.cos(ang-offset+self.cpad)
                s1 = math.sin(ang-offset+self.cpad)
                c2 = math.cos(ang+offset-self.cpad)
                s2 = math.sin(ang+offset-self.cpad)
                w = self.pygame_width/2
                h = self.pygame_height/2
                pygame.draw.polygon(self.pygame_screen, (255,0,0), [(r2*c1+w, r2*s1+h), (r2*c2+w,r2*s2+h), (r1*c2+w, r1*s2+h), (r1*c1+w, r1*s1+h)])

            pygame.display.flip()
        self.root.after(math.floor(1*100/24), self.pygame_update)

if __name__ == "__main__":
    m = MusicVisualizer()

''' FFT IDEA
for each timestep of our song, utilize fft to find the frequencies and their amplitudes, then display them
'''