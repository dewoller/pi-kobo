import threading
main_thread = threading.current_thread()
import paho.mqtt.client as client 
import paho.mqtt.publish as publish
import time
from socket import error as socket_error
import logging
logger = logging.getLogger(__name__)
if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
import string
import const

#"""" take care of incomign and outgoing MQTT messages """"
# any incoming messages get put into the eventQueue
# outgoing messages call publish direclty




class MQTT:
    def __init__(self, serverIP, eventQueue, clientID, inTopic, outTopic):
    
        logger.info("Starting")
        self.serverIP =  serverIP
        self.eventQueue = eventQueue
        self.inTopic = inTopic
        self.outTopic = outTopic
        self.client = client.Client( clientID )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(serverIP, 1883, 60)
        self.client.subscribe(self.inTopic)
        self.client.loop_start()
        logger.info("finished starting")


    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.inTopic + "/#")

    # The callback for when a PUBLISH message is received from the server.
    # can be published as /inTopic/, message 0|keystrokes
    # or /inTopic/subTopic, message details
    def on_message(self, client, userdata, msg):
        msg.payload = msg.payload.decode('utf-8')
        logger.info("Message received on topic %s with QoS %i and payload %s"%(  msg.topic, msg.qos, msg.payload))
        event=['','']
        # strip out inTopic, leave the chunk at the end as the payload 
        # e.g. dispatcher/water/balcony, 600
        event[0] = msg.topic[ (len(self.inTopic )+1): ]  
        event[1] = msg.payload

        self.eventQueue.put(event);

    def publish(self, topic, msg=''):
        
        logger.info("Publishing msg %s with topic %s" %  (msg, topic))
        try:
            publish.single(topic,msg, hostname= self.serverIP)
        except socket_error:
            self.eventQueue.put([const.EVENT_MQTTERROR,"socket error"])
            self.socketError = True
            logger.error("Socket error when trying to publish %s" % (msg) )
            logger.error("Socket Error Flag = %s" % (self.socketError))

            


 
if __name__ == "__main__":
    logging.basicConfig()
    import queue
    q = queue.Queue()
    logger.info('starting')
    mqtt = MQTT(  "127.0.0.1", q, clientID="door", inTopic="dispatcher", outTopic="keypad" )
    while True:
        time.sleep(3)
        logger.info('publishing')
        mqtt.publish( 'dispatcher/unlock')
        #mqtt.publish( 'dispatcher', '0|123')
        logger.info('waiting')
        payload = q.get(True, 300)
        q.task_done()
        logger.info(payload)
