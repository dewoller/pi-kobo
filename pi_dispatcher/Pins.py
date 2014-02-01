import time
from Queue import Queue
from threading import Timer
onPi=False

        
class Pins:
    class P():
        if onPi:
            OFF=GPIO.HIGH
            ON=GPIO.LOW
        else:
            OFF="ON"
            ON="OFF"
    def __init__(self):
        timerq = Queue()

        self.controlPins=(5,9,13,10)
        self.lockPinIndex=3;
        if (onPi) :
            try:
                import RPi.GPIO as GPIO
            except RuntimeError:
                print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
            GPIO.setmode(GPIO.BOARD)
            map(GPIO.setup, self.controlPins, GPIO.OUT, initial=P.OFF)


    def GPIO_output( self, pin, what):
        if (onPi):
            GPIO.output(pin, what)
        else:
            print "setting pin ", pin, " to state ", what, "at time ", time.time()

    def enablePin( self, n, duration=8):
        self.GPIO_output(self.controlPins[n], self.P.ON)
        Timer(duration, self.disablePin, [n]).start()


    def disablePin(self, n):
        self.GPIO_output(self.controlPins[n], self.P.OFF)

    def disableAllPins(self ):
        map(self.GPIO_output, self.controlPins, self.P.OFF)


    def water(self, n, duration=120):
        if (n<4):
            self.enablePin(n-1, duration)

    def unlock(self):
        self.enablePin(self.lockPinIndex, 8)




