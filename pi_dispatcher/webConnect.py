
#!/bin/python 

import logging, traceback, sys
logger = logging.getLogger( "dispatcher.webConnect")
if __name__ == '__main__' and __package__ is None:
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

import time
import const
from threading import Timer
import queue
import requests
from dateutil import parser
import datetime

nextTrainParams = dict(
    stopId=10001168,
    limit=20,
    mode=0
)
nextTrainURL = "https://ptv.vic.gov.au/transport/direct/chronos.php"
        
# get the next 20 trains
# store city bound trains and time leaving
# at 7..1 minutes to train departure, display
# when last train gone, get next 20 trains
class webConnect():
    def __init__(self, eventQueue):
        self.nextTrains = self.getNextTrains()
        self.eventQueue = eventQueue
        self.scheduleNextNotification()
    
    def getTrains( self ):
        rv = []
        trainsJSON = requests.get( url=nextTrainURL, params=nextTrainParams ).json()
        for train in trainsJSON['values']:
             if train['platform']['direction']['direction_id']==1:
                 rv.append( parser.parse(train['time_timetable_utc']) )
        return rv



    # continuiously runs, reading and posting tags on event queue
    def scheduleNextNotification( self ):
        if len(self.nextTrains) == 0:
            self.getTrains()
        nextTrain = self.nextTrains[0]
        tm = datetime.now( timezone.utc )
        if nextTrain < tm:
            # past by
            self.nextTrains.pop(0)
            return( self.scheduleNextNotification() )
        secondsRemaining = tm < nextTrain
        minutesRemaining = round( secondsRemaining / 60, 0 )
        if minutesRemaining<= 7: 
            eventQueue.put([const.EVENT_NEXTTRAIN,  minutesRemaining ])
            if minutesRemaining<=1:
                self.nextTrains.pop(0)
                return( self.scheduleNextNotification() )
            secsUntilNextEvent = 60
        else:
            secsUntilNextEvent = max( 10, secondsRemaining - 420 )
        Timer( secsUntilNextEvent, self.scheduleNextNotification)
        

def main( ):
    q=queue.Queue()
    
if __name__ == '__main__':
    main()




