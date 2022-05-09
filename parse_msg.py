EASYPAIRING_FRAGMENT_1 = 0xb3 # 179
EASYPAIRING_FRAGMENT_2 = 0xb4 # 180
REQUEST_ID_READ_STATUS = 0xca # 202
REQUEST_ID_READ_BATTERY = 0xce # 206
REQUEST_ID_SEND_MESSAGE = 0xd0 # 208
REQUEST_ID_SET_OWNER = 0xa0
SHARELOCATION = 0xe0 # 224 
ECC = 0xe3 # 227
RADIO_RESPONSE = 0xee # 238


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
    def from_bytes(cls, msg):
        src = int.from_bytes(msg[1:1+6], "little")
        dst = int.from_bytes(msg[8:8+6], "little")
        type_code = msg[14]
        latitude = int.from_bytes(msg[15:15+4], "little")
        longitude = int.from_bytes(msg[19:19+4],"little")
        message_id = int.from_bytes(msg[23:23+4],"little")
        content = msg[27:]
        return cls(src,dst,type_code,latitude,longitude,message_id,content)

    def to_bytes(self):
        msg = bytearray(len(content)+27)
        msg[0] = self.cmd
        msg[1:1+6] = int.to_bytes(self.src,length=6,byteorder="little")
        msg[8:8+6] = int.to_bytes(self.dst,length=6,byteorder="little")
        msg[14] = self.type_code
        msg[15:15+4] = int.to_bytes(self.latitude,length=4,byteorder="little")
        msg[19:19+4] = int.to_bytes(self.longitude,length=4,byteorder="little")
        msg[23:23+4] = int.to_bytes(self.message_id,length=4,byteorder="little")
        msg[27:] = content
        return bytes(msg)

        

import binascii
msg = binascii.unhexlify(b'd08936d9625b5300bebafeca3713a0359a4800f76045ff923df43a')
txt = Message.from_bytes(msg)
print('src: {:012x}, dst: {:012x}'.format(txt.src,txt.dst))
print(txt.__dict__)
