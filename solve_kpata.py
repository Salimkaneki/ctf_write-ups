#!/usr/bin/env python3
"""Attaque de Manger (CRYPTO 2001) sur l'oracle OAEP de kpata.
Oracle(c') = True si le 1er octet du déchiffrement est 0x00 (i.e. m' < B).
Usage : python3 -I solve_kpata.py  (adapter URL + format oracle après probe)."""
import urllib.request, urllib.error, json, sys

U = sys.argv[1] if len(sys.argv) > 1 else "PLACEHOLDER"
_n = 0

def http(path):
    return urllib.request.urlopen(U + path, timeout=15).read().decode()

def get_challenge():
    d = json.loads(http("/challenge"))
    return int(d["n"]), int(d["e"]), int(d["c"])

def oracle_raw(cprime):
    global _n; _n += 1
    for _ in range(6):
        try:
            r = http("/oracle?c=%d" % cprime)
            return json.loads(r)["valid"] is True
        except urllib.error.HTTPError:
            return False
        except Exception:
            continue
    return False

def ceildiv(a, b): return -(-a // b)

def manger(n, e, c):
    k = (n.bit_length() + 7) // 8
    B = 1 << (8 * (k - 1))
    assert 2 * B <= n, "2B<=n requis (sinon variante)"
    def O(f):                      # oracle : f*m mod n < B ?
        return oracle_raw((c * pow(f, e, n)) % n)

    # Étape 1
    f1 = 2
    while O(f1):
        f1 *= 2
    # f1*m in [B, 2B)
    # Étape 2
    f2 = ((n + B) // B) * (f1 // 2)
    while not O(f2):
        f2 += f1 // 2
    # f2*m in [n, n+B)
    # Étape 3
    m_min = ceildiv(n, f2)
    m_max = (n + B) // f2
    while m_min < m_max:
        ftmp = (2 * B) // (m_max - m_min)
        i = (ftmp * m_min) // n
        f3 = ceildiv(i * n, m_min)
        if O(f3):
            m_max = (i * n + B) // f3
        else:
            m_min = ceildiv(i * n + B, f3)
    return m_min

def main():
    n, e, c = get_challenge()
    k = (n.bit_length() + 7) // 8
    print(f"[*] k={k} bits={n.bit_length()}")
    m = manger(n, e, c)
    raw = m.to_bytes(k, "big")
    print("[+] m hex:", raw.hex(), "| queries:", _n)
    import re, hashlib
    def mgf1(seed, length, hfn):
        out = b""; i = 0
        while len(out) < length:
            out += hfn(seed + i.to_bytes(4, "big")).digest(); i += 1
        return out[:length]
    def oaep_decode(em, hfn):
        hlen = hfn().digest_size
        if len(em) != k or em[0] != 0: return None
        masked_seed = em[1:1+hlen]; masked_db = em[1+hlen:]
        seed = bytes(a ^ b for a, b in zip(masked_seed, mgf1(masked_db, hlen, lambda x: hfn(x))))
        db = bytes(a ^ b for a, b in zip(masked_db, mgf1(seed, len(masked_db), lambda x: hfn(x))))
        idx = db.find(b"\x01", hlen)
        return db[idx+1:] if idx >= 0 else None
    found = False
    for name, hfn in [("sha256", hashlib.sha256), ("sha1", hashlib.sha1), ("sha512", hashlib.sha512)]:
        msg = oaep_decode(raw, hfn)
        if msg is not None:
            print(f"[+] OAEP/{name} -> {msg}")
            fm = re.search(rb"NCTF\{[^}]+\}", msg)
            if fm: print("\n[+] FLAG:", fm.group().decode()); found = True; break
    if not found:
        fm = re.search(rb"NCTF\{[^}]+\}", raw)
        if fm: print("[+] FLAG (brut):", fm.group().decode())
        else: print("[!] pas décodé —", raw[-50:])

if __name__ == "__main__":
    main()
