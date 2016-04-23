from i2clibraries import i2c_lcd_smbus
from time import * 

# Configuration parameters
# I2C Address, Port, Enable pin, RW pin, RS pin, Data 4 pin, Data 5 pin, Data 6 pin, Data 7 pin, Backlight pin (optional)
lcd = i2c_lcd_smbus.i2c_lcd(0x27,1, 2, 1, 0, 4, 5, 6, 7, 3)

# If you want to disable the cursor, uncomment the following line
lcd.command(lcd.CMD_Display_Control | lcd.OPT_Enable_Display)

lcd.backLightOn()

lcd.writeString("Python I2C LCD")
for i in range(1,100): 
    lcd.setPosition(2, 1) 
    lcd.writeString("%i" % i)
