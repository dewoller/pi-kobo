import time
from threading import Timer

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
P.OFF=GPIO.HIGH
P.ON=GPIO.LOW

GPIO.setmode(GPIO.BOARD)


controlPins=(5,9,13,10)
unlockPinIndex=3;

map(GPIO.setup, controlPins, GPIO.OUT, initial=P.OFF)


def enablePin( n, duration=8):
    GPIO.output(controlPins[n], P.ON)
    Timer(duration, disablePin, (n)).start()


def disablePin(n):
    GPIO.output(channel, P.OFF)

def disableAllPins():
    map(GPIO.output, controlPins, P.OFF)


def water( n, duration=120):
    if (n<4):
        enablePin(n-1, duration)

def unlock( ):
    enablePin(3, 8)




