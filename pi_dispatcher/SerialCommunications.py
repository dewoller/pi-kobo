import logging, traceback
logger = logging.getLogger( "dispatcher.serial")
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

import time, sys
import const
import subprocess

from Queue import Queue, Empty

import serial.tools.list_ports
import serial, re 

import thread, sys


class SerialCommunications():
    def __init__(self, eventQueue):
	self.ser=serial.Serial()
	thread.start_new_thread(self.main, (eventQueue, ))
	self.hasError = False

    def main( self, eventQueue ):
	while (True):
	    portName = self.getPort()
            while portName == '':
                time.sleep(1)
                portName = self.getPort()

            logger.debug( "using port {}" .format(portName))
            self.initPort(portName)
            self.hasError=False
            while (not self.hasError):
                try:
                    logger.debug("about to read") 
                    result = self.readlineCR().rstrip("\r").rstrip("\n")
                    #logger.debug( "Serial Communication Encountered {}, " .format( result))
                    if result <> "":    
                        eventQueue.put([const.EVENT_KEYS,  result])
                except (IOError,ValueError) as e:
                    logger.error( "Reading Error {} {} " .format(e.errno, e.strerror))
                    if self.ser.isOpen():
                        self.ser.close()
                    #time.sleep(5)
                    self.hasError=True
                except Exception:
                    logger.error( "Other error:")
                    logger.error(traceback.format_exc())
                    self.hasError=True

    def initPort(self, portName):
        try:
            logger.debug("About to open port") 
            self.ser=serial.Serial(portName, 115200, timeout=20.0 )
            logger.debug("opened port") 
        except (IOError, ValueError) as e:
            logger.error( "Opening Error {} {} " .format(e.errno, e.strerror))
            #time.sleep(10)
        except Exception:
	    #import pdb; pdb.set_trace()
            logger.error(traceback.format_exc())

    def getPort(self):
        for port, desc, hwid in  serial.tools.list_ports.comports():
            print port
            if re.search('/dev/ttyACM.', port,re.I ): 
                return port
        logger.error("There is no port to open")
        return '' 


    def readlineCR(self):
        rv = ""
        while True:
            ch = self.ser.read()
            rv += ch
            if ch=='\r' or ch=='':
                return rv

    def publish(self, command):
        if self.hasError:
            logger.error( "Attempting to write when port closed, will try later")
            return
        try:
            self.ser.write( "%03d:%s\n"% (command[0], command[1]) )
            logger.debug( "Sending Command {}" .format(command))
        except Exception: 
            self.hasError=True
            logger.debug(traceback.format_exc())


def main( ):
    # testing harness code
    q=Queue()
    sc = SerialCommunications(q)
    while True:
	i=0	
	try:
            print "about to get keys" 
	    payload = q.get(True)
            print "got keys %s" % payload
            i = i + 1
            sc.publish([1,"hello %i" % i])
            time.sleep(2)
	    q.task_done()
	except Empty as e:
	    pass
	except Exception as e:
            time.sleep(2)
            logger.debug( "writing error:", sys.exc_info()[0])
	    pass
	except KeyboardInterrupt:
            sys.exit()

    
if __name__ == '__main__':
    main()




