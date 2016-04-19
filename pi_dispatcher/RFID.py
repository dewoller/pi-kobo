#!/bin/python 

import logging, traceback, sys
logger = logging.getLogger( "dispatcher.RFID")
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
import serial
import Queue

sm130Code = {
    "Reset": 0x80,
    "Firmware": 0x81,
    "Seek": 0x82,
    "Select": 0x83,
    "Authenticate": 0x85,
    "ReadBlock": 0x86,
    "ReadValue": 0x87,
    "WriteBlock": 0x89,
    "WriteValue": 0x8A,
    "Write4": 0x8B,
    "WriteKey": 0x8C,
    "Increment": 0x8D,
    "Decrement": 0x8E,
    "Antenna": 0x90,
    "ReadPort": 0x91,
    "WritePort": 0x92,
    "Halt": 0x93,
    "Baud": 0x94,
    "Sleep": 0x96
    }

sm130Val = dict([[v,k] for k,v in sm130Code.items()])


class RFID():
    def __init__(self, eventQueue):
        self.ser=getSerial()
        time.sleep(1)
        self.resetRFID()
        thread.start_new_thread(self.reader, (eventQueue, ))
    
    def prepareRFID( self, eventQueue ):
        eventQueue.task_done()

    def reader( self, eventQueue ):
        lastSwitch = '\x00'
        while (True):
            (eventType, payload) = self.read_command( )
            eventName = sm130Val[ eventType ]
            if eventName == 'Firmware'  or eventName == 'Reset':
                logger.info("Firmware: %s" % (payload))
            elif eventName == 'Seek' :
                if payload <> '\x4c':
                    logger.info("Real Tag: %s" % ( payload.encode("hex")))
                    eventQueue.put([const.EVENT_RFID_HASTAG,  payload])
                    self.getNextTag()
            elif eventName == 'ReadPort' :
                logger.info("Port Status %s" % ( payload.encode("hex")))
                if payload <> lastSwitch:
                    # we have a change
                    for (tbit, lbit, switch) in zip(bits(payload), bits(lastSwitch), range(2)):
                        if tbit>lbit:
                            eventQueue.put([const.EVENT_RFID_SWITCHDOWN, switch ])
                        elif tbit<lbit:
                            eventQueue.put([const.EVENT_RFID_SWITCHUP, switch ])



#EVENT_RFID_SWITCHDOWN           = "22"
#EVENT_RFID_SWITCHUP             = "28"
    def send_command(self, command, payload=''):
        packet = build_packet(command, payload)
        self.ser.write(packet)
        logger.debug(packet.encode('hex'))

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
        time.sleep(2)
    
        logger.debug("reading Port")
        sc.readPort()
        while True:
            time.sleep(.1)
            try:
                payload = q.get(True, .1)
                logger.debug("switch %s state %s" % payload)
            except Queue.Empty:
                break
        for i in range(4):
            logger.debug("Writing Port with %s" % i )
            sc.writePort( bytes(chr(i) ))
            time.sleep(.1)
    
if __name__ == '__main__':
    main()




