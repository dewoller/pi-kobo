import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 5000)  # channel=12 frequency=50Hz
p.start(90)
try:
    while 1:
        for dc in range(1, 10001, 100):
            print( dc )
            p.ChangeFrequency(dc)
            time.sleep(0.1)
        for dc in range(10000, 1, -100):
            print( dc )
            p.ChangeFrequency(dc)
            time.sleep(0.1)
except KeyboardInterrupt:
    pass
p.stop()
GPIO.cleanup()

