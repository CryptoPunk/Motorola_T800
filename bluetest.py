#!/usr/bin/env python3
import asyncio
import binascii
from functools import partial
from bleak import BleakClient


EASYPAIRING_FRAGMENT_1 = 0xb3 # 179
EASYPAIRING_FRAGMENT_2 = 0xb4 # 180
REQUEST_ID_READ_STATUS = 0xca # 202
REQUEST_ID_READ_BATTERY = 0xce # 206
REQUEST_ID_SEND_MESSAGE = 0xd0 # 208
REQUEST_ID_SET_OWNER = 0xa0

SHARELOCATION = 0xe0 # 224 
ECC = 0xe3 # 227
RADIO_RESPONSE = 0xee # 238


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

SERVICE_CMD_SERVICE = "01000100-0000-1000-8000-009078563412"
CHARACTERISTICS_TX = "02000200-0000-1000-8000-009178563412"
CHARACTERISTICS_RX = "03000300-0000-1000-8000-009278563412"

class MotoT800Client():
    def __init__(self, address):
        self.client = BleakClient(address)
        self.address = address
        self.tx_queue = asyncio.Queue()
        
    def notify_callback(self, sender, data):
        self.tx_queue.put_nowait(data)

    @staticmethod
    def msg_encode(data):
        #if len(data) > 20:
        #    raise ValueError("payload size over 20 not implemented currently")
        out = bytearray(len(data)+4)
        out[0] = 126
        out[1] = len(data)+2
        out[2:len(data)+2] = data
        out[len(data)+2] = sum(out[1:]) & 0xFF
        out[len(data)+3] = 239

        return out

    async def connect(self):
        await self.client.connect()
        svcs = await self.client.get_services()
        cmd_svc = svcs.get_service(SERVICE_CMD_SERVICE)
        self.tx_char = cmd_svc.get_characteristic(CHARACTERISTICS_TX)
        self.rx_char = cmd_svc.get_characteristic(CHARACTERISTICS_RX)
        await self.client.start_notify(self.tx_char, self.notify_callback)

    async def disconnect(self):
        for worker in self.workers:
            worker.cancel()
        asyncio.gather(*self.workers, return_exceptions=True)
        await self.client.disconnect()
        self.tx_char = None
        self.rx_char = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self):
        await self.disconnect()

    async def recv(self):
        data = await self.tx_queue.get()
        reads = 1
        try:
            if data[0] != 0x7e:
                raise ValueError("Received invalid start byte")
            while len(data)-2 < data[1]:
                data += await self.tx_queue.get()
                reads += 1

            cksum = sum(data[1:-2]) & 0xFF
            if data[-2] != cksum:
                raise ValueError("checksum error in decode")
            if data[-1] != 0xef:
                raise ValueError("Received invalid stop byte")
            print(binascii.hexlify(data[2:-2]))
            return data[2:-2]
        except Exception as e:
            raise e
        finally:
            for i in range(reads):
                self.tx_queue.task_done()

    async def send(self,msg):
        data = self.msg_encode(msg)
        while len(data) > 20:
            await self.client.write_gatt_char(self.rx_char, data[:20])
            data = data[20:]
        await self.client.write_gatt_char(self.rx_char, data)

    async def set_owner(self,owner_id):
        msg = bytearray(7)
        msg[0] = REQUEST_ID_SET_OWNER
        msg[1:7] = owner_id.to_bytes(length=6,byteorder='little')
        await self.send(msg)


class Message():
    def __init__(self,src,dst,type_code,latitude,longitude,message_id,content):
        self.cmd = 0xd0
        self.src = src
        self.dst = dst
        self.type_code = type_code
        self.latitude = latitude
        self.longitude = longitude
        self.message_id = message_id
        self.content = content

    @classmethod
    def acknowledge(cls, other):
        ack = cls(other.dst,other.src,other.type_code|128,other.latitude,other.longitude,other.message_id,b'')
        return ack

    @classmethod
    def from_bytes(cls, msg):
        src = int.from_bytes(msg[1:1+6], "little")
        dst = int.from_bytes(msg[8:8+6], "little")
        type_code = msg[14]
        latitude = int.from_bytes(msg[15:15+4], "little")
        longitude = int.from_bytes(msg[19:19+4],"little")
        message_id = int.from_bytes(msg[23:23+4],"little")
        content = msg[27:]
        self = cls(src,dst,type_code,latitude,longitude,message_id,content)
        return self

    def to_bytes(self):
        msg = bytearray(len(self.content)+27)
        msg[0] = self.cmd
        msg[1:1+6] = int.to_bytes(self.src,length=6,byteorder="little")
        msg[8:8+6] = int.to_bytes(self.dst,length=6,byteorder="little")
        msg[14] = self.type_code
        msg[15:15+4] = int.to_bytes(self.latitude,length=4,byteorder="little")
        msg[19:19+4] = int.to_bytes(self.longitude,length=4,byteorder="little")
        msg[23:23+4] = int.to_bytes(self.message_id,length=4,byteorder="little")
        msg[27:] = self.content
        return bytes(msg)


async def main():
    address = "44:D5:F2:98:A7:97"
    async with MotoT800Client(address) as client:
        await client.set_owner(0x1337cafebabe)

        msg = await client.recv()
        
        msg = Message(0x1337cafebabe, 91651965531785, 32, 4758068, 4282736887, 989085074, b'yeah!')
        await client.send(msg.to_bytes())
        for i in range(100):
            msg = await client.recv()
            if msg[0] == 0xd0:
                txt = Message.from_bytes(msg)
                print('type_code: {:08b}'.format(txt.type_code))
                if txt.type_code & 128 != 128 and txt.dst == 0x1337cafebabe:
                    ack = Message.acknowledge(txt)
                    await client.send(ack.to_bytes())
                    print("sent ack")

asyncio.run(main())
