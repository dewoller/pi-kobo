#!/usr/bin/python 
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

#import pdb ;pdb.set_trace()
from Pins import Pins
from Queue import Queue, Empty
from subprocess import call
import logging
logger = logging.getLogger("dispatcher")
import const
from MQTT import MQTT
import bluescan
import SerialCommunications

import string
rot13 = string.maketrans( 
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz", 
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")


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



def processKeyCodes( pins, mqtt, sercon, payload):

    logger.info("processing payload %s" % payload)
    if payload == "3695147" or payload == "69Z32147XY" :
        pins.unlock()
        sercon.publish([2, "Door Unlocked"] )
        mqtt.publish("door", string.translate(payload, rot13))
    elif payload == "369":
        pins.disableAllPins()
        sercon.publish([5, "All Pins Off"] )
        mqtt.publish("water/0", "0")
    elif payload[0:2] == "XY":
        try:
	    pin = int(payload[2:3]) - 6
	    duration = int(payload[3:])
	    pins.water(pin, duration)
	    sercon.publish([5, "Water zone #%s for  %s sec" % (pin, duration)])
            mqtt.publish("water/%s" % pin, "%s" % duration)
	except ValueError:
	    sercon.publish([1, "What?"])
	    logger.info( "incomprehensible message %s " %(payload))
	    
    elif payload == "147":
        vals = pins.readTemperature()
        sercon.publish([20,"Temp:{:.1f},Humidity:{:.1f},DewPoint:{:.1f}".format(*vals)])
        mqtt.publish("sensor1/temperature","{:.1f}".format(vals[0]))
        mqtt.publish("sensor1/humidity","{:.1f}".format(vals[1]))
        mqtt.publish("sensor1/dewpoint","{:.1f}".format(vals[2]))
    else:
	sercon.publish([1, "What?"])
	logger.info( "incomprehensible message %s " %(payload))


def dispatcherLoop( q, mqtt, sercon, pins ):
    ignoreBlueEvent=False
    while True:
	try:
	    payload = q.get(True, 20)
	    if payload[0] == const.EVENT_KEYS:
		    processKeyCodes( pins, mqtt, sercon, payload[1])
	    elif (payload[0] == const.EVENT_BLUEDEVICETOGGLE):
		ignoreBlueEvent= not ignoreBlueEvent
		if ignoreBlueEvent :
		    logger.debug( "Ignoring Bluetooth unlock events" )
		else:
		    logger.debug( "Paying attention to Bluetooth unlock events" )

	    elif (payload[0] == const.EVENT_BLUEDEVICE) & (not ignoreBlueEvent):
		pins.unlock(70)
                #sercon.publish([5, "Bluetooth door unlock from: %s" % payload[1] ] )
                mqtt.publish("blueEvent", payload[ 1 ])

	    q.task_done()
	except Empty as e:
		pass

def startDispatcher():
    try:
	q = Queue()
        sercon = SerialCommunications.SerialCommunications(q)
	mqtt = MQTT(  "127.0.0.1", q, "dispatcher", "dispatcher", "keypad" )
	bs1 = bluescan.bluescan(q)
        mqtt.publish("pi", "starting")
	
	pins =Pins()
	dispatcherLoop( q, mqtt, sercon, pins)
    except Exception as inst:
	logger.info(type(inst))
	logger.info(inst)
	logger.exception(inst)

    sercon.publish([const.EVENT_FLASHMSG, "Exiting Dispatcher"] )
    call(["sudo", "/usr/bin/allPinsOff"])
    pins.cleanup()


if __name__ == "__main__":
    logger = logging.getLogger('dispatcher')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("/var/log/dispatcher.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger = logging.getLogger('dispatcher')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    startDispatcher()


