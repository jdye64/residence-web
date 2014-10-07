# Component for controlling a WebCam connected to a RPi device
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
import base64
import os

class RPiWebCamComponent(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        print "RPiWebCamComponent is online!"
        yield self.register(self)
        yield self.subscribe(self)

    @wamp.register(u'com.jeremydyer.residence.rpi.webcam.takesnapshot')
    def take_snapshot(self):

        print "Taking snapshot image"
        # os.makedirs('/home/pi/images')
        # cmd = "fswebcam -r 400x400 /home/pi/images/image.jpg"
        # os.system(cmd)
        #
        # fd = open("/home/pi/images/image.jpg", "rb")
        fd = open("/home/pi/moose.jpg")
        encoded_string = base64.b64encode(fd.read())
        return {"image": encoded_string}


if __name__ == '__main__':
    runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "realm1")
    runner.run(RPiWebCamComponent)