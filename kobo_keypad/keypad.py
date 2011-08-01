#!/usr/bin/python
import pygame
from pygame.locals import *
import struct
import  os
import  time
from subprocess import call
import thread
from Queue import Queue
from MQTT import MQTT
import threading

import TSDriver


onKobo=True

TOUCHDOWN=1
TOUCHUP=2
FLASHSCREEN=3
FLASHMSG=5
CLEARMSG=6
BLACK=(0,0,0)
WHITE=(255,255,255)

# Tell SDL that there is no mouse.

if onKobo: os.environ['SDL_NOMOUSE'] = '1' 

keys="123456789B0G"

tsdevice = "/dev/input/event1"
format = "iihhi"
buff=""



class TextRectException:
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

def render_textrect(string, font, rect, text_color, background_color, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    import pygame
    
    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.    
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]

    return surface


def buffer( ch ):
    global buff,  mqtt 
    if (ch=="B"): 
        if(len(buff) > 0):
            buff=buff[:-1]
    elif (ch=="G"):
        mqtt.publish(buff )
        buff=""
    else:
        buff += ch
    print "Buff=", buff


        
def get_touch_input(eventQueue):
    processedQueue = Queue()
    t=TSDriver.TSDriver(processedQueue)
    while(1):
	(x,y) = processedQueue.get()
	eventQueue.put([TOUCHDOWN, x, y])
        
        
def keyUpEvent(q, x,y):
    print "Key Up Event %s %s " % (x,y)
    q.put([TOUCHUP, x, y])
        
def flash_screen(screen, font, labels, buff):
    screen.fill( BLACK )
    pygame.display.update()
    call(["./full_updatescreen"])
    time.sleep(0.2)
    drawBaseScreen( screen, labels )
    updateBuff( screen, font, buff)
    pygame.display.update()
    call(["./full_updatescreen"])
       


def setupKeypad( screen, font):
    # setup screen and keypad;  return keyboard data 

    labels=[]
    rects=[]
    px=0
    py=0
    for i in keys:
        l= font.render(i, 0, BLACK)
        lw= font.render(i, 0, (100,100,100))

        lr=l.get_rect()
        lrx = px*150+75
        lry= py*120+120
        
        lr.center=(lrx+75,lry+60)
        lr.union_ip( Rect(lrx, lry, 150,120) )


        # labels in the (0)form index, (1)rendered font, (2)enclosing rectangle, and (3)xy coord pair
        labels.append([i,l,lr, (lrx,lry), lw])
        rects.append(lr)
        
        px +=1
        if (px>2):
            px=0
            py+=1
    drawBaseScreen( screen, labels )
    if (onKobo):  call(["./full_monochrome"])
    return(rects, labels)

def drawBaseScreen( screen, labels):
    # draw the initial screen, in white background
    screen.fill( WHITE )
    for i in range(len(labels)):
        # blit what, where
        screen.blit(labels[i][1], labels[i][3])

        # draw the enclosing rectangle, in black
        pygame.draw.rect(screen, BLACK, labels[i][2], 2)
    pygame.display.update()

def updateBuff(screen, font, buff):
    pygame.draw.rect(screen, WHITE, pygame.rect.Rect(0,0,800,100))
    screen.blit(font.render(buff, 0, (0,0,0)), (10,10))

################################## ################################## ##################################
################################## ################################## ##################################
################################## ################################## ##################################

pygame.init()
#import pdb; pdb.set_trace()
screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
font = pygame.font.Font("Cabin-Regular.otf", 90)
(rects, labels)= setupKeypad(screen, font)

eventQueue= Queue();
thread.start_new_thread(get_touch_input, (eventQueue, ))
mqtt = MQTT(eventQueue)

touch_rect = pygame.rect.Rect(0,0, 5, 5)
msg_rect = pygame.rect.Rect(600,100,200,500)

keyDownDuration=.01
toUpdate=False
while 1:
    try:
        event = eventQueue.get(True, 20 ) 
        print event
    except Exception as e:
	    print "error, maybe timeout %s" % e
    if ((event[0] == TOUCHDOWN) | (event[0] == TOUCHUP)  ):

	touch_rect.center = event[1:3]
	which=touch_rect.collidelist(rects)
	if (which>=0):
	    # we have a valid touch event
	    if  (event[0] == TOUCHDOWN):
	        print "touch event"
		pygame.draw.rect(screen, BLACK, labels[which][2])
		threading.Timer(keyDownDuration, keyUpEvent, (eventQueue, event[1], event[2])).start()
		toUpdate=True
	    else:
		ch  = labels[which][0]
		buffer(ch)
		print ch
		updateBuff(screen, font, buff)
		pygame.draw.rect(screen, WHITE, labels[which][2]) # white rectangle
		screen.blit(labels[which][1], labels[which][3])  # print the black key
		pygame.draw.rect(screen, BLACK, labels[which][2], 2) # black rectangle
		toUpdate=True
    elif (event[0]==FLASHSCREEN):
	flash_screen( screen, font, labels, buff)
    elif (event[0]==FLASHMSG):
        screen.blit( render_textrect( event[1], font, msg_rect, BLACK, WHITE), msg_rect)
	toUpdate=True
    elif (event[0]==CLEARMSG):
	pygame.draw.rect(screen, WHITE, msg_rect)
	toUpdate=True

    if (toUpdate):
	pygame.display.update()
	if (onKobo):  call(["./full_monochrome"])
	toUpdate=False
        
        


mosquittoClient.disconnect() 

