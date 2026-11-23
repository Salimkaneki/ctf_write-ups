#!/usr/bin/env python3
"""Bleichenbacher (BB'98) sur l'oracle PKCS#1 v1.5 de enye. Parallélisé."""
import sys, json, urllib.request, urllib.error, threading
from concurrent.futures import ThreadPoolExecutor

U = "https://6m56oellw6sdmcld.t.ctf.tg"
WORKERS = 48
_count = 0
_lock = threading.Lock()

def oracle(cprime):
    global _count
    with _lock: _count += 1
    for _ in range(5):
        try:
            r = urllib.request.urlopen(U + "/oracle?c=" + str(cprime), timeout=15).read()
            return bool(json.loads(r)['valid'])
        except Exception:
            continue
    raise RuntimeError("oracle fail")

def ceildiv(a, b): return -(-a // b)

def get_challenge():
    d = json.loads(urllib.request.urlopen(U + "/challenge", timeout=15).read())
    return int(d['n']), int(d['e']), int(d['c'])

def main():
    n, e, c = get_challenge()
    k = (n.bit_length() + 7) // 8
    B = 1 << (8 * (k - 2)); B2 = 2 * B; B3 = 3 * B
    print(f"[*] k={k} n_bits={n.bit_length()}")
    # c conforme ?
    assert oracle(c), "c non conforme — blinding requis (non implémenté)"
    print("[*] c est PKCS-conforme (s0=1)")

    def o_s(s):  # oracle sur c*s^e
        return oracle((c * pow(s, e, n)) % n)

    def find_s_from(s_start):
        s = s_start
        while True:
            hi = s + WORKERS
            with ThreadPoolExecutor(max_workers=WORKERS) as ex:
                res = list(ex.map(o_s, range(s, hi)))
            for j, ok in enumerate(res):
                if ok: return s + j
            s = hi

    def search_2c(a, b, s_prev):
        r = ceildiv(2 * (b * s_prev - B2), n)
        while True:
            s_lo = ceildiv(B2 + r * n, b)
            s_hi = (B3 - 1 + r * n) // a
            s = s_lo
            while s <= s_hi:
                hi = min(s + WORKERS, s_hi + 1)
                with ThreadPoolExecutor(max_workers=WORKERS) as ex:
                    res = list(ex.map(o_s, range(s, hi)))
                for j, ok in enumerate(res):
                    if ok: return s + j
                s = hi
            r += 1

    def update(M, s):
        new = set()
        for (a, b) in M:
            r_lo = ceildiv(a * s - B3 + 1, n)
            r_hi = (b * s - B2) // n
            for r in range(r_lo, r_hi + 1):
                na = max(a, ceildiv(B2 + r * n, s))
                nb = min(b, (B3 - 1 + r * n) // s)
                if na <= nb: new.add((na, nb))
        return list(new)

    M = [(B2, B3 - 1)]
    s = ceildiv(n, B3)
    i = 1
    while True:
        if i == 1:
            s = find_s_from(ceildiv(n, B3))
        elif len(M) > 1:
            s = find_s_from(s + 1)
        else:
            a, b = M[0]
            s = search_2c(a, b, s)
        M = update(M, s)
        total = sum(b - a + 1 for a, b in M)
        print(f"[i={i}] intervalles={len(M)} largeur≈{total.bit_length()} bits queries={_count}")
        if len(M) == 1 and M[0][0] == M[0][1]:
            m = M[0][0]
            raw = m.to_bytes(k, 'big')
            print("[+] m (hex tail):", raw.hex()[-80:])
            # retirer padding PKCS1 v1.5 : 00 02 PS 00 msg
            if raw[0] == 0 and raw[1] == 2:
                idx = raw.find(b'\x00', 2)
                msg = raw[idx + 1:]
            else:
                msg = raw
            print("[+] message:", msg)
            import re
            fl = re.search(rb'NCTF\{[^}]+\}', raw)
            if fl: print("\n[+] FLAG:", fl.group().decode())
            return
        i += 1

if __name__ == "__main__":
    main()
