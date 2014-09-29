from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.types import RegisterOptions
from RPi import RPi
import jsonpickle


class AppSession(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        clients = [] # List of connected clients that will control the RPi devices
        rpis = [RPi("10.0.1.50"), RPi("10.0.1.51"), RPi("10.0.1.52")]   # List of connected RPi devices

        def clientjoin(clientinfo):
            print "Client has joined the server session"
            print clientinfo
            clients.append(clientinfo)
            print "Number of connected clients " + str(len(clients))
            print "Number of connected RPIs " + str(len(rpis))
            return jsonpickle.encode(rpis)
        yield self.register(clientjoin, 'com.jeremydyer.gpio.client.join')
        print "procedure clientjoin() registered"

        @inlineCallbacks
        def rpijoin(rpiinfo):
            print "A RaspberryPI has joined the session"
            print rpiinfo
            yield self.publish('com.jeremydyer.gpio.rpi.join.notify', 'A new RPi has joined the session!')
        yield self.register(rpijoin, 'com.jeremydyer.gpio.rpi.join')
        print "Registered rpijoin()"

        ## REGISTER a topic to turn ON an outlet
        @inlineCallbacks
        def turnon():
            print "Turning ON an outlet"
            yield self.publish('com.jeremydyer.gpio.turnon.notify', 'Outlet was turned on!')
        yield self.register(turnon, 'com.jeremydyer.gpio.turnon')
        print("procedure turnon() registered")

        ## REGISTER a procedure to turn OFF an outlet
        @inlineCallbacks
        def turnoff():
            print "Turning OFF an outlet"
            yield self.publish('com.jeremydyer.gpio.turnoff.notify', 'Outlet was turned off!')
        yield self.register(turnoff, 'com.jeremydyer.gpio.turnoff')
        print("procedure turnoff() registered")

        ## session metaevents: these are fired by Crossbar.io
        ## upon _other_ WAMP sessions joining/leaving the router
        ##

        @inlineCallbacks
        def on_session_join(details):
            print("on_session_join: {}".format(details))

        yield self.subscribe(on_session_join, 'wamp.metaevent.session.on_join')


        @inlineCallbacks
        def on_session_leave(details):
            print("on_session_leave: {}".format(details))

        yield self.subscribe(on_session_leave, 'wamp.metaevent.session.on_leave')
