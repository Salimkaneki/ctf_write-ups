#!/usr/bin/env python3
"""DFA (Piret-Quisquater) sur l'AES-128 de sokode-crypto.
Faute 1 octet injectée avant MixColumns du round 9 (colonne connue).
Récupère K10 colonne par colonne, puis inverse le key schedule -> clé maître.
Usage: python3 -I solve_sokode.py challenges/sokode-crypto/challenge.txt
"""
import sys, re, hashlib

SBOX = bytes([
0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16])
INV = [0]*256
for i,v in enumerate(SBOX): INV[v]=i
RCON=[0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36]

def gf(a,b):
    p=0
    for _ in range(8):
        if b&1: p^=a
        hi=a&0x80; a=(a<<1)&0xff
        if hi: a^=0x1b
        b>>=1
    return p

# matrice MixColumns : colonne rr = (M[0][rr],..M[3][rr])
M=[[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]]

def b16(x): return x.to_bytes(16,'big')

def parse(path):
    txt=open(path,encoding='utf-8').read()
    def grab(name):
        m=re.search(name+r'\s*=\s*(0x[0-9a-fA-F]+|\d+)',txt)
        return int(m.group(1),0)
    tels=[]
    for i in range(1,17):
        n=f'{i:02d}'
        tels.append(dict(
            pt=b16(grab('PT_'+n)), ct=b16(grab('CT_'+n)),
            ctf=b16(grab('CT_'+n+'_FAULT')), col=grab('FAULT_COL_'+n)))
    return tels

# positions de sortie (index octet = 4*c+r) affectees par une faute colonne F
def positions(F):
    return [4*F+0, 4*((F-1)%4)+1, 4*((F-2)%4)+2, 4*((F-3)%4)+3]

def col_candidates(tel):
    """Ensembles de 4-uplets (k à positions p0..p3) compatibles avec UN télégramme."""
    F=tel['col']; ps=positions(F); ct=tel['ct']; ctf=tel['ctf']
    cands=set()
    for rr in range(4):              # ligne d'injection de la faute
        coefs=[M[r][rr] for r in range(4)]
        for fval in range(1,256):
            dmc=[gf(coefs[r],fval) for r in range(4)]
            ksets=[]
            ok=True
            for r in range(4):
                p=ps[r]; want=dmc[r]; s=[]
                for k in range(256):
                    if INV[ct[p]^k]^INV[ctf[p]^k]==want: s.append(k)
                if not s: ok=False; break
                ksets.append(s)
            if not ok: continue
            for k0 in ksets[0]:
                for k1 in ksets[1]:
                    for k2 in ksets[2]:
                        for k3 in ksets[3]:
                            cands.add((k0,k1,k2,k3))
    return ps,cands

def recover_k10(tels):
    k10=[None]*16
    for F in range(4):
        group=[t for t in tels if t['col']==F]
        ps=positions(F); inter=None
        for t in group:
            _,c=col_candidates(t)
            inter = c if inter is None else (inter & c)
        assert inter and len(inter)==1, f'colonne {F}: {0 if not inter else len(inter)} candidats'
        tup=next(iter(inter))
        for r in range(4): k10[ps[r]]=tup[r]
    return bytes(k10)

def inv_key_schedule(k10):
    # k10 = mots w40..w43 (flat 16 octets, index 4*c+r mapping column-major deja coherent)
    w=[[0,0,0,0] for _ in range(44)]
    for wi in range(4):
        for j in range(4): w[40+wi][j]=k10[4*wi+j]
    for i in range(43,3,-1):
        if i%4==0:
            t=w[i-1][1:]+w[i-1][:1]
            t=[SBOX[b] for b in t]; t[0]^=RCON[i//4-1]
        else:
            t=w[i-1]
        w[i-4]=[w[i][j]^t[j] for j in range(4)]
    key=b''.join(bytes(w[i]) for i in range(4))
    return key

# verif AES standard
def key_exp(key):
    w=list(key)
    for i in range(4,44):
        t=w[(i-1)*4:i*4]
        if i%4==0:
            t=t[1:]+t[:1]; t=[SBOX[b] for b in t]; t[0]^=RCON[i//4-1]
        for j in range(4): w.append(w[(i-4)*4+j]^t[j])
    return [bytes(w[i*16:(i+1)*16]) for i in range(11)]
def enc(pt,key):
    rk=key_exp(key)
    s=[[pt[r+4*c] for c in range(4)] for r in range(4)]
    def ark(s,k):
        ks=[[k[r+4*c] for c in range(4)] for r in range(4)]
        return [[s[r][c]^ks[r][c] for c in range(4)] for r in range(4)]
    def sb(s): return [[SBOX[s[r][c]] for c in range(4)] for r in range(4)]
    def sr(s): return [[s[r][(c+r)%4] for c in range(4)] for r in range(4)]
    def mc(s):
        o=[[0]*4 for _ in range(4)]
        for c in range(4):
            col=[s[r][c] for r in range(4)]
            o[0][c]=gf(2,col[0])^gf(3,col[1])^col[2]^col[3]
            o[1][c]=col[0]^gf(2,col[1])^gf(3,col[2])^col[3]
            o[2][c]=col[0]^col[1]^gf(2,col[2])^gf(3,col[3])
            o[3][c]=gf(3,col[0])^col[1]^col[2]^gf(2,col[3])
        return o
    s=ark(s,rk[0])
    for rnd in range(1,10):
        s=sb(s); s=sr(s); s=mc(s); s=ark(s,rk[rnd])
    s=sb(s); s=sr(s); s=ark(s,rk[10])
    return bytes(s[r][c] for c in range(4) for r in range(4))

def main():
    path=sys.argv[1] if len(sys.argv)>1 else 'challenges/sokode-crypto/challenge.txt'
    tels=parse(path)
    print('[*] diff positions / colonne (sanity):')
    for t in tels[:5]:
        diff=[i for i in range(16) if t['ct'][i]!=t['ctf'][i]]
        print(f"  col={t['col']} diff={diff} attendu={sorted(positions(t['col']))}")
    k10=recover_k10(tels)
    print('[+] K10 =', k10.hex())
    key=inv_key_schedule(k10)
    print('[+] CLE MAITRE =', key.hex())
    # verification
    ok=all(enc(t['pt'],key)==t['ct'] for t in tels)
    print('[+] verif AES(PT,key)==CT pour les 16 telegrammes :', ok)
    print('    key ascii repr:', key)
    for tag in [key.hex(), key.hex().upper()]:
        print('    sha256(%s..)='%tag[:8], hashlib.sha256(tag.encode()).hexdigest())
    print('    sha256(rawkey)=', hashlib.sha256(key).hexdigest())

if __name__=='__main__':
    main()
