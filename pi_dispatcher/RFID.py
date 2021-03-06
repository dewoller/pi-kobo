#!/bin/python 

import logging, traceback, sys
logger = logging.getLogger(__name__)

import time
import const
import struct
import queue
import serial
import threading
main_thread = threading.current_thread()

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

def encode2hex( packet ):
    return( ''.join(format(x, '02x') for x in packet) )

class RFID():
    def __init__(self, eventQueue):
        logger.info("Starting")
        self.eventQueue = eventQueue
        self.ser=getSerial()
        time.sleep(.1)
        self.resetRFID()
        time.sleep(.1)
        self.getFirmwareVersion()
        time.sleep(.1)
        self.readTag()
        self.currentWritePort = 0
        self.t = threading.Thread(target=self.reader)
        self.t.daemon = True
        self.t.start()
    
    def prepareRFID( self ):
        self.eventQueue.task_done()

    # continuiously runs, reading and posting tags on event queue
    def reader( self ):
        logger.info("Inside RFID reader")
        while (main_thread.is_alive()):
            try:   ## make sure this thing does not crash due to transient electrical things
                ## maybe put self.readTag here so that we are really ALWAYS reading tags
                (eventType, payload) = self.read_command( )
                try:
                    eventName = sm130Val[ eventType ]
                except KeyError:
                    logger.error("Key Error read from serial %s" % eventType)
                    #self.readTag()  # dont care what happened, get back to reading tags
                    continue

                if eventName == 'Firmware'  or eventName == 'Reset':
                    logger.info("Firmware: %s" % (payload))
                    self.readTag()  # our job is to always be reading tags
                elif eventName == 'Seek' :
                    if payload != b'\x4c':
                        tag =encode2hex( payload )
                        logger.info("Real Tag: %s" % ( tag ))
                        self.eventQueue.put([const.EVENT_RFID_HASTAG,  tag ])
                        time.sleep(.01)
                        self.getNextTag()
                elif (eventName == 'Halt') or (eventName == 'WritePort' ) :
                    time.sleep(.01)
                    self.readTag() # get back to reading tags
                else:
                    logger.error("Unhandled RFID event %s" % eventName)
                    self.readTag()  # dont care what happened, get back to reading tags
            except KeyboardInterrupt:
                System.exit(0)
            except Exception:
                logger.error( "Other RFID error:")
                time.sleep(.1)
                logger.error(traceback.format_exc())
                #self.readTag()  # dont care what happened, get back to reading tags
                continue
        
    def send_command(self, command, payload=''):
        packet = build_packet(command, payload)
        self.ser.write(packet)
        logger.debug("Sent a packet %s" % encode2hex( packet ))

    def read_command(self ):
        header = ""
        while header != b"\xff":
            header = self.ser.read(1)
        
        reserved, len, response_to = struct.unpack('BBB', self.ser.read(3))
        try:
            assert header == b'\xff'
            assert reserved == 0  
            response = self.ser.read(len - 1)
            response_checksum = struct.unpack("B", self.ser.read(1)) [0]
            computed_checksum = build_packet(response_to, response)[-1]
            assert computed_checksum == response_checksum
        except AssertionError:
            logger.error("Serial read error")
            return ("","")
        return (response_to, response)

    def getFirmwareVersion(self): 
        self.send_command(sm130Code['Firmware'])

    def resetRFID(self): 
        self.send_command(sm130Code['Reset'])

    def getNextTag(self): 
        self.haltTag()
    
    def readTag(self): 
        self.send_command(sm130Code['Seek'])

    def readPort(self): 
        self.send_command(sm130Code['ReadPort'])

    def writePort(self, value): 
        self.send_command(sm130Code['WritePort'], struct.pack("B",value))

    def lightOn(self, whichLight): 
        self.currentWritePort = self.currentWritePort | 1 << whichLight
        self.writePort( self.currentWritePort )

    def lightOff(self, whichLight): 
        self.currentWritePort = self.currentWritePort & (~ (1 << whichLight ))
        self.writePort( self.currentWritePort )

    def haltTag(self): 
        self.send_command(sm130Code['Halt'])

def getSerial(dev="/dev/ttyAMA0", baudrate=19200, timeout=.1):
    return( serial.Serial(dev, 19200, timeout=timeout))

def sm130_checksum(packet):
    return sum(x for x in packet) % 256

def build_packet(command, payload):
    packet = struct.pack('BBB', 0x00, len(payload) + 1, command)
    if len(payload) > 0:
        packet += payload
    packet = b'\xff' + packet + struct.pack('B', sm130_checksum(packet))
    return packet

def bits( number ):
     return [int(i) for i in list(bin(number)[2:])]

def mai1( ):
    q=queue.Queue()
    sc = RFID(q)
    while True:
        logger.debug("getting Firmware")
        sc.getFirmwareVersion()
        time.sleep(1)   # check for timeout
        logger.debug("getting Tag")
        sc.readTag()
        time.sleep(10)
        for i in range(4):
            logger.debug("Writing Port with %s" % i )
            sc.writePort( i )
            time.sleep(5)

def main():
        q=queue.Queue()
        sc = RFID(q)
        while True:
                time.sleep(3)
                logger.info('TESTING: waiting in main testing harness loop')
                payload = q.get(True, 3000)
                q.task_done()
                logger.info(payload)
        
if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    main()




