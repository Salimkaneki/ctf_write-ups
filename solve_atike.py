#!/usr/bin/env python3
"""Padding oracle CBC (Vaudenay) sur atike. Déchiffre IV||C1||C2 octet par octet."""
import urllib.request, urllib.error, threading
from concurrent.futures import ThreadPoolExecutor

import sys as _sys
U = _sys.argv[1] if len(_sys.argv) > 1 else "https://7tyrjrpzvr6y4mep.t.ctf.tg"
WORKERS = 48
_n = 0; _lock = threading.Lock()

def oracle(data: bytes) -> bool:
    global _n
    with _lock: _n += 1
    import time
    for _ in range(10):
        try:
            r = urllib.request.urlopen(U + "/oracle?data=" + data.hex(), timeout=15).read()
            return r.strip() == b"valid padding"      # 200 = valide (exact)
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return False                           # 400 = invalid padding (decisif)
            time.sleep(0.4)                            # 429/5xx -> backoff puis retry
            continue
        except Exception:
            time.sleep(0.2)
            continue
    return False

def get_target():
    import json
    d = json.loads(urllib.request.urlopen(U + "/challenge", timeout=15).read())
    return d["block_size"], bytes.fromhex(d["target"])

def decrypt_block(prev, cur, bs):
    inter = [0] * bs
    for i in range(bs - 1, -1, -1):
        pad = bs - i
        def test(g):
            cp = bytearray(bs)
            cp[i] = g
            for j in range(i + 1, bs):
                cp[j] = inter[j] ^ pad
            return g, oracle(bytes(cp) + cur)
        from concurrent.futures import as_completed
        cands = []
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {ex.submit(test, g): g for g in range(256)}
            for f in as_completed(futs):
                g, ok = f.result()
                if ok:
                    cands.append(g)
                    if pad > 1:       # positions >1 : un seul candidat suffit -> stop
                        for ff in futs:
                            ff.cancel()
                        break
        if not cands:
            raise RuntimeError(f"aucun candidat i={i}")
        g = cands[0]
        if len(cands) > 1:  # faux positif (souvent pad=1) -> confirmer en bougeant l'octet i-1
            for c in cands:
                cp = bytearray(bs); cp[i] = c
                for j in range(i + 1, bs): cp[j] = inter[j] ^ pad
                if i - 1 >= 0: cp[i - 1] ^= 0xff
                if oracle(bytes(cp) + cur):
                    g = c; break
        inter[i] = g ^ pad
    return bytes(inter[j] ^ prev[j] for j in range(bs)), inter

def main():
    bs, target = get_target()
    blocks = [target[i:i + bs] for i in range(0, len(target), bs)]
    print(f"[*] bs={bs} nb_blocs={len(blocks)} (IV + {len(blocks)-1} blocs CT)")
    pt = b""
    for b in range(1, len(blocks)):
        pb, _ = decrypt_block(blocks[b - 1], blocks[b], bs)
        print(f"[+] bloc {b}: {pb!r}  (queries={_n})")
        pt += pb
    # retirer padding PKCS#7
    if pt and 1 <= pt[-1] <= bs:
        pt2 = pt[:-pt[-1]]
    else:
        pt2 = pt
    print("\n[+] PLAINTEXT:", pt2)
    import re
    m = re.search(rb"NCTF\{[^}]+\}", pt)
    if m: print("[+] FLAG:", m.group().decode())

if __name__ == "__main__":
    main()
