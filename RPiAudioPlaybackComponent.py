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

        # Create the in-memory cache from all of the files already in the directory.
        self.rebuild_inmemory_cache()

    def play_cached_file(self, url):
        cache_file = self.cachedFilesMap.get(url)
        if cache_file is None:
            cache_file = self.cache_audio(url)
            self.cachedFilesMap[url] = cache_file

        # Plays the cached file
        file_parts = cache_file.split(".")
        ext = file_parts[len(file_parts) - 1]

        if ext == 'mp3':
            os.system('mpg123 ' + cache_file + ' &')
        else:
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

    def rebuild_inmemory_cache(self):
        for file in os.listdir(self.cache_dir):
            self.cachedFilesMap[self.s3url + file] = self.cache_dir + file

class RPiAudioPlaybackComponent(ApplicationSession):

    cache = LocalAudioCacheStore("/home/pi/.audio/", "https://s3.amazonaws.com/makeandbuild/courier/audio/")

    @inlineCallbacks
    def onJoin(self, details):
        print "RPiAudioPlaybackComponent is online!"
        yield self.register(self)
        yield self.subscribe(self)

    @wamp.register(u'com.jeremydyer.residence.rpi.audio.play')
    def play_sound(self, audio_info):
        self.cache.play_cached_file(audio_info["source_url"])

if __name__ == '__main__':
    runner = ApplicationRunner("ws://pi.jeremydyer.me:9000/ws", "realm1")
    runner.run(RPiAudioPlaybackComponent)