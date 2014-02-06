import time
from Queue import Queue
from threading import Timer
from functools import partial
import logging
logger = logging.getLogger()

wateringPins=(7,11,15,12)
lockPinIndex=3;
sht1x_dataPin = 22
sht1x_clkPin = 18


try:
    import RPi.GPIO as GPIO
except RuntimeError:
    import RPiMock.GPIO as GPIO
    logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


class P():
    OFF=GPIO.HIGH
    ON=GPIO.LOW
   

class Pins:
    def __init__(self):
	self.logger = logging.getLogger()

    def GPIO_output( self, pin, what):
        self.logger.info( "setting pin ", pin, " to state ", what, "at time ", time.time())
        if (onPi):
            GPIO.output(pin, what)

    def enablePin( self, n, duration=8):
        self.GPIO_output(wateringPins[n], P.ON)
        Timer(duration, self.disablePin, [n]).start()


    def disablePin(self, n):
        self.GPIO_output(wateringPins[n], P.OFF)

    def disableAllPins(self ):
	for wateringPin in wateringPins:
	    GPIO.output(wateringPin, P.OFF)


    def water(self, n, duration=120):
        if (n<4):
            self.enablePin(n-1, duration)

    def unlock(self):
        self.enablePin(lockPinIndex, 8)

    def readTemperature( self ):
        return readTemp()

def readTemp( ):
    temperature = sht1x.read_temperature_C()
    humidity = sht1x.read_humidity()
    dewPoint=0
    dewPoint = sht1x.calculate_dew_point(temperature, humidity)
    
    logger.info("Temperature: {} Humidity: {} Dew Point: {}".format(temperature, humidity, dewPoint))
    return [temperature, humidity, dewPoint]
   
 
from sht1x.Sht1x import Sht1x as SHT1x
sht1x = SHT1x(sht1x_dataPin, sht1x_clkPin, SHT1x.GPIO_BOARD)
#print readTemp()

GPIO.setmode(GPIO.BOARD)
#print readTemp()

for wateringPin in wateringPins:
    GPIO.setup(wateringPin, GPIO.OUT)
    GPIO.output(wateringPin, P.OFF)
#print readTemp()
     
