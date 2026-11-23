#!/usr/bin/env python3
"""crc-forge : CRC32 par octet (init=~i, xorout=0xffffffff) ; brute-force chaque position."""
import sys
data=open(sys.argv[1] if len(sys.argv)>1 else 'chall','rb').read()
targets=[int.from_bytes(data[0x2060+4*i:0x2064+4*i],'little') for i in range(28)]
POLY=0xedb88320
def cs(i,c):
    reg=(~i)&0xffffffff
    for _ in range(8): reg=((reg>>1)^(POLY if reg&1 else 0))&0xffffffff
    r=(c^reg)&0xffffffff
    for _ in range(8): r=((r>>1)^(POLY if r&1 else 0))&0xffffffff
    return (~r)&0xffffffff
print(''.join(chr(next(c for c in range(256) if cs(i,c)==targets[i])) for i in range(28)))
