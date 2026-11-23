#!/usr/bin/env python3
"""twister-tell : untemper 624 sorties MT19937, cloner, prédire le keystream, XOR flag.enc."""
import random,sys
outs=[int(x) for x in open(sys.argv[1] if len(sys.argv)>1 else 'outputs.txt').read().split()]
enc=bytes.fromhex(open(sys.argv[2] if len(sys.argv)>2 else 'flag.enc').read().strip())
M=0xffffffff
def undo_r(y,s):
    x=y
    for _ in range(40): x=(y^(x>>s))&M
    return x
def undo_l(y,s,mask):
    x=y
    for _ in range(40): x=(y^((x<<s)&mask))&M
    return x
def untemper(y):
    y=undo_r(y,18); y=undo_l(y,15,0xefc60000); y=undo_l(y,7,0x9d2c5680); y=undo_r(y,11); return y&M
state=[untemper(o) for o in outs]
r=random.Random(); r.setstate((3,tuple(state+[624]),None))
ks=b''.join(r.getrandbits(32).to_bytes(4,'big') for _ in range((len(enc)+3)//4))[:len(enc)]
print(bytes(a^b for a,b in zip(enc,ks)).decode())
