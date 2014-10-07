# Component for playing Audio files on the RPi device that the component is running on
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
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
        os.system('mpg321 /home/pi/MyKindOfCrazy.mp3 &')



if __name__ == '__main__':
    runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "realm1")
    runner.run(RPiAudioPlaybackComponent)