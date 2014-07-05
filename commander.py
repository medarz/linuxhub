#!/usr/bin/python   
# -*- coding: iso-8859-15 -*-
# Lee publicaciones y las envia mediante el puerto serial a un micro
# Mario Medina
# 17-Abr-2012 - version inicial 
# 11-Abr-2014 - se actualiza a Paho
# 13-May-2014 - Se anexan mensajes en log
# 02-Jul-2014 - Se agrega conexion con BD
                                                                                                                                 
import serial                                                                                                                                                                                                                                                                                               
import datetime  
import time
import threading
import ap      
import messenger
import globvars as gv
import argparse
import logging        
import paho.mqtt.client as paho                                                                                                                        
from uuid import getnode as get_mac


def on_connect(mqttc, obj, rc):
    if rc == 0:
    #rc 0 successful connect
        logging.info("%sConnected to: %s",LXP,gv.public_broker)
    else:
    	logging.error("%sCould not connect to %s",LXP,gv.public_broker)
        raise Exception
        
# Estructura del mensaje
# linuxhub/user/type/subtype/device/device_id/action  arguments
# linuxhub/user/type/subtype/group/number/action      arguments
        
def on_message(mqttc, obj, msg):

	logging.info('%s{TPC: %s},{MSG: %s},{QoS: %s}', LXP, msg.topic, msg.payload, msg.qos)
	
	if gv.cmdACK == True:
		serialCMD = messenger.parse_message(msg.topic, msg.payload)
		if  serialCMD.split()[0][0] != "I":
			logging.warning("%sBAD COMMAND: %s",LXP,serialCMD)
			#escribir comando para limpiar el buffer serial
		else:
			logging.debug("%s%s",LXP,serialCMD)
			serial_port.write(serialCMD)
			gv.cmdACK = False
			time.sleep(0.1)
			
	else:
		logging.error("%sNoResponseFromAP",LXP)

	
def on_publish(mqttc, obj, mid):
    logging.debug("%sMyId: %s",LXP,str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    logging.debug("%sSubscribed: %s",LXP,str(mid))

def publica():
	mqttc.publish.single("paho/test/single", "test", hostname=gv.public_host)

def on_log(mqttc, obj, level, string):
	logging.debug("%s%s",LXP,string)

def cleanup():
    logging.info("%sClosing Commander",LXP)
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

	p = argparse.ArgumentParser(
	    description='Copyright MBR Solutions. All rights reserved. 2014'
	)
	p.add_argument("-v", "--verbose", const = 1, default = 0, type = int, nargs="?", help="Increase verbosity: 0 = warnings, 1 = info, 2 = debug")
	p.add_argument("-s", "--screen", help="Print on screen instead of log file", action="store_true")
	args = p.parse_args()

	connected = False

	LXP = "LH > "
	APP = "AP > "

	# Banderas para obtener ACKs que nos envie el AP
	gv.cmdACK = True
	cmdDoneACK = True

	if args.verbose == 0:
		log_l=logging.WARN 
	elif args.verbose == 1:
		log_l=logging.INFO  
	elif args.verbose == 2:
		log_l=logging.DEBUG

	if args.screen:
		logging.basicConfig(format='%(asctime)s: %(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S',level=log_l)
	else:
		logging.basicConfig(filename='/var/log/mbr/commander.log',format='%(asctime)s: %(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S',level=log_l)
	
	logging.info("%sInitializing...",LXP)
	logging.debug("%sOpening serial port",LXP)

	try:
	    serial_port = serial.Serial(gv.serialdev, 9600, timeout=20)
	    logging.info("%sSuccess!",LXP)  
	except:
	    logging.critical("%sFailed to connect serial",LXP)
	    raise SystemExit

	try:
		logging.debug("%sID: %s",LXP,mac)
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
		private_device = gv.lh+"/+/+/+/device/+/+"
		private_group  = gv.lh+"/+/+/+/group/+/+"

		#Posiblemente esta conexion haya que habilitarla solo "on request"
		private_system = gv.lh+"/+/system/+/+/+"

		mqttc.subscribe(private_device, 0)
		mqttc.subscribe(private_group, 0)
		mqttc.subscribe(private_system, 0)

		rc = 0

		thread = threading.Thread(target=read_from_port, args=(serial_port,))
		thread.start()

		while rc == 0:
			rc = mqttc.loop()
	         
	# handle list index error (i.e. assume no data received)
	except (IndexError):
	    logging.error("%sNo data received within serial timeout period",LXP)
	    cleanup()
	# handle app closure
	except (KeyboardInterrupt):
		logging.critical("%sInterrupt received - Exiting...",LXP)
		cleanup()
	except (RuntimeError):
	    logging.critical("%sRuntime Error",LXP)
	    cleanup()

