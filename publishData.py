import time
import datetime
import socket
import sys
import os
import re
import commands
import paho.mqtt.client as mqtt
import json

THINGSBOARD_HOST = 'demo.thingsboard.io'
#ACCESS_TOKEN = 'fnRngyfVryqOJiCM6Cxb'

ACCESS_TOKEN = '2dqjjwFVcWhyZxmcBOkx'

sensor_data = {'temperature':0, 'humidity':0, 'pressure':0}

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)

sensor_data['temperature'] = sys.argv[1]
sensor_data['humidity'] = sys.argv[2]
sensor_data['pressure'] = sys.argv[3]

try:
	# Sending humidity and temperature data to ThingsBoard
	client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)
except:
	x=1
	# Nothing to do
finally:
	x=2
	# Nothing
	

	
