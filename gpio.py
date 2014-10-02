#Contains all of the classes that support the RPi GPIO efforts.
import jsonpickle
import subprocess
import os
import time

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
    secretKey = None
    outlets = []
    turnOnOutletRPC = None
    turnOffOutletRPC = None
    updateDeviceRPC = None
    lastheartbeat = None

    def __init__(self, uid):
        self.uid = uid
        self.ip = "10.0.1.52"
        self.secretKey = "123456789qazwsx"
        self.outlets = []
        self.turnOffOutletRPC = None
        self.turnOffOutletRPC = None
        self.outlets.append(GPIO(0))
        self.outlets.append(GPIO(1))
        self.outlets.append(GPIO(2))
        self.outlets.append(GPIO(3))
        self.outlets.append(GPIO(4))
        self.outlets.append(GPIO(5))
        self.outlets.append(GPIO(6))
        self.outlets.append(GPIO(7))

    def from_json(self, jsonData):
        data = jsonpickle.decode(jsonData)
        print data

    def to_json(self):
        return jsonpickle.encode(self)

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

# class RPi:
#
#     ip = None
#     ram = None
#     cpuspeed = None
#     temperature = None
#     processcount = None
#
#     def __init__(self):
#         pi = RPi_Info()
#         self.ip = pi.get_ipaddress()
#         self.ram = pi.get_ram()
#         self.cpuspeed = pi.get_cpu_speed()
#         self.temperature = pi.get_temperature()
#         self.processcount = pi.get_process_count()
#
#     def to_json(self):
#         return jsonpickle.encode(self)

#
# class Outlet:
#
#     outlet_id = 0
#     gpioPort = 0
#     description = ''
#     on = True
#
#     def __init___(self, outlet_id):
#         self.outlet_id = outlet_id
#         self.on = True


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

    def get_cpu_speed(self):
        f = os.popen('/opt/vc/bin/vcgencmd get_config arm_freq')
        cpu = f.read()
        return cpu