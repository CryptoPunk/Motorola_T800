#!/usr/bin/env python3
import asyncio
from functools import partial
from bleak import BleakClient

address = "44:D5:F2:98:A7:97"
SERVICE_CMD_SERVICE = "01000100-0000-1000-8000-009078563412"
CHARACTERISTICS_TX = "02000200-0000-1000-8000-009178563412"
CHARACTERISTICS_RX = "03000300-0000-1000-8000-009278563412"


EASYPAIRING_FRAGMENT_1 = 179
EASYPAIRING_FRAGMENT_2 = 180
REQUEST_ID_READ_STATUS = 202
REQUEST_ID_READ_BATTERY = 206
REQUEST_ID_SEND_MESSAGE = 208
SHARELOCATION = 224 
ECC = 227
RADIO_RESPONSE = 238


MSG_TYPE_TEXT            = 0
MSG_TYPE_LOCATION        = 2
MSG_TYPE_TRACK           = 3
MSG_TYPE_OFFLINE_MAP     = 4
MSG_TYPE_LOCATION        = 5
MSG_TYPE_GEOFENCE        = 6
MSG_TYPE_GEOFENCE_SET    = 7
MSG_TYPE_GEOFENCE_DENY   = 8
#                           9 & PERSONAL
#                           10 | 11 & GROUP
MSG_TYPE_LEAVE_GROUP     = 12
#                           13
#                           14 LOCATION


MSG_IS_PERSONAL  = 32  # 00100000
MSG_IS_GROUP     = 64  # 01000000
MSG_IS_SHOUT     = 96  # 01100000
MSG_BIT_RESPONSE = 128 # 10000000

def notify_callback(client: BleakClient, sender: int, data: bytearray):
    if data[2] in (REQUEST_ID_SEND_MESSAGE, SHARELOCATION, ECC, RADIO_RESPONSE):
        cmd = msg[0]
        src = msg[1:8]
        dst = msg[8:14]
        _type = msg[14]
        latitude = msg[15:15+4]
        longitude = msg[19:19+4]
        message_id = msg[23:23+4]

        content = msg[27:]

    """Notification callback with client awareness"""
    print(
        f"Notification from device with address {client.address} and characteristic with handle {client.services.get_characteristic(sender)}. Data: {data}"
    )

def msg(data):
    out = bytearray(len(data)+4)
    out[0] = 126
    out[1] = len(data)+2
    out[2:len(data)+2] = data
    out[len(data)+2] = sum(out[1:]) & 0xFF
    out[len(data)+3] = 239

    return out
 

async def main():
    async with BleakClient(address) as client:
        #await client.connect()
        svcs = await client.get_services()
        cmd_svc = svcs.get_service(SERVICE_CMD_SERVICE)
        tx = cmd_svc.get_characteristic(CHARACTERISTICS_TX)
        await client.start_notify(tx, partial(notify_callback, client))
        rx = cmd_svc.get_characteristic(CHARACTERISTICS_RX)

        #await client.write_gatt_char(rx, msg(bytearray([256-50])))
        #await client.write_gatt_char(rx, msg(bytearray([256-56])))
        await client.write_gatt_char(rx, msg(bytearray([256-96, 0xbe, 0xba, 0xfe, 0xca, 0x37, 0x13])))
        #data = await client.read_gatt_char(tx)
        #print(data)
        await asyncio.sleep(100.0)
        
asyncio.run(main())
