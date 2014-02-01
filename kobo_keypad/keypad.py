import struct
import  pygame
import  os
import  time
from pygame.locals import *
from subprocess import call
import thread
from Queue import Queue
from MQTT import MQTT

onKobo=False

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


        
def get_touch_input(eventQueue):
    """Runs in a loop getting the touch position"""
    pendingTouchEvent=False
    touchedState = False 
    touchscreen = open(tsdevice,"rb")
    x=-1
    y=-1
    def haveClearUpEvent(x, y):
        pendingTouchEvent.cancel()
        if (x>=0) & (y>=0): 
                eventQueue.put([TOUCHUP, x, y ])
                print "touch up event: %s %s " %(x,y)
                x=-1
                y=-1
    
    ts_event = touchscreen.read(16)
    while running:
        # The touch screen.
        (ts_time1, ts_time2, ts_type, ts_code, ts_value) = struct.unpack(format,ts_event)

        # we have an event if 1) we have had a touch down event, 
        #       2) we have a touch up event, without  
        #       another touch event within minTouchDuration seconds
        # so, when we get a touch up event, set a timer to for touch up event
        # cancel timer if we have another touch up event in the meantime
        if (pendingTouchEvent):
            pendingTouchEvent.cancel()
        # 
        # touch down Event

        if ts_type == 3:
            # at the touch down event, capture first X and Y position
            if ts_code == 0 and x==-1:
                x = ts_value
            if ts_code == 1 and y==-1:
                y = ts_value
            touchedState = True
            if (x>=0) & (y>=0): 
                eventQueue.put([TOUCHDOWN, x, y])
                
        elif ts_type == 0:
            pass
        elif ts_type == 1:
            # we have liftoff
            touching = False
            pendingTouchEvent=Timer(minDuration, haveEvent )
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
        lr=l.get_rect()
        lrx = px*150+120
        lry= py*120+120
        
        lr.topleft=(lrx,lry)

        # labels in the (0)form index, (1)rendered font, (2)enclosing rectangle, and (3)xy coord pair
        labels.append([i,l,lr, (lrx,lry)])
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
    return(rects, labels)

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
font = pygame.font.Font("Cabin-Regular.otf", 90)
(rects, labels)= setupKeypad(screen, font)

eventQueue= Queue();
thread.start_new_thread(get_touch_input, (eventQueue, ))
mqtt = MQTT(eventQueue)

touch_rect = pygame.rect.Rect(0,0, 5, 5)


while 1:
    try:
        event = eventQueue.get(True, 20 ) 
        if ((event[0] == TOUCHDOWN) | (event[0] == TOUCHUP)):
            touch_rect.center = event[1:2]
            which=touch_rect.collidelist(rects)
            if (which>=0):
                # we have a valid touch event
                if  (event[0] == TOUCHDOWN):
                    ch  = labels[which][0]
                    buffer(ch)
                    print ch
                    pygame.draw.rect(screen, BLACK, labels[which][2])
                else:
                    pygame.draw.rect(screen, WHITE, labels[which][2])
                    screen.blit(labels[which][1], labels[which][3])  # print the black key

        pygame.display.update()
        if (onKobo):  call(["./full_monochrome"])
        
    except Exception as e:
            print e
        


mosquittoClient.disconnect() 
