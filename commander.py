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
import messenger                                                                                                                                
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

	if cmdACK == True:
		serialCMD = parse_message(msg.topic, msg.payload)

		if  serialCMD.split()[0][0] != "I":
			print LXP + serialCMD
		else
			serial_port.write(serialCMD);
			cmdACK = False
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
			elif command == "DATA"
			    print status

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

