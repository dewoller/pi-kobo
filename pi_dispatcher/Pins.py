import time
from Queue import Queue
from threading import Timer
from functools import partial
import logging
logger = logging.getLogger()


onPi=True
controlPins=(7,11,15,12)
lockPinIndex=3;

if (onPi) :
    try:
	import RPi.GPIO as GPIO
    except RuntimeError:
	logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

class P():
	if onPi:
	    OFF=GPIO.HIGH
	    ON=GPIO.LOW
	else:
	    OFF="ON"
	    ON="OFF"


if (onPi) :
    GPIO.setmode(GPIO.BOARD)
    for controlPin in controlPins:
        GPIO.setup(controlPin, GPIO.OUT)
	GPIO.output(controlPin, P.OFF)


        
class Pins:
    def __init__(self):
	self.logger = logging.getLogger()

    def GPIO_output( self, pin, what):
        self.logger.info( "setting pin ", pin, " to state ", what, "at time ", time.time())
        if (onPi):
            GPIO.output(pin, what)

    def enablePin( self, n, duration=8):
        self.GPIO_output(controlPins[n], P.ON)
        Timer(duration, self.disablePin, [n]).start()


    def disablePin(self, n):
        self.GPIO_output(controlPins[n], P.OFF)

    def disableAllPins(self ):
	for controlPin in controlPins:
	    GPIO.output(controlPin, P.OFF)


    def water(self, n, duration=120):
        if (n<4):
            self.enablePin(n-1, duration)

    def unlock(self):
        self.enablePin(lockPinIndex, 8)




