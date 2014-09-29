from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

class AppSession(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        yield self.publish('com.jeremydyer.gpio.rpi.join', 'Just a test')
        print 'joined to crossbar session'
