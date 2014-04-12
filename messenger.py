#!/usr/bin/python   


def parse_message(topic, payload):

    # 66619478619276L/led/dim/device/0x01/onboardled
	message = topic.split("/")
	action  = message[5].rstrip()    
	device  = message[3]
	args    = payload

	tipoED = {'led': 1, 'curtain': 2, 'sensor': 3}

	#print "0x%02X" % 1
	cmd = 0
	msg = 0
	arg = 0
	ad1 = 0
	ad2 = 0
	ad3 = 0
	ad4 = 0
	typ = tipoED[message[1]]
	grp = 0
	lnk = 0
	ack = 0
	add = 0
 
	if device == "device":
		lnk = int(message[4],0)

		if message[1] == "led":

			if  action == "power":
				print LXP + "Power:", args
				
			elif action == "onboardled":
				
				if args == "ON":
					cmd=0x11
					msg=0xA0
				elif args == "OFF":
					cmd=0x11
					msg=0xA1
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
		grp = int(message[4])
		#print LXP + "Group:", group_id

	cmd2ap =  "I|0x%02X|0x%02X|0x%02X|0x%02X,0x%02X,0x%02X,0x%02X|0x%02X|0x%04X|0x%02X|0x%d|%02d|U" % (cmd,msg,arg,ad1,ad2,ad3,ad4,lnk,grp,typ,ack,add)
	print cmd2ap
