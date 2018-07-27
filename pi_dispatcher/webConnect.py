
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
    limit=10,
    mode=0
)
nextTrainURL = "https://www.ptv.vic.gov.au/langsing/stop-services"
        
# get the next 10 trains
# store city bound trains and time leaving
# at 7..1 minutes to train departure, display
# when last train gone, get next 10 trains
class webConnect():
    def __init__(self, eventQueue):
        logger.info("Starting")
        self.htmlErrorDelay=0
        self.eventQueue = eventQueue

        try:
            self.getNextTrains()
            self.scheduleNextNotification()
        except Exception:
            pass # I don't care if trains dont work
    
    def getNextTrains( self ):
        self.nextTrains = []
        trainsJSON={}
        trainsJSON['values']=[]
        time.sleep(self.htmlErrorDelay)
        try:
            trainsJSON = requests.get( url=nextTrainURL, params=nextTrainParams ).json()
        except ValueError:
            logger.warning("Error when getting URL %s" % nextTrainURL)

        logger.info( "ntrains = %s",len( trainsJSON['values'] ))
        for train in trainsJSON['values']:
            #print("Train %s dir %i" % 
            if ((   train['platform']['direction']['direction_id']==0 
                    or train['platform']['direction']['direction_id']==1 
                )
                    and 
                (
                    train['run']['destination_name'] == "Flinders Street"
                    or train['run']['destination_name'] == "Clifton Hill"
                    or train['run']['destination_name'] == "Parliament"
                    or train['run']['destination_name'] == "Heidelberg"
                )):
                self.nextTrains.append( parser.parse(train['time_timetable_utc']) )
                logger.info( train['time_timetable_utc'] ) 
            elif train['platform']['direction']['direction_id']!=8:
                logger.warning("I have a train going direction %i and destination %s" % ( 
                     train['platform']['direction']['direction_id'], train['run']['destination_name']))

        if ( len( self.nextTrains ) == 0):
            # we had an error, wait until trying again
            self.htmlErrorDelay=max( (self.htmlErrorDelay + 1) * 2, 3600)
            raise ValueError('No Trains')
        else:
            self.htmlErrorDelay=0

        return 

    # continuiously runs, reading and posting train notifications on event queue
    # always ends with a Timer set to run again as needed
    def scheduleNextNotification( self ):
        secsUntilNextEvent = 55

        try:
            secondsRemaining = self.secondsUntilNextTrain()
        except ValueError:
            Timer( secsUntilNextEvent, self.scheduleNextNotification).start()
            return

        self.eventQueue.put([const.EVENT_NEXTTRAIN,  secondsRemaining ])
        if secondsRemaining < secsUntilNextEvent:
            self.nextTrains.pop(0)
        Timer( secsUntilNextEvent, self.scheduleNextNotification).start()
        logger.debug('Next train notification check in %i seconds' % secsUntilNextEvent )

    def notifyNextTrain( self ):        
        try:
            self.eventQueue.put([const.EVENT_NEXTTRAIN, self.secondsUntilNextTrain()])
        except ValueError:
            return

    def secondsUntilNextTrain( self ):        
        if len(self.nextTrains) == 0: # we have no trains, go get some
            self.getNextTrains()   # might raise ValueError, but taken care of in outer level

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




