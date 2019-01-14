#!/bin/python 

import logging, traceback
logger = logging.getLogger(__name__)
if __name__ == '__main__' and __package__ is None:
    import sys
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

import time, sys
import const
import Adafruit_MPR121.MPR121 as MPR121

import threading
main_thread = threading.current_thread()

keymap=['1','2','3','X','4','5','6','Y','7','8','9','Z']
#keymap=['X','7','4','1','Y','8','5','2','Z','9','6','3']

class Keypad():
    def __init__(self, eventQueue):
        logger.info("Starting")
        self.eventQueue = eventQueue
        self.cap = None
        t=threading.Thread( target=self.main )
        t.daemon = True
        t.start()


    def getCap( self ):
        cap = None
        sleep_time=1
        while (cap == None):
            try:
                # Create MPR121 instance.
                cap = MPR121.MPR121()
                cap.begin()
            except OSError:
                logger.info( 'Error initializing MPR121.  Check your wiring!')
                cap=None
            except Exception:
                logger.error( "Other Keyboard error:")
                logger.error(traceback.format_exc())
                cap=None
            if (cap==None):
                time.sleep( sleep_time -1)
                sleep_time = sleep_time * 2

        return(cap)

    def main( self):
        last_touched=0
        while ( main_thread.is_alive() ):
            if (self.cap == None):
                self.cap=self.getCap()
            try:
                current_touched = self.cap.touched()
                for i in range(12):
                    pin_bit = 1 << i
                    key=keymap[i]
                    if not current_touched & pin_bit and last_touched & pin_bit:
                        self.eventQueue.put([const.EVENT_TOUCHUP,  key])
                        logger.debug( "key pressed '%s'" % (key) )
                last_touched = current_touched
                time.sleep(.01)
            except KeyboardInterrupt:
                System.exit(0)
            except Exception:
                logger.error( "Other Keyboard error:")
                logger.error(traceback.format_exc())
                self.cap=None

def main( ):
    import queue
    q = queue.Queue()
    sc = Keypad(q)
    while True:
        logger.info( "about to get keys" )
        payload = q.get(True)
        q.task_done()
        logger.info( "got keys %s" % payload)
        if payload[1]=="111":
            break

    
if __name__ == '__main__':
    main()




