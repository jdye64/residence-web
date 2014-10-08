# Component for playing Audio files on the RPi device that the component is running on
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
import os

#Caches audio files downloaded from the S3 bucket to the local device for faster load times
class LocalAudioCacheStore:

    s3url = None
    cache_dir = None  #Cache directory on the local device
    cachedFilesMap = {}    #Map of the cached URLs and their corelating file on the local filesystem.

    def __init__(self, cache_dir, s3Url):
        self.s3url = s3Url
        self.cache_dir = cache_dir
        print "Creating Audio Cache Store instance"
        print "Audio Cached from " + str(s3Url)

    def play_cached_file(self, url):
        cache_file = self.cachedFilesMap.get(url)
        if cache_file == None:
            cache_file = self.cache_audio(url)
            self.cachedFilesMap[url] = cache_file

        # Plays the cached file
        #os.system('mpg123 ' + destfile + ' &')
        os.system('aplay ' + cache_file)

    def cache_audio(self, url):
        print "Downloading and caching the audio file " + str(url)
        url_parts = url.split("/")
        filename = url_parts[len(url_parts) - 1]
        print str(filename)
        destfile = self.cache_dir + filename

        downloadcmd = "wget " + url + " -O " + destfile
        print "Running download cmd " + downloadcmd
        os.system(downloadcmd)
        print "S3 download is complete"
        return destfile


class RPiAudioPlaybackComponent(ApplicationSession):

    cache = LocalAudioCacheStore("/home/pi/.audio/", "https://s3.amazonaws.com/makeandbuild/courier/audio/")

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
        self.cache.play_cached_file(sourceURL)

if __name__ == '__main__':
    #runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "realm1")
    #runner.run(RPiAudioPlaybackComponent)

    test = RPiAudioPlaybackComponent()
    test.cache.play_cached_file("https://s3.amazonaws.com/makeandbuild/courier/audio/1.wav")
    test.cache.play_cached_file("https://s3.amazonaws.com/makeandbuild/courier/audio/1.wav")
    test.cache.play_cached_file("https://s3.amazonaws.com/makeandbuild/courier/audio/2.wav")
    test.cache.play_cached_file("https://s3.amazonaws.com/makeandbuild/courier/audio/3.wav")
    test.cache.play_cached_file("https://s3.amazonaws.com/makeandbuild/courier/audio/2.wav")