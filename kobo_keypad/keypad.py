#!/usr/bin/python
import struct
import  pygame
import  os
import  time
from pygame.locals import *
from subprocess import call
import thread
from Queue import Queue
from MQTT import MQTT
from threading import Timer

import touchScreenDriver


onKobo=True

TOUCHDOWN=1
TOUCHUP=2
FLASH_ON=3
FLASH_OFF=4
FLASH_MSG=5
CLEAR_MSG=6
BLACK=(0,0,0)
WHITE=(255,255,255)

# Tell SDL that there is no mouse.

if onKobo: os.environ['SDL_NOMOUSE'] = '1' 

keys="123456789B0G"
execute=False

tsdevice = "/dev/input/event1"
keydevice = "/dev/input/event0"
format = "iihhi"
buff=""


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
    """Runs in a loop getting the touch position"""
    global pendingTouchEvent, touchedState, x, y
    pendingTouchEvent=False
    touchedState = False 
    touchscreen = open(tsdevice,"rb")
    x=-1
    y=-1
    minDuration=.05
    def debugPrint():
        print "TIMER EVENT HIT" 

    def haveRealTouchUpEvent(tx, ty):
        global pendingTouchEvent, touchedState, x, y
        touchedState=False
        if (tx>=0) & (ty>=0): 
                print "touch up event: %s %s " %(tx,ty)
                eventQueue.put([TOUCHUP, tx, ty ])
        else:
            print "touch up event without proper X and Y coordinates"
        pendingTouchEvent=False
        x=-1
        y=-1

    def cancelPendingTouchUpEvent():
        global pendingTouchEvent
	if (type(pendingTouchEvent) != bool): 
            pendingTouchEvent.cancel()
            print "Existing touchup cancelled"
        pendingTouchEvent=False

    
    ts_event = touchscreen.read(16)
    while 1:
        # The touch screen.
        (ts_time1, ts_time2, ts_type, ts_code, ts_value) = struct.unpack(format,ts_event)
        print "type:",ts_type, " code:", ts_code, "Value:", ts_value," x:",x, "y:", y, ":", ts_time1, ":", ts_time2  , ":", pendingTouchEvent


        # we have an event if 1) we have had a touch down event, 
        #       2) we have a touch up event, without  
        #       another touch event within minTouchDuration seconds
        # so, when we get a touch up event, set a timer to for touch up event
        # cancel timer if we have another touch up event in the meantime

        if (ts_type == 3) & (not touchedState):
            # touch down Event
            # at the touch down event, capture first X and Y position
            if ts_code == 0 :
                x = ts_value
            if ts_code == 1 :
                y = ts_value
            if (x>=0) & (y>=0): 
                eventQueue.put([TOUCHDOWN, x, y])
                touchedState = True
                
        elif ts_type == 0:
            pass
        elif ts_type == 1:
            if (type(pendingTouchEvent)!=bool ):
                cancelPendingTouchUpEvent()
            # we have liftoff
            print "touchup pending"
            pendingTouchEvent=Timer(minDuration, haveRealTouchUpEvent, (x+0,y+0) )
            Timer(minDuration, debugPrint )
            pendingTouchEvent.start()
            
            
        ts_event = touchscreen.read(16)

    
        
def flash_screen(screen):
    screen.fill( WHITE )
    pygame.display.update()
    call(["./full_updatescreen"])
    time.sleep(0.2)
    screen.fill( BLACK )
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

    # draw the initial screen, in white background
    screen.fill( WHITE )
    for i in range(len(keys)):
        # blit what, where
        screen.blit(labels[i][1], labels[i][3])

        # draw the enclosing rectangle, in black
        pygame.draw.rect(screen, BLACK, labels[i][2], 2)
    print(labels)    
    pygame.display.update()
    if (onKobo):  call(["./full_monochrome"])
    return(rects, labels)

################################## ################################## ##################################
################################## ################################## ##################################
################################## ################################## ##################################

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
font = pygame.font.Font("Cabin-Regular.otf", 90)
#import pdb; pdb.set_trace()
(rects, labels)= setupKeypad(screen, font)

eventQueue= Queue();
thread.start_new_thread(get_touch_input, (eventQueue, ))
mqtt = MQTT(eventQueue)

touch_rect = pygame.rect.Rect(0,0, 5, 5)


while 1:
    try:
        event = eventQueue.get(True, 20 ) 
        if ((event[0] == TOUCHDOWN) | (event[0] == TOUCHUP)):

            touch_rect.center = event[1:3]
            which=touch_rect.collidelist(rects)
            if (which>=0):
                # we have a valid touch event
                if  (event[0] == TOUCHDOWN):

                    pygame.draw.rect(screen, BLACK, labels[which][2])
                else:
                    ch  = labels[which][0]
                    buffer(ch)
                    print ch
                    pygame.draw.rect(screen, WHITE, pygame.rect.Rect(0,0,800,100))
                    screen.blit(font.render(buff, 0, (0,0,0)), (10,10))
                    pygame.draw.rect(screen, WHITE, labels[which][2]) # white rectangle
                    screen.blit(labels[which][1], labels[which][3])  # print the black key
                    pygame.draw.rect(screen, BLACK, labels[which][2], 2) # black rectangle

        pygame.display.update()
        if (onKobo):  call(["./full_monochrome"])
        
    except Exception as e:
	    print "error, maybe timeout %s" % e
        


mosquittoClient.disconnect() 

