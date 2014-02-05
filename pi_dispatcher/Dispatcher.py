#!/usr/bin/python 

#import pdb ;pdb.set_trace()
from MQTT import MQTT
from Pins import Pins
from Queue import Queue, Empty
import logging
logger = logging.getLogger()

TOUCHDOWN=1
TOUCHUP=2
FLASHSCREEN=3
FLASHMSG=5
CLEARMSG=6

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


def process( pins, mqtt, payload ):
    logger.info("processing payload %s" % payload)
    #pdb.set_trace()
    if payload == "119":
        pins.unlock()
        mqtt.publish("%i|Door Unlocked" % (FLASHMSG))
    elif payload == "666":
        pins.disableAllPins()
        mqtt.publish("%i|All Pins off" % (FLASHMSG))
    elif payload[0:3] == "999":
        pin = int(payload[3:4])
        duration = int(payload[4:])
        pins.water(pin, duration)
        mqtt.publish("%i|Water zone #%s for  %s sec" % (FLASHMSG, pin, duration))
    else:
        mqtt.publish("%i" % (FLASHSCREEN))
        logger.info( "incomprehensible message %s " %(payload))


def startDispatcher():
	q = Queue()
	mqtt = MQTT( q )
	pins =Pins()

	while True:
	    try:
		payload = q.get(True, 20)
		process( pins, mqtt, payload )
		q.task_done()
	    except Empty as e:
		    pass
    


if __name__ == "__main__":
     startDispatcher()


