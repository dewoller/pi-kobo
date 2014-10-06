#!/usr/bin/python 
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

#import pdb ;pdb.set_trace()
from Pins import Pins
from Queue import Queue, Empty
from subprocess import call
import logging
logger = logging.getLogger()
import const
from MQTT import MQTT
import bluescan


validBluetoothId = [
    "B0:EC:71:C9:28:0E", # Galaxy Nexus
    "98:D6:F7:B7:A5:DA", # nexus 4 
    "B0:EC:71:C9:28:0E"	  #Lees' phone
    "A4:3D:78:DB:60:72", # Oppo Dennis
    "00:18:6B:30:47:00",  # White headset
    ]  
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


def processKeyCodes( pins, mqtt, payload ):
    logger.info("processing payload %s" % payload)
    #pdb.set_trace()
    if payload == "119":
        pins.unlock()
        mqtt.publish([const.EVENT_FLASHMSG, "Door Unlocked"] )
    elif payload == "666":
        pins.disableAllPins()
        mqtt.publish([const.EVENT_FLASHMSG, "All Pins Off"] )
    elif payload[0:3] == "999":
        try:
	    pin = int(payload[3:4])
	    duration = int(payload[4:])
	    pins.water(pin, duration)
	    mqtt.publish([const.EVENT_FLASHMSG, "Water zone #%s for  %s sec" % (pin, duration)])
	except ValueError:
	    mqtt.publish([const.EVENT_FLASHMSG, "What?"])
	    logger.info( "incomprehensible message %s " %(payload))
	    
    elif payload == "1":
        vals = pins.readTemperature()
        mqtt.publish([const.EVENT_FLASHMSG,"T:{:.1f}\nH:{:.1f}\nD:{:.1f}".format(*vals)])
    else:
	mqtt.publish([const.EVENT_FLASHMSG, "What?"])
	logger.info( "incomprehensible message %s " %(payload))


def dispatcherLoop( q, mqtt, pins ):
    ignoreBlueEvent=False
    while True:
	try:
	    payload = q.get(True, 20)
	    if payload[0] == const.EVENT_KEYS:
		    processKeyCodes( pins, mqtt, payload[1] )
	    elif (payload[0] == const.EVENT_BLUEDEVICETOGGLE):
		ignoreBlueEvent= not ignoreBlueEvent
		if ignoreBlueEvent :
		    logger.debug( "Ignoring Bluetooth unlock events" )
		else:
		    logger.debug( "Paying attention to Bluetooth unlock events" )

	    elif (payload[0] == const.EVENT_BLUEDEVICE) & (not ignoreBlueEvent):
		pins.unlock(70)
		mqtt.publish([const.EVENT_FLASHMSG, "blue tooth door unlock"] )
	    q.task_done()
	except Empty as e:
		pass

def startDispatcher():
    try:
	q = Queue()
	mqtt = MQTT(  "127.0.0.1", q, "dispatcher", "dispatcher", "keypad" )
	bs1 = bluescan.bluescan(q, validBluetoothId)
	
	pins =Pins()
	dispatcherLoop( q, mqtt, pins)
    except Exception as inst:
	logger.info(type(inst))
	logger.info(inst)
	logger.exception(inst)

    mqtt.publish([const.EVENT_FLASHMSG, "Exiting Dispatcher"] )
    call(["sudo", "/usr/bin/allPinsOff"])
    pins.cleanup()


if __name__ == "__main__":
     startDispatcher()


