
#!/bin/python 

import logging, traceback, sys
logger = logging.getLogger(__name__)

import time
import const
from threading import Timer
import queue
import requests
from dateutil import parser
from datetime import datetime, timezone

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
    
    def getNextTrains( self ):
        rv = []
        trainsJSON = requests.get( url=nextTrainURL, params=nextTrainParams ).json()
        for train in trainsJSON['values']:
             if train['platform']['direction']['direction_id']==1:
                 rv.append( parser.parse(train['time_timetable_utc']) )
        return rv

    # continuiously runs, reading and posting train notifications on event queue
    # always ends with a Timer set to run again as needed
    def scheduleNextNotification( self ):
        if len(self.nextTrains) == 0:
            self.getNextTrains()
        nextTrain = self.nextTrains[0]
        tm = datetime.now( timezone.utc )
        if nextTrain < tm:
            # past by
            self.nextTrains.pop(0)
            return( self.scheduleNextNotification() )
        secondsRemaining = (nextTrain - tm ).seconds
        minutesRemaining = secondsRemaining / 60
        if minutesRemaining<= 7: 
            self.eventQueue.put([const.EVENT_NEXTTRAIN,  minutesRemaining ])
            if minutesRemaining<=1:
                self.nextTrains.pop(0)
                return( self.scheduleNextNotification() )
            secsUntilNextEvent = 55
        else:
            secsUntilNextEvent = max( 10, secondsRemaining - 420 )
        Timer( secsUntilNextEvent, self.scheduleNextNotification).start()
        logger.info('Next train notification in %i seconds' % secsUntilNextEvent )
        

def main( ):
    q=queue.Queue()
    wc = webConnect(q)
    print (wc.nextTrains)


    
if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    main()




