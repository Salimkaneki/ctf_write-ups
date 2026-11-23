#!/usr/bin/env python3
"""MD5 length extension pour agbale : forge MD5(SECRET||user=guest||pad||append)."""
import struct, urllib.request, urllib.parse, urllib.error, sys, json

# --- MD5 permettant d'initialiser l'état et le compteur d'octets déjà traités ---
import math
_s=[7,12,17,22]*4+[5,9,14,20]*4+[4,11,16,23]*4+[6,10,15,21]*4
_K=[int(abs(math.sin(i+1))*2**32)&0xffffffff for i in range(64)]
def _lrot(x,c): x&=0xffffffff; return ((x<<c)|(x>>(32-c)))&0xffffffff

def md5_from(state, msg, prelen):
    """MD5 en continuant depuis `state` (a,b,c,d), avec `prelen` octets déjà absorbés
    (multiple de 64). `msg` = octets supplémentaires à hacher ; le padding final encode
    la longueur totale prelen+len(msg)."""
    a0,b0,c0,d0=state
    total=prelen+len(msg)
    data=bytearray(msg)
    data+=b'\x80'
    while len(data)%64!=56: data+=b'\x00'
    data+=struct.pack('<Q', total*8)
    for off in range(0,len(data),64):
        M=list(struct.unpack('<16I', data[off:off+64]))
        A,B,C,D=a0,b0,c0,d0
        for i in range(64):
            if i<16: F=(B&C)|(~B&D); gidx=i
            elif i<32: F=(D&B)|(~D&C); gidx=(5*i+1)%16
            elif i<48: F=B^C^D; gidx=(3*i+5)%16
            else: F=C^(B|(~D&0xffffffff)); gidx=(7*i)%16
            F=(F+A+_K[i]+M[gidx])&0xffffffff
            A,D,C=D,C,B
            B=(B+_lrot(F,_s[i]))&0xffffffff
        a0=(a0+A)&0xffffffff; b0=(b0+B)&0xffffffff
        c0=(c0+C)&0xffffffff; d0=(d0+D)&0xffffffff
    return struct.pack('<4I',a0,b0,c0,d0).hex()

def state_from_hex(h):
    return list(struct.unpack('<4I', bytes.fromhex(h)))

def md5_padding(msglen):
    pad=b'\x80'
    while (msglen+len(pad))%64!=56: pad+=b'\x00'
    pad+=struct.pack('<Q', msglen*8)
    return pad

U="https://wilzgkcphewktgh7.t.ctf.tg"
def admin(raw_msg_bytes, sig):
    q=urllib.parse.quote(raw_msg_bytes, safe='')
    url=U+'/admin?msg='+q+'&sig='+sig
    try: return urllib.request.urlopen(url,timeout=10).read().decode()
    except urllib.error.HTTPError as e: return e.read().decode()
    except Exception as e: return 'ERR'+str(e)

def main():
    base=b'user=guest'
    sig0='8dd74dbec521888d04dcbf55050e2475'   # MD5(SECRET||user=guest)
    state=state_from_hex(sig0)
    appends=[b'&admin=true', b'&admin=1', b'&admin=True', b'&role=admin', b'&admin=yes', b';admin=true']
    for ap in appends:
        for klen in range(1,65):
            L=klen+len(base)
            pad=md5_padding(L)
            forged_sig=md5_from(state, ap, klen+len(base)+len(pad))
            raw=base+pad+ap   # ce que /admin reçoit comme msg (octets bruts)
            r=admin(raw, forged_sig)
            if 'bad' not in r.lower():
                print('>>> SUCCESS klen=%d append=%r'%(klen,ap))
                print('    reponse:', r[:300])
                return
    print('[!] aucun succes — condition admin ou append a revoir')

if __name__=='__main__': main()
