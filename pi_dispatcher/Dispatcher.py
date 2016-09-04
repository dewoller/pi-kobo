#!/usr/bin/python 
import queue
import sys
from subprocess import call
import string
import time

import logging, logging.handlers, logging.config
logging.config.fileConfig('log.conf' )
logging.getLogger("Adafruit_I2C.Device.Bus.1.Address.0X5A").setLevel(logging.WARNING)
logger=logging.getLogger( "Dispatcher" )

import os
logger.info("Current Nice Level is %s" % os.nice(-19))


import const
import MQTT
import Pins
import LCD
import Music
import Keypad
import RFID
import db
import webConnect

q = queue.Queue()
LCDScreen = LCD.LCD()
mqtt = MQTT.MQTT(  "192.168.1.38", q, clientID="Dispatcher", inTopic="dispatcher", outTopic="keypad" )
mqtt.publish("pi", "starting")
pins =Pins.Pins( q )
keypad = Keypad.Keypad(q)
music = Music.Music()
RFIDReader = RFID.RFID(q)
webConnection = webConnect.webConnect(q)

def restart():
    logger.info( "rebooting: %s" %( output ))
    command = "/sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]

def processKeyCodes( payload):
    badMessage=False

    logger.info("processing payload '%s'" % payload)
    if payload == "3695147" :
        pins.unlock()
    elif payload == "" or payload == "X":
        # z pressed
        webConnection.notifyNextTrain()
    elif payload == "666":
        sys.exit()
    elif payload == "667":
        LCDScreen.publish([5, "Rebooting"] )
        time.sleep(1)
        restart()
    elif payload == "369":
        pins.disableAllPins()
        LCDScreen.publish([5, "All Pins Off"] )
        mqtt.publish("water/0", "0")
    elif payload[0:2] == "XY":
        try:
            pin = int(payload[2:3])
            duration = int(payload[3:])
        except ValueError:
            badMessage=True
        if pin<1 or pin > 3:
            badMessage=True
        if not badMessage: 
            pins.water(pin, duration)
            LCDScreen.publish([5, "Water zone #%s for  %s sec" % (pin, duration)])
            mqtt.publish("water/%s" % pin, "%s" % duration)
        
    elif payload == "147":
        vals = pins.readTemperature()
        LCDScreen.publish([20,"Temperature:{:.1f} \nHumidity:   {:.1f}%".format(*vals)])
        mqtt.publish("sensor1/temperature","{:.1f}".format(vals[0]))
        mqtt.publish("sensor1/humidity","{:.1f}".format(vals[1]))
        mqtt.publish("sensor1/dewpoint","{:.1f}".format(vals[2]))
    else:
        badMessage=True

    if badMessage:
        LCDScreen.publish([1, "What?"])
        logger.warning( "incomprehensible message %s " %(payload))



def startDispatcher( ):
    logger.info("inside startDispatcher")
    while True:
        try:
            dispatcherLoop()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            logger.error('Some Overall error, capture it and continue, this should be handled at lower level', exc_info=True)
            time.sleep(1)

def dispatcherLoop( ):
    # reinitialize because we might be coming in after an error
    currentStateIndex=0
    nextState=[1,3,1,5,1,3,1,5]
    finalStateIndex=len(nextState)
    logger.info("inside dispatcherloop")
    RFIDReader.readTag()
    saveRFID=False
    while True:
        try:
            payload = q.get(True, 300)
            q.task_done()
        except queue.Empty as e:
            RFIDReader.readTag()   # maybe we have forgotten that we need to be reading tags
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
            logger.info("tag received: %s " % payload[1])
            if (saveRFID):
                db.addCard( payload[1])
                logger.info("tag saved: %s " % payload[1])
                music.playSong("beeps2")
            elif db.hasCard( payload[1]):
                pins.unlock()
            else:
                LCDScreen.publish([1, "I don't know that card"])

        elif payload[0] == const.EVENT_TOUCHED:
            logger.info("touched received: %s " % payload[1])

            if payload[1] == nextState[ currentStateIndex ]:
                logger.info("Next State: %s " % currentStateIndex)
                currentStateIndex=currentStateIndex + 1
                if currentStateIndex >1 :
                    LCDScreen.display("Current State %s" % currentStateIndex)

            else:
                currentStateIndex=0

            if currentStateIndex == finalStateIndex:
                # we have a winner
                currentStateIndex=0
                music.playSong("beeps1")
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
            music.playSong("long")
            mqtt.publish("door", "unlocked")

        elif payload[0] == const.EVENT_LOCKED:
            LCDScreen.display("DOOR LOCKED " )
            RFIDReader.lightOff(0)
            music.stopPlay()
        elif payload[0] == const.EVENT_NEXTTRAIN:
            if payload[1] >= 0:
                LCDScreen.display("NEXT TRAIN IN\n{minutes:.2f} MINUTES".format( minutes=payload[1] ) )
            else:
                LCDScreen.display("Error getting\nnext train")
        else:
            logger.error("Unknown event: %s " % payload[0])


            

if __name__ == "__main__":

    startDispatcher()

    call(["sudo", "/usr/bin/allPinsOff"])
    pins.cleanup()

