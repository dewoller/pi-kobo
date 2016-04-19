#!/usr/bin/python 
from Queue import Queue, Empty
import sys
from subprocess import call
import logging
import string
logger = logging.getLogger("dispatcher" )

import const
import MQTT
import Pins
import LCD
import Music
import Keypad

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



def processKeyCodes( pins, mqtt, LCDScreen, keypad, music, payload):

    logger.info("processing payload %s" % payload)
    if payload == "3695147" or payload == "6932147XY" :
        pins.unlock()
        LCDScreen.publish([2, "Door Unlocked"] )
        mqtt.publish("door", string.translate(payload, rot13))
    elif payload == "369":
        pins.disableAllPins()
        LCDScreen.publish([5, "All Pins Off"] )
        mqtt.publish("water/0", "0")
    elif payload[0:2] == "XY":
        try:
            pin = int(payload[2:3]) - 6
            duration = int(payload[3:])
            pins.water(pin, duration)
            LCDScreen.publish([5, "Water zone #%s for  %s sec" % (pin, duration)])
            mqtt.publish("water/%s" % pin, "%s" % duration)
        except ValueError:
            LCDScreen.publish([1, "What?"])
            logger.info( "incomprehensible message %s " %(payload))
	    
    elif payload == "147":
        vals = pins.readTemperature()
        LCDScreen.publish([20,"Temp:{:.1f},Humidity:{:.1f},DewPoint:{:.1f}".format(*vals)])
        mqtt.publish("sensor1/temperature","{:.1f}".format(vals[0]))
        #mqtt.publish("sensor1/humidity","{:.1f}".format(vals[1]))
        #mqtt.publish("sensor1/dewpoint","{:.1f}".format(vals[2]))
    else:
        LCDScreen.publish([1, "What?"])
        logger.info( "incomprehensible message %s " %(payload))


def dispatcherLoop( q, mqtt, LCDScreen, pins , keypad, music):
    while True:
	try:
	    payload = q.get(True, 20)
	    q.task_done()
	    if payload[0] == const.EVENT_KEYS:
		    processKeyCodes( pins, mqtt, LCDScreen, keypad, music, payload[1])

	except Empty as e:
		pass

def startDispatcher():
    try:
        q = Queue()
        LCDScreen = LCD.LCD()
        mqtt = MQTT.MQTT(  "192.168.1.38", q, "newDispatcher", "dispatcher", "keypad" )
        mqtt.publish("pi", "starting")
        pins =Pins.Pins()
        keypad = Keypad.Keypad(q)
        music = Music.Music(q)
        dispatcherLoop( q, mqtt, LCDScreen, pins, keypad, music)
    except Exception as inst:
        logger.info(type(inst))
        logger.info(inst)
        logger.exception(inst)

    LCDScreen.publish([const.EVENT_FLASHMSG, "Exiting Dispatcher"] )
    call(["sudo", "/usr/bin/allPinsOff"])
    pins.cleanup()


if __name__ == "__main__":

    logger = logging.getLogger('dispatcher')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    startDispatcher()


