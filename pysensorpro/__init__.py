import asyncio
import logging
from datetime import datetime, timedelta
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from struct import unpack


def _log(event):
    logging.info(event)
    return event


_CALLBACKS=[_log]
_RATELIMIT=1
_RATELIMIT_TRACKER={}


def add_callback(callback):
    _CALLBACKS.append(callback)


def set_rate_limit(sec):
    _RATELIMIT=sec

def _parse_manufacturer_data(msg):
        if 43605 not in msg:
            raise ValueError("No Manufacturer data ID 43605 in message")
        data = msg[43605]
        if not data:
            raise ValueError("No Manufacturer data in ID 43605 of message")
        
        if not data.startswith(b"\x01\x01\xa4\xc1") and not data.startswith(
            b"\x01\x05\xa4\xc1"
        ):
            raise ValueError("Invalid prefix in message data")

        (temp, humi, batt) = unpack(">hHB", data[10:15])
        reading = {
            'temp': temp / 100,
            'rel_humi': humi / 100,
            'batt': batt
        }
        return reading


def _on_event(device: BLEDevice, advertisement_data: AdvertisementData):
    if advertisement_data.local_name == 'T201':
        
        event = {
                'Timestamp': datetime.now(),
                'MAC' : device.details['props']['Address'],
                'RSSI': device.details['props']['RSSI']}

        event.update(_parse_manufacturer_data(advertisement_data.manufacturer_data))

        if event['MAC'] in _RATELIMIT_TRACKER:
            if datetime.now() - _RATELIMIT_TRACKER[event['MAC']] < timedelta(seconds=_RATELIMIT):
                return

        else:
            _RATELIMIT_TRACKER[event['MAC']] = event['Timestamp']

        for call_fn in _CALLBACKS:
            event = call_fn(event)


async def _run(): 
    scanner = BleakScanner()
    scanner.register_detection_callback(_on_event)

    while True:
        await scanner.start()
        await asyncio.sleep(1.0)
        await scanner.stop()

def Start():
    asyncio.run(_run())

