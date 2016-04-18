# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys
import time

import Adafruit_MPR121.MPR121 as MPR121

from i2clibraries import i2c_lcd_smbus

# Configuration parameters
# I2C Address, Port, Enable pin, RW pin, RS pin, Data 4 pin, Data 5 pin, Data 6 pin, Data 7 pin, Backlight pin (optional)
lcd = i2c_lcd_smbus.i2c_lcd(0x27,1, 2, 1, 0, 4, 5, 6, 7, 3)

# If you want to disable the cursor, uncomment the following line
lcd.command(lcd.CMD_Display_Control | lcd.OPT_Enable_Display)

lcd.backLightOn()

print 'Adafruit MPR121 Capacitive Touch Sensor Test'

# Create MPR121 instance.
cap = MPR121.MPR121()

# Initialize communication with MPR121 using default I2C bus of device, and 
# default I2C address (0x5A).  On BeagleBone Black will default to I2C bus 0.
if not cap.begin():
    print 'Error initializing MPR121.  Check your wiring!'
    sys.exit(1)

# Alternatively, specify a custom I2C address such as 0x5B (ADDR tied to 3.3V),
# 0x5C (ADDR tied to SDA), or 0x5D (ADDR tied to SCL).
#cap.begin(address=0x5B)

# Also you can specify an optional I2C bus with the bus keyword parameter.
#cap.begin(bus=1)

# Main loop to print a message every time a pin is touched.
print 'Press Ctrl-C to quit.'
last_touched = cap.touched()

while True:
    current_touched = cap.touched()
    # Check each pin's last and current state to see if it was pressed or released.
    for i in range(12):
        # Each pin is represented by a bit in the touched value.  A value of 1
        # means the pin is being touched, and 0 means it is not being touched.
        pin_bit = 1 << i
        # First check if transitioned from not touched to touched.
        if current_touched & pin_bit and not last_touched & pin_bit:
            print '{0} touched!'.format(i)
            lcd.setPosition(1, 0) 
            lcd.writeString("Touched  %i" % i)
        if not current_touched & pin_bit and last_touched & pin_bit:
            print '{0} released!'.format(i)
            lcd.setPosition(1, 0) 
            lcd.writeString("Released %i" % i)
    # Update last state and wait a short period before repeating.
    last_touched = current_touched
    if current_touched==1:
        lcd.backLightOff()
    if current_touched==2:
        lcd.backLightOn()

    time.sleep(0.1)

    # Alternatively, if you only care about checking one or a few pins you can 
    # call the is_touched method with a pin number to directly check that pin.
    # This will be a little slower than the above code for checking a lot of pins.
    #if cap.is_touched(0):
    #    print 'Pin 0 is being touched!'
    
    # If you're curious or want to see debug info for each pin, uncomment the
    # following lines:
    #print '\t\t\t\t\t\t\t\t\t\t\t\t\t 0x{0:0X}'.format(cap.touched())
    #filtered = [cap.filtered_data(i) for i in range(12)]
    #print 'Filt:', '\t'.join(map(str, filtered))
    #base = [cap.baseline_data(i) for i in range(12)]
    #print 'Base:', '\t'.join(map(str, base))
