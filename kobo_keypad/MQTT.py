from threading import Thread
import mosquitto
import time
from socket import error as socket_error
import logging

#"""" take care of incomign and outgoing MQTT messages """"

class MQTT:
    def __init__(self, outQ):
    
        self.logger = logging.getLogger("mosquitto")
        self.outQ = outQ
        self.client = mosquitto.Mosquitto("kobo")
        self.connect()

        self.t = Thread(target=self.loop)
        self.t.daemon = True
        self.t.start()

    def connect(self):
	def on_message(obj, userdata, msg):
	    self.logger.info("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)
	    event = [int(msg.payload[0]), msg.payload[2:]]
	    self.outQ.put(event);
	    
	def on_disconnect(mosq, obj, rc):
	    if (rc==1):
		self.logger.info("Disconnection unexpected")
		self.connect()

    
        retry=True
        while ( retry ):
	    self.logger.info("initial connect")
            try:
                self.client.connect("192.168.1.38")  # pi
		self.inTopic="keypad"
                self.client.subscribe(self.inTopic, 0)
                self.client.on_message = on_message
                self.client.on_disconnect = on_disconnect
                retry=False
            except socket_error:
                retry =  True
                self.outQ.put([5,"retry MQTT connect 2pi"])
                self.logger.info("retrying connect")
                time.sleep(5)
                
    def publish(self, msg):
	self.logger.info("publishing %s" % (msg))
        try:
	    self.outTopic="dispatcher"
	    self.client.publish(self.outTopic,msg)
	except socket_error:
            self.outQ.put([5,"socket error"])
	    self.logger.info("socket error" )
	    


    def loop( self ):
        while True:
            self.client.loop()
            time.sleep(2)

    
