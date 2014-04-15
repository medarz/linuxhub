#!/usr/bin/python   
import logging
import globvars as gv

LXP = "LH > "
APP = "AP > "

def parse_message(topic, payload):
    #         0         1   2   3    4      5     6
    # 66619478619276L/user/led/dim/device/0x01/onboardled
	message = topic.split("/")
	device  = message[4]
	args    = payload

	cmd = 0
	msg = 0
	arg = 0
	ad1 = 0
	ad2 = 0
	ad3 = 0
	ad4 = 0
	grp = 0
	lnk = 0
	typ = 0
	ack = 0
	add = 0

	if  message[2] != "system":

		if gv.tipoED.has_key(message[2]):
				typ = gv.tipoED[message[2]]
		else:
			return "DeviceNotSupported"

		#print "0x%02X" % 1

		action  = message[6].rstrip()    

		if device == "device":
			lnk = int(message[5],0)

			if message[2] == "led":

				if  action == "power":
					print LXP + "Power:", args
					
				elif action == "onboardled":
					
					if args == "ON":
						cmd=0x11 #Send_ByID
						msg=0xA1 
					elif args == "OFF":
						cmd=0x11
						msg=0xA0
					elif args == "TOGGLE":
						cmd=0x11
						msg=0xA3	
					else:
						return "MessageNotRecognized"

				else:
					return "CommandNotRecognized"
			else:
					return "DeviceNotSupported"
					
		elif device == "group":
			grp = int(message[5])
			#print LXP + "Group:", group_id
	else:
		if message[3]=="config":
			if message[5]=="add":
				cmd=0x81
			else:
				return "CommandNotRecognized"
	#Mensaje de sistema

	cmd2ap =  "I|0x%02X|0x%02X|0x%02X|0x%02X,0x%02X,0x%02X,0x%02X|0x%02X|0x%04X|0x%02X|%d|%02d|U" % (cmd,msg,arg,ad1,ad2,ad3,ad4,lnk,grp,typ,ack,add)
	
	return cmd2ap
