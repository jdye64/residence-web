__author__ = 'jeremydyer'

class RPi:

    deviceIP = "0.0.0.0"

    def __init__(self, ip):
        self.deviceIP = ip

    def something(self):
        print 'something'
