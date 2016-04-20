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

EVENT_RFID_HASTAG               = "21"
EVENT_RFID_SWITCHDOWN           = "22"
EVENT_RFID_SWITCHUP             = "28"

EVENT_PINON = 31
EVENT_PINOFF = 32

EVENT_SONG1="93"
EVENT_SONG2="94"
EVENT_SONG3="95"



