#This component is used to scan the region by the RPi device for iBeacon devices
import os
import sys

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.twisted.util import sleep

import blescanner
from iBeacon import Beacons


class iBeaconScannerComponent(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        # Subscribes to the annotation defined RPC methods and PUB/SUB events
        yield self.register(self)
        yield self.subscribe(self)

        #Setup the BLE Scanner
        sock = blescanner.setup(0)

        #Creates an infinite loop to post the ibeacon detections back to the server
        breaking = False
        while breaking is False:
            beacons = Beacons()
            heartbeats = blescanner.parse_events(sock, 1)

            for beat in heartbeats:
                beacons.heartbeat(beat)

            json_data = beacons.to_json()

            #Publish beacons
            yield self.publish('com.makeandbuild.coffee.ibeacons', json_data)
            yield sleep(1)


if __name__ == '__main__':
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.")
        sys.exit(0)

    runner = ApplicationRunner("ws://courier.makeandbuildatl.com:9015/ws", "coffee")
    runner.run(iBeaconScannerComponent)