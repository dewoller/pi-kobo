#!/bin/python 

import logging
logger = logging.getLogger(__name__)
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
import queue
import const
from threading import Timer
from i2clibraries import i2c_lcd_smbus
timeout = 10

class LCD():
    def __init__(self):

        # Configuration parameters
        # I2C Address, Port, Enable pin, RW pin, RS pin, Data 4 pin, Data 5 pin, Data 6 pin, Data 7 pin, Backlight pin (optional)
        logger.info("Starting")
        try:
            self.lcd = i2c_lcd_smbus.i2c_lcd(0x27,1, 2, 1, 0, 4, 5, 6, 7, 3)

            # If you want to disable the cursor, uncomment the following line
            self.lcd.command(self.lcd.CMD_Display_Control | self.lcd.OPT_Enable_Display)
            self.lcd.backLightOn()
        except IOError:
            self.lcd = None   # communication error with screen;  giveup
            logger.info("Cant connect to LCD screen")

        self.isLighted=True
        self.lastDisplayTime=time.time()
        self.timer = self.initializeTimer()
        self.pos=0
        
    def displayChar( self, char ):

        if (self.lcd == None):
            return

        self.prepareWrite()
        if self.pos==0:
            self.displayClear()
        if (a != None):
            self.lcd.setPosition(self.pos // 16+1,self.pos % 16)
            self.lcd.writeString( char )
        self.pos=self.pos+len(char)
        if self.pos>=32:
            self.pos=0

    def displayClear( self) :
        if (self.lcd == None):
            return

        self.prepareWrite()
        self.lcd.clear()
        self.pos=0

    def displayOff( self) :
        if (self.lcd == None):
            return

        self.lcd.backLightOff()
        self.isLighted=False

    def publish( self, message ):
        if (self.lcd == None):
            return

        self.display( message )

    def display( self, message ):
        if (self.lcd == None):
            return

        self.prepareWrite()
        self.displayClear()
        if "\n" in message:
            (ln1, ln2) =message.split("\n")
        else:
            ln1=message[:16]
            ln2=message[17:]

        self.displayLine1(ln1)
        self.displayLine2(ln2)

    def displayLine1( self, message) :
        if (self.lcd == None):
            return

        self.pos=0
        self.prepareWrite()
        self.lcd.home()
        self.lcd.writeString( message )

    def displayLine2( self, message) :
        if (self.lcd == None):
            return

        self.pos=0
        self.prepareWrite()
        self.lcd.setPosition(2, 0) 
        self.lcd.writeString( message ) 

    def prepareWrite( self):
        if (self.lcd == None):
            return

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




