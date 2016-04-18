

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
import const
import thread, sys
from i2clibraries import i2c_lcd_smbus

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
            if payload[0]==const.EVENT_DISPLAYLINE1:
                self.prepareLCD( eventQueue )
                self.lcd.home()
                self.lcd.writeString(payload[1])
            elif payload[0]==const.EVENT_DISPLAYLINE2:
                self.prepareLCD( eventQueue )
                self.lcd.setPosition(2, 0) 
                self.lcd.writeString(payload[1])
            elif payload[0]==const.EVENT_DISPLAYCLEAR:
                self.prepareLCD( eventQueue )
                self.lcd.clear()
            elif payload[0]==const.EVENT_DISPLAYOFF:
                self.prepareLCD( eventQueue )
                self.lcd.backLightOff()
                self.isLighted=False
    
    def prepareLCD( self, eventQueue ):
        if not self.isLighted:
            self.lcd.backLightOn()
            self.isLighted=True
        eventQueue.task_done()
            

def main( ):
    from Queue import Queue
    q=Queue()
    sc = LCD(q)
    while True:
        q.put([const.EVENT_DISPLAYLINE1, "hello"])
        time.sleep(2)
        q.put([const.EVENT_DISPLAYCLEAR,"" ])
        time.sleep(1)
        q.put([const.EVENT_DISPLAYLINE2, "hello"])
        time.sleep(2)
        q.put([const.EVENT_DISPLAYCLEAR,"" ])
        time.sleep(1)
        q.put([const.EVENT_DISPLAYOFF, "hello"])
        time.sleep(2)
        q.put([const.EVENT_DISPLAYCLEAR,"" ])
        time.sleep(1)
    
if __name__ == '__main__':
    main()




