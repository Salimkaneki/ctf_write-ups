#!/usr/bin/env python3
"""commit-bias : Berlekamp-Massey sur F_p pour prédire la vault draw, desceller le flag."""
import re,hashlib,sys
txt=open(sys.argv[1] if len(sys.argv)>1 else 'ledger.coinvault').read()
p=int(re.search(r'^P=([0-9a-f]+)',txt,re.M).group(1),16); FE=(p.bit_length()+7)//8
Y=[int(m.group(1),16) for m in re.finditer(r'\|Y=([0-9a-f]+)\|',txt)]
vm=re.search(r'^VAULT\|IDX=(\d+)\|C=([0-9a-f]+)\|CT=([0-9a-f]+)',txt,re.M)
vidx=int(vm.group(1)); vC=vm.group(2); CT=bytes.fromhex(vm.group(3))
def bm(s,p):
    n=len(s);C=[1]+[0]*n;B=[1]+[0]*n;L=0;m=1;b=1
    for i in range(n):
        d=s[i]%p
        for j in range(1,L+1): d=(d+C[j]*s[i-j])%p
        if d==0: m+=1
        elif 2*L<=i:
            T=C[:];co=d*pow(b,-1,p)%p
            for j in range(n+1-m): C[j+m]=(C[j+m]-co*B[j])%p
            L=i+1-L;B=T;b=d;m=1
        else:
            co=d*pow(b,-1,p)%p
            for j in range(n+1-m): C[j+m]=(C[j+m]-co*B[j])%p
            m+=1
    return C[:L+1],L
C,L=bm(Y,p)
Yv=(-sum(C[j]*Y[len(Y)-j] for j in range(1,L+1)))%p
assert hashlib.sha256(Yv.to_bytes(FE,'big')+vidx.to_bytes(4,'big')).digest()[:16].hex()==vC
key=hashlib.sha256(Yv.to_bytes(FE,'big')).digest(); st=b'';i=0
while len(st)<len(CT): st+=hashlib.sha256(key+i.to_bytes(4,'big')).digest();i+=1
print("order",L,"FLAG:",bytes(x^y for x,y in zip(CT,st)).decode())
