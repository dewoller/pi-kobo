#!/usr/bin/python
import struct
import  time
from threading import Thread
from Queue import Queue

tsdevice = "/dev/input/event1"
format = "iihhi"


class TSDriver:

    def __init__(self, outQ):
	self.xs=[]
	self.ys=[]
	self.touchscreen = open(tsdevice,"rb")
	self.tsq = Queue()
        t = Thread(target=self.get_touch_input, args=(self.tsq, ))
        t.daemon = True
        t.start()
        t = Thread(target=self.process_touch_input, args=(outQ, ))
        t.daemon = True
        t.start()
	
    def process_touch_input( self, outQ ):
	waitDuration=.1
	while (1):
	    try:
		self.processTsEvent( self.tsq.get( True, waitDuration))
	    except:
		# we have a break in the stream, time to summarise
		if (len(self.xs) > 0):
		
		    x=sum(self.xs) / len(self.xs)
		    y=sum(self.ys) / len(self.ys)
		    outQ.put( ( x,y)) 
		    self.xs=[]
		    self.ys=[]
        
    def get_touch_input(self, q):
	"""Runs in a loop getting the touch position"""
	while (1):
	    ts_event= self.touchscreen.read(16)
	    q.put(ts_event)

    def processTsEvent( self, ts_event ):
	(ts_time1, ts_time2, ts_type, ts_code, ts_value) = struct.unpack(format,ts_event)

	if (ts_type == 3): 
	    # touch down Event
	    if ts_code == 0 :
		self.xs.append( ts_value)
	    if ts_code == 1 :
		self.ys.append( ts_value )


