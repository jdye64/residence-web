# Component for keeping track of the connected devices to the Residence application

import time

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
import jsonpickle
from autobahn.twisted.util import sleep


# Registry that holds all of the information about the connected devices
class DeviceRegistry:

    heartbeatmaxthreshold = 15  #Seconds that after a heartbeat hasn't been received for a device it is considered to be offline
    offlineDeviceCheckInterval = 5  #Seconds between checking registry for offline devices
    uid = 0
    rpiDevices = []

    def __init__(self):
        self.rpiDevices = []

    def registerRPiDevice(self, rpiJson):
        self.rpiDevices.append(jsonpickle.decode(rpiJson))

    def removeRPiFromRegistryByUid(self, uid):
        rpi = self.findRPiDeviceByUID(uid)
        self.rpiDevices.remove(rpi)

    def getUid(self):
        val = self.uid
        self.uid += 1
        return val

    def findRPiDeviceByUID(self, uid):
        for rpi in self.rpiDevices:
            if rpi.uid == uid:
                return rpi

    def updateHeartbeat(self, heartbeat):
        rpi = self.findRPiDeviceByUID(heartbeat.uid)
        if rpi:
            rpi.lastheartbeat = heartbeat.timestamp
        else:
            print "Unable to find a RPi device in the registry for the heartbeat received!"


    def checkForOfflineDevices(self):
        #Loop through all of the devices and check for the devices that have not responded in a certain threshold
        offlinedevices = []
        for rpi in self.rpiDevices:
            if not rpi.lastheartbeat:
                 #This is the first heartbeat for this device so lets update it.
                rpi.lastheartbeat = time.time()
            else:
                if (time.time() - rpi.lastheartbeat) > self.heartbeatmaxthreshold:
                    #Add the RPi Device to the list of offline devices.
                    offlinedevices.append(rpi)

        return offlinedevices



class RPiDeviceRegistryComponent(ApplicationSession):

    devReg = DeviceRegistry()

    @inlineCallbacks
    def onJoin(self, details):
        print "RPiDeviceRegistryComponent is online"
        yield self.register(self)
        yield self.subscribe(self)

        #Register to start checking for offline device
        while True:
            offlinedevices = yield self.devReg.checkForOfflineDevices()
            for off in offlinedevices:
                # PULISH a message and remove the device from the registry
                yield self.publish(u'com.jeremydyer.residence.rpi.offline', jsonpickle.encode(off))
                self.devReg.removeRPiFromRegistryByUid(off.uid)

            yield sleep(self.devReg.offlineDeviceCheckInterval)

    #RPC for a RPi device to REQUEST to join the session.
    @wamp.register(u'com.jeremydyer.residence.rpi.join.request')
    def rpi_join_request(self):
        print "RPi device is requesting to join the session"
        # Normally here we would validate that the device is allowed to join the session
        return self.devReg.getUid()

    #RPC for a RPi device to call to officially join the Residence session
    @wamp.register(u'com.jeremydyer.residence.rpi.join')
    def rpi_join_session(self, rpiJson):
        print "RPiDevice joined the session"
        print rpiJson
        self.devReg.registerRPiDevice(rpiJson)
        return len(self.devReg.rpiDevices)

    #Returns the list RPi Devices to the requesting client
    @wamp.register(u'com.jeremydyer.residence.rpi.list')
    def list_rpi_devices(self):
        return jsonpickle.encode(self.devReg.rpiDevices)

    #Listens for the RPi device heartbeats
    @wamp.subscribe(u'com.jeremydyer.residence.rpi.heartbeat')
    def heartbeat_listen(self, heartbeat):
        self.devReg.updateHeartbeat(jsonpickle.decode(heartbeat))


if __name__ == '__main__':
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(RPiDeviceRegistryComponent)