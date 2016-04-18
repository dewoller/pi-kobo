#!/bin/python 

import logging, traceback
logger = logging.getLogger( "dispatcher.music")
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

import time
import const
import thread, sys
from i2clibraries import i2c_lcd_smbus

songs = [
	([392,294,0,392,294,0,392,0,392,392,392,0,1047,262], [0.2,0.2,0.2,0.2,0.2,0.2,0.1,0.1,0.1,0.1,0.1,0.1,0.8,0.4]),
	([262,330,392,523,1047], [0.2,0.2,0.2,0.2,0.2,0,5]),
	([262,294,330,349,392,440,494,523, 587, 659,698,784,880,988,1047], [.1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1])
	]


class LCD():
    def __init__(self, eventQueue):

        # Configuration parameters
        # I2C Address, Port, Enable pin, RW pin, RS pin, Data 4 pin, Data 5 pin, Data 6 pin, Data 7 pin, Backlight pin (optional)
        self.lcd = i2c_lcd_smbus.i2c_lcd(0x27,1, 2, 1, 0, 4, 5, 6, 7, 3)

        # If you want to disable the cursor, uncomment the following line
        self.lcd.command(self.lcd.CMD_Display_Control | self.lcd.OPT_Enable_Display)
        self.lcd.backLightOn()
        self.isLighted=True
	thread.start_new_thread(self.main, (eventQueue, ))

    def main( self, eventQueue ):
	while (True):
	    payload = eventQueue.get(True)
            if payload[0]==const.EVENT_SONG1:
                self.playSong( eventQueue , songs[0])
            elif payload[0]==const.EVENT_SONG2:
                self.playSong( eventQueue, songs[1] )
            elif payload[0]==const.EVENT_SONG3:
                self.playSong( eventQueue, songs[2] )
    
    def playSong( self, eventQueue, song ):
        eventQueue.task_done()
        GPIO.setup(12, GPIO.OUT)
        pin = GPIO.PWM(12, 5000)  # channel=12 frequency=50Hz
        pin.start(0)
        self.playSong(pin, song)
            

    def beep( self, pin, frequency, length ):
        if frequency>0:
            pin.ChangeDutyCycle(50)
            pin.ChangeFrequency( frequency )
        time.sleep( length )
        pin.ChangeDutyCycle(0)
        time.sleep( length/2)

    def playSong( self, pin, song ):
        for note in zip( song[0], song[1]):
            self.beep(pin, note[0], note[1] )

def main( ):
    from Queue import Queue
    q=Queue()
    sc = LCD(q)
    while True:
        q.put([const.EVENT_SONG1, "hello"])
        time.sleep(20)
        q.put([const.EVENT_SONG2,"" ])
        time.sleep(10)
        q.put([const.EVENT_SONG3, "hello"])
        time.sleep(20)
    
if __name__ == '__main__':
    main()





