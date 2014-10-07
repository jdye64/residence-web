# Component for controlling a WebCam connected to a RPi device
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
import base64
import os

class RPiWebCamComponent(ApplicationSession):

    image_dir = '/home/pi/images'

    @inlineCallbacks
    def onJoin(self, details):
        print "RPiWebCamComponent is online!"
        yield self.register(self)
        yield self.subscribe(self)

    @wamp.register(u'com.jeremydyer.residence.rpi.webcam.takesnapshot')
    def take_snapshot(self):

        print "Taking snapshot image"

        #If the images directory does not exist then lets make it
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        cmd = "fswebcam -r 352x288 " + self.image_dir + "/image.jpg"
        os.system(cmd)

        fd = open(self.image_dir + "/this.jpg", "rb")
        encoded_string = base64.b64encode(fd.read())
        return {"image": encoded_string}


if __name__ == '__main__':
    runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "realm1")
    runner.run(RPiWebCamComponent)