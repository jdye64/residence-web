#Classes for holding media representations to deliver them via WAMP
import jsonpickle

class image:

    base64_imagedata = None

    def __init__(self, base64_imagedata):
        print "Initializing media/image"
        self.base64_imagedata = base64_imagedata

    def to_json(self):
        return jsonpickle.encode(self)
