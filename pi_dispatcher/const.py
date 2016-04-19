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

EVENT_DISPLAYLINE1 = "13"
EVENT_DISPLAYLINE2 = "10"
EVENT_DISPLAYCLEAR = "11"
EVENT_DISPLAYOFF   = "12"

EVENT_RFID_GETFIRMWAREVERSION   = "23"
EVENT_RFID_GETTAG               = "24"
EVENT_RFID_READPORT             = "25"
EVENT_RFID_WRITEPORT            = "26"
EVENT_RFID_SELECTTAG            = "27"

EVENT_RFID_HASTAG               = "21"
EVENT_RFID_SWITCHDOWN           = "22"
EVENT_RFID_SWITCHUP             = "28"

EVENT_SONG1="93"
EVENT_SONG2="94"
EVENT_SONG3="95"



sm130Names = {
    "Reset": 0x80,
    "Firmware": 0x81,
    "Seek": 0x82,
    "Select": 0x83,
    "Authenticate": 0x85,
    "ReadBlock": 0x86,
    "ReadValue": 0x87,
    "WriteBlock": 0x89,
    "WriteValue": 0x8A,
    "Write4": 0x8B,
    "WriteKey": 0x8C,
    "Increment": 0x8D,
    "Decrement": 0x8E,
    "Antenna": 0x90,
    "ReadPort": 0x91,
    "WritePort": 0x92,
    "Halt": 0x93,
    "Baud": 0x94,
    "Sleep": 0x96
    }

sm130Vals = dict([[v,k] for k,v in sm130Names.items()])

