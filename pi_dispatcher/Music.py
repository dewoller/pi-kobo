#!/bin/python 

import logging, traceback
logger = logging.getLogger( "dispatcher.music")
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

import time
import const
import _thread

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    import GPIO as GPIO
    logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

GPIO.setmode(GPIO.BOARD)

songs = [
    ([392,294,0,392,294,0,392,0,392,392,392,0,1047,262], [0.2,0.2,0.2,0.2,0.2,0.2,0.1,0.1,0.1,0.1,0.1,0.1,0.8,0.4]),
    ([262,330,392,523,1047], [0.2,0.2,0.2,0.2,0.2,0,5]),
    ([262,294,330,349,392,440,494,523, 587, 659,698,784,880,988,1047], [.1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1])
    ]


class Music():
    def __init__(self):
        self.keepPlaying=False
    def playSong( self, songIndex ):
        self.keepPlaying=True
        thread.start_new_thread(self.playSongInBackground, (songIndex, ))

    def stopPlay( self ):
        self.keepPlaying=False

    def playSongInBackground( self, songIndex ):
        while self.keepPlaying:
            GPIO.setup(12, GPIO.OUT)
            pin = GPIO.PWM(12, 5000)  # channel=12 frequency=50Hz
            pin.start(0)
            self.playNotes(pin, songs[ songIndex ])
            time.sleep(1)
            self.keepPlaying=False
            
    def playNotes( self, pin, song ):
        for note in zip( song[0], song[1]):
            if not self.keepPlaying:
                break
            self.playNote(pin, note[0], note[1] )

    def playNote( self, pin, frequency, length ):
        if frequency>0:
            pin.ChangeDutyCycle(50)
            pin.ChangeFrequency( frequency )
        time.sleep( length )
        pin.ChangeDutyCycle(0)
        time.sleep( length/2)

def main( ):
    sc = Music()
    while True:
        sc.playSong(0)
        time.sleep(10)
        sc.playSong(1)
        time.sleep(10)
        sc.playSong(2)
        time.sleep(10)
    
if __name__ == '__main__':
    main()





