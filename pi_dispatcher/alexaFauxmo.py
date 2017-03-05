""" fauxmo_minimal.py - Fabricate.IO

    This is a demo python file showing what can be done with the debounce_handler.
    The handler prints True when you say "Alexa, device on" and False when you say
    "Alexa, device off".

    If you have two or more Echos, it only handles the one that hears you more clearly.
    You can have an Echo per room and not worry about your handlers triggering for
    those other rooms.

    The IP of the triggering Echo is also passed into the act() function, so you can
    do different things based on which Echo triggered the handler.
"""

import logging, traceback
logger = logging.getLogger(__name__)
if __name__ == '__main__' and __package__ is None:
    import sys
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

import fauxmo
import threading
import time
from debounce_handler import debounce_handler

# ---------- Network constants -----------
MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
# ---------- Network constants -----------

logging.basicConfig(level=logging.DEBUG)

import const
main_thread = threading.current_thread()
TRIGGERS = {
          "water":      52000
        , "door":       52001
        , "irrigate":   52002
        }


class alexaFauxmo():
    def __init__(self, eventQueue):
        logger.info("Starting")
        self.eventQueue = eventQueue

        t=threading.Thread( target=self.main )
        t.daemon = True
        t.start()
        # Startup the fauxmo server
        fauxmo.DEBUG = True
        self.p = fauxmo.poller()
        self.u = fauxmo.upnp_broadcast_responder()
        self.u.init_socket()
        self.p.add(self.u)

        # Register the device callback as a fauxmo handler
        self.d = device_handler( self.eventQueue )
        for trig, port in TRIGGERS.items():
            fauxmo.fauxmo(trig, self.u, self.p, None, port, self.d)


    def main( self ):
        # Loop and poll for incoming Echo requests
        logging.debug("Entering fauxmo polling loop")
        while True:
            try:
                # Allow time for a ctrl-c to stop the process
                self.p.poll(100)
                time.sleep(0.1)
            except Exception as e:
                logging.critical("Critical exception: " + str(e))
                break



class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """

    def __init__(self, eventQueue ):
        debounce_handler.__init__(self)
        self.eventQueue = eventQueue

    # TODO convert to direct pushes to the eventqueue
    def act(self, client_address, state, name):
        logging.debug("client %s state %s name %s" % (client_address, state,name) )
        if name=="water" and state==True:
            self.eventQueue.put([const.EVENT_WATER3,  300])
        elif name=="irrigate" and state==True:
            self.eventQueue.put([const.EVENT_WATER1,  300])
        elif name=="door" and state==True:
            self.eventQueue.put([const.EVENT_UNLOCKED,  0])
        elif name=="door" and state==False:
            self.eventQueue.put([const.EVENT_LOCKED,  0])
        elif (name=="irrigate" ) and state==False:
            self.eventQueue.put([const.EVENT_WATER1,  -1])
        elif (name=="water") and state==False:
            self.eventQueue.put([const.EVENT_WATER3,  -1])

        return True



def main( ):
    import queue
    q = queue.Queue()
    sc = alexaFauxmo(q)
    while True:
        logger.info( "waiting for alexa " )
        payload = q.get(True)
        q.task_done()
        logger.info( "got keys %s" % payload)
        if payload[1]==const.EVENT_LOCKED:
            break

    
if __name__ == '__main__':
    main()

