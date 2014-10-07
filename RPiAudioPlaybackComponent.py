# Component for playing Audio files on the RPi device that the component is running on
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

class RPiAudioPlaybackComponent(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        print "RPiAudioPlaybackComponent is online!"
        yield self.register(self)
        yield self.subscribe(self)


if __name__ == '__main__':
    runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "realm1")
    runner.run(RPiAudioPlaybackComponent)