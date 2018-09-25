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
#import RFID
import db
import webConnect
import alexaFauxmo as alexa

#TODO; delete lcd.publish
#TODO: convert messages to functional


pinNames =  [ "water/alley", "water/balcony"]

baseOutTopic = "door"
eventQueue = queue.Queue()
LCDScreen = LCD.LCD()
mqtt = MQTT.MQTT(  "127.0.0.1", eventQueue, clientID="Dispatcher", inTopic="dispatcher", outTopic="keypad" )
mqtt.publish(baseOutTopic, "starting")
pins =Pins.Pins( eventQueue )
keypad = Keypad.Keypad(eventQueue)
music = Music.Music()
#RFIDReader = RFID.RFID(eventQueue)
#webConnection = webConnect.webConnect(eventQueue)
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
    elif keys == "7415963" :
        eventQueue.put(["door/saveRFID",""])
    elif keys == "" or keys == "X":
        # z pressed
        #webConnection.notifyNextTrain()
        pass
    elif keys == "666":
        eventQueue.put(["restart",""])
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
        eventQueue.put(["door/temperature",""])
    else:
        badMessage=True

    if badMessage:
        LCDScreen.publish( "What?")
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
    #RFIDReader.readTag()
    saveRFID=False
    savedKeys=""

    while True:
        try:
            payload = eventQueue.get(True, 300)
            eventQueue.task_done()
        except queue.Empty as e:
            # timeout
            saveRFID=False
            savedKeys=""
            continue
        logger.info("processing event %s payload %s", payload[0], payload[1] ) 

        # access pins by name
        pinIndex =  -1
        try:
            pinIndex =  pinNames.index( payload[0] ) + 1
        except:
            pass

        # we have a task to do
        if payload[0] == const.EVENT_TOUCHUP:
            key=payload[1]
            LCDScreen.displayChar(key)
            if key=="Z":
                processKeyCodes( savedKeys )
                savedKeys=""
            else:
                savedKeys = savedKeys + key

        elif payload[0] == "system/restart":
            restart()

        elif payload[0] == "door/saveRFID":
            mqtt.publish(baseOutTopic + "/saveRFID", "" )
            LCDScreen.publish( "Saving RFID")
            music.playSong("beeps1")
            saveRFID=True
        elif  payload[0] == "door/rfid":
            logger.info("tag received: %s " % payload[1])
            if db.hasCard( payload[1]):
                logger.info("tag found: %s " % payload[1])
                mqtt.publish(baseOutTopic + "/usedTag", payload[1] )
                unlockDoor( payload[1] )
            elif (saveRFID):
                db.addCard( payload[1])
                logger.info("tag saved: %s " % payload[1])
                mqtt.publish(baseOutTopic + "/savedRFID", payload[1] )
                music.playSong("beeps2")
            else:
                LCDScreen.publish( "Unknown RFID tag")
                mqtt.publish(baseOutTopic + "/unknownRFID",payload[1] )
            saveRFID=False

        elif  payload[0] == "door/temperature":
            getAndSendTemperature()
        elif pinIndex > 0:
        	water(pinIndex, payload[1], payload[0])
        elif payload[0] == const.EVENT_WATER1  or payload[0]=="water1":
        	water(2, payload[1], "balcony")
        elif payload[0] == const.EVENT_WATER3  or payload[0]=="water3":
        	water(3, payload[1], "alley")
        elif payload[0] == const.EVENT_WATEROFF or payload[0]=="water/off":
        	AllWaterOff()
        elif payload[0] == const.EVENT_UNLOCK or payload[0]=="door/unlock":
        	unlockDoor( payload[1] )
        elif payload[0] == const.EVENT_LOCK or payload[0]=="door/lock":
                lockDoor()
        elif payload[0] == const.MQTT_MESSAGE:
                mqtt.publish( baseOutTopic + "/message", vals[0])
        elif payload[0] == const.EVENT_NEXTTRAIN:
            if payload[1] >= 0:
                LCDScreen.display("NEXT TRAIN IN\n{minutes:.0f}:{seconds:.0f} ".format( minutes=payload[1]//60, seconds=payload[1]%60 ) )
                logger.debug("time til next train: %s " % payload[1])
            else:
                LCDScreen.display("Error getting\nnext train")
        else:
            logger.error("Unknown event: %s " % payload[0])

def getAndSendTemperature():
    vals = pins.readTemperature()
    LCDScreen.publish("Temperature:{:.1f} \nHumidity:   {:.1f}%".format(*vals))
    mqtt.publish( baseOutTopic + "/sensor1/temperature","{:.1f}".format(vals[0]))
    mqtt.publish( baseOutTopic + "/sensor1/humidity","{:.1f}".format(vals[1]))
    mqtt.publish( baseOutTopic + "/sensor1/dewpoint","{:.1f}".format(vals[2]))


def unlockDoor( howUnlocked = "Unknown" ):
	pins.unlock()
	LCDScreen.display("DOOR UNLOCKED " )
	#RFIDReader.lightOn(0)
	music.playSong("long")
	mqtt.publish( baseOutTopic + "/unlocked", howUnlocked )

def lockDoor( ): 
	pins.lock()
	LCDScreen.display("DOOR LOCKED " )
	#RFIDReader.lightOff(0)
	music.stopPlay()
	mqtt.publish( baseOutTopic + "/locked")

def AllWaterOff():
	pins.disableAllPins()
	LCDScreen.publish( "All Pins Off" )
	mqtt.publish("water/all/off", "0")

def water( pin, duration, where="unknown"): 
    duration = int(duration)
    if duration <0  :
            pins.disablePin( pin )
            LCDScreen.publish( "Water #%s off " % (where))
            mqtt.publish("water/%s/off" % where )
    else:
            pins.water(pin, duration)
            LCDScreen.publish( "Water #%s for  %s sec" % (where, duration))
            mqtt.publish("water/%s/on" % where, "%s" % duration)
            

if __name__ == "__main__":
    # cleanup before and after
    call(["sudo", "/usr/bin/allPinsOff"])
    pins.cleanup()

    startDispatcher()

    call(["sudo", "/usr/bin/allPinsOff"])
    pins.cleanup()

