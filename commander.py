#!/usr/bin/python   
# -*- coding: iso-8859-15 -*-
# Lee publicaciones y las envia mediante el puerto serial a un micro
# Mario Medina
# 17-Abr-2012 - version inicial 
# 11-Abr-2014 - se actualiza a Paho
                                                                                                                                 
import serial                                                                                                                                                 
import sqlite3                                                                                                                                                
import datetime         
import threading                                                                                                                                      
import paho.mqtt.client as mqtt
from uuid import getnode as get_mac

serialdev = '/dev/ttyUSB0'
broker    = "192.241.195.144"
port      = 1883
connected = False
mac = get_mac()

LXP = "LH > "
APP = "AP > "

# Banderas para obtener ACKs que nos envie el AP
cmdACK = True
cmdDoneACK = True

def on_connect(mqttc, obj, rc):
    if rc == 0:
    #rc 0 successful connect
        print LXP + "Connected to:" + broker
    else:
        raise Exception
        
# Estructura del mensaje
# linuxhub/type/subtype/device/device_id/action  arguments
# linuxhub/type/subtype/group/number/action      arguments

        
def on_message(mqttc, obj, msg):
	
	global cmdACK
	print(LXP + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
	FILE.write(msg.topic)
	FILE.write("\t")
	FILE.write(msg.payload)
	FILE.write("\n")  
	message = msg.topic.split("/")   
 
	#second list element is temp
	action = message[5].rstrip()    
	device = message[3]
	args   = msg.payload
   
	if cmdACK == True:
		
		if device == "device":
			device_id = message[4]
			print LXP + "Device ID:", device_id
			
			if  action == "power":
				print LXP + "Power:", args
				
			elif action == "onboardled":
				
				if args == "ON":
					serial_port.write("I|0x11|0xA1|0x00|0x78,0x56,0x34,0x11|0x01|0x0010|0x01|0|--|U")
					cmdACK = False	
				elif args == "OFF":
					serial_port.write("I|0x11|0xA0|0x00|0x78,0x56,0x34,0x11|0x01|0x0010|0x01|0|--|U")
					cmdACK = False	
				elif args == "TOGGLE":
					serial_port.write("I|0x11|0xA3|0x00|0x78,0x56,0x34,0x11|0x01|0x0010|0x01|0|--|U")
					cmdACK = False	
				else:
					print LXP + "MessageNotRecognized"
			else:
				print LXP + "CommandNotRecognized"
						
		elif device == "group":
			group_id = message[4]
			print LXP + "Group:", group_id
	else:
		print LXP + "NoResponseFromAP"
	
      
def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print(LXP+"Subscribed:"+str(mid))

def on_log(mqttc, obj, level, string):
    print(string)

def cleanup():
    print LXP + "ClosingCommander."
    thread._Thread__stop()
    serial_port.close()
    mqttc.disconnect()
    
def handle_data(data):
	global cmdACK
	if len(data)>2:
		fromAP = data.split("|")
		command = fromAP[0].rstrip()
		status  = fromAP[1].rstrip()
		if cmdACK == False:
			if command == "CMD" and status =="OK":
				print APP + "CommandInProgress"
				cmdACK = True
		elif cmdACK == True:
			if command == "SEND" and status =="OK":
				print APP + "CommandExecuted"

def read_from_port(ser):
	global connected
	while not connected:
		#serin = ser.read() 
		connected = True

        while True:
           reading = ser.readline().decode()
           handle_data(reading)

try:
    print LXP + "Connecting... ", serialdev
    #connect to serial port
    serial_port = serial.Serial(serialdev, 9600, timeout=20)
    print LXP + "Serial port "+ serialdev +" opened"      
                                                                                                                     
except:
    print LXP + "Failed to connect serial"
    #unable to continue with no serial input
    raise SystemExit

print LXP + "Creating log file" 
filename = "loginfo.log"
FILE = open(filename,"w")

try:
	print LXP + "MyID: ",mac
	mqttc = mqtt.Client()
	serial_port.flushInput()
	
	#callbacks
	mqttc.on_message = on_message
	mqttc.on_connect = on_connect
	mqttc.on_publish = on_publish
	mqttc.on_subscribe = on_subscribe

	# Uncomment to enable debug messages
	# mqttc.on_log = on_log
	mqttc.connect(broker, port, 60)

	#Subscriptions
	private_device = `mac`+"/+/+/device/+/+"
	private_group = `mac`+"/+/+/group/+/+"
	
	mqttc.subscribe(private_device, 0)
	mqttc.subscribe(private_group, 0)
	#
	rc = 0

	thread = threading.Thread(target=read_from_port, args=(serial_port,))
	thread.start()

	while rc == 0:
		rc = mqttc.loop()

	print "rc:", rc    
          
     
# handle list index error (i.e. assume no data received)
except (IndexError):
    print LXP + "No data received within serial timeout period"
    cleanup()
# handle app closure
except (KeyboardInterrupt):
	print "\n"
	print LXP + "Interrupt received"
	cleanup()
except (RuntimeError):
    print LXP + "uh-oh! Something Happened"
    cleanup()

