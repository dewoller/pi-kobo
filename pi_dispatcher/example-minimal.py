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

import fauxmo
import logging
import threading
import time
import paho.mqtt.client as paho
from debounce_handler import debounce_handler

# ---------- Network constants -----------
MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
# ---------- Network constants -----------

logging.basicConfig(level=logging.DEBUG)

class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """
    TRIGGERS = {
            "water": 52000
            , "door": 52001
            , "irrigate": 52002
            }

    def __init__(self, mqtt):
        debounce_handler.__init__(self)
        self.mqtt = mqtt

    def act(self, client_address, state, name):
        logging.debug("client %s state %s name %s" % (client_address, state,name) )
        if name=="water" and state==True:
            self.mqtt.publish("waterBalcony", "300")
        elif name=="irrigate" and state==True:
            self.mqtt.publish("waterParkingLot", "300")
        elif name=="door" and state==True:
            self.mqtt.publish("door", "unlock")
        elif name=="door" and state==False:
            self.mqtt.publish("door", "lock")
        elif (name=="irrigate" ) and state==False:
            self.mqtt.publish("irrigate", "off")
        elif (name=="water") and state==False:
            self.mqtt.publish("waterBalcony", "off")

        return True

if __name__ == "__main__":
    # Startup the MQTT client in a separate thread
    mqtt = paho.Client(client_id="testuser", clean_session=True)
    mqtt.connect(MQTT_HOST, MQTT_PORT, 60)
    mqtt.publish("fauxmo", "starting", qos=1, retain=True)
    ct = threading.Thread(target=mqtt.loop_forever)
    ct.daemon = True
    ct.start()

    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    d = device_handler( mqtt )
    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            time.sleep(0.1)
        except Exception, e:
            logging.critical("Critical exception: " + str(e))
            break
