#!/bin/bash
 [ -z $(pgrep -f Dispatcher.py | head -1) ] && sudo /code/pi-kobo/pi_dispatcher/allPinsOff 

