from collections import deque
import time
import json

class iBeaconMapping():

    owner_mappings = {"b9407f30f5f8466eaff925556b57fe6d:1:1": "Jeremy Dyer",
                "b9407f30f5f8466eaff925556b57fe6d:1:2": "Andrew Zuercher",
                "b9407f30f5f8466eaff925556b57fe6d:1:3": "Jeff Pierce",
                "b9407f30f5f8466eaff925556b57fe6d:1:4": "Tom Elrod",
                "b9407f30f5f8466eaff925556b57fe6d:1:5": "Ed Grasing",
                "b9407f30f5f8466eaff925556b57fe6d:1:6": "Evan",
                "b9407f30f5f8466eaff925556b57fe6d:1:7": "Ken Orji",
                "b9407f30f5f8466eaff925556b57fe6d:1:8": "Tyler Porter",
                "b9407f30f5f8466eaff925556b57fe6d:1:9": "Gabe Arronte",
                "b9407f30f5f8466eaff925556b57fe6d:1:10": "Laura Robi"}

    def __init__(self):
        print "Initializing iBeaconMapping"

    def map_beacon_to_name(self, data):
        beacon_id = str(data['uuid']) + ":" + str(data['major']) + ":" + str(data['minor'])
        person = self.owner_mappings.get(beacon_id)
        if person:
            return person
        else:
            return "UNKNOWN"

class Beacon:

    #This is bad but for testing lets define a hardcoded list of people -> iBeacons
    mapping = iBeaconMapping()

    def __init__(self, data):
        self.distances = deque(maxlen=10)
        self.distance = 0
        self.last_seen = 0
        self.uuid = data['uuid']
        self.major = data['major']
        self.minor = data['minor']
        self.rssi = data['rssi']
        self.tx = data['tx']
        self.update(data)
        self.owner = self.mapping.map_beacon_to_name(data)

    def update(self, data):
        self.distances.append(data['proximity'])
        self.distance = self.avg()
        self.last_seen = data['time']

    def avg(self):
        """ A basic average. It would be better to use an EMA. """
        return round(sum(self.distances) / len(self.distances), 2)

    def to_dict(self):
        return {
            'time': self.last_seen,
            'uuid': self.uuid,
            'major': self.major,
            'minor': self.minor,
            'tx': self.tx,
            'rssi': self.rssi,
            'distance': self.distance,
            'owner': self.owner
        }


class Beacons(dict):
    """ A container for tracking beacons """

    def heartbeat(self, data):
        """ Update or add a beacon """

        key = self._make_key(data)

        if key in self:
            self[key].update(data)
        else:
            beacon = Beacon(data)

            #Beacons that are not mapped are ignored!
            if not beacon.mapping.map_beacon_to_name(data) == "UNKNOWN":
                self[key] = Beacon(data)

    def _make_key(self, data):
        """ Make a concatenated key """

        return "%s:%s:%s" % (
            data['uuid'],
            data['major'],
            data['minor']
        )

    def expirations(self):
        """ Remove beacons not seen for a minute """

        now = time.time()
        cutoff = now - (60 * 1)  # one minute ago

        truncate = []
        for key, beacon in self.items():
            if now - beacon.last_seen > cutoff:
                self.truncate.append(key)

        for key in truncate:
            del(self[key])

    def to_json(self):
        json_data = []
        for key, beacon in self.items():
            json_data.append(beacon.to_dict())
        return json.dumps(json_data)