#!/usr/bin/env python3
"""fast-enough (509) — attaque algebrique (Courtois-Meier) sur un filter generator.
Cipher = LFSR Fibonacci L=80 + filtre f(5 taps) non lineaire (deg 4) mais qui admet
des annihilateurs de degre 2 pour f et f+1. Chaque bit de sortie -> 1 equation deg 2
sur les 80 bits d'etat initial -> linearisation (80 + C(80,2) = 3240 inconnues) ->
Gauss GF(2). On recupere l'etat puis on predit les 64 bits suivants.

Phase 1 (pre-calcul, hors deadline) : formes lineaires L_t[j] + lignes g/h par t.
Phase 2 (par round, <deadline) : choisir g/h selon le bit, Gauss, lire l'etat, predire.
"""
import sys, time, itertools, hashlib, struct
import numpy as np

# ---- config publique (c4_config.py) ----
L = 80
POLY_INT = 1377573749490194700300181
TAPS = [0, 14, 32, 53, 76]
COEF = [2, 3, 4, 5, 8]
CST = 19
BYTE = 0
NBITS = 4860
PREDICT = 64

def fb_taps():
    return [i for i in range(L) if (POLY_INT >> i) & 1]
FB = fb_taps()

# ---- filtre f (c4_proto.py) ----
def filter_bit(taps):
    val = CST + sum(c*int(b) for c, b in zip(COEF, taps))
    return hashlib.sha256(str(val).encode()).digest()[BYTE] & 1

def keystream(state, n):
    s = list(state); out = []
    for _ in range(n):
        out.append(filter_bit([s[p] for p in TAPS]))
        fbit = 0
        for j in FB: fbit ^= s[j]
        s = s[1:] + [fbit]
    return out

# ---- truth table + ANF + annihilateurs deg<=2 de f et f+1 ----
PTS = list(itertools.product([0,1], repeat=5))
TT = [filter_bit(list(b)) for b in PTS]
# monomes deg<=2 sur 5 vars
MONO5 = [()] + [(i,) for i in range(5)] + [tuple(c) for c in itertools.combinations(range(5),2)]
def mono_eval(m, b):
    r = 1
    for i in m: r &= b[i]
    return r
def annihilator(target):
    # g tel que g(x)=0 pour tout x avec TT[x]==target ; renvoie coeffs ANF sur MONO5
    rows = [[mono_eval(m, PTS[i]) for m in MONO5] for i in range(32) if TT[i]==target]
    A = [r[:] for r in rows]  # GF(2) kernel de A^T ... on veut coeffs c : A c = 0
    nvar = len(MONO5)
    # resoudre A c = 0, prendre un vecteur non trivial du noyau
    mat = [row[:] for row in A]; nr = len(mat)
    where = [-1]*nvar; r = 0
    for col in range(nvar):
        piv = next((rr for rr in range(r, nr) if mat[rr][col]), None)
        if piv is None: continue
        mat[r], mat[piv] = mat[piv], mat[r]
        for rr in range(nr):
            if rr != r and mat[rr][col]:
                mat[rr] = [a ^ b for a, b in zip(mat[rr], mat[r])]
        where[col] = r; r += 1
    free = [c for c in range(nvar) if where[c] == -1]
    if not free: return None
    c = [0]*nvar; fcol = free[0]; c[fcol] = 1
    for col in range(nvar):
        if where[col] != -1:
            c[col] = mat[where[col]][fcol]
    return c  # coeffs sur MONO5

G = annihilator(1)   # annule f  (utilise quand bit==1)
H = annihilator(0)   # annule f+1 (utilise quand bit==0)

# ---- formes lineaires : L_t[j] = s_t[TAPS[j]] comme vecteur 80 bits sur s_0 ----
def build_linear_forms(T):
    # state_forms[i] = np.uint8 vecteur (80,) : s_t[i] en fonction de s_0
    forms = np.eye(L, dtype=np.uint8)
    tapforms = np.zeros((T, 5, L), dtype=np.uint8)
    for t in range(T):
        for j in range(5):
            tapforms[t, j] = forms[TAPS[j]]
        # avance : new[i]=forms[i+1] (i<79) ; new[79]=XOR forms[FB]
        nf = np.empty_like(forms)
        nf[:L-1] = forms[1:]
        fb = np.zeros(L, dtype=np.uint8)
        for j in FB: fb ^= forms[j]
        nf[L-1] = fb
        forms = nf
    return tapforms

# ---- lignes d'equations linearisees ----
IU = np.triu_indices(L, 1)           # ordre pairs (a<b) row-major
NQUAD = IU[0].size                   # C(80,2)=3160
NVARS = L + NQUAD                    # 3240
WORDS = (NVARS + 1 + 63)//64         # +1 pour RHS

def ann_row(coeffs, tapf_t):
    """Construit (lin(80), quad(3160), rhs) pour annihilateur 'coeffs' aux formes tapf_t[j]."""
    lin = np.zeros(L, dtype=np.uint8)
    quad = np.zeros(NQUAD, dtype=np.uint8)
    rhs = 0
    for m, cf in zip(MONO5, coeffs):
        if not cf: continue
        if len(m) == 0:
            rhs ^= 1
        elif len(m) == 1:
            lin ^= tapf_t[m[0]]
        else:
            a = tapf_t[m[0]]; b = tapf_t[m[1]]
            lin ^= (a & b)                     # diagonale -> termes lineaires
            Q = np.outer(a, b) & 1
            qt = Q ^ Q.T
            quad ^= qt[IU]
    return lin, quad, rhs

def pack_row(lin, quad, rhs):
    bits = np.concatenate([lin, quad, [rhs & 1]]).astype(np.uint8)
    out = np.zeros(WORDS, dtype=np.uint64)
    # pack little : bit k -> word k//64, position k%64
    for k in np.nonzero(bits)[0]:
        out[k >> 6] |= np.uint64(1) << np.uint64(int(k) & 63)
    return out

def precompute():
    t0 = time.time()
    tapf = build_linear_forms(NBITS + PREDICT)
    GROW = np.zeros((NBITS, WORDS), dtype=np.uint64)
    HROW = np.zeros((NBITS, WORDS), dtype=np.uint64)
    for t in range(NBITS):
        lg = ann_row(G, tapf[t]); GROW[t] = pack_row(*lg)
        lh = ann_row(H, tapf[t]); HROW[t] = pack_row(*lh)
    return GROW, HROW, tapf, time.time()-t0

# ---- Gauss GF(2) sur matrice packee (lignes = uint64[WORDS]) ----
RHS_COL = NVARS  # colonne 3240 = RHS
_ONE = np.uint64(1)

def _getbit(row, col):
    return int((row[col >> 6] >> np.uint64(col & 63)) & _ONE)

def gf2_rref(M):
    """RREF (Gauss-Jordan) sur colonnes 0..NVARS-1. Renvoie (M, pivrow_of_col, rang)."""
    R = M.shape[0]; r = 0; piv = {}
    for col in range(NVARS):
        w = col >> 6; bit = np.uint64(col & 63)
        colbits = (M[:, w] >> bit) & _ONE
        cand = np.nonzero(colbits[r:])[0]
        if cand.size == 0:
            continue
        p = r + int(cand[0])
        if p != r:
            M[[r, p]] = M[[p, r]]
        colbits = (M[:, w] >> bit) & _ONE; colbits[r] = 0
        M ^= colbits.astype(np.uint64)[:, None] * M[r][None, :]
        piv[col] = r; r += 1
        if r == R: break
    return M, piv, r

def _gf2_basis(vecs):
    """Base GF(2) d'une liste de vecteurs (80,) uint8 ; renvoie liste reduite."""
    basis = []
    for v in vecs:
        x = v.copy()
        for b in basis:
            lb = int(np.nonzero(b)[0][0])
            if x[lb]: x ^= b
        if x.any(): basis.append(x)
    return basis

def solve_candidates(M, max_dim=18):
    """Renvoie la liste des etats lineaires candidats (80 bits) compatibles."""
    M, piv, rank = gf2_rref(M)
    sol = np.zeros(NVARS, dtype=np.uint8)
    for col, pr in piv.items():
        sol[col] = _getbit(M[pr], RHS_COL)
    freecols = [c for c in range(NVARS) if c not in piv]
    # vecteurs du noyau, partie lineaire (0..79) seulement
    nulls = []
    for fc in freecols:
        nv = np.zeros(L, dtype=np.uint8)
        if fc < L: nv[fc] ^= 1
        for col, pr in piv.items():
            if col < L and _getbit(M[pr], fc): nv[col] ^= 1
        if nv.any(): nulls.append(nv)
    basis = _gf2_basis(nulls)
    d = len(basis)
    base = sol[:L].copy()
    if d > max_dim:
        return [[int(x) for x in base]]   # trop d'ambiguite -> 1 seul essai
    cands = []
    for mask in range(1 << d):
        c = base.copy()
        for i in range(d):
            if (mask >> i) & 1: c ^= basis[i]
        cands.append([int(x) for x in c])
    return cands

def _verify(state, given, ncheck=200):
    ks = keystream(state, ncheck)
    return ks == list(given[:ncheck])

def recover_state(given_bits, GROW, HROW):
    gb = np.array(given_bits, dtype=np.uint8)
    sel = gb[:NBITS].astype(bool)
    M = np.where(sel[:, None], GROW, HROW).copy()
    for cand in solve_candidates(M):
        if _verify(cand, gb):
            return cand
    return None

def predict(state):
    full = keystream(state, NBITS + PREDICT)
    return full[NBITS:]

# ---------------- auto-test hors-ligne ----------------
def selftest():
    print("[*] annihilateurs: G deg", max((len(m) for m,c in zip(MONO5,G) if c), default=0),
          "| H deg", max((len(m) for m,c in zip(MONO5,H) if c), default=0))
    import random
    print("[*] pre-calcul...")
    GROW, HROW, tapf, dt = precompute()
    print(f"[*] pre-calcul OK en {dt:.1f}s  (WORDS={WORDS}, NVARS={NVARS})")
    ok = 0
    for trial in range(3):
        st = [random.randrange(2) for _ in range(L)]
        full = keystream(st, NBITS + PREDICT)
        given = full[:NBITS]; nxt = full[NBITS:]
        t0 = time.time()
        rec = recover_state(given, GROW, HROW)
        dts = time.time()-t0
        if rec is None:
            print(f"  essai {trial}: ETAT LIBRE (rang insuffisant)"); continue
        match_state = (rec == st)
        pred = predict(rec)
        match_pred = (pred == nxt)
        print(f"  essai {trial}: etat_exact={match_state} pred64_exact={match_pred} solve={dts:.2f}s")
        if match_pred: ok += 1
    print(f"[*] {ok}/3 predictions correctes")
    return ok == 3

# ---------------- client reseau TLS ----------------
def solve_network(host, port):
    import socket, ssl, re
    print(f"[*] pre-calcul (hors horloge serveur)...")
    GROW, HROW, tapf, dt = precompute()
    print(f"[*] pre-calcul OK en {dt:.1f}s — connexion {host}:{port}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    raw = socket.create_connection((host, port), timeout=30)
    s = ctx.wrap_socket(raw, server_hostname=host)
    f = s.makefile("rwb", buffering=0)
    def readline():
        return f.readline().decode(errors="replace")
    t0 = time.time()
    rounds_done = 0
    while True:
        line = readline()
        if not line:
            print("[!] connexion fermee"); break
        line = line.rstrip("\n")
        if "FLAG" in line:
            print("\n[+] " + line)
            mm = re.search(r'NCTF\{[^}]+\}', line)
            if mm: print("\n[+][+][+] FLAG:", mm.group())
            break
        if line.startswith("[round"):
            mk = re.search(r'\]\s*([01]+)', line)
            if not mk:
                print("[!] round sans bits:", line[:80]); continue
            given = [int(ch) for ch in mk.group(1)]
            if len(given) < NBITS:
                print(f"[!] seulement {len(given)} bits recus"); continue
            tr = time.time()
            st = recover_state(given, GROW, HROW)
            if st is None:
                print("[!] etat non recupere a ce round");
                f.write(b"0"*PREDICT + b"\n"); continue
            nxt = predict(st)
            f.write(("".join(map(str, nxt)) + "\n").encode())
            rounds_done += 1
            print(f"  round {rounds_done}/25 envoye (recup {time.time()-tr:.2f}s, total {time.time()-t0:.1f}s)")
        else:
            print("  [srv]", line[:120])
            if line.strip() == "wrong" or line.strip() == "timeout":
                print("[!] rejet serveur:", line); break
    s.close()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        solve_network(sys.argv[1], int(sys.argv[2]))
    else:
        selftest()
