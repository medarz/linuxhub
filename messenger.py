#!/usr/bin/python   
import logging
import globvars as gv

LXP = "LH > "
APP = "AP > "

def parse_message(topic, payload):
    #         0         1   2   3    4      5     6
    # 66619478619276L/user/led/dim/device/0x01/onboardled   payload
	message = topic.split("/")
	device  = message[4]
	subtype = message[3]
	edtype  = message[2]
	payld   = payload.split(":")
	args    = payld[0]

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

    #ACK es el ultimo elemento del mensaje. Si hay mas de una opcion se asume debe venir
    #  ON:ACK   
    #  OFF:NOACK  
    #  50:ARG1:ARG2:ACK  
	payldsize = len(payld)
	if  payldsize > 1:
		withack = payld[payldsize-1]
		if withack == "ACK":
			ack = 1

	if  edtype != "system":
		command = message[6]
		if gv.tipoED.has_key(edtype):
				typ = gv.tipoED[edtype]
		else:
			return "DeviceNotSupported"

		action  = command.rstrip()    

		if device == "device":
			lnk = int(message[5],0)

			if edtype == "led":
                
                #Comandos comunes para todos los tipos de LED

                #power ON/OFF  - compatible entre dimming y ON/OFF
				if  action == "power":
					print LXP + "Power:", args

				elif action == "setgroup":
					cmd=0x20  #SET_GROUP
					msg=0x20  #SET_GROUP
					grp=int(args,0)  # Debe llegar - 0x0001
					
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

				elif action == "dimming":

					if subtype == "dim":
						cmd=0x11 #Send_byID
						msg=0x50 #DIM_PWM
					else:
						return "CommandNotSupported"
				else:
					return "CommandNotRecognized"
			else:
					return "DeviceNotSupported"
					
		elif device == "group":
			grp = int(message[5])
			if edtype == "led":
                
                #Comandos comunes para todos los tipos de LED
                #power ON/OFF  - compatible entre dimming y ON/OFF
				if  action == "power":
					print LXP + "Power:", args
				
				elif action == "onboardled":
					
					if args == "ON":
						cmd=0x12 #Send_ByGroup
						msg=0xA1 
					elif args == "OFF":
						cmd=0x12
						msg=0xA0
					elif args == "TOGGLE":
						cmd=0x12
						msg=0xA3	
					else:
						return "MessageNotRecognized"

				elif action == "dimming":

					if subtype == "dim":
						cmd=0x11 #Send_byID
						msg=0x50 #DIM_PWM
					else:
						return "CommandNotSupported"
				else:
					return "CommandNotRecognized"
			else:
					return "DeviceNotSupported"
			#print LXP + "Group:", group_id

	# ---------------- System Messages ------------------
	else:
		if message[3]=="config":
			if message[5]=="request":
				cmd=0x81 
			else:
				return "CommandNotRecognized"
	#Mensaje de sistema

	cmd2ap =  "I|0x%02X|0x%02X|0x%02X|0x%02X,0x%02X,0x%02X,0x%02X|0x%02X|0x%04X|0x%02X|%d|%02d|U" % (cmd,msg,arg,ad1,ad2,ad3,ad4,lnk,grp,typ,ack,add)
	
	return cmd2ap
