# Component for controlling a Raspberry PI device connected to the Residence session

import time

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.twisted.util import sleep
import jsonpickle

from gpio import RPi, RPiHeartBeat


class RPiComponent(ApplicationSession):

    #Unique identifier for this device that will be used to register all of its RPC and Events.
    deviceRegUID = None
    rpi = None
    heartbeatinterval = 5   #Measured in seconds

    @inlineCallbacks
    def onJoin(self, details):
        self.deviceRegUID = yield self.call('com.jeremydyer.residence.rpi.join.request')
        print "Device Registry Unique Identifier -> " + str(self.deviceRegUID)

        #Registers the RPC components for this device with their unique values received from the device registry
        self.rpi = RPi(self.deviceRegUID)
        self.rpi.turnOnOutletRPC = "com.jeremydyer.gpio.power.{}.turnon".format(str(self.deviceRegUID))
        self.rpi.turnOffOutletRPC = "com.jeremydyer.gpio.power.{}.turnoff".format(str(self.deviceRegUID))
        self.rpi.updateDeviceRPC = "com.jeremydyer.gpio.residence.{}.update".format(str(self.deviceRegUID))
        yield self.register(self.turn_on_outlet, self.rpi.turnOnOutletRPC)
        yield self.register(self.turn_off_outlet, self.rpi.turnOffOutletRPC)
        yield self.register(self.update_device, self.rpi.updateDeviceRPC)

        #Now that all of the registration has occured call back and give the list of subscriptions you have
        self.deviceRegUID = yield self.call('com.jeremydyer.residence.rpi.join', self.rpi.to_json())

        #Publish a message letting all connected devices know that a newly connected device is now available
        yield self.publish('com.jeremydyer.residence.rpi.join.notify', self.rpi.to_json())

        #Creates the heartbeat object that
        heartbeat = RPiHeartBeat(self.rpi.uid)

        #Creates an infinite loop to post the heartbeat back to the device registry.
        while True:
            heartbeat.timestamp = time.time()
            yield self.publish(u'com.jeremydyer.residence.rpi.heartbeat', jsonpickle.encode(heartbeat))
            yield sleep(self.heartbeatinterval)

    @inlineCallbacks
    def update_device(self, rpiDevice):
        print "Updating RPi Device"
        self.rpi = jsonpickle.decode(rpiDevice)
        responsejson = jsonpickle.encode(self.rpi)
        print responsejson
        yield self.publish('com.jeremydyer.residence.rpi.update.notify', responsejson)

    @inlineCallbacks
    def turn_on_outlet(self, portNumber):
        print "Turning ON GPIO outlet"
        print "Must perform the actual GPIO commands here on the RPi device ..."
        print portNumber
        yield self.publish('com.jeremydyer.residence.rpi.outlet.update', 'RaspberryPI GPIO outlet has been turned ON')

    @inlineCallbacks
    def turn_off_outlet(self, portNumber):
        print "Turning OFF GPIO outlet"
        print portNumber
        yield self.publish('com.jeremydyer.residence.rpi.outlet.update', 'RaspberryPI GPIO outlet has been turned OFF')

if __name__ == '__main__':
    runner = ApplicationRunner("ws://10.0.1.49:8080/ws", "realm1")
    runner.run(RPiComponent)