import sys

from twisted.internet import reactor
from twisted.python import log

from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS


class EchoClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print(response)

    def sendHello(self):
        self.sendMessage("Hello, world!".encode('utf8'))

    def onOpen(self):
        #self.sendHello()
        print "Hello World"

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Text message received: {}".format(payload.decode('utf8')))
        reactor.callLater(1, self.sendHello)



if __name__ == '__main__':
    log.startLogging(sys.stdout)
    headers = {'rpi': {'DeviceIP': '10.0.1.50', "LocationId": '1'}}
    factory = WebSocketClientFactory("ws://localhost:9000", headers=headers, debug=False, debugCodePaths=False)
    factory.protocol = EchoClientProtocol
    connectWS(factory)

    reactor.run()