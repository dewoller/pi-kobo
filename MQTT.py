from threading import Thread
import mosquitto
import time
from socket import error as socket_error
import logging
import string
import const

#"""" take care of incomign and outgoing MQTT messages """"
# any incoming messages get put into the eventQueue
# outgoing messages call publish direclty

class MQTT:
    def __init__(self, eventQueue, clientID, inTopic, outTopic):
    
        self.logger = logging.getLogger(clientID + "_MQTT")
        self.eventQueue = eventQueue
	self.inTopic = inTopic
	self.outTopic = outTopic
        self.client = mosquitto.Mosquitto(clientID)
        self.connect()
        self.socketError = False

        self.t = Thread(target=self.loop)
        self.t.daemon = True
        self.t.start()

    def connect(self):
	def on_message(obj, userdata, msg):
	    self.logger.info("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)
            event = string.split(msg.payload, "|")
	    self.eventQueue.put(event);
	    
	def on_disconnect(mosq, obj, rc):
	    if (rc==1):
		self.logger.info("Disconnection unexpected")
		self.connect()

	def on_publish(obj, userdata, msg):
		self.logger.info( "completed publish %s " %( msg))

	self.socketError = False 
        retry=True
        while ( retry ):
	    self.logger.info("initial connect")
            try:
                self.client.connect("192.168.1.38")  # pi
                self.client.subscribe(self.inTopic, 0)
                self.client.on_message = on_message
                self.client.on_disconnect = on_disconnect
		self.client.on_publish = on_publish
                retry=False
            except socket_error:
                retry =  True
                self.eventQueue.put([const.EVENT_FLASHMSG,"retry MQTT connect"])
                self.logger.info("retrying connect")
                time.sleep(5)
                
    def publish(self, msg):
	self.logger.info("publishing %s" % (msg))
	msg_str = string.join(msg, "|")
        try:
	    self.client.publish(self.outTopic,msg_str, 2)
	except socket_error:
            self.eventQueue.put([const.EVENT_FLASHMSG,"socket error"])
	    self.logger.info("socket error" )
	    self.socketError = True
	    


    def loop( self ):
        while True:
	    if self.socketError:
		self.connect()	
            self.client.loop()
            time.sleep(2)

    
