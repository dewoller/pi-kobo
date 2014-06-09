EVENT_KEYS="0"  # message from keypad to dispatcher, a set of keys
EVENT_TOUCHDOWN="1" # intra keypad events
EVENT_TOUCHUP="2"

# messages from dispatcher to keypad, to control ui
EVENT_FLASHSCREEN="3"  
EVENT_FLASHMSG="5"
EVENT_CLEARMSG="6"

EVENT_BLUEDEVICE="7"  # intradispatcher message;  we have seen a compatible bluetooth device
EVENT_BLUEDEVICETOGGLE="8"  # turn bluetooth on and off, (for security?)

BLACK=(0,0,0)
COLOR_BLACK =(0,0,0)
COLOR_WHITE=(255,255,255)

