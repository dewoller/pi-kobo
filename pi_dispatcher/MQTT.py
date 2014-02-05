from threading import Thread
import mosquitto
import time
import logging
logger = logging.getLogger()

#"""" take care of incomign and outgoing MQTT messages """"
class MQTT:

    def __init__(self, outQ):

        def on_message( obj, userdata, msg):
            logger.info("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)
            self.q.put(msg.payload);

        def on_disconnect(mosq, obj, rc):
            if (rc==1):
                logger.info("Unexpected disconnection to MQTT server, retrying ")
                self.connect()

        self.q = outQ
        self.client = mosquitto.Mosquitto("pi")
        self.connect()

        inTopic="dispatcher"
        self.outTopic="keypad"
        self.client.subscribe(inTopic, 0)
        self.client.on_message = on_message
        self.t = Thread(target=self.loop)
        self.t.daemon = True
        self.t.start()

    def publish(self, msg):
        self.client.publish(self.outTopic,msg)

    def connect(self):
    
        retry=True
        while ( retry ):
            try:
                self.client.connect("127.0.0.1")  # pi
		logger.info("connecting to remote MQTT Server")
                retry=False
            except socket_error:
                retry =  True
                time.sleep(5)
		logger.info("retrying connection to remote MQTT Server")

    def loop( self ):
        while True:
            self.client.loop()
            time.sleep(0.5)

    
