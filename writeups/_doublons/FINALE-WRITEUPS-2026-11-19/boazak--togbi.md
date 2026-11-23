# boazak--togbi (web / JWT RS256→HS256 confusion, id 467)

**Flag (finale) :** `NCTF{7bf81884cfbd023b49935d93}`

## Contexte
API avec rôles `U_SER → A_DMIN → SUPER_A_DMIN`. JWT signés **RS256** (asymétrique).
`GET /dashboard` : « Seuls les SUPER_A_DMIN peuvent voir le flag ». Pas de clé publique exposée.

## Attaque : confusion d'algorithme RS256 → HS256
Le serveur vérifie avec la clé publique. S'il accepte aussi `alg:HS256`, on peut forger
un token signé en **HMAC-SHA256 avec la clé publique comme secret** (on connaît la clé pub).

### 1. Récupérer la clé publique (sign2n) — car non exposée
Avec ≥2 tokens RS256 du même serveur (exp différent → messages différents) :
`n | gcd( sig_i^e − PKCS1v15(SHA256(msg_i)) )`, e=65537.
Calcul lourd (`sig^65537` non modulaire ~16 Mo) → utiliser **gmpy2** (GMP). 3 tokens suffisent.
Reconstruire la clé publique DER/PEM depuis (n, e).

### 2. Forger le token HS256
- header `{"typ":"JWT","alg":"HS256"}`, payload avec `role:"SUPER_A_DMIN"`, `exp` futur.
- secret HMAC = clé publique en **PEM SPKI avec newline final** (c'est l'encodage qui a marché ;
  tester aussi SPKI sans newline, PKCS1 PEM, DER).

```bash
# login x3 -> togbi_tokens.txt, puis :
~/ctf/.venv/bin/python togbi_solve.py   # gmpy2 requis
# -> [200] spki_pem  FLAG! NCTF{...}
```

## Note
Script `togbi_solve.py` (scratchpad) : récup modulus + 7 encodages de secret testés contre /dashboard.
