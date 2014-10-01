# Component for keeping track of the connected devices to the Residence application

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
from gpio import RPi, Outlet
import jsonpickle


# Registry that holds all of the information about the connected devices
class DeviceRegistry:

    uid = 0
    rpiDevices = []

    def __init__(self):
        self.rpiDevices = []

    def registerRPiDevice(self, rpiJson):
        self.rpiDevices.append(jsonpickle.decode(rpiJson))

    def getUid(self):
        val = self.uid;
        self.uid += 1
        return val


class DeviceRegistryComponent(ApplicationSession):

    devReg = DeviceRegistry()

    @inlineCallbacks
    def onJoin(self, details):
        print "DeviceRegistryComponent is online"
        yield self.register(self)

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
        print "Listing all of the available RPi devices that are connected"
        return jsonpickle.encode(self.devReg.rpiDevices)


if __name__ == '__main__':
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(DeviceRegistryComponent)