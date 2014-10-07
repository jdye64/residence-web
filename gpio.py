#Contains all of the classes that support the RPi GPIO efforts.
import jsonpickle
import subprocess
import os
import time
import json
from pprint import pprint
import os.path

#Defines the heartbeat object that will be published by each connected RPi device
class RPiHeartBeat:

    timestamp = None
    uid = None

    def __init__(self, uid):
        self.timestamp = time.time()
        self.uid = uid

class RPi:

    uid = None
    ip = None
    eth0_mac = None
    secretKey = None
    outlets = []
    turnOnOutletRPC = None
    turnOffOutletRPC = None
    updateDeviceRPC = None
    lastheartbeat = None

    def __init__(self, uid):
        #Creates an instance of RPi_Info
        rpiInfo = RPi_Info()

        # Attempts to load a previous instance from the filesystem.
        if self.load():
            print "Successfully loaded the GPIO Configuration"
        else:
            print "Unable to load GPIO configuration. Creating new blank template and saving"
            self.ip = rpiInfo.get_ipaddress()
            self.eth0_mac = rpiInfo.getmac("eth0")
            self.secretKey = "123456789qazwsx"
            self.outlets = []
            self.turnOffOutletRPC = None
            self.turnOffOutletRPC = None
            self.updateDeviceRPC = None

            # Saves/Creates the current randomish configuration
            self.save()

        self.uid = uid

    def from_json(self, jsonData):
        data = jsonpickle.decode(jsonData)
        print data

    def to_json(self):
        return jsonpickle.encode(self)

    def save(self):
        print "Saving RPi file"

        if not os.path.exists('~/.residence'):
            os.makedirs('~/.residence')

        f = open('~/.residence/GPIOConfig.json', 'w')
        json_data = self.to_json()
        pprint(json_data)
        f.write(json_data)
        f.close()

    def load(self):
        if os.path.exists('~/.residence/GPIOConfig.json'):
            json_data = open('~/.residence/GPIOConfig.json')
            data = self.from_json(json_data)
            pprint(data)
            json_data.close()
            return True
        else:
            print "~/.residence/GPIOConfig.json RPi information file does not exist!"
            return False

# Defines a generic GPIO outlet on a raspberry pi device
class GPIO:

    portsNumber = None
    on = 0
    outletDescription = None

    def __init__(self, portNum):
        self.portNumber = portNum
        self.on = 0
        self.outletDescription = "Test Description " + str(portNum)

    def to_json(self):
        return jsonpickle.encode(self)


class RPi_Info:

    def get_ram(self):
        try:
            s = subprocess.check_output(["free", "-m"])
            lines = s.split('\n')
            return (int(lines[1].split()[1]), int(lines[2].split()[3]))
        except:
            return 0


    def get_process_count(self):
        try:
            s = subprocess.check_output(["ps", "-e"])
            return len(s.split('\n'))
        except:
            return 0


    def get_up_stats(self):
        try:
            s = subprocess.check_output(["uptime"])
            load_split = s.split('load average: ')
            load_five = float(load_split[1].split(',')[1])
            up = load_split[0]
            up_pos = up.rfind('','',0,len(up)-4)
            up = up[:up_pos].split('up ')[1]
            return ( up , load_five )
        except:
            return ('', 0)


    def get_connections(self):
        try:
            s = subprocess.check_output(["netstat","-tun"])
            return len([x for x in s.split() if x == 'ESTABLISHED'])
        except:
            return 0

    def get_temperature(self):
        try:
            s = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_temp"])
            return float(s.split('=')[1][:-3])
        except:
            return 0

    def get_ipaddress(self):
        arg = 'ip route list'
        p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)
        data = p.communicate()
        split_data = data[0].split()
        ipaddr = split_data[split_data.index('src') + 1]
        return ipaddr

    def getmac(self, interface):
        # Return the MAC address of interface
        try:
            str = open('/sys/class/net/%s/address', interface).readline()
        except:
            str = "00:00:00:00:00:00"
        return str[0:17]

    def get_cpu_speed(self):
        f = os.popen('/opt/vc/bin/vcgencmd get_config arm_freq')
        cpu = f.read()
        return cpu