import sys

from twisted.internet import reactor
from twisted.python import log

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS


class EchoServerProtocol(WebSocketServerProtocol):

    rpis = []

    def __init__(self):
        self.rpis = []

    def onConnect(self, request):
        headers = {}
        print "Connecting to Server"
        if request.headers.has_key('rpi'):
            #Make sure the RPi instance doesn't already exist in the list
            print request.headers['rpi']
        else:
            print "No request headers to print!"
        return (None, headers)

    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)


if __name__ == '__main__':

    log.startLogging(sys.stdout)
    factory = WebSocketServerFactory("ws://localhost:9000", debug=False, debugCodePaths=False)
    factory.protocol = EchoServerProtocol
    listenWS(factory)

    reactor.run()