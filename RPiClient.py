from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp


class Component(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")
        yield self.register(self)

    @wamp.subscribe(u'com.jeremydyer.gpio.turnon')
    def turnOnOutlet(self):
        print "Turning ON GPIO outlet"

    @wamp.subscribe(u'com.jeremydyer.gpio.turnoff')
    def turnOffOutlet(self):
        print "Turning OFF GPIO outlet"

if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://10.0.1.51:8080/ws", "realm1", extra={'authmethods': ['ticket'], 'authid': 'jdye64'})
    runner.run(Component)