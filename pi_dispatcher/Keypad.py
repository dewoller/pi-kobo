#!/bin/python 

import logging, traceback
logger = logging.getLogger( "dispatcher.keys")
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

import time, sys
import const
import thread, sys
import Adafruit_MPR121.MPR121 as MPR121

keymap=['X','7','4','1','Y','8','5','2','Z','9','6','3']

class Keypad():
    def __init__(self, eventQueue):
        # Create MPR121 instance.
        self.cap = MPR121.MPR121()

        if not self.cap.begin():
            print 'Error initializing MPR121.  Check your wiring!'
	thread.start_new_thread(self.main, (eventQueue, ))

    def main( self, eventQueue ):
        result=''
        last_touched=0
	while (True):
            try:
                current_touched = self.cap.touched()
                for i in range(12):
                    pin_bit = 1 << i
                    #if current_touched & pin_bit and not last_touched & pin_bit:
                    if not current_touched & pin_bit and last_touched & pin_bit:
                        key=keymap[i]
                        print(i, key)
                        if key=='Z':
                            if result <> '':
                                eventQueue.put([const.EVENT_KEYS,  result])
                            result=""
                        else:
                            result = result + keymap[ i ]
                # Update last state and wait a short period before repeating.
                last_touched = current_touched
                #time.sleep(.1)
            except KeyboardInterrupt:
                System.exit(0)
            except Exception:
                logger.error( "Other error:")
                logger.error(traceback.format_exc())

def main( ):
    from Queue import Queue
    q=Queue()
    sc = Keypad(q)
    while True:
            print "about to get keys" 
	    payload = q.get(True)
	    q.task_done()
            print "got keys %s" % payload
            if payload[1]=="111":
                break

    
if __name__ == '__main__':
    main()




