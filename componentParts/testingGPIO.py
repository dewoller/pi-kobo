import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
wateringPins=(3,5,7,11,15,13, 18,22, 8,10)

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    import GPIO as GPIO
    logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


GPIO.setmode(GPIO.BOARD)

while True:
    for pin in wateringPins:  
#        print(pin)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(.001)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(.001)

p.stop()
GPIO.cleanup()
