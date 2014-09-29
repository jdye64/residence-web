__author__ = 'jeremydyer'

from RPi import RPi
import json
import jsonpickle

rpis = []   # List of connected RPi devices

rpis.append(RPi("10.0.1.50"))
rpis.append(RPi("10.0.1.51"))
rpis.append(RPi("10.0.1.52"))

print 'Testing JSON data'
jsonData = jsonpickle.encode(rpis)
print jsonData
print str(jsonData)