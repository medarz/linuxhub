#!/usr/bin/python   

import logging
import globvars as gv
import paho.mqtt.publish as publish

LXP = "LH > "
APP = "AP > "

def handle_data(data):

	if len(data)>1:
		fromAP = data.split("|")
		fields = len(fromAP)
		command = fromAP[0].rstrip()
		if(fields>1):
			status  = fromAP[1].rstrip()
		if(fields>2):
			argscmd = fromAP[2].rstrip()

		if gv.cmdACK == False:
			if command == "CMD" and status =="OK":
				logging.debug("%sCommandInProgress",APP)
				gv.cmdACK = True
		elif gv.cmdACK == True:
			if command == "SEND" and status =="OK":
				logging.debug("%sCommandExecuted",APP)
			elif command == "DATA":
				logging.debug("%s%s",APP,status)

		if command == "INITIALIZING":
				logging.debug("%sAccess point restarted",LXP)
				gv.cmdACK = True

		if command == "JOIN":
			if status == "PENDING":
				logging.debug("%sJoinPending",APP)
				gv.cmdACK = True
			elif status == "SUCCESS":
				logging.debug("%sJoinSuccess",APP)
				gv.cmdACK = True
			elif status == "FAIL":
				logging.error("%sJoinFailed",APP)
				gv.cmdACK = True

		#REGISTER|NEWDEV|0x01|0x79|0x56|0x35|0x12|0x33|0x44|0x43|0x41
		if command=="REGISTER":
			if status =="NEWDEV":
				#TEnemos que obtener la informacion del AP y luego formar el mensaje
				logging.debug("%s%s",APP,data)

				#LinkxID Invalido.. La direccion ya existe
				if fromAP[3]=="0x":
					logging.error("%sAddressError",APP)
					return 
			          
				linkID = int(fromAP[2], 0)
				Addr1  = int(fromAP[3], 0)
				Addr2  = int(fromAP[4], 0)
				Addr3  = int(fromAP[5], 0)
				Addr4  = int(fromAP[6], 0)
				Type   = int(fromAP[7], 0)
				Model  = int(fromAP[8], 0)
				Sensors= int(fromAP[9], 0)
				Flags  = int(fromAP[10].rstrip(), 0)

				#From database read model, type, subtype
				msg =  "0x%02X|0x%02X%02X%02X%02X|0x%02X|0x%02X|0x%02X|0x%02X" % (linkID,Addr1,Addr2,Addr3,Addr4,Type,Model,Sensors,Flags)
				#Enviar commando MQTT de publish
				publish.single(gv.lh +"/user/web/config/add/confirm", msg, hostname=gv.public_broker)
				logging.debug("%sPublshed: %s/user/web/config/add/confirm %s",LXP, gv.lh ,msg)
     
