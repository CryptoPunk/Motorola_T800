#!/usr/bin/env python3
import binascii
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


