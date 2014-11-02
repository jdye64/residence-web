import sys
import os

# Adds the coffee root directory to the PYTHONPATH so that common modules can be shared.
# Note I know this is really ugly BUT crossbar.io has a bug where the PYTHONPATH cannot
# be set in the config.json currently
add_on_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd())))  # Gets 2 parents dirs up to the root folder
sys.path.append(add_on_dir)

# Component for controlling a Raspberry PI GPIO ports for devices connected to the session.

import time

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.twisted.util import sleep
import jsonpickle

from common.gpio import RPi, RPiHeartBeat

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges."
          "You can achieve this by using 'sudo' to run your script")

class RPiComponent(ApplicationSession):

    #Unique identifier for this device that will be used to register all of its RPC and Events.
    deviceRegUID = None
    rpi = None
    heartbeatinterval = 5   #Measured in seconds

    gpio_mode = GPIO.BOARD
    all_gpio_channels = [3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26]

    # Outlets are laid out on the board physically just like they are listed below
    # A = 5, B = 8, C = 11, D = 13
    # E = 3, F = 7, G = 10, H = 12
    board_gpio_channels = [3, 5, 7, 8, 10, 11, 12, 13]
    # Maps the user friendly outlet values to their underlying GPIO outlet values
    outlet_to_gpio_mapping = {"A": 5, "B": 8, "C": 11, "D": 13, "E": 3, "F": 7, "G": 10, "H": 12}

    GPIO_OFF = True
    GPIO_ON = False

    @inlineCallbacks
    def onJoin(self, details):
        GPIO.setmode(self.gpio_mode)
        for channel in self.board_gpio_channels:
            GPIO.setup(channel, GPIO.OUT)
            GPIO.output(channel, self.GPIO_OFF)

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
    def turn_on_outlet(self, outlet):
        print "Turning ON GPIO outlet " + outlet
        GPIO.output(self.outlet_to_gpio_mapping[outlet], self.GPIO_ON)
        yield self.publish('com.jeremydyer.residence.rpi.outlet.update.dummy', 'RaspberryPI GPIO outlet has been turned ON')

    @inlineCallbacks
    def turn_off_outlet(self, outlet):
        print "Turning OFF GPIO outlet " + outlet
        GPIO.output(self.outlet_to_gpio_mapping[outlet], self.GPIO_OFF)
        yield self.publish('com.jeremydyer.residence.rpi.outlet.update.dummy', 'RaspberryPI GPIO outlet has been turned OFF')

if __name__ == '__main__':
    runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "residence")
    runner.run(RPiComponent)