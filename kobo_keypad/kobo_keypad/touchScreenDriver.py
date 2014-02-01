#!/usr/bin/python
import struct
import  time
import thread
from Queue import Queue

tsdevice = "/dev/input/event1"
keydevice = "/dev/input/event0"
format = "iihhi"
buff=""
xs=[]
ys=[]


touchscreen = open(tsdevice,"rb")

        
def get_touch_input(q):
    """Runs in a loop getting the touch position"""
    while (1):
        ts_event= touchscreen.read(16)
        q.put(ts_event)

def processTsEvent( ts_event ):
    global xs, ys
    (ts_time1, ts_time2, ts_type, ts_code, ts_value) = struct.unpack(format,ts_event)

    if (ts_type == 3): 
	# touch down Event
	if ts_code == 0 :
	    xs.append( ts_value)
	if ts_code == 1 :
	    ys.append( ts_value )
    
def process_touch_input( processedQueue ):
    """Runs in a loop getting the touch position"""
    import pdb; pdb.set_trace();
    global xs, ys
    tsq = Queue()
    waitDuration=.1
    thread.start_new_thread(get_touch_input, (tsq, ))
    while (1):
        try:
            processTsEvent( tsq.get( True, waitDuration))
        except:
            # we have a break in the stream, time to summarise
            if (len(xs) > 0):
		x=sum(xs) / len(xs)
		y=sum(ys) / len(ys)
		xs=[]
		ys=[]
		processedQueue.put( (x,y))


