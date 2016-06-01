import threading
main_thread = threading.current_thread()
import mosquitto
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
        self.client = mosquitto.Mosquitto(clientID)
        self.socketError = False
        self.connect()

        self.t = threading.Thread(target=self.loop)
        self.t.daemon = True
        self.t.start()

    def connect(self):
        def on_message(obj, userdata, msg):
            msg.payload = msg.payload.decode('utf-8')
            logger.info("Message received on topic %s with QoS %i and payload %s"%(  msg.topic, msg.qos, msg.payload))
            event = msg.payload.split( "|")
            self.eventQueue.put(event);
            
        def on_disconnect(mosq, obj, rc):
            if (rc==1):
                logger.error("Disconnection unexpected")
                self.connect()

        def on_publish(obj, other, msg ):
            logger.info( "completed publish %s " %( msg))

        retry=True
        while ( retry ):
            try:
                self.client.connect(self.serverIP)  # pi
                self.client.subscribe(self.inTopic, 0)
                logger.info("Connecting, subscribing to topic %s" % (self.inTopic))
                self.client.on_message = on_message
                self.client.on_disconnect = on_disconnect
                self.client.on_publish = on_publish
                retry=False
            except socket_error:
                retry =  True
                self.eventQueue.put([const.EVENT_MQTTERROR,"Retry MQTT connect"])
                logger.error("Retrying MQTT connect")
                time.sleep(5)

        self.socketError = False 
                
    def publish(self, topic, msg):
        logger.info("Publishing msg %s with topic %s" %  (msg, topic))
        try:
            self.client.publish(topic,msg)
        except socket_error:
            self.eventQueue.put([const.EVENT_MQTTERROR,"socket error"])
            self.socketError = True
            logger.error("Socket error when trying to publish %s" % (msg) )
            logger.error("Socket Error Flag = %s" % (self.socketError))

            


    def loop( self ):
        while main_thread.is_alive():
            if self.socketError:
                logger.error("Socket Error Flag = %s in Loop" % (self.socketError))
                self.connect()        
                
            self.client.loop()
            time.sleep(2)

 
if __name__ == "__main__":
    logging.basicConfig()
    import queue
    q = queue.Queue()
    logger.info('starting')
    mqtt = MQTT(  "127.0.0.1", q, clientID="dispatcher", inTopic="dispatcher", outTopic="keypad" )
    while True:
        logger.info('publishing')
        mqtt.publish( 'dispatcher', '0|123')
        logger.info('waiting')
        payload = q.get(True, 300)
        q.task_done()
        print(payload)
