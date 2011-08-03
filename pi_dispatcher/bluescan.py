import time
import const
import logging
logger = logging.getLogger( "Bluescan")
import subprocess

from Queue import Queue, Empty
import thread


class bluescan():
    def __init__(self, eventQueue, ids):
	self.ids = ids
	thread.start_new_thread(self.main, (eventQueue, ))

    def main( self, eventQueue ):
	while (True):
	    result = ""
	    for id in self.ids:
		result += subprocess.check_output(["/usr/bin/hcitool", "name",id])
	    if (result !=""):
		logger.debug( "Bluetooth device nearby %s " % (result))
		eventQueue.put([const.EVENT_BLUEDEVICE])
		time.sleep(30)
	    time.sleep(10)



