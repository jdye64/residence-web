# Component for playing Audio files on the RPi device that the component is running on
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
import time
import os

class RPiAudioPlaybackComponent(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        print "RPiAudioPlaybackComponent is online!"
        yield self.register(self)
        yield self.subscribe(self)

    @wamp.register(u'com.jeremydyer.residence.rpi.audio.play')
    def play_sound(self):
        print "Playing dummy sound"

        # Source file. This will ultimately be present in the JSON payload received by this method.
        sourceURL = "https://s3.amazonaws.com/makeandbuild/courier/audio/1.wav"

        timestamp = time.time()
        destfile = '/home/pi/.audio/' + timestamp + ".wav"

        downloadcmd = "wget " + sourceURL + " -p " + destfile
        os.system(downloadcmd)

        os.system('mpg123 ' + destfile + ' &')
        os.remove(destfile)


if __name__ == '__main__':
    runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "realm1")
    runner.run(RPiAudioPlaybackComponent)