
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
import thread, sys, struct
from threading import Timer
import Queue
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
        while (True):
            (eventType, payload) = self.read_command( )
            eventName = sm130Val[ eventType ]
            if eventName == 'Firmware'  or eventName == 'Reset':
                logger.info("Firmware: %s" % (payload))
                self.readTag()  # our job is to always be reading tags
            elif eventName == 'Seek' :
                if payload <> '\x4c':
                    tag =payload.encode("hex") 
                    logger.info("Real Tag: %s" % ( tag ))
                    eventQueue.put([const.EVENT_RFID_HASTAG,  tag ])
                    self.getNextTag()
            else:
                self.readTag()  # dont care what happened, get back to reading tags
        
    def send_command(self, command, payload=''):
        packet = build_packet(command, payload)
        self.ser.write(packet)
        logger.debug("Sent a packet %s" % packet.encode('hex'))

    def read_command(self ):
        header = ""
        while header <> "\xff":
            header = self.ser.read(1)
        reserved, len, response_to = struct.unpack('BBB', self.ser.read(3))
        try:
            assert header == '\xff'
            assert reserved == 0x00
            response = self.ser.read(len - 1)
            response_checksum = self.ser.read(1)
            computed_checksum = build_packet(response_to, response)[-1]
            assert computed_checksum == response_checksum
        except AssertionError:
            logging.info("Serial read error")
            return ("","")
        return (response_to, response)


    def hexput(self, str):
        self.ser.write( str.decode("hex"))

    def getFirmwareVersion(self): 
        self.send_command(sm130Code['Firmware'])

    def resetRFID(self): 
        self.send_command(sm130Code['Reset'])

    def getNextTag(self): 
        time.sleep(.01)
        self.haltTag()
        time.sleep(.01)
        self.readTag()
    
    def readTag(self): 
        self.send_command(sm130Code['Seek'])

    def readPort(self): 
        self.send_command(sm130Code['ReadPort'])

    def writePort(self, value): 
        self.send_command(sm130Code['WritePort'], value)

    def haltTag(self): 
        self.send_command(sm130Code['Halt'])

def getSerial(dev="/dev/ttyAMA0", baudrate=19200, timeout=.1):
    return( serial.Serial(dev, 19200, timeout=timeout))

def sm130_checksum(packet):
    return sum(ord(x) for x in packet) % 256

def build_packet(command, payload):
    packet = struct.pack('BBB', 0x00, len(payload) + 1, command)
    packet += payload
    packet = '\xff' + packet + struct.pack('B', sm130_checksum(packet))
    return packet

def bits( number ):
     return [int(i) for i in list(bin(number)[2:])]

def main( ):
    q=Queue.Queue()
    sc = RFID(q)
    while True:
#EVENT_RFID_READPORT             = "25"
#EVENT_RFID_WRITEPORT            = "26"
        logger.debug("getting Firmware")
        sc.getFirmwareVersion()
        time.sleep(1)   # check for timeout
        logger.debug("getting Tag")
        sc.readTag()
        time.sleep(10)
    
        for i in range(4):
            logger.debug("Writing Port with %s" % i )
            sc.writePort( bytes(chr(i) ))
            time.sleep(.1)
    
if __name__ == '__main__':
    main()




