#!/bin/python 

import logging, traceback
logger = logging.getLogger( "dispatcher.LCD")
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
from Queue import Queue
import const
import thread, sys
from threading import Timer
from i2clibraries import i2c_lcd_smbus
timeout = 10

class LCD():
    def __init__(self):

        # Configuration parameters
        # I2C Address, Port, Enable pin, RW pin, RS pin, Data 4 pin, Data 5 pin, Data 6 pin, Data 7 pin, Backlight pin (optional)
        self.lcd = i2c_lcd_smbus.i2c_lcd(0x27,1, 2, 1, 0, 4, 5, 6, 7, 3)

        # If you want to disable the cursor, uncomment the following line
        self.lcd.command(self.lcd.CMD_Display_Control | self.lcd.OPT_Enable_Display)
        self.lcd.backLightOn()
        self.isLighted=True
        self.lastDisplayTime=time.time()
        self.timer = self.initializeTimer()

    def displayLine1( self, message) :
        self.prepareWrite()
        self.lcd.home()
        self.lcd.writeString( message )

    def displayLine2( self, message) :
        self.prepareWrite()
        self.lcd.setPosition(2, 0) 
        self.lcd.writeString( message )

    def displayClear( self) :
        self.prepareWrite()
        self.lcd.clear()

    def displayOff( self) :
        self.lcd.backLightOff()
        self.isLighted=False

    def publish( self, message ):
        self.prepareWrite()
        self.displayClear()
        self.displayLine1(message[1][:16])
        self.displayLine2(message[1][17:])
    
    def prepareWrite( self):
        if not self.isLighted:
            self.lcd.backLightOn()
            self.isLighted=True

        self.lastDisplayTime=time.time()
        if not self.timer.finished:
            self.timer.cancel()
        self.timer = self.initializeTimer()
        return self.timer

    def initializeTimer( self ):
        timer= Timer(timeout + 1, self.checkForTimeout, [])
        timer.start()
        return timer

    def checkForTimeout(self):
        if self.lastDisplayTime + timeout <= time.time():
            self.displayOff()

def main( ):
    sc = LCD()
    while True:
        sc.displayLine1("hello")
        time.sleep(15)   # check for timeout
        sc.displayClear()
        time.sleep(1)
        sc.displayLine2("hello")
        time.sleep(1)
        sc.displayOff()
        time.sleep(1)
        sc.displayClear()
    
if __name__ == '__main__':
    main()




