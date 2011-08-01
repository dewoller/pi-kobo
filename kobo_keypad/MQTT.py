from threading import Thread
import mosquitto
import time

#"""" take care of incomign and outgoing MQTT messages """"

class MQTT:

    def __init__(self, outQ):
        def on_message(obj, userdata, msg):
            print("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)
            event = [int(msg.payload[0]), msg.payload[2:]]
            self.outQ.put(event);

        self.outQ = outQ
        self.client = mosquitto.Mosquitto("kobo")
        self.client.connect("192.168.2.1")
        #self.client.connect("localhost")
        inTopic="keypad"
        self.outTopic="dispatcher"
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

    
