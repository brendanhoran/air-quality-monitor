# Author Brendan Horan
# License : BSD 3-Clause
# Description : Combine all sensors and display on a LCD

import c02
import pm25
import dht
import machine
import time
from time import sleep
from machine import Pin, I2C
from esp8266_i2c_lcd import I2cLcd


def hardware_setup():
  lcd_address = 0x27
  lcd_cols = 40
  lcd_row= 4

  # Set up LCD
  i2c = I2C(scl=Pin(5), sda=Pin(2), freq=100000)
  lcd = I2cLcd(i2c, 0x27, 4, 40)
  lcd.clear()
  # set up DHT11
  dht_sensor = dht.DHT11(machine.Pin(27))
  # Set up c02
  c02_sensor = c02.C02_sensor(36)
  # Set up pm2.2
  pm25_sensor = pm25.PM25_sensor(25,26)
  return(lcd, dht_sensor, c02_sensor, pm25_sensor)


def read_sensors(dht_sensor, c02_sensor, pm25_sensor):
  dht_sensor.measure()
  c02_value = c02_sensor.read_sensor()
  pm25_vale = pm25_sensor.read_sensor()
  temp_value = dht_sensor.temperature()
  humidity_value = dht_sensor.humidity()
  return(c02_value, pm25_vale, temp_value, humidity_value)

def read_dht(dht_sensor):
  dht_sensor.measure()
  temp_value = dht_sensor.temperature()
  humidity_value = dht_sensor.humidity()
  return(temp_value, humidity_value)

def read_c02(c02_sensor):
  c02_value = c02_sensor.read_sensor()
  return(c02_value)

def read_pm25(pm25_sensor):
  pm25_vale = pm25_sensor.read_sensor()
  return(pm25_sensor)

def update_lcd(dht_value_task, c02_value_task, pm25_value_task):
   dht_temp = str(dht_value_task[0])
   dht_humidity = str(dht_value_task[1])
 
   pm25_value_task = pm25_value_task.replace('(','')
   pm25_value_task = pm25_value_task.replace(')','')
   pm25_value_task = pm25_value_task.replace(',','')

   lcd.putstr('Temperature: '+dht_temp+'c\n')
   lcd.putstr('Humidity: '+dht_humidity+'%\n')
   lcd.putstr('co2: '+c02_value_task,+' ppm\n')
   lcd.putstr('PM2.5: '+pm25_value_task+' ugm3\n')

def write_values_lcd(lcd):
  sensor_values = read_sensors(dht_sensor, c02_sensor, pm25_sensor)
  c02 = str(sensor_values[0])
  pm25 = str(sensor_values[1])
  temp = str(sensor_values[2])
  humidity = str(sensor_values[3])
  pm25 = pm25.replace('(','')
  pm25 = pm25.replace(')','')
  pm25 = pm25.replace(',','')

  lcd.clear()
  lcd.putstr('Temperature: '+temp+'c\n')
  lcd.putstr('Humidity: '+humidity+'%\n')
  lcd.putstr('co2 ppm: '+c02+'\n')
  lcd.putstr('PM2.5: '+pm25+' ugm3\n')


# Init all the attached h/w
hardware = hardware_setup()
lcd = hardware[0]
dht_sensor = hardware[1]
c02_sensor = hardware[2]
pm25_sensor = hardware[3]


# Let the sensors warm up
# only happens on power on
# c02 sensor is an exception, it can take upwards of 3mins (worst case)
# c02 will display negative values till its ready
lcd.putstr('Sensor warm up\n')
lcd.putstr('Sleeping 15 seconds\n')
sleep(15)
lcd.clear()

# main loop
# for now just one big dumb loop
# better would be asyncio so we can do other stuff too (http etc)
while True:
  read_dht(dht_sensor)
  read_pm25(pm25_sensor)
  read_c02(c02_sensor)
  write_values_lcd(lcd)
  # 5s is a good average pol time for the sensors
  time.sleep(5)
