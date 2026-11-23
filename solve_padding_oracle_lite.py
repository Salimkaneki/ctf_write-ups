import socket, ssl, struct, sys, threading, time
HOST="ee6ymmrkb4ge7faf.t.ctf.tg"; PORT=1337
NCONN=12
def connect():
    raw=socket.create_connection((HOST,PORT),timeout=20)
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    s=ctx.wrap_socket(raw, server_hostname=HOST)
    # read banner
    read_frame(s)
    return s
def frame(op,pl=b""):
    chk=op
    for b in pl: chk^=b
    return bytes([0xAA,op])+struct.pack('<H',len(pl)//2)+pl+bytes([chk&0xFF])
def readn(s,n):
    buf=b""
    while len(buf)<n:
        d=s.recv(n-len(buf))
        if not d: raise EOFError
        buf+=d
    return buf
def read_frame(s):
    while readn(s,1)!=b"\xAA": pass
    op=readn(s,1)[0]; ln=struct.unpack('<H',readn(s,2))[0]
    pl=readn(s,ln*2); readn(s,1)
    return op,pl
def getct(s):
    s.sendall(frame(0x10,b"")); op,ct=read_frame(s); assert op==0x12; return ct
def oracle(s,blob):
    s.sendall(frame(0x20,blob)); op,pl=read_frame(s); assert op==0x21,(op,pl)
    return struct.unpack('>H',pl)[0]

conns=[connect() for _ in range(NCONN)]
ct=getct(conns[0])
IV=ct[:16]; blocks=[ct[i:i+16] for i in range(16,len(ct),16)]
allb=[IV]+blocks
VALID=oracle(conns[0],ct)
tmp=bytearray(ct); tmp[-17]^=0xFF
INV=oracle(conns[0],bytes(tmp))
print("CTlen",len(ct),"nblk",len(blocks),"VALID",VALID,"INV",INV,flush=True)

def find_pos(Ctar, inter, pos, pad):
    # prepare base Cp with known tail
    base=bytearray(16)
    for k in range(pos+1,16): base[k]=inter[k]^pad
    result={'g':None}
    lock=threading.Lock()
    guesses=list(range(256))
    def worker(conn, mine):
        for g in mine:
            if result['g'] is not None: return
            Cp=bytearray(base); Cp[pos]=g
            st=oracle(conn, bytes(Cp)+Ctar)
            if st==VALID:
                if pad==1:
                    Cp2=bytearray(Cp); Cp2[pos-1]^=0xFF
                    if oracle(conn,bytes(Cp2)+Ctar)!=VALID: continue
                with lock:
                    if result['g'] is None: result['g']=g
                return
    ths=[]
    for i,conn in enumerate(conns):
        mine=guesses[i::NCONN]
        t=threading.Thread(target=worker,args=(conn,mine)); t.start(); ths.append(t)
    for t in ths: t.join()
    return result['g']

recovered=b""
for j in range(len(blocks)):
    Cprev=allb[j]; Ctar=blocks[j]; inter=bytearray(16); plain=bytearray(16)
    for pad in range(1,17):
        pos=16-pad
        g=find_pos(Ctar,inter,pos,pad)
        if g is None: print("FAIL blk",j,"pad",pad,flush=True); sys.exit(1)
        inter[pos]=g^pad
    for k in range(16): plain[k]=inter[k]^Cprev[k]
    recovered+=bytes(plain); print("blk",j,repr(bytes(plain)),flush=True)
padlen=recovered[-1]; token=recovered[:-padlen] if 1<=padlen<=16 else recovered
print("TOKEN",len(token),repr(token),flush=True)
# submit
sub=token if len(token)%2==0 else token+b'\x00'
conns[0].sendall(frame(0x30,sub)); op,pl=read_frame(conns[0])
print("SUBMIT op=%02x %r"%(op,pl),flush=True)
