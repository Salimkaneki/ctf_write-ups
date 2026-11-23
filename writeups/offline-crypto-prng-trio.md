# Trio offline crypto/reverse — crc-forge, twister-tell, commit-bias

Trois challenges offline (données fournies) résolus par solveurs locaux. Thème commun :
**une structure prévisible/linéaire casse le secret**.

## crc-forge (reverse/crypto)
`chall` contient 28 cibles CRC32 (une par octet du flag), à l'offset `0x2060`.
Chaque octet est protégé par un CRC32 **par octet** avec `init = ~i`, `xorout = 0xffffffff`.
→ pour chaque position `i`, on **brute les 256 valeurs** d'octet et on garde celle dont le CRC
égale la cible. CRC32 fuit chaque octet indépendamment.
`python3 -I crc-forge/solve_crc_forge.py crc-forge/chall`
**Flag :** `NCTF{crc32_le4ks_ev3ry_byt3}`

## twister-tell (crypto — MT19937)
`outputs.txt` = 624 sorties consécutives de MT19937. On **untemper** les 624 valeurs pour
reconstruire l'état interne, on **clone** le générateur, on prédit le keystream, et on
**XOR** `flag.enc`. 624 sorties = état complet → futur déterministe.
`python3 -I twister-tell/solve_twister.py twister-tell/outputs.txt twister-tell/flag.enc`
**Flag :** `NCTF{mt19937_untempered_then_the_future_is_yours}`

## commit-bias (crypto — LFSR sur F_p)
`ledger.coinvault` : schéma commit-reveal dont les tirages `Y` sont liés **linéairement**
(récurrence sur F_p). On applique **Berlekamp–Massey** sur la suite des `Y` (mod p) pour
retrouver la récurrence (ordre 7), on **prédit** le tirage de la vault à l'index scellé, et on
descelle le flag.
`python3 -I commit-bias/solve_commit_bias.py commit-bias/ledger.coinvault`
**Flag :** `NCTF{c0mmit_r3v34l_but_th3_dr4ws_w3re_l1n34rly_l1nk3d}`
