import time
import const
import logging
logger = logging.getLogger( "dispatcher.Bluescan")
import subprocess

from Queue import Queue, Empty
import thread

validBluetoothId = [
    "B0:EC:71:C9:28:0E",	  #Lees' phone
    "A4:3D:78:DB:60:72", # Oppo Dennis
    "00:18:6B:30:47:00",  # White LG headset
    "00:18:6B:A4:3D:FF",  # black LG  headset
    ]  


class bluescan():
    def __init__(self, eventQueue):
	thread.start_new_thread(self.main, (eventQueue, ))

    def main( self, eventQueue ):
	while (True):
	    result = ""
	    for id in validBluetoothId:
		startTime = time.time()
                logger.debug( "Searching for Bluetooth {}".format(id))
		result = subprocess.check_output(["/usr/bin/hcitool", "name",id])
                logger.debug( "finished searching {}, poll took {} seconds".format(id, time.time()-startTime))
		if (result !=""):
		    logger.debug( "FOUND device {}".format(result))
		    eventQueue.put([const.EVENT_BLUEDEVICE])
		    time.sleep(20)
		    break
	    time.sleep(.1)


