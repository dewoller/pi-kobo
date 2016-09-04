
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
nextTrainURL = "https://www.ptv.vic.gov.au/langsing/stop-services"
        
# get the next 20 trains
# store city bound trains and time leaving
# at 7..1 minutes to train departure, display
# when last train gone, get next 20 trains
class webConnect():
    def __init__(self, eventQueue):
        logger.info("Starting")
        self.nextTrains = self.getNextTrains()
        self.eventQueue = eventQueue
        self.scheduleNextNotification()
    
    def getNextTrains( self ):
        rv = []
        trainsJSON={}
        trainsJSON['values']=[]
        try:
            trainsJSON = requests.get( url=nextTrainURL, params=nextTrainParams ).json()
        except ValueError:
            logger.warning("Error when getting URL %s" % nextTrainURL)

        for train in trainsJSON['values']:
            #print("Train %s dir %i" % 
            if ((   train['platform']['direction']['direction_id']==0 
                    or train['platform']['direction']['direction_id']==1 
                )
                    and 
                (
                    train['run']['destination_name'] == "Flinders Street"
                    or train['run']['destination_name'] == "Parliament"
                    or train['run']['destination_name'] == "Heidelberg"
                )):
                rv.append( parser.parse(train['time_timetable_utc']) )
            elif train['platform']['direction']['direction_id']!=8:
                logger.warning("I have a train going direction %i and destination %s" % ( 
                     train['platform']['direction']['direction_id'], train['run']['destination_name']))
        return rv

    # continuiously runs, reading and posting train notifications on event queue
    # always ends with a Timer set to run again as needed
    def scheduleNextNotification( self ):

        secondsRemaining = self.secondsUntilNextTrain()
        if secondsRemaining <0  : # we had an error, wait an hour until trying again
            secondsRemaining=60*60 
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
        logger.info('Next train notification check in %i seconds' % secsUntilNextEvent )

    def notifyNextTrain( self ):        
        secondsRemaining = self.secondsUntilNextTrain()
        if secondsRemaining >0  : # if we had an error, do nothing
            minutesRemaining = secondsRemaining / 60
            self.eventQueue.put([const.EVENT_NEXTTRAIN,  minutesRemaining ])

    def secondsUntilNextTrain( self ):        
        if len(self.nextTrains) == 0:
            self.getNextTrains()
        if len(self.nextTrains) == 0:  # error, we have no trains
            return(-1)
        nextTrain = self.nextTrains[0]
        tm = datetime.now( timezone.utc )
        if nextTrain < tm:
            # past by
            self.nextTrains.pop(0)
            return( self.secondsUntilNextTrain() )
        return (nextTrain - tm ).seconds

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




