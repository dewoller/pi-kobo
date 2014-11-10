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
    def __init__(self, serverIP, eventQueue, clientID, inTopic, outTopic):
    
        self.serverIP =  serverIP
        self.logger = logging.getLogger(clientID + "_MQTT")
        self.eventQueue = eventQueue
	self.inTopic = inTopic
	self.outTopic = outTopic
        self.client = mosquitto.Mosquitto(clientID)
        self.socketError = False
        self.logger.debug("Socket Error Flag = %s" % (self.socketError))
        self.connect()

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

	def on_publish(obj, other, msg ):
	    self.logger.debug( "completed publish %s " %( msg))
	    self.logger.debug("Socket Error Flag = %s" % (self.socketError))

        retry=True
        while ( retry ):
            try:
                self.client.connect(self.serverIP)  # pi
                self.client.subscribe(self.inTopic, 0)
	        self.logger.info("Connecting, subscribing to topic %s" % (self.inTopic))
		self.logger.debug("Socket Error Flag = %s" % (self.socketError))
                self.client.on_message = on_message
                self.client.on_disconnect = on_disconnect
		self.client.on_publish = on_publish
                retry=False
            except socket_error:
                retry =  True
                self.eventQueue.put([const.EVENT_FLASHMSG,"Retry MQTT connect"])
                self.logger.info("Retrying MQTT connect")
                time.sleep(5)

	self.socketError = False 
                
    def publish(self, msg):
	self.logger.info("Publishing msg %s with topic %s" %  (msg, self.outTopic))
	self.logger.debug("Socket Error Flag = %s" % (self.socketError))
        try:
	    self.client.publish(self.outTopic,string.join(msg, "|"), 2)
	except socket_error:
            self.eventQueue.put([const.EVENT_FLASHMSG,"socket error"])
	    self.socketError = True
	    self.logger.info("Socket error when trying to publish %s" % (msg) )
	    self.logger.debug("Socket Error Flag = %s" % (self.socketError))

	    


    def loop( self ):
        while True:
	    if self.socketError:
		self.logger.debug("Socket Error Flag = %s in Loop" % (self.socketError))
		self.connect()	
		
            self.client.loop()
            time.sleep(2)

    
