EASYPAIRING_FRAGMENT_1 = 0xb3 # 179
EASYPAIRING_FRAGMENT_2 = 0xb4 # 180
REQUEST_ID_READ_STATUS = 0xca # 202
REQUEST_ID_READ_BATTERY = 0xce # 206
REQUEST_ID_SEND_MESSAGE = 0xd0 # 208
REQUEST_ID_SET_OWNER = 0xa0
SHARELOCATION = 0xe0 # 224 
ECC = 0xe3 # 227
RADIO_RESPONSE = 0xee # 238

def parse_msg(data):
    if data[0] in (REQUEST_ID_SEND_MESSAGE, SHARELOCATION, ECC, RADIO_RESPONSE):
        msg = data[:]
        cmd = msg[0]
        src = int.from_bytes(msg[1:1+6], "little")
        dst = int.from_bytes(msg[8:8+6], "little")
        _type = msg[14]
        latitude = int.from_bytes(msg[15:15+4], "little")
        longitude = int.from_bytes(msg[19:19+4],"little")
        message_id = int.from_bytes(msg[23:23+4],"little")

        content = msg[27:]
        print("cmd: {}, src: {:012d}, dst: {:012x}, _type: {}, latitude: {}, longitude: {}, message_id: {}".format(cmd, src, dst, _type, latitude, longitude, message_id))

import binascii
msg = binascii.unhexlify(b'd08936d9625b5300bebafeca371320349a4800f76045ff953df43a74657374')
parse_msg(msg)
