#!/usr/bin/python
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import os
import const
from subprocess import call
import time
os.environ['SDL_NOMOUSE'] = '1'
import pygame
from pygame.locals import *
        
def clear_screen(screen):
    print "hello clear black"
    screen.fill( const.COLOR_BLACK )
    pygame.display.update()
    call(["/kobo_keypad/full_updatescreen"])
    time.sleep(2)

    print "hello clear white"
    screen.fill( const.COLOR_WHITE )
    pygame.display.update()
    call(["/kobo_keypad/full_updatescreen"])
    time.sleep(0.2)

def junk():
    l=pygame.image.load("/kobo_keypad/bs.png")
    drawBaseScreen( screen, labels )
    if (onKobo):  call(["/kobo_keypad/full_updateScreen"])

def drawBaseScreen( screen, labels):
    # draw the initial screen, in white background
    screen.fill( const.COLOR_WHITE )
    for i in range(len(labels)):
        # blit what, where
        screen.blit(labels[i][1], labels[i][3])

        # draw the enclosing rectangle, in black
        pygame.draw.rect(screen, const.COLOR_BLACK, labels[i][2], 2)
    pygame.display.update()

def displayBufferOnScreen(screen, font, buff):
    pygame.draw.rect(screen, const.COLOR_WHITE, pygame.rect.Rect(0,0,800,100))
    screen.blit(font.render(buff, 0, (0,0,0)), (10,10))

from signal import alarm, signal, SIGALRM, SIGKILL

def init_Pygame():

    # this section is an unbelievable nasty hack - for some reason Pygame
    # needs a keyboardinterrupt to initialise in some limited circs (second time running)
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    signal(SIGALRM, alarm_handler)
    alarm(3)
    screen=0
    try:
        print "init"
	pygame.init()
	screen = pygame.display.set_mode((600, 800), pygame.FULLSCREEN)
        alarm(0)
    except Alarm:
        raise KeyboardInterrupt
    return screen
################################## ################################## ##################################
################################## ################################## ##################################
################################## ################################## ##################################

def processKeypad():
    #import pdb; pdb.set_trace()
    screen = init_Pygame()
    pygame.mouse.set_visible(False)
    clear_screen( screen )
    time.sleep(100)
    
    pygame.quit()
    mosquittoClient.disconnect() 
    sys.exit()

if __name__ == "__main__":
    processKeypad()
