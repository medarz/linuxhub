#!/usr/bin/python  
import pycouchdb
import logging

def comission():
	from uuid import getnode as get_mac
	logging.info("%sComissioning System..",LXP)
	mac = get_mac()
	cfg['linuxhub']=`mac`
	lh=`mac`
	db.save(cfg)

	#Actualizar los grupos con esta informacion
	grps=list(db.query("group/byhub"))

	for group in grps:
		grp_id = group["id"]
		update_grp = db.get(grp_id)
		update_grp["linuxhub"] = lh
		db.save(update_grp)

	logging.info("%sSaving to database..",LXP)

LXP = "LH > "
APP = "AP > "

server=pycouchdb.Server("http://localhost:5984/")
db=server.database("local")
cfg=db.get("config")

lhu=cfg['linuxhub']

#Mandar llamar una funcion para comisionar la base de datos
if lhu is None:
	comission()
	cfg=db.get("config")
	lhu=cfg['linuxhub']

#####################################
#       Global Variables
#####################################
serialdev 		 = '/dev/ttyUSB0'
public_host	     = cfg['wan']['host'].encode("ascii")
public_broker    = cfg['mq']['host'].encode("ascii")
port      		 = cfg['mq']['port']		
cmdACK 			 = True
dbName			 = "local"
lh 				 = lhu.encode('ascii')	
#TODO: Obtenerlos de la base de datos
tipoED = {'led': 1, 'curtain': 2, 'sensor': 3}


logging.debug("%s%s",LXP,lh)




