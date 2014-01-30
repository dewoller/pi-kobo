import pdb 
#pdb.set_trace()
from MQTT import MQTT
from Pins import Pins
from Queue import Queue




class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


def process( payload ):
    print("processing payload %s" % payload)
    #pdb.set_trace()
    if payload == "119":
        p.unlock()
    elif payload == "666":
        p.disableAllPins()
    elif payload[0:3] == "999":
        pin = int(payload[3:4])
        duration = int(payload[4:])
        p.water(pin, duration)
    else:
        print "Huh?"



q = Queue()
m = MQTT( q )
p=Pins()

while True:
    try:
        payload = q.get(True, 20)
        process( payload )
        q.task_done()
    except Exception as e:
            print e
    




