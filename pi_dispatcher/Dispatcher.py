#!/usr/bin/python 
import queue
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
import RFID
import db

rot13 = string.maketrans( 
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz", 
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")

q = Queue()
LCDScreen = LCD.LCD()
mqtt = MQTT.MQTT(  "192.168.1.38", q, clientID="newDispatcher", inTopic="dispatcher", outTopic="keypad" )
mqtt.publish("pi", "starting")
pins =Pins.Pins( q )
keypad = Keypad.Keypad(q)
music = Music.Music()
RFIDReader = RFID.RFID(q)


def processKeyCodes( payload):

    logger.info("processing payload %s" % payload)
    if payload == "3695147" or payload == "6932147XY" :
        pins.unlock()
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
        LCDScreen.publish([20,"Temperature:{:.1f} \nHumidity:   {:.1f}%".format(*vals)])
        mqtt.publish("sensor1/temperature","{:.1f}".format(vals[0]))
        mqtt.publish("sensor1/humidity","{:.1f}".format(vals[1]))
        mqtt.publish("sensor1/dewpoint","{:.1f}".format(vals[2]))
    else:
        LCDScreen.publish([1, "What?"])
        logger.info( "incomprehensible message %s " %(payload))


def dispatcherLoop( ):
    RFIDReader.readTag()
    saveRFID=False
    while True:
        try:
            payload = q.get(True, 30)
            q.task_done()
        except queue.Empty as e:
            RFIDReader.readTag()
            continue
        
        # we have a task to do
        if payload[0] == const.EVENT_KEYS:
            #LCDScreen.displayClear()
            processKeyCodes( payload[1])

        elif payload[0] == const.EVENT_TOUCHUP:
            LCDScreen.displayChar(payload[1])

        elif payload[0] == const.EVENT_TOUCHDOWN:
            pass

        elif payload[0] == const.EVENT_RFID_HASTAG:
            logger.debug("tag received: %s " % payload[1])
            if (saveRFID):
                db.addCard( payload[1])
                logger.info("tag saved: %s " % payload[1])
            elif db.hasCard( payload[1]):
                pins.unlock()
            else:
                displayError('Bad card')

        elif payload[0] == const.EVENT_TOUCHED:
            logger.debug("touched received: %s " % payload[1])
            if payload[1] & 15 == 15:
                # keys 0123 are pressed
                saveRFID=True
            else:
                saveRFID=False

        elif payload[0] == const.EVENT_PINON:
            LCDScreen.display("WATER ZN %s" % payload[1] )

        elif payload[0] == const.EVENT_PINOFF:
            LCDScreen.display("STOP WATER ZN %s" % payload[1] )

        elif payload[0] == const.EVENT_UNLOCKED:
            LCDScreen.display("DOOR UNLOCKED " )
            RFIDReader.lightOn(0)
            music.playSong(1)
            mqtt.publish("door", "unlocked")

        elif payload[0] == const.EVENT_LOCKED:
            LCDScreen.display("DOOR LOCKED " )
            RFIDReader.lightOff(0)
            music.stopPlay()
        else:
            logger.info("Unknown event: %s " % payload[0])


            

if __name__ == "__main__":

    logger = logging.getLogger('dispatcher')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
#    ch.setLevel(logging.DEBUG)
#    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#   ch.setFormatter(formatter)
#    logger.addHandler(ch)
    dispatcherLoop()

    call(["sudo", "/usr/bin/allPinsOff"])
    pins.cleanup()

