import time
import const
import logging
logger = logging.getLogger( "dispatcher.Bluescan")
import subprocess

import queue, Empty
import thread

validBluetoothId = [
    "A4:3D:78:DB:60:49",  # Lees' phone
    "A4:3D:78:DB:60:72",  # Oppo Dennis
    "98:FE:94:38:58:B4",  # cheriePhone
    ]  


class bluescan():
    def __init__(self, eventQueue):
	thread.start_new_thread(self.main, (eventQueue, ))

    def main( self, eventQueue ):
	while (True):
	    result = ""
	    for id in validBluetoothId:
		startTime = time.time()
                #logger.debug( "Searching for Bluetooth {}".format(id))
		result = subprocess.check_output(["/usr/bin/hcitool", "name",id]).strip("\r\n")
                #logger.debug( "finished searching {}, poll took {} seconds".format(id, time.time()-startTime))
		if (result !=""):
		    logger.debug( "FOUND device {}".format(result))
		    eventQueue.put([const.EVENT_BLUEDEVICE, result])
		    time.sleep(20)
		    break
	    time.sleep(.1)


