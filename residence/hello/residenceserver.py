from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession


class AppSession(ApplicationSession):

    #List of trusted keys that this server will allow to join the session
    trustedRPiKeys = []
    rpis = []

    @inlineCallbacks
    def onJoin(self, details):

        @inlineCallbacks
        def rpijoin(rpiinfo):
            print "A RaspberryPI has joined the session"
            print rpiinfo
            print details
            yield self.publish('com.jeremydyer.gpio.rpi.join.notify', 'A new RPi has joined the session!')
        yield self.register(rpijoin, 'com.jeremydyer.gpio.rpi.join')
        print "Registered rpijoin()"

        @inlineCallbacks
        def on_session_join(joinDetails):
            print("on_session_join: {}".format(joinDetails))
        yield self.subscribe(on_session_join, 'wamp.metaevent.session.on_join')

        @inlineCallbacks
        def on_session_leave(details):
            print("on_session_leave: {}".format(details))
        yield self.subscribe(on_session_leave, 'wamp.metaevent.session.on_leave')