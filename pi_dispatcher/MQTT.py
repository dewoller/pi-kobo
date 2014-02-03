from threading import Thread
import mosquitto
import time

#"""" take care of incomign and outgoing MQTT messages """"
class MQTT:

    def __init__(self, outQ):
        def on_message( obj, userdata, msg):
            print("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)
            self.q.put(msg.payload);

        self.q = outQ
        self.client = mosquitto.Mosquitto("pi")
        self.client.connect("127.0.0.1")
        #self.client.connect("192.168.1.12")
        inTopic="dispatcher"
        self.outTopic="keypad"
        self.client.subscribe(inTopic, 0)
        self.client.on_message = on_message
        self.t = Thread(target=self.loop)
        self.t.daemon = True
        self.t.start()

    def publish(self, msg):
        self.client.publish(self.outTopic,msg)


    def loop( self ):
        while True:
            self.client.loop()
            time.sleep(0.5)

    
