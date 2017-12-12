#!/bin/python 
import time
import queue
from threading import Timer
import _thread
from functools import partial
from sht1x.Sht1x import Sht1x as SHT1x
import logging
logger = logging.getLogger(__name__)
import const

wateringPins=(7,16,13,15)
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
        logger.info("Starting")
        self.eventQueue = eventQueue
        self.disableAllPins()

    def GPIO_output( self, pin, what):
        logger.debug( "setting pin {} to state {} ".format( pin, what))
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings( False )
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, what)

    def enablePin( self, pinIndex, duration=20):
        logger.info( "trying to enable pin {} ".format( pinIndex))

        toStartThread = False
        if (latestOffTime[ pinIndex ] < 0 ) :  # was off, need to turn on and keep on
            toStartThread = True

        latestOffTime[ pinIndex ] = max( latestOffTime[ pinIndex ], time.time() + duration)
        if ( toStartThread ) :
            logger.info( "actually enabling pin {} ".format( pinIndex))
            _thread.start_new_thread(self.persistPinEnabled, (pinIndex, ))

    def persistPinEnabled( self, pinIndex):
        logger.debug( "initial checking pin {} latestoff {} compared to time {}  ".format( pinIndex, latestOffTime[ pinIndex ],time.time()))
        while (latestOffTime[ pinIndex ] > time.time() ):
            self.GPIO_output(wateringPins[ pinIndex ], P.ON)
            time.sleep(1)
        self.disablePin( pinIndex )


    def disablePin(self,  pinIndex):
        logger.info( "Disabling pin {} latestoff {} compared to time {}  ".format( pinIndex, latestOffTime[ pinIndex ],time.time()))
        latestOffTime[ pinIndex ] = -1
        self.GPIO_output(wateringPins[ pinIndex ], P.OFF)

    def disableAllPins(self ):
        for pinIndex in range(len(wateringPins)):
            self.disablePin( pinIndex )

    def water(self, n, duration=120):
        # 0'th pin is lock mechanism, pins 1..3 are 
        if (n<4) & (n>0): # error checking
            self.enablePin(n, duration)
        else:
            logger.error( "Invalid watering pin %s " %( n ))
        

    def unlock(self, nseconds=8):
        self.enablePin(lockPinIndex, nseconds)

    def lock(self):
        self.disablePin( lockPinIndex )

    def readTemperature( self ):
        return readTemp()

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

