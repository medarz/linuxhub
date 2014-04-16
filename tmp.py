#!/usr/bin/python  

sertxt = "REGISTER|NEWDEV|0x01|0x79|0x56|0x35|0x12|0x33|0x44|0x43|0x41"

fromAP = sertxt.split("|")



linkID = int(fromAP[2], 0)
Addr1  = int(fromAP[3], 0)
Addr2  = int(fromAP[4], 0)
Addr3  = int(fromAP[5], 0)
Addr4  = int(fromAP[6], 0)
Model  = int(fromAP[7], 0)
Type   = int(fromAP[8], 0)
Subtype= 99
Sensors= int(fromAP[9], 0)
Flags  = int(fromAP[10].rstrip(), 0)

#From database read model, type, subtype
#
msg =  "confirm|0x%02X|0x%02X%02X%02X%02X|0x%02X|0x%02X|0x%02X|0x%02X|0x%02X" % (linkID,Addr1,Addr2,Addr3,Addr4,Model,Type,Subtype,Sensors,Flags)

print msg 