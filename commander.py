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
import ap      
import messenger
import globvars as gv
import logging        
import paho.mqtt.client as paho                                                                                                                        
from uuid import getnode as get_mac


def on_connect(mqttc, obj, rc):
    if rc == 0:
    #rc 0 successful connect
        print LXP + "Connected to:" + gv.public_broker
    else:
        raise Exception
        
# Estructura del mensaje
# linuxhub/user/type/subtype/device/device_id/action  arguments
# linuxhub/user/type/subtype/group/number/action      arguments
        
def on_message(mqttc, obj, msg):

	print(LXP + "{TPC: "+ msg.topic+"},{MSG: "+str(msg.payload)+"},{QoS: "+str(msg.qos)+"}")
	logging.info('%s{TPC: %s},{MSG: %s},{QoS: %s}', LXP, msg.topic, msg.payload, msg.qos)

	if gv.cmdACK == True:
		serialCMD = messenger.parse_message(msg.topic, msg.payload)
		if  serialCMD.split()[0][0] != "I":
			logging.warning('%s%s',LXP,serialCMD)
			print LXP + serialCMD
		else:
			print LXP + serialCMD
			serial_port.write(serialCMD);
			gv.cmdACK = False
	else:
		print LXP + "NoResponseFromAP"
		logging.error("%sNoCommandACKFromAP",LXP)

	
def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print(LXP+"Subscribed:"+str(mid))

def publica():
	mqttc.publish.single("paho/test/single", "test", hostname="medarz.info")

def on_log(mqttc, obj, level, string):
    print(string)

def cleanup():
    print LXP + "ClosingCommander."
    thread._Thread__stop()
    serial_port.close()
    mqttc.disconnect()
    

def read_from_port(ser):
	global connected
	while not connected:
		connected = True
        while True:
           reading = ser.readline().decode()
           ap.handle_data(reading)



if __name__ == "__main__":

	connected = False
	mac = get_mac()

	LXP = "LH > "
	APP = "AP > "

	# Banderas para obtener ACKs que nos envie el AP
	gv.cmdACK = True
	cmdDoneACK = True

	print LXP + "Creating log file" 
	logging.basicConfig(filename='logs/commander.log',format='%(asctime)s:%(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S',level=logging.DEBUG)


	try:
	    print LXP + "Connecting... ", gv.serialdev
	    #connect to serial port
	    serial_port = serial.Serial(gv.serialdev, 9600, timeout=20)
	    print LXP + "Serial port "+ gv.serialdev +" opened"      
	                                                                                                                     
	except:
	    print LXP + "Failed to connect serial"
	    logging.error("%sFailed to connect serial",LXP)
	    #unable to continue with no serial input
	    raise SystemExit

	try:
		print LXP + "MyID: ",mac
		mqttc = paho.Client()
		serial_port.flushInput()
		
		#callbacks
		mqttc.on_message = on_message
		mqttc.on_connect = on_connect
		mqttc.on_publish = on_publish
		mqttc.on_subscribe = on_subscribe

		# Uncomment to enable debug messages
		# mqttc.on_log = on_log
		mqttc.connect(gv.public_broker, gv.port, 60)

		#Subscriptions
		private_device = `mac`+"/+/+/+/device/+/+"
		private_group  = `mac`+"/+/+/+/group/+/+"

		#Posiblemente esta conexion haya que habilitarla solo "on request"
		private_system = `mac`+"/+/system/+/+/+"

		mqttc.subscribe(private_device, 0)
		mqttc.subscribe(private_group, 0)
		mqttc.subscribe(private_system, 0)
		#

		rc = 0

		thread = threading.Thread(target=read_from_port, args=(serial_port,))
		thread.start()

		while rc == 0:
			rc = mqttc.loop()
	        
     
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

