#!/usr/bin/env python3
"""C4 fast-enough : attaque algebrique (AI=2) sur filter-LFSR 80 bits.
Annihilateurs deg2 : F=1 -> x4(x1+x3)=0 ; F=0 -> x2+x4+x1x2+x1x3+x1x4+x2x3+x3x4=0.
On lineaire sur les monomes {x_i, x_i x_j}, on resout le noyau GF(2),
on retrouve l'etat z[0..79], on predit les 64 bits suivants.
Usage: python3 -I solve_fast_enough.py HOST PORT    (ssl)
       python3 -I solve_fast_enough.py --selftest
"""
import sys, hashlib, numpy as np

L=80
POLY_INT=1377573749490194700300181
TAPS=[0,14,32,53,76]
COEF=[2,3,4,5,8]; CST=19; BYTE=0
NBITS=4860; PREDICT=64
FB=[i for i in range(L) if (POLY_INT>>i)&1]

def filter_bit(taps):
    val=CST+sum(c*int(b) for c,b in zip(COEF,taps))
    return hashlib.sha256(str(val).encode()).digest()[BYTE]&1

def keystream(state,n):
    s=list(state); out=[]
    for _ in range(n):
        out.append(filter_bit([s[p] for p in TAPS]))
        fb=0
        for j in FB: fb^=s[j]
        s=s[1:]+[fb]
    return out

# ---- z[k] comme vecteur GF(2) sur base x0..x79 (bitmask 80 bits) ----
def build_z(maxk):
    z=[1<<i for i in range(L)]           # z[i]=x_i
    for k in range(L,maxk+1):
        v=0
        for j in FB: v^=z[k-L+j]
        z.append(v)
    return z

# ---- monomes : lineaires x_i (idx i), quadratiques x_i x_j i<j ----
# index quad: on precompute un dict (i,j)->col
_QIDX={}
def _buildidx():
    c=L
    for i in range(L):
        for j in range(i+1,L):
            _QIDX[(i,j)]=c; c+=1
    return c
NCOL=_buildidx()   # total colonnes (lineaires + quad), pas de constante

def lin_bits(mask):
    """liste des indices i tq bit i set dans mask (vecteur lineaire)."""
    out=[]
    m=mask; i=0
    while m:
        if m&1: out.append(i)
        m>>=1; i+=1
    return out

def prod_cols(A,B):
    """monomes GF(2) du produit (<A,x>)(<B,x>). Renvoie set de colonnes a XORer."""
    ai=lin_bits(A); bi=set(lin_bits(B))
    cols={}
    # terme x_i x_j : coeff = A_i B_j + A_j B_i (i<j), et x_i x_i=x_i (lineaire)
    Abits=lin_bits(A); Bbits=lin_bits(B)
    Aset=set(Abits); Bset=set(Bbits)
    for i in Abits:
        for j in Bbits:
            if i==j:
                col=i
            else:
                a,b=(i,j) if i<j else (j,i)
                col=_QIDX[(a,b)]
            cols[col]=cols.get(col,0)^1
    return [c for c,v in cols.items() if v]

def xor_cols(acc,cols):
    for c in cols: acc[c]^=1

def build_equation(z,t,o):
    V=[z[t+off] for off in TAPS]   # x0..x4 vecteurs
    acc=[0]*NCOL
    if o==1:
        # x4(x1+x3) = x4 x1 + x4 x3
        xor_cols(acc,prod_cols(V[4],V[1]))
        xor_cols(acc,prod_cols(V[4],V[3]))
    else:
        # x2 + x4 + x1x2+x1x3+x1x4+x2x3+x3x4
        for i in lin_bits(V[2]): acc[i]^=1
        for i in lin_bits(V[4]): acc[i]^=1
        for (a,b) in [(1,2),(1,3),(1,4),(2,3),(3,4)]:
            xor_cols(acc,prod_cols(V[a],V[b]))
    return acc

_TRIU=np.triu_indices(L,1)   # (3160,) paires i<j, meme ordre que _QIDX
def _zmat(maxk):
    z=build_z(maxk)
    A=np.zeros((len(z),L),dtype=np.uint8)
    for k,v in enumerate(z):
        for i in range(L):
            if (v>>i)&1: A[k,i]=1
    return A

def build_matrix(given):
    """Construit M (m x 51) uint64, bit c -> mot c>>6, bit c&63. Vectorise numpy."""
    m=len(given)
    zmat=_zmat(NBITS+PREDICT+max(TAPS))
    Mu8=np.zeros((m,NCOL),dtype=np.uint8)
    ti,tj=_TRIU
    g=np.asarray(given,dtype=np.uint8)
    V=[zmat[np.arange(m)+off] for off in TAPS]   # chaque (m,80)
    for t in range(m):
        if g[t]:
            Q=(np.outer(V[4][t],V[1][t]) ^ np.outer(V[4][t],V[3][t]))
            lin=np.diagonal(Q).copy()
        else:
            Q=(np.outer(V[1][t],V[2][t])^np.outer(V[1][t],V[3][t])^np.outer(V[1][t],V[4][t])
               ^np.outer(V[2][t],V[3][t])^np.outer(V[3][t],V[4][t]))
            lin=(V[2][t]^V[4][t]^np.diagonal(Q)).astype(np.uint8)
        S=(Q^Q.T)
        Mu8[t,:L]=lin&1
        Mu8[t,L:]=S[ti,tj]&1
    # packing en uint64 : bit c -> mot c>>6, position c&63
    words=(NCOL+63)//64
    pad=words*64
    P=np.zeros((m,pad),dtype=np.uint64)
    P[:,:NCOL]=Mu8
    P=P.reshape(m,words,64)
    w=(np.uint64(1)<<np.arange(64,dtype=np.uint64))
    M=(P*w).sum(axis=2).astype(np.uint64)
    return M

def solve(given):
    M=build_matrix(given)
    return gf2_nullspace(M,NCOL)

def gf2_nullspace(M,ncol):
    M=M.copy(); m=M.shape[0]; words=M.shape[1]
    pivot_col_of_row=[]
    pivcols={}
    r=0
    rows=list(range(m))
    row=0
    pivot_rows=[]
    col_pivot={}
    for c in range(ncol):
        w=c>>6; bit=np.uint64(1)<<np.uint64(c&63)
        piv=-1
        for rr in range(row,m):
            if M[rr,w]&bit: piv=rr;break
        if piv<0: continue
        M[[row,piv]]=M[[piv,row]]
        mask=(M[:,w]&bit)!=0
        mask[row]=False
        if mask.any():
            M[mask]^=M[row]
        col_pivot[c]=row
        pivot_rows.append(c)
        row+=1
        if row==m: break
    # colonnes libres
    pivot_set=set(pivot_rows)
    free=[c for c in range(ncol) if c not in pivot_set]
    basis=[]
    for fc in free:
        vec=np.zeros(words,dtype=np.uint64)
        def setbit(v,c): v[c>>6]|=np.uint64(1)<<np.uint64(c&63)
        setbit(vec,fc)
        # pour chaque pivot row: pivot var = somme des autres colonnes de la row * vec
        for c in pivot_rows:
            rr=col_pivot[c]
            # bit = parite du produit de la ligne rr avec vec, en excluant col c
            inter=M[rr]&vec
            par=0
            x=0
            for wv in inter: par^=bin(int(wv)).count('1')&1
            # exclure la colonne pivot c elle-meme (M[rr,c]=1 ; vec[c] peut etre 0)
            if par: setbit(vec,c)
        basis.append(vec)
    return free,basis

def vec_state(vec):
    """extrait x0..x79 (partie lineaire) d'un vecteur colonne."""
    return [int((vec[i>>6]>>np.uint64(i&63))&np.uint64(1)) for i in range(L)]

def recover_state(given):
    free,basis=solve(given)
    d=len(basis)
    # candidats = combinaisons non nulles de la base (d petit espere)
    import itertools
    if d>20:
        raise RuntimeError("noyau trop grand dim=%d"%d)
    for bits in range(1,1<<d):
        vec=np.zeros(basis[0].shape,dtype=np.uint64) if basis else None
        for k in range(d):
            if (bits>>k)&1: vec^=basis[k]
        st=vec_state(vec)
        if keystream(st,NBITS)==list(given):
            return st
    return None

def selftest():
    import secrets
    rng=secrets.SystemRandom()
    st=[rng.randrange(2) for _ in range(L)]
    full=keystream(st,NBITS+PREDICT)
    given=full[:NBITS]; nxt=full[NBITS:]
    import time; t0=time.time()
    rec=recover_state(given)
    dt=time.time()-t0
    if rec is None: print("[!] echec recover (%.1fs)"%dt); return
    pred=keystream(rec,NBITS+PREDICT)[NBITS:]
    ok = pred==nxt
    print("[%s] recover=%s predict_next64_ok=%s  (%.1fs)"%("+" if ok else "!",rec==st,ok,dt))

def run(host,port):
    import socket,ssl,time,re
    ctx=ssl._create_unverified_context()
    raw=socket.create_connection((host,port),timeout=30)
    s=ctx.wrap_socket(raw,server_hostname=host)
    buf=b''
    def readline():
        nonlocal buf
        while b'\n' not in buf:
            d=s.recv(65536)
            if not d: return None
            buf+=d
        line,buf=buf.split(b'\n',1)
        return line.decode('utf-8','replace')
    t0=time.time()
    rounds_done=0
    while True:
        line=readline()
        if line is None:
            print('[!] connexion fermee'); break
        line=line.strip()
        if line.startswith('[round'):
            mbits=line.split(']',1)[1].strip()
            given=[int(c) for c in mbits if c in '01']
            assert len(given)==NBITS, len(given)
            st=recover_state(given)
            if st is None:
                print('[!] recover echec'); return
            pred=keystream(st,NBITS+PREDICT)[NBITS:]
            s.sendall((''.join(map(str,pred))+'\n').encode())
            rounds_done+=1
            print('[+] round %d envoye (t=%.1fs)'%(rounds_done,time.time()-t0))
        elif 'FLAG' in line:
            print('\n'+line); return line
        elif line in ('wrong','timeout'):
            print('[!] %s au round %d'%(line,rounds_done)); return
        elif line and not line.startswith('=='):
            print('   >',line[:120])

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--selftest':
        selftest()
    elif len(sys.argv)>2:
        run(sys.argv[1],int(sys.argv[2]))
