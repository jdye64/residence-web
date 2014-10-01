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
    rpiDevices = []
    heartbeatinterval = 5   #Measured in seconds

    @inlineCallbacks
    def onJoin(self, details):
        self.deviceRegUID = yield self.call('com.jeremydyer.residence.rpi.join.request')
        print "Device Registry Unique Identifier -> " + str(self.deviceRegUID)

        #Registers the RPC components for this device with their unique values received from the device registry
        rpi = RPi(self.deviceRegUID)
        rpi.turnOnOutletRPC = "com.jeremydyer.gpio.power.{}.turnon".format(str(self.deviceRegUID))
        rpi.turnOffOutletRPC = "com.jeremydyer.gpio.power.{}.turnoff".format(str(self.deviceRegUID))
        yield self.register(self.turn_on_outlet, rpi.turnOnOutletRPC)
        yield self.register(self.turn_off_outlet, rpi.turnOffOutletRPC)

        #Now that all of the registration has occured call back and give the list of subscriptions you have
        self.deviceRegUID = yield self.call('com.jeremydyer.residence.rpi.join', rpi.to_json())

        #Publish a message letting all connected devices know that a newly connected device is now available
        yield self.publish('com.jeremydyer.residence.rpi.join.notify', rpi.to_json())

        #Creates the heartbeat object that
        heartbeat = RPiHeartBeat(rpi.uid)

        #Creates an infinite loop to post the heartbeat back to the device registry.
        while True:
            heartbeat.timestamp = time.time()
            yield self.publish(u'com.jeremydyer.residence.rpi.heartbeat', jsonpickle.encode(heartbeat))
            yield sleep(self.heartbeatinterval)

    @inlineCallbacks
    def turn_on_outlet(self, powerOutDesc):
        print "Turning ON GPIO outlet"
        print powerOutDesc
        yield self.publish('com.jeremydyer.gpio.rpi.turnon.notify', 'RaspberryPI GPIO outlet has been turned ON')

    @inlineCallbacks
    def turn_off_outlet(self, powerOutDesc):
        print "Turning OFF GPIO outlet"
        yield self.publish('com.jeremydyer.gpio.rpi.turnoff.notify', 'RaspberryPI GPIO outlet has been turned OFF')

if __name__ == '__main__':
    runner = ApplicationRunner("ws://10.0.1.49:8080/ws", "realm1")
    runner.run(RPiComponent)