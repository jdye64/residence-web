# Component for controlling a Raspberry PI device connected to the Residence session

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


class RPiComponent(ApplicationSession):

    #Unique identifier for this device that will be used to register all of its RPC and Events.
    deviceRegUID = None
    rpiDevices = []

    @inlineCallbacks
    def onJoin(self, details):
        print "Getting the list of devices I guess"
        devices = yield self.call('com.jeremydyer.residence.rpi.list')
        print devices

if __name__ == '__main__':
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(RPiComponent)