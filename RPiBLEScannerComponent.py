# Component for Scanning for BLE devices in range of the RPi device
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

class RPiBLEScannerComponent(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        print "RPiBLEScannerComponent is online!"
        yield self.register(self)
        yield self.subscribe(self)


if __name__ == '__main__':
    runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "realm1")
    runner.run(RPiBLEScannerComponent)