#!/usr/bin/env python3
"""CBC-R : forger un ciphertext décryptant vers un plaintext choisi, via l'oracle de padding.
Puis soumettre à /check."""
import urllib.request, urllib.error, os, sys, threading
from concurrent.futures import ThreadPoolExecutor

import sys as _sys
U = _sys.argv[1] if len(_sys.argv) > 1 else "https://7tyrjrpzvr6y4mep.t.ctf.tg"
BS = 16; WORKERS = 48

def oracle(data: bytes) -> bool:
    import time
    for _ in range(10):
        try:
            r = urllib.request.urlopen(U + "/oracle?data=" + data.hex(), timeout=15).read()
            return r.strip() == b"valid padding"
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return False
            time.sleep(0.4); continue
        except Exception:
            time.sleep(0.2); continue
    return False

def intermediate(block):
    """Récupère D_K(block) via l'oracle (block = bloc ciphertext cible)."""
    inter = [0]*BS
    for i in range(BS-1, -1, -1):
        pad = BS-i
        def test(g):
            cp = bytearray(BS); cp[i] = g
            for j in range(i+1, BS): cp[j] = inter[j] ^ pad
            return g, oracle(bytes(cp) + block)
        from concurrent.futures import as_completed
        cands = []
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {ex.submit(test, g): g for g in range(256)}
            for f in as_completed(futs):
                g, ok = f.result()
                if ok:
                    cands.append(g)
                    if pad > 1:
                        for ff in futs: ff.cancel()
                        break
        g = cands[0]
        if len(cands) > 1:
            for c in cands:
                cp = bytearray(BS); cp[i] = c
                for j in range(i+1, BS): cp[j] = inter[j] ^ pad
                if i-1 >= 0: cp[i-1] ^= 0xff
                if oracle(bytes(cp)+block): g = c; break
        inter[i] = g ^ pad
    return bytes(inter)

def xorb(a, b): return bytes(x ^ y for x, y in zip(a, b))

def pkcs7(p):
    n = BS - (len(p) % BS)
    return p + bytes([n])*n

def forge(plaintext):
    P = pkcs7(plaintext)
    pblocks = [P[i:i+BS] for i in range(0, len(P), BS)]
    C = [None]*(len(pblocks)+1)
    C[-1] = os.urandom(BS)                 # dernier bloc ciphertext arbitraire
    for i in range(len(pblocks)-1, -1, -1):
        I = intermediate(C[i+1])
        C[i] = xorb(I, pblocks[i])         # C[i] (ou IV si i==0)
    return b"".join(C)

def check(data):
    try:
        return urllib.request.urlopen(U + "/check?data=" + data.hex(), timeout=15).read().decode()
    except urllib.error.HTTPError as e:
        return str(e.code)+":"+e.read().decode()

def main():
    for pt in [b"permission:admin@corp.io", b"permission:superadmin@corp.io",
               b"permission:root@corp.io", b"permission:admin@corp.io\n"]:
        fc = forge(pt)
        # vérifier que c'est bien valide côté oracle
        ok = oracle(fc)
        r = check(fc)
        print(f"[{pt!r}] oracle_valid={ok} /check -> {r[:200]}")
        if "NCTF" in r or ("no" not in r.lower()[:5] and r and not r.startswith("4")):
            print(">>> PISTE:", r);
        import re
        m = re.search(r'NCTF\{[^}]+\}', r)
        if m: print("[+] FLAG:", m.group()); return

if __name__ == "__main__":
    main()
