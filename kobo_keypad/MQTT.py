from threading import Thread
import mosquitto
import time
from socket import error as socket_error

#"""" take care of incomign and outgoing MQTT messages """"

class MQTT:

    def __init__(self, outQ):
        def on_message(obj, userdata, msg):
            print("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)
            event = [int(msg.payload[0]), msg.payload[2:]]
            self.outQ.put(event);
            
        def on_disconnect(mosq, obj, rc):
            if (rc==1):
                print("Disconnection unexpected")
                self.connect()
    
        self.outQ = outQ
        self.client = mosquitto.Mosquitto("kobo")
        self.connect()

        inTopic="keypad"
        self.outTopic="dispatcher"
        self.client.subscribe(inTopic, 0)
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        self.t = Thread(target=self.loop)
        self.t.daemon = True
        self.t.start()

    def connect(self):
    
        retry=True
        while ( retry ):
            try:
                self.client.connect("192.168.1.38")  # pi
                retry=False
            except socket_error:
                retry =  True
                self.outQ.put([5,"retry MQTT connect 2pi"])
                time.sleep(5)
                
    def publish(self, msg):
        try:
	    self.client.publish(self.outTopic,msg)
	except socket_error:
            self.outQ.put([5,"socket error"])
	    


    def loop( self ):
        while True:
            self.client.loop()
            time.sleep(2)

    
