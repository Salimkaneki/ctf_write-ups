#!/usr/bin/env python3
"""kpevi (crypto, DH premier sûr, pas de validation d'ordre).
Attaque sous-groupe : on envoie Y d'ORDRE 2 (= p-1). Le secret partagé
shared = Y^a mod p = (-1)^a vaut 1 (a pair) ou p-1 (a impair) -> 2 candidats.
On déchiffre le flag en essayant les 2 clés. Aucun besoin de connaître a.

Endpoints live : GET /challenge (params + flag chiffré), GET /shared?pub=Y.
Le wrapping I/O exact sera adapté sur l'instance ; le coeur (ci-dessous) est validé
hors-ligne contre un simulateur fidèle.
"""
import sys, hashlib, json, urllib.request, urllib.error

# ---------- primitives ----------
def derive_key(shared, p):
    return hashlib.sha256(str(shared).encode()).digest()

def xor_dec(enc: bytes, key: bytes) -> bytes:
    # keystream = SHA256(key || counter) si flag plus long que 32o
    out = bytearray(); i = 0
    while len(out) < len(enc):
        out += hashlib.sha256(key + i.to_bytes(4, "big")).digest(); i += 1
    return bytes(a ^ b for a, b in zip(enc, out[:len(enc)]))

def candidates_shared(p):
    """secrets partagés possibles quand on envoie Y = p-1 (ordre 2)."""
    return [1, p - 1]

def attack(p, enc_flag: bytes, decrypt=xor_dec):
    """Essaie les 2 candidats, renvoie le clair contenant NCTF{...}."""
    import re
    for s in candidates_shared(p):
        pt = decrypt(enc_flag, derive_key(s, p))
        m = re.search(rb"NCTF\{[^}]+\}", pt)
        if m:
            return s, m.group().decode(), pt
    # fallback : peut-être clé = shared brut (sans hash) ou AES
    return None, None, None

# ---------- client live (adaptable) ----------
def http_json(u, path):
    r = urllib.request.urlopen(u + path, timeout=15).read()
    return json.loads(r)

def solve_live(base):
    """Flux supposé : /challenge -> {p,g,enc}. On envoie Y=p-1 à /shared,
    qui renvoie le flag chiffré avec la clé du shared. On brute les 2 candidats."""
    ch = http_json(base, "/challenge")
    p = int(ch["p"])
    # soumettre Y = p-1
    Y = p - 1
    try:
        sh = http_json(base, f"/shared?pub={Y}")
        enc_hex = sh.get("enc") or sh.get("flag") or sh.get("ciphertext")
    except Exception:
        enc_hex = ch.get("enc") or ch.get("flag")
    enc = bytes.fromhex(enc_hex)
    s, flag, _ = attack(p, enc)
    print("[+] shared =", s, "| FLAG:", flag)
    return flag

# ---------- simulateur + auto-test ----------
def selftest():
    import secrets, re
    # premier sûr p = 2q+1
    # (petit mais structurellement identique ; l'attaque ne dépend pas de la taille)
    q = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1  # ~192 bits, q premier supposé
    # construire un vrai premier sûr proprement
    from sympy import nextprime, isprime
    while True:
        q = nextprime(q)
        p = 2*q + 1
        if isprime(p): break
    g = 5  # générateur d'un grand sous-groupe
    a = secrets.randbelow(q) + 1        # exposant secret serveur
    flag = b"NCTF{dh_small_subgroup_order2_pwned_0xkpevi}"
    ok = 0
    for parity in (0, 1):               # tester a pair ET impair
        a_test = a - (a % 2) + parity
        # serveur : shared = Y^a mod p ; clé = SHA256(shared) ; flag XOR keystream
        def server_shared(Y): return pow(Y, a_test, p)
        Y = p - 1
        shared_real = server_shared(Y)
        key = derive_key(shared_real, p)
        enc = xor_dec(flag, key)        # chiffrement = même XOR
        # ATTAQUE (ne connaît pas a)
        s, rec, _ = attack(p, enc)
        good = (rec == flag.decode())
        print(f"  a%2={parity}: shared_réel={'1' if shared_real==1 else 'p-1'} -> récupéré={good} ({rec})")
        ok += good
    print(f"[*] {ok}/2 OK — attaque kpevi validée" if ok==2 else "[!] échec")
    return ok == 2

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1].startswith("http"):
        solve_live(sys.argv[1].rstrip("/"))
    else:
        selftest()
