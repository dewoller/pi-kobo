
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 5000)  # channel=12 frequency=50Hz
p.start(0)

def beep( frequency, length ):
    print( "Frequency %s length %s " % (frequency, length))
    if frequency>0:
        p.ChangeDutyCycle(30)
        p.ChangeFrequency( frequency )
    time.sleep( length)
    p.ChangeDutyCycle(0)
    time.sleep( length/2)

def delay( length ):
    time.sleep( length/10000.0)


def playSong( pitch, duration):
    print( pitch, duration, zip(pitch, duration))
    for tuple in zip(pitch, duration):
        beep(tuple[0], tuple[1] )


def doit():
    beep(frequency=660,length=100)
    delay(150)
    beep(frequency=660,length=100)
    delay(300)
    beep(frequency=660,length=100)
    delay(300)
    beep(frequency=510,length=100)
    delay(100)
    beep(frequency=660,length=100)
    delay(300)
    beep(frequency=770,length=100)
    delay(550)
    beep(frequency=380,length=100)
    delay(575)
    
    beep(frequency=510,length=100)
    delay(450)
    beep(frequency=380,length=100)
    delay(400)
    beep(frequency=320,length=100)
    delay(500)
    beep(frequency=440,length=100)
    delay(300)
    beep(frequency=480,length=80)
    delay(330)
    beep(frequency=450,length=100)
    delay(150)
    beep(frequency=430,length=100)
    delay(300)
    beep(frequency=380,length=100)
    delay(200)
    beep(frequency=660,length=80)
    delay(200)
    beep(frequency=760,length=50)
    delay(150)
    beep(frequency=860,length=100)
    delay(300)
    beep(frequency=700,length=80)
    delay(150)
    beep(frequency=760,length=50)
    delay(350)
    beep(frequency=660,length=80)
    delay(300)
    beep(frequency=520,length=80)
    delay(150)
    beep(frequency=580,length=80)
    delay(150)
    beep(frequency=480,length=80)
    delay(500)
    
    beep(frequency=510,length=100)
    delay(450)
    beep(frequency=380,length=100)
    delay(400)
    beep(frequency=320,length=100)
    delay(500)
    beep(frequency=440,length=100)
    delay(300)
    beep(frequency=480,length=80)
    delay(330)
    beep(frequency=450,length=100)
    delay(150)
    beep(frequency=430,length=100)
    delay(300)
    beep(frequency=380,length=100)
    delay(200)
    beep(frequency=660,length=80)
    delay(200)
    beep(frequency=760,length=50)
    delay(150)
    beep(frequency=860,length=100)
    delay(300)
    beep(frequency=700,length=80)
    delay(150)
    beep(frequency=760,length=50)
    delay(350)
    beep(frequency=660,length=80)
    delay(300)
    beep(frequency=520,length=80)
    delay(150)
    beep(frequency=580,length=80)
    delay(150)
    beep(frequency=480,length=80)
    delay(500)
    
    beep(frequency=500,length=100)
    delay(300)
    
    beep(frequency=760,length=100)
    delay(100)
    beep(frequency=720,length=100)
    delay(150)
    beep(frequency=680,length=100)
    delay(150)
    beep(frequency=620,length=150)
    delay(300)
    
    beep(frequency=650,length=150)
    delay(300)
    beep(frequency=380,length=100)
    delay(150)
    beep(frequency=430,length=100)
    delay(150)
    
    beep(frequency=500,length=100)
    delay(300)
    beep(frequency=430,length=100)
    delay(150)
    beep(frequency=500,length=100)
    delay(100)
    beep(frequency=570,length=100)
    delay(220)
    
    beep(frequency=500,length=100)
    delay(300)
    
    beep(frequency=760,length=100)
    delay(100)
    beep(frequency=720,length=100)
    delay(150)
    beep(frequency=680,length=100)
    delay(150)
    beep(frequency=620,length=150)
    delay(300)
    
    beep(frequency=650,length=200)
    delay(300)
    
    beep(frequency=1020,length=80)
    delay(300)
    beep(frequency=1020,length=80)
    delay(150)
    beep(frequency=1020,length=80)
    delay(300)
    
    beep(frequency=380,length=100)
    delay(300)
    beep(frequency=500,length=100)
    delay(300)
    
    beep(frequency=760,length=100)
    delay(100)
    beep(frequency=720,length=100)
    delay(150)
    beep(frequency=680,length=100)
    delay(150)
    beep(frequency=620,length=150)
    delay(300)
    
    beep(frequency=650,length=150)
    delay(300)
    beep(frequency=380,length=100)
    delay(150)
    beep(frequency=430,length=100)
    delay(150)
    
    beep(frequency=500,length=100)
    delay(300)
    beep(frequency=430,length=100)
    delay(150)
    beep(frequency=500,length=100)
    delay(100)
    beep(frequency=570,length=100)
    delay(420)
    
    beep(frequency=585,length=100)
    delay(450)
    
    beep(frequency=550,length=100)
    delay(420)
    
    beep(frequency=500,length=100)
    delay(360)
    
    beep(frequency=380,length=100)
    delay(300)
    beep(frequency=500,length=100)
    delay(300)
    beep(frequency=500,length=100)
    delay(150)
    beep(frequency=500,length=100)
    delay(300)
    
    beep(frequency=500,length=100)
    delay(300)
    
    beep(frequency=760,length=100)
    delay(100)
    beep(frequency=720,length=100)
    delay(150)
    beep(frequency=680,length=100)
    delay(150)
    beep(frequency=620,length=150)
    delay(300)
    
    beep(frequency=650,length=150)
    delay(300)
    beep(frequency=380,length=100)
    delay(150)
    beep(frequency=430,length=100)
    delay(150)
    
    beep(frequency=500,length=100)
    delay(300)
    beep(frequency=430,length=100)
    delay(150)
    beep(frequency=500,length=100)
    delay(100)
    beep(frequency=570,length=100)
    delay(220)
    
    beep(frequency=500,length=100)
    delay(300)
    
    beep(frequency=760,length=100)
    delay(100)
    beep(frequency=720,length=100)
    delay(150)
    beep(frequency=680,length=100)
    delay(150)
    beep(frequency=620,length=150)
    delay(300)
    
    beep(frequency=650,length=200)
    delay(300)
    
    beep(frequency=1020,length=80)
    delay(300)
    beep(frequency=1020,length=80)
    delay(150)
    beep(frequency=1020,length=80)
    delay(300)
    
    beep(frequency=380,length=100)
    delay(300)
    beep(frequency=500,length=100)
    delay(300)
    
    beep(frequency=760,length=100)
    delay(100)
    beep(frequency=720,length=100)
    delay(150)
    beep(frequency=680,length=100)
    delay(150)
    beep(frequency=620,length=150)
    delay(300)
    
    beep(frequency=650,length=150)
    delay(300)
    beep(frequency=380,length=100)
    delay(150)
    beep(frequency=430,length=100)
    delay(150)
    
    beep(frequency=500,length=100)
    delay(300)
    beep(frequency=430,length=100)
    delay(150)
    beep(frequency=500,length=100)
    delay(100)
    beep(frequency=570,length=100)
    delay(420)
    
    beep(frequency=585,length=100)
    delay(450)
    
    beep(frequency=550,length=100)
    delay(420)
    
    beep(frequency=500,length=100)
    delay(360)
    
    beep(frequency=380,length=100)
    delay(300)
    beep(frequency=500,length=100)
    delay(300)
    beep(frequency=500,length=100)
    delay(150)
    beep(frequency=500,length=100)
    delay(300)
    
    beep(frequency=500,length=60)
    delay(150)
    beep(frequency=500,length=80)
    delay(300)
    beep(frequency=500,length=60)
    delay(350)
    beep(frequency=500,length=80)
    delay(150)
    beep(frequency=580,length=80)
    delay(350)
    beep(frequency=660,length=80)
    delay(150)
    beep(frequency=500,length=80)
    delay(300)
    beep(frequency=430,length=80)
    delay(150)
    beep(frequency=380,length=80)
    delay(600)
    
    beep(frequency=500,length=60)
    delay(150)
    beep(frequency=500,length=80)
    delay(300)
    beep(frequency=500,length=60)
    delay(350)
    beep(frequency=500,length=80)
    delay(150)
    beep(frequency=580,length=80)
    delay(150)
    beep(frequency=660,length=80)
    delay(550)
    
    beep(frequency=870,length=80)
    delay(325)
    beep(frequency=760,length=80)
    delay(600)
    
    beep(frequency=500,length=60)
    delay(150)
    beep(frequency=500,length=80)
    delay(300)
    beep(frequency=500,length=60)
    delay(350)
    beep(frequency=500,length=80)
    delay(150)
    beep(frequency=580,length=80)
    delay(350)
    beep(frequency=660,length=80)
    delay(150)
    beep(frequency=500,length=80)
    delay(300)
    beep(frequency=430,length=80)
    delay(150)
    beep(frequency=380,length=80)
    delay(600)
    
    beep(frequency=660,length=100)
    delay(150)
    beep(frequency=660,length=100)
    delay(300)
    beep(frequency=660,length=100)
    delay(300)
    beep(frequency=510,length=100)
    delay(100)
    beep(frequency=660,length=100)
    delay(300)
    beep(frequency=770,length=100)
    delay(550)
    beep(frequency=380,length=100)
    delay(575)


    
if __name__ == '__main__':
#    import pdb; pdb.set_trace()
#    doit()
    for i in range(3): 
        playSong([392,294,0,392,294,0,392,0,392,392,392,0,1047,262], [0.2,0.2,0.2,0.2,0.2,0.2,0.1,0.1,0.1,0.1,0.1,0.1,0.8,0.4])
    #    playSong([262,330,392,523,1047], [0.2,0.2,0.2,0.2,0.2,0,5])
        #playSong([262,294,330,349,392,440,494,523, 587, 659,698,784,880,988,1047], [.1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1])
    p.stop()
    GPIO.cleanup()

