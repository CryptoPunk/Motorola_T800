#!/usr/bin/env python3
import binascii
'''
bArr = b"test"
length = len(bArr)+4
bArr2 = bytearray(length)
bArr2[0] = 126
bArr2[1] = len(bArr)+2
bArr2[2:2+len(bArr)] = bArr
print(binascii.hexlify(bArr2))
i = 0
i2 = 1
for i2 in range(1,len(bArr)+2):
    i = (i + bArr2[i2]) & 255
bArr2[len(bArr)+2] = i
bArr2[len(bArr)+3] = 256-17
'''
def msg_gen():
    yield binascii.unhexlify(b'7e21d08936d9625b530000000000000000369a48')
    yield binascii.unhexlify(b'00f46045ff29e8f6027465737412ef')

def msg_decode(gen):
    data = next(gen)
    if data[0] != 0x7e:
        raise ValueError("Received invalid start byte")
    while len(data)-2 < data[1]:
        data += next(gen)

    cksum = sum(data[1:-2]) & 0xFF
    if data[-2] != cksum:
        raise ValueError("checksum error in decode")
    if data[-1] != 0xef:
        raise ValueError("Received invalid stop byte")
    return data[2:-2]

msg_decode(msg_gen())

def msg_encode(data):
    if len(data) > 20:
        raise ValueError("payload size over 20 not implemented currently")
    out = bytearray(len(data)+4)
    out[0] = 126
    out[1] = len(data)+2
    out[2:len(data)+2] = data
    out[len(data)+2] = sum(out[1:]) & 0xFF
    out[len(data)+3] = 0xef

    return out
