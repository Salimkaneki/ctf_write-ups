#!/usr/bin/env python3
"""dodo (crypto, ECDH courbe y^2 = x^3 + x, pas de validation de point).
#E = 2^128 * r. On envoie un point Q d'ORDRE 2^128 ; le serveur renvoie S = D*Q.
On resout le DLP 2-adique (Pohlig-Hellman dans le sous-groupe cyclique d'ordre 2^128)
pour recuperer D mod 2^128, bit par bit. Si D < 2^128 c'est la cle complete.

Endpoints live : GET /challenge (p, courbe, flag chiffre), GET /shared?x=&y= (-> S).
Coeur valide hors-ligne contre un simulateur fidele ; wrapping I/O adapte sur l'instance.
"""
import sys, os, hashlib, json, urllib.request, urllib.error

A, B = 1, 0   # courbe y^2 = x^3 + A x + B

# ---------- arithmetique EC sur GF(p) ----------
def inv(a, p): return pow(a % p, p - 2, p)

def is_on(P, p):
    if P is None: return True
    x, y = P
    return (y*y - (x*x*x + A*x + B)) % p == 0

def add(P, Q, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P == Q:
        m = (3*x1*x1 + A) * inv(2*y1, p) % p
    else:
        m = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (m*m - x1 - x2) % p
    y3 = (m*(x1 - x3) - y1) % p
    return (x3, y3)

def mul(k, P, p):
    R = None; k %= (p + 1)  # ordre = p+1 (supersingulier p=3 mod4) ; k mod ordre
    base = P
    while k > 0:
        if k & 1: R = add(R, base, p)
        base = add(base, base, p); k >>= 1
    return R

def order_pow2(P, p, maxe=130):
    """ordre de P s'il divise 2^maxe : renvoie e tel que ord(P)=2^e (sinon None)."""
    if P is None: return 0
    Q = P
    for e in range(1, maxe + 1):
        Q = add(Q, Q, p)
        if Q is None: return e
    return None

def rand_point(p):
    while True:
        x = int.from_bytes(os.urandom((p.bit_length()+7)//8), "big") % p
        rhs = (x*x*x + A*x + B) % p
        if pow(rhs, (p-1)//2, p) != 1 and rhs != 0:
            continue
        y = pow(rhs, (p+1)//4, p)   # p = 3 mod 4
        if (y*y - rhs) % p == 0:
            return (x, y)

def point_of_order_2k(p, k, r):
    """point d'ordre exactement 2^k (ici k=128), via P -> (r * 2^(128-k)) * P."""
    cof = r * (1 << (128 - k))
    while True:
        P = rand_point(p)
        Q = mul(cof, P, p)
        if order_pow2(Q, p) == k:
            return Q

# ---------- DLP 2-adique : D mod 2^k tel que S = D*Q, ord(Q)=2^k ----------
def dlp_2adic(Q, S, p, k=128):
    n = 1 << k
    gamma = mul(n >> 1, Q, p)        # element d'ordre 2
    d = 0
    cur = S                          # S - d*Q, maintenu au fil des bits
    for i in range(k):
        Hi = mul(n >> (i + 1), cur, p)
        if Hi is None:
            bit = 0
        elif Hi == gamma:
            bit = 1
        else:
            raise ValueError(f"bit {i}: point inattendu (Q pas d'ordre 2^{k} ?)")
        if bit:
            d |= (1 << i)
            cur = add(cur, mul(-(1 << i) % n, Q, p), p)   # cur -= 2^i * Q
    return d

# ---------- simulateur + auto-test ----------
def build_prime():
    """p = 2^128 * r - 1 premier, p = 3 mod 4 (=> y^2=x^3+x supersingulier, #E=p+1=2^128 r)."""
    from sympy import isprime
    import secrets
    base = 1 << 128
    r = (secrets.randbits(96) | 1)
    while True:
        p = base * r - 1
        if p % 4 == 3 and isprime(p):
            return p, r
        r += 2

def selftest():
    import secrets
    print("[*] construction p (2^128 * r - 1 premier)...")
    p, r = build_prime()
    print(f"[*] p ~{p.bit_length()} bits, #E=p+1=2^128*r  (r impair={r&1==1})")
    Q = point_of_order_2k(p, 128, r)
    assert order_pow2(Q, p) == 128 and is_on(Q, p)
    ok = 0
    for t in range(3):
        D = secrets.randbits(128)                    # cle privee < 2^128
        S = mul(D, Q, p)                             # reponse serveur /shared
        rec = dlp_2adic(Q, S, p, 128)
        good = (rec % (1 << 128)) == (D % (1 << 128))
        print(f"  essai {t}: D recupere exact = {good}")
        # verif : rec*Q == S
        assert mul(rec, Q, p) == S
        ok += good
    print(f"[*] {ok}/3 — DLP 2-adique dodo valide" if ok == 3 else "[!] echec")
    return ok == 3

# ---------- client live (adaptable) ----------
def http_json(u, path):
    return json.loads(urllib.request.urlopen(u + path, timeout=20).read())

def solve_live(base):
    ch = http_json(base, "/challenge")
    p = int(ch["p"]); r = int(ch.get("r", (p + 1) >> 128))
    Q = point_of_order_2k(p, 128, r)
    sh = http_json(base, f"/shared?x={Q[0]}&y={Q[1]}")
    S = (int(sh["x"]), int(sh["y"]))
    D = dlp_2adic(Q, S, p, 128)
    print("[+] D =", D)
    # flag : adapter selon /challenge (ex: AES/XOR clef = SHA256(D) ou shared reel)
    enc = ch.get("enc") or ch.get("flag")
    if enc:
        key = hashlib.sha256(str(D).encode()).digest()
        ct = bytes.fromhex(enc)
        out = bytearray(); i = 0
        while len(out) < len(ct):
            out += hashlib.sha256(key + i.to_bytes(4, "big")).digest(); i += 1
        pt = bytes(a ^ b for a, b in zip(ct, out))
        import re; m = re.search(rb"NCTF\{[^}]+\}", pt)
        print("[+] FLAG:", m.group().decode() if m else pt[:60])
    return D

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1].startswith("http"):
        solve_live(sys.argv[1].rstrip("/"))
    else:
        selftest()
