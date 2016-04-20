#!/bin/python 
import time
from Queue import Queue
from threading import Timer
from functools import partial
from sht1x.Sht1x import Sht1x as SHT1x
import logging
logger = logging.getLogger("dispatcher")

import const

wateringPins=(7,11,13,15)
#wateringPins=(11,11,11,11)
lockPinIndex=0;
latestOffTime=dict()

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    import GPIO as GPIO
    logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
GPIO.setmode(GPIO.BOARD)

sht1x_dataPin = 22
sht1x_clkPin = 18
sht1x = SHT1x(sht1x_dataPin, sht1x_clkPin, SHT1x.GPIO_BOARD)

class P():
    OFF=GPIO.HIGH
    ON=GPIO.LOW
   

class Pins:
    def __init__(self, eventQueue):
        # need eventQueue because we want to be able to pass messages back, eg saying when done
        self.eventQueue = eventQueue

    def GPIO_output( self, pin, what):
        logger.info( "setting pin {} to state {} ".format( pin, what))
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, what)

    def enablePin( self, pinIndex, duration=20):
        self.GPIO_output(wateringPins[ pinIndex ], P.ON)
        Timer(duration, self.disablePin, [ pinIndex ]).start()
        latestOffTime[ pinIndex ] = max( latestOffTime[ pinIndex ], time.time() + duration)
        if pinIndex == lockPinIndex:
            self.eventQueue.put([const.EVENT_UNLOCKED,pinIndex])
        else:
            self.eventQueue.put([const.EVENT_PINON,pinIndex])


    def disablePin(self,  pinIndex):
        logger.debug( "latestoff {} compared to time {} , pin {}".format( latestOffTime[ pinIndex ],time.time(), pinIndex))

        if latestOffTime[ pinIndex ]-1 <= time.time():
            self.GPIO_output(wateringPins[ pinIndex ], P.OFF)
        if pinIndex == lockPinIndex:
            self.eventQueue.put([const.EVENT_LOCKED,pinIndex])
        else:
            self.eventQueue.put([const.EVENT_PINOFF,pinIndex ])

    def disableAllPins(self ):
        for pinIndex in range(len(wateringPins)):
            latestOffTime[ pinIndex ] = -1
            self.GPIO_output(wateringPins[ pinIndex ], P.OFF)


    def water(self, n, duration=120):
        # 0'th pin is lock mechanism, pins 1..3 are 
        if (n<4) & (n>0): # error checking
	    # subtract 1 because pins number from 1-3, and the fourth pin is for the lock mechanism
            self.enablePin(n, duration)
        else:
            logger.debug( "Invalid watering pin %s " %( n ))
	    

    def unlock(self, nseconds=8):
        self.enablePin(lockPinIndex, nseconds)
        #blink1.startBlink(nseconds)

    def readTemperature( self ):
        return readTemp()
        #return [0,0,0]

    def cleanup( self ):
        GPIO.cleanup()

def readTemp( ):
    temperature = 0
    humidity = 0
    dewPoint=0
    GPIO.setmode(GPIO.BOARD) 
    temperature = sht1x.read_temperature_C()
    humidity = sht1x.read_humidity()
    dewPoint=0
    dewPoint = sht1x.calculate_dew_point(temperature, humidity)
    
    logger.info("Temperature: {} Humidity: {} Dew Point: {}".format(temperature, humidity, dewPoint))
    return [temperature, humidity, dewPoint]
   
 
GPIO.setmode(GPIO.BOARD)

for pinIndex in range(len(wateringPins)):
    latestOffTime[ pinIndex ] = -1

