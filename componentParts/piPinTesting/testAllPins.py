import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
#wateringPins=(3,5,7,11,15,13, 18,22, 8,10)
wateringPins=(7,11, 13, 15, 16)
#wateringPins=(7, 11, 16)

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    import GPIO as GPIO
    logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

div=.1
r=int(1000//div)
GPIO.setmode(GPIO.BOARD)

for i in range(r):
    for pin in wateringPins:  
#        print(pin)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        time.sleep( div )
        GPIO.output(pin, GPIO.HIGH)
        time.sleep( div )
for pin in wateringPins:  
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

p.stop()
GPIO.cleanup()
