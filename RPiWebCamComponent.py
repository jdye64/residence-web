# Component for controlling a WebCam connected to a RPi device
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from gpio import RPi
import base64

class RPiWebCamComponent(ApplicationSession):

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

    def take_snapshot(self):
        fd = open("yourfile.ext", "rb")
        encoded_string = base64.b64encode(fd.read())


if __name__ == '__main__':
    runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "realm1")
    runner.run(RPiWebCamComponent)