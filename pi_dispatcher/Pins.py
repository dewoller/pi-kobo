#!/bin/python 
import time
from Queue import Queue
from threading import Timer
from functools import partial
from sht1x.Sht1x import Sht1x as SHT1x


#from blink1_pyusb import Blink1 as Blink1_pyusb
#blink1 = Blink1_pyusb()

import logging
logger = logging.getLogger("dispatcher.pins")

wateringPins=(7,12,15,11)
#wateringPins=(11,11,11,11)
lockPinIndex=3;
sht1x_dataPin = 22
sht1x_clkPin = 18
sht1x = SHT1x(sht1x_dataPin, sht1x_clkPin, SHT1x.GPIO_BOARD)
latestOffTime=dict()

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    import GPIO as GPIO
    logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


GPIO.setmode(GPIO.BOARD)

class P():
    OFF=GPIO.HIGH
    ON=GPIO.LOW
   

class Pins:
    def __init__(self):
	self.logger = logging.getLogger()

    def GPIO_output( self, pin, what):
        self.logger.info( "setting pin {} to state {} ".format( pin, what))
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, what)

    def enablePin( self, n, duration=20):
	wateringPin = wateringPins[n]
        self.GPIO_output(wateringPin, P.ON)
        Timer(duration, self.disablePin, [ wateringPin ]).start()
        latestOffTime[ wateringPin ] = max( latestOffTime[ wateringPin ], time.time() + duration)


    def disablePin(self,  wateringPin):
        self.logger.debug( "latestoff {} compared to time {} , pin {}".format( latestOffTime[ wateringPin ],time.time(), wateringPin))

	if latestOffTime[ wateringPin ]-1 <= time.time():
	    self.GPIO_output(wateringPin, P.OFF)

    def disableAllPins(self ):
	for wateringPin in wateringPins:
	    latestOffTime[ wateringPin ] = -1
	    self.GPIO_output(wateringPin, P.OFF)


    def water(self, n, duration=120):
        if (n<4 ) &  (n>0): # error checking
	    # subtract 1 because pins number from 1-3, and the fourth pin is for the lock mechanism
            self.enablePin(n-1, duration)
        else:
	    self.logger.debug( "Invalid watering pin %s " %( n ))
	    

    def unlock(self, nseconds=8):
        self.enablePin(lockPinIndex, nseconds)
        #blink1.startBlink(nseconds)

    def readTemperature( self ):
        return readTemp()
        #return [0,0,0]

    def cleanup( self ):
        GPIO.cleanup()

def readTemp( ):
    temperature = sht1x.read_temperature_C()
    humidity = sht1x.read_humidity()
    dewPoint=0
    dewPoint = sht1x.calculate_dew_point(temperature, humidity)
    
    logger.info("Temperature: {} Humidity: {} Dew Point: {}".format(temperature, humidity, dewPoint))
    return [temperature, humidity, dewPoint]
   
 
GPIO.setmode(GPIO.BOARD)

for wateringPin in wateringPins:
    latestOffTime[ wateringPin ] = -1

