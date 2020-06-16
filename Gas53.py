#
#   Program name    |   Gas53.py
#   Written by      |   Steven Owen
#   Date            |   January 2019
#   Version         |   1.0
#
#   Description     |   A program to read electrode responses from an Alphasense AFE through the
#                       South Coast SCience DFE via a Raspberry Pi3.
#
#   Comments        |   This version is functionally correctly.  Try loops with error handling
#                       for connection errors have been included.
#

#   Import necessary libraries.
import time
import datetime
import socket
import sys
import os
import re
import commands
import ADS1x15
from Adafruit_SHT31 import *
import paho.mqtt.client as mqtt
import json

#   Setup Thingsboard access and data package
THINGSBOARD_HOST = 'demo.thingsboard.io'
ACCESS_TOKEN = 'fnRngyfVryqOJiCM6Cxb'
sensor_data = {'NO_WE': 0, 'NO_AE': 0, 'NO2_WE': 0, 'NO2_AE': 0, 'NO':0, 'temperature':0, 'humidity':0}
client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
# The Try Loop prevents program crashes if a connection to Thingsboard can't be made.
connections = 0
while connections < 1:
	try:
		client.connect(THINGSBOARD_HOST, 1883, 60)
		connections += 1

	except Exception as e:
		pass

# Measure and correct temperature and humidity data
sensor = SHT31(address = 0x44)
#sensor = SHT31(address = 0x45)

degrees = sensor.read_temperature()
humidity = sensor.read_humidity()

# Now include temperature and humidity correction.
# New temperature correction added 1 Sept 2019

corr_temperature=round(0.7325*degrees+4.8183,2)
#corr_temperature=round(0.9243*degrees+0.8065,2) - old version
corr_humidity=round(1.1672*humidity-19.546,2)
#corr_temperature=round(degrees,2)
#corr_humidity=round(humidity,2)

sensor_data['temperature'] = corr_temperature
sensor_data['humidity'] = corr_humidity

# Create ADS1115 ADC (16-bit) instances.
adcFE = ADS1x15.ADS1115(address=0x48, busnum=1) # FE prfeix = Forty Eight (Auxilliary Electrode)
adcFN = ADS1x15.ADS1115(address=0x49, busnum=1) # FN prefix = Forty Nine  (Working Electrode)
GAIN=8


# Create a loop to smooth Nitrogen Dioxide electrode readings.
NO2samples = 1
count = 0
FEvalues = [0]*4
FNvalues = [0]*4
while (count < NO2samples):
    count = count + 1
    #for i in range(4):  
    FEvalues[3] = FEvalues[3]+adcFE.read_adc(3, gain=GAIN)
    FNvalues[3] = FNvalues[3]+adcFN.read_adc(3, gain=GAIN)

#   Calculate NO2 electrode voltages
NO2_WE=round((FNvalues[3]*4.096/NO2samples)/(32768*GAIN),5)
NO2_AE=round((FEvalues[3]*4.096/NO2samples)/(32768*GAIN),5)

# Create a loop to smooth Nitric Oxide electrode readings.
NOsamples = 1
count = 0
FEvalues = [0]*4
FNvalues = [0]*4
while (count < NOsamples):
    count = count + 1
    #for i in range(4):  
    FEvalues[2] = FEvalues[2]+adcFE.read_adc(2, gain=GAIN)
    FNvalues[2] = FNvalues[2]+adcFN.read_adc(2, gain=GAIN)

#   Calculate NO electrode voltages and NO ppmV concentration
NO_WE=round((FNvalues[2]*4.096/NOsamples)/(32768*GAIN),5)
NO_AE=round((FEvalues[2]*4.096/NOsamples)/(32768*GAIN),5)
NO=round(((NO_WE-0.285)-(1.37*(NO_AE-0.290)))/0.0002844,2)

#   Assign the values to the sensor package variables.
sensor_data['NOWE'] = NO_WE
sensor_data['NOAE'] = NO_AE
sensor_data['NO2WE'] = NO2_WE
sensor_data['NO2AE'] = NO2_AE
sensor_data['NO'] = NO

# Publish to ThingsBoard to provide a graphical representation of the data.
try:	
	client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)
	print '{0:0.5f}'.format(NO_WE)
	print '{0:0.5f}'.format(NO_AE)
	print '{0:0.5f}'.format(NO2_WE)
	print '{0:0.5f}'.format(NO2_AE)   
	print '{0:0.2f}'.format(corr_temperature)
	print '{0:0.2f}'.format(corr_humidity)
	
except:
	pass
    
finally:
	pass

#   End of program.




	
