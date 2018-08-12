#from sht1x.Sht1x import Sht1x as SHT1x
from pi_sht1x import SHT1x
import RPi.GPIO as GPIO
dataPin = 22
clkPin = 18

with SHT1x(18, 22, gpio_mode=GPIO.BOARD) as sensor:
    temp = sensor.read_temperature()
    humidity = sensor.read_humidity(temp)
    sensor.calculate_dew_point(temp, humidity)
    print(sensor)
#sht1x = SHT1x(dataPin, clkPin, GPIO.BOARD)

#temperature = sht1x.read_temperature_C()
#humidity = sht1x.read_humidity()
#dewPoint = sht1x.calculate_dew_point(temperature, humidity)

#print("Temperature: {} Humidity: {} Dew Point: {}".format(temperature, humidity, dewPoint))
