#!/usr/bin/python
""" based on code from arduino soundlight project """
import pyaudio
import numpy # for fft
import audioop
import sys
import math
import struct
import time
import curses
from socket import *

def list_devices():
    """ List all audio input devices """
    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print str(i)+'. '+dev['name']
        i += 1
 
def analyze(data, width, sample_rate, bins):
    # Convert raw sound data to Numpy array
    fmt = "%dH"%(len(data)/2)
    data2 = struct.unpack(fmt, data)
    data2 = numpy.array(data2, dtype='h')
 
    # FFT black magic
    fourier = numpy.fft.fft(data2)
    ffty = numpy.abs(fourier[0:len(fourier)/2])/1000
    ffty1=ffty[:len(ffty)/2]
    ffty2=ffty[len(ffty)/2::]+2
    ffty2=ffty2[::-1]
    ffty=ffty1+ffty2
    ffty=numpy.log(ffty)-2
    
    fourier = list(ffty)[4:-4]
    fourier = fourier[:len(fourier)/2]
    
    size = len(fourier)
 
    # Split into desired number of frequency bins
    levels = [sum(fourier[i:(i+size/bins)]) for i in xrange(0, size, size/bins)][:bins]
    
    return levels

def visualize(device):    
    chunk    = 2048 # Change if too fast/slow, never less than 1024
    scale    = 200   # Change if bars too short/long
    exponent = .5    # Change if too little/too much difference between loud and quiet sounds
    sample_rate = 44100 
    
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = sample_rate,
                    input = True,
                    frames_per_buffer = chunk,
                    input_device_index = device)
    
    print "Starting, use Ctrl+C to stop"
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0) # invisible cursor
    curses.init_pair(1, -1, curses.COLOR_BLUE)
    curses.init_pair(2, -1, -1)
    
    term_height = screen.getmaxyx()[0]
    term_width = screen.getmaxyx()[1]

    min_bar_height = 1
    bar_width = 4
    bar_spacing = 2
    vertical_offset = 2
    bins = term_width / (bar_width + bar_spacing) 

    bars = []
    for i in range(bins):
        xcoord = bar_spacing + i*(bar_width + bar_spacing) 
        bars.append(curses.newwin(min_bar_height, bar_width, term_height - vertical_offset , xcoord)) 
   
    try:
        while True:
            # handle terminal resizing
            if curses.is_term_resized(term_height, term_width): 
                screen.clear()
                screen.refresh()

                term_height = screen.getmaxyx()[0]
                term_width = screen.getmaxyx()[1]
                
                bins = term_width / (bar_width + bar_spacing)
                bars = []
                
                for i in range(bins):
                    xcoord = bar_spacing + i*(bar_width + bar_spacing) 
                    bars.append(curses.newwin(min_bar_height, bar_width, term_height - vertical_offset, xcoord)) 

            data = stream.read(chunk)
            levels = analyze(data, chunk, sample_rate, bins)
 
            for i in range(bins):
                height = max(min((levels[i]*1.0)/scale, 1.0), 0.0)
                height = height**exponent
                height = int(height*term_height*1.5)
                
                prev_coords = bars[i].getbegyx()
                prev_bar_height = bars[i].getmaxyx()[0]

                bars[i].bkgd(' ', curses.color_pair(2)) # recolor to default
                bars[i].erase()
                bars[i].refresh()
        
                new_bar_height = max(height, min_bar_height)
                bars[i] = curses.newwin(new_bar_height, bar_width, prev_coords[0] - (new_bar_height - prev_bar_height) , prev_coords[1]) 
                bars[i].bkgd(' ', curses.color_pair(1)) # set color     
                bars[i].refresh()
            

    except KeyboardInterrupt:
        pass
    finally:
        print "\nStopping"
        stream.close()
        p.terminate()
        curses.endwin()

def main():
    list_devices()
    device = None
    while not device:
        try:
            device = int(raw_input("Enter device number for desired audio source: "))
        except ValueError:
            print "not a number"
    visualize(device)

if __name__ == '__main__':
    main()    
