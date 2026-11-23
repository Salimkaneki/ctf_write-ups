#!/usr/bin/env python3
"""afagnan : ECB byte-at-a-time pour récupérer le suffixe secret, puis unlock."""
import urllib.request, urllib.error, json, sys
from concurrent.futures import ThreadPoolExecutor

U="https://tfvulk3d37vcy2ri.t.ctf.tg"

def enc(ptbytes):
    h=ptbytes.hex()
    for _ in range(3):
        try:
            r=urllib.request.urlopen(U+'/enc?pt='+h,timeout=12).read().decode()
            return bytes.fromhex(json.loads(r)['ct'])
        except Exception:
            continue
    raise RuntimeError('enc fail')

def first_block(pt): return enc(pt)[:16]

def recover():
    known=b''
    for i in range(16):
        pad=b'A'*(15-len(known)%16)
        target=first_block(pad)[:16]
        def trial(g):
            return g, enc(pad+known+bytes([g]))[:16]
        found=None
        with ThreadPoolExecutor(max_workers=16) as ex:
            for g,blk in ex.map(trial, range(256)):
                if blk==target: found=g; break
        if found is None:
            print('[*] stop a len',len(known)); break
        known+=bytes([found])
        print('[+] suffixe[%d]=%r  ->  %r'%(i,chr(found) if 32<=found<127 else found, known))
        if found==0x01 and i>0:  # padding atteint ?
            pass
    return known

if __name__=='__main__':
    s=recover()
    print('\n[=] SUFFIXE =', s, '| hex', s.hex())
