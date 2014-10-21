#Contains all of the classes that support the RPi GPIO efforts.
import jsonpickle
import subprocess
import os
import time
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

    # Metadata about the location of the RPi
    city = None
    state = None
    zip = None
    address1 = None
    address2 = None
    location_name = None    # Friendly name associated with the physical address of the device
    room_name = None    # Friendly name associated with the room that the RPi is located in the physical address

    def __init__(self, uid):
        #Creates an instance of RPi_Info
        rpiInfo = RPi_Info()

        self.uid = uid

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
            self.turnOnOutletRPC = None
            self.updateDeviceRPC = None
            self.city = None
            self.state = None
            self.zip = None
            self.address1 = None
            self.address2 = None
            self.location_name = None    # Friendly name associated with the physical address of the device
            self.room_name = None # Friendly name associated with the room that the RPi is located in the physical address

            #Creates 8 filler GPIO outlets since all of the devices I have currently built are 8 outlets.
            self.outlets.append(GPIO(0))
            self.outlets.append(GPIO(1))
            self.outlets.append(GPIO(2))
            self.outlets.append(GPIO(3))
            self.outlets.append(GPIO(4))
            self.outlets.append(GPIO(5))
            self.outlets.append(GPIO(6))
            self.outlets.append(GPIO(7))

            # Saves/Creates the current random-ish configuration
            self.save()

    def from_json(self, json_data):
        saved_data = jsonpickle.decode(json_data)

        self.eth0_mac = saved_data.eth0_mac
        self.ip = saved_data.ip
        self.lastheartbeat = saved_data.lastheartbeat
        self.outlets = saved_data.outlets
        self.secretKey = saved_data.secretKey
        self.turnOffOutletRPC = saved_data.turnOffOutletRPC
        self.turnOnOutletRPC = saved_data.turnOnOutletRPC
        self.updateDeviceRPC = saved_data.updateDeviceRPC
        self.city = saved_data.city
        self.state = saved_data.state
        self.zip = saved_data.zip
        self.address1 = saved_data.address1
        self.address2 = saved_data.address2
        self.location_name = saved_data.location_name
        self.room_name = saved_data.room_name

    def to_json(self):
        return jsonpickle.encode(self)

    def save(self):
        print "Saving RPi file"

        if not os.path.exists('/home/pi/.residence'):
            os.makedirs('/home/pi/.residence')

        f = open('/home/pi/.residence/GPIOConfig.json', 'w')
        json_data = self.to_json()
        pprint(json_data)
        f.write(json_data)
        f.close()

    def load(self):
        if os.path.exists('/home/pi/.residence/GPIOConfig.json'):
            f = open('/home/pi/.residence/GPIOConfig.json')
            json_data = f.read()
            self.from_json(json_data)
            f.close()
            return True
        else:
            print "/home/pi/.residence/GPIOConfig.json RPi information file does not exist!"
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

    def from_json(self, json_data):
        saved_data = jsonpickle.decode(json_data)
        self.portsNumber = saved_data.portsNumber
        self.on = saved_data.on
        self.outletDescription = saved_data.outletDescription

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
            str = open('/sys/class/net/{}/address'.format(interface)).readline()
        except:
            str = "00:00:00:00:00:00"
        return str[0:17]

    def get_cpu_speed(self):
        f = os.popen('/opt/vc/bin/vcgencmd get_config arm_freq')
        cpu = f.read()
        return cpu