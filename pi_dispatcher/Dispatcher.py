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
import alexaFauxmo as alexa

#TODO; delete lcd.publish
#TODO: convert messages to functional

eventQueue = queue.Queue()
LCDScreen = LCD.LCD()
mqtt = MQTT.MQTT(  "192.168.1.38", eventQueue, clientID="Dispatcher", inTopic="dispatcher", outTopic="keypad" )
mqtt.publish("door/dispatcher", "starting")
pins =Pins.Pins( eventQueue )
keypad = Keypad.Keypad(eventQueue)
music = Music.Music()
RFIDReader = RFID.RFID(eventQueue)
webConnection = webConnect.webConnect(eventQueue)
alexa = alexa.alexaFauxmo( eventQueue )

def restart():
    logger.info( "rebooting: %s" %( output ))
    command = "/sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]

def processKeyCodes( keys):
    badMessage=False

    logger.info("processing keys '%s'" % keys)
    if keys == "3695147" :
    	unlockDoor( keys )
    elif keys == "" or keys == "X":
        # z pressed
        webConnection.notifyNextTrain()
    elif keys == "666":
        eventQueue.put(["restart",""])
    elif keys == "667":
        LCDScreen.publish([5, "Rebooting"] )
        time.sleep(1)
        restart()
    elif keys == "369":
    	AllWaterOff()
    elif keys[0:2] == "XY":
        try:
            pin = int(keys[2:3])
            duration = int(keys[3:])
        except ValueError:
            badMessage=True
        if pin<1 or pin > 3:
            badMessage=True
        if not badMessage: 
            water(pin, duration)
        
    elif keys == "147":
        getAndSendTemperature()
    else:
        badMessage=True

    if badMessage:
        LCDScreen.publish([1, "What?"])
        logger.warning( "incomprehensible message %s " %(keys))

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
            payload = eventQueue.get(True, 300)
            eventQueue.task_done()
        except queue.Empty as e:
            RFIDReader.readTag()   # maybe we have forgotten that we need to be reading tags
            continue
        
        # we have a task to do
        if payload[0] == const.EVENT_KEYS:
            processKeyCodes( payload[1])

        elif payload[0] == const.EVENT_TOUCHUP:
            LCDScreen.displayChar(payload[1])

        elif payload[0] == const.EVENT_TOUCHDOWN:
            pass

        elif payload[0] == "restart":
            system.exit(0)

        elif payload[0] == const.EVENT_RFID_HASTAG or payload[0] == "door/rfid":
            logger.info("tag received: %s " % payload[1])
            if (saveRFID):
                db.addCard( payload[1])
                logger.info("tag saved: %s " % payload[1])
                music.playSong("beeps2")
            elif db.hasCard( payload[1]):
                unlockDoor( payload[1] )
            else:
                LCDScreen.publish([1, "I don't know that card"])
                mqtt.publish("door/unknownRFID",payload[1] )

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

        elif payload[0] == const.EVENT_WATER1 or payload[0]=="water":
        	water(1, payload[1])
        elif payload[0] == const.EVENT_WATER2 or payload[0]=="water":
        	water(2, payload[1])
        elif payload[0] == const.EVENT_WATER3 or payload[0]=="water":
        	water(3, payload[1])
        elif payload[0] == const.EVENT_WATEROFF or payload[0]=="wateroff":
        	AllWaterOff()
        elif payload[0] == const.EVENT_UNLOCK or payload[0]=="unlock":
        	unlockDoor( payload[1] )
        elif payload[0] == const.EVENT_LOCK or payload[0]=="lock":
        	lockDoor()
        elif payload[0] == const.EVENT_NEXTTRAIN:
            if payload[1] >= 0:
                LCDScreen.display("NEXT TRAIN IN\n{minutes:.0f}:{seconds:.0f} ".format( minutes=payload[1]//60, seconds=payload[1]%60 ) )
                logger.info("time til next train: %s " % payload[1])
            else:
                LCDScreen.display("Error getting\nnext train")
        else:
            logger.error("Unknown event: %s " % payload[0])

def getAndSendTemperature():
    vals = pins.readTemperature()
    LCDScreen.publish([20,"Temperature:{:.1f} \nHumidity:   {:.1f}%".format(*vals)])
    mqtt.publish("sensor1/temperature","{:.1f}".format(vals[0]))
    mqtt.publish("sensor1/humidity","{:.1f}".format(vals[1]))
    mqtt.publish("sensor1/dewpoint","{:.1f}".format(vals[2]))


def unlockDoor( howUnlocked = "Unknown" ):
	pins.unlock()
	LCDScreen.display("DOOR UNLOCKED " )
	RFIDReader.lightOn(0)
	music.playSong("long")
	mqtt.publish("door/unlocked", howUnlocked )

def lockDoor( ): 
	pins.lock()
	LCDScreen.display("DOOR LOCKED " )
	RFIDReader.lightOff(0)
	music.stopPlay()
	mqtt.publish("door/locked")

def AllWaterOff():
	pins.disableAllPins()
	LCDScreen.publish([5, "All Pins Off"] )
	mqtt.publish("water/0", "0")

def water( pin, duration ): 
	if duration <0  :
		pins.disablePin( pin )
		LCDScreen.publish([5, "Water zone #%s off " % (pin)])
		mqtt.publish("water/%s/off" % pin )
	else:
		pins.water(pin, duration)
		LCDScreen.publish([5, "Water zone #%s for  %s sec" % (pin, duration)])
		mqtt.publish("water/%s" % pin, "%s" % duration)
            

if __name__ == "__main__":

    startDispatcher()

    call(["sudo", "/usr/bin/allPinsOff"])
    pins.cleanup()

