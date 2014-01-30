import time
from Queue import Queue
from threading import Timer

class Pins:
    class P():
        OFF="ON"
        ON="OFF"
    def __init__(self):
        timerq = Queue()

        self.controlPins=(5,9,13,10)
        self.lockPinIndex=3;

    #map(GPIO.setup, controlPins, GPIO.OUT, initial=P.OFF)

    def GPIO_output( self, i, what):
        print "setting pin ", i, " to state ", what, "at time ", time.time()

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




