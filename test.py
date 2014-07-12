#!/usr/bin/env python

import curses 
import time

screen = curses.initscr()

try:
    #screen.border(0)
    maxy = screen.getmaxyx()[0]
    
    height = 20
    ycoord = maxy-height

    box1 = curses.newwin(20, 20, ycoord, 5)
    box2 = curses.newwin(20, 20, ycoord, 30)
    box3 = curses.newwin(20, 20, ycoord, 55)
    box4 = curses.newwin(20, 20, ycoord, 80)

    box1.box()    
    box2.box()
    box3.box()
    box4.box()

    screen.refresh()
    box1.refresh()
    box2.refresh()
    box3.refresh()
    box4.refresh()

    for i in range(5): 
        time.sleep(5) 
        box1.erase()
        box1.refresh()
        box1.resize(30 + i,20)
        #print 30+i
        box1 = curses.newwin(20 + i , 20, ycoord - i , 5)
        box1.box()
        #screen.refresh()
        box1.refresh()
        #box1.mvwin(ycoord - i, 5)
        #box1.box()
        #box1.refresh()

    
    screen.getch()
finally:
    curses.endwin()
