from __future__ import division
import sys
import struct
from struct import unpack
from binascii import b2a_hex
from time import time

import dateutil


try:
    import bluetooth._bluetooth as bluez
except ImportError:
    print("WARNING: Unable to import bluetooth module")

# Events
LE_META_EVENT = 0x3e  # basically any LE event...

# LE META SUBEVENTS
EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02
EVT_LE_CONN_UPDATE_COMPLETE = 0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE = 0x04

OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C


def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)


def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x02)


def hci_toggle_le_scan(sock, mode):
    cmd_pkt = struct.pack("<BB", mode, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)


def hci_le_set_scan_parameters(sock):
    SCAN_TYPE = 0x01
    INTERVAL = 0x10
    WINDOW = 0x10
    OWN_TYPE = 0x00
    FILTER = 0x00  # all advertisements, not just whitelisted devices

    cmd_pkt = struct.pack("<BBBBBBB", SCAN_TYPE, 0x0, INTERVAL, 0x0, WINDOW, OWN_TYPE, FILTER)

    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_PARAMETERS, cmd_pkt)

    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    filtr = bluez.hci_filter_new()

    bluez.hci_filter_all_events(filtr)
    bluez.hci_filter_set_ptype(filtr, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(filtr, LE_META_EVENT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, filtr)


def proximity(tx, rssi):
    """ A rough algo to figure distance in meters """

    if rssi == 0:
        return -1.0

    ratio = rssi * 1.0 / tx

    if ratio < 1.0:
        return ratio ** 10
    else:
        return 0.89976 * (ratio ** 7.7095) + 0.111


def parse_events(sock, seconds=1):
    heartbeats = []

    end = time() + seconds

    while time() < end:
        packet = sock.recv(1024)

        ptype, event, plen = unpack("BBB", packet[:3])

        # LE_META_EVENT seems to be all we care about for beacons
        if event != LE_META_EVENT:
            continue

        subevent = unpack("B", packet[3])[0]

        # Again, EVT_LE_ADVERTISING_REPORT is all we care about for beacons.
        # It might be interesting at some point to explore more of BLE
        if subevent != EVT_LE_ADVERTISING_REPORT:
            continue

        # Ignore packets too short to be of use to us
        if len(packet) <= 15:
            continue

        company_code = "%02x%02x%02x%02x" % (unpack('BBBB', packet[19:23]))

        # 4c000215 for Apple ibeacon
        if company_code != '4c000215':
            continue

        heartbeat = {
            'time': dateutil.current_time_stamp(),
            'uuid': b2a_hex(packet[-22:-6]),
            'major': int(b2a_hex(packet[-6:-4]), 16),
            'minor': int(b2a_hex(packet[-4:-2]), 16),
            'tx': unpack("b", packet[-2])[0],
            'rssi': unpack("b", packet[-1])[0],
        }

        heartbeat['proximity'] = proximity(heartbeat['tx'], heartbeat['rssi'])
        heartbeats.append(heartbeat)

    #sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
    return heartbeats


def setup(device_id):
    """ Setup a BLE scanner on a device """

    try:
        sock = bluez.hci_open_dev(device_id)
    except:
        sys.exit('Error: Unable to open device %s' % device_id)

    hci_le_set_scan_parameters(sock)
    hci_enable_le_scan(sock)

    return sock
