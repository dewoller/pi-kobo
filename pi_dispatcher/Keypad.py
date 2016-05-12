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
        # Create MPR121 instance.
        logger.debug("Starting")
        self.cap = MPR121.MPR121()
        self.eventQueue = eventQueue

        if not self.cap.begin():
            print( 'Error initializing MPR121.  Check your wiring!')
        t=threading.Thread( target=self.main )
        t.daemon = True
        t.start()

    def main( self):
        result=''
        last_touched=0
        while ( main_thread.is_alive() ):
                try:
                    current_touched = self.cap.touched()
                    if current_touched!=last_touched:
                        self.eventQueue.put([const.EVENT_TOUCHED,  current_touched])
                    for i in range(12):
                        pin_bit = 1 << i
                        key=keymap[i]
                        if current_touched & pin_bit and not last_touched & pin_bit:
                            self.eventQueue.put([const.EVENT_TOUCHDOWN,  key])
                        if not current_touched & pin_bit and last_touched & pin_bit:
                            self.eventQueue.put([const.EVENT_TOUCHUP,  key])
                            if key=='Z':
                                self.eventQueue.put([const.EVENT_KEYS,  result])
                                result=""
                            else:
                                result = result + key
                            logger.debug( "key pressed '%s', current result '%s'" % (key, result) )
                    last_touched = current_touched
                    time.sleep(.01)
                except KeyboardInterrupt:
                    System.exit(0)
                except Exception:
                    logger.error( "Other Keyboard error:")
                    logger.error(traceback.format_exc())

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




