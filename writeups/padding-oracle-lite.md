# padding-oracle-lite (crypto, 346) — RÉSOLU

## Challenge
Service binaire maison **POP1** sur TLS (`ncat --ssl host 1337`), pas HTTP (padbuster/Burp inutiles).
Framing : `0xAA | opcode(1) | length(2 LE, en MOTS de 2 octets) | payload | checksum(1)=XOR(opcode,payload)`.
Opcodes : GETCT(0x10)→CT(0x12) `IV(16)‖CT`, VERIFY(0x20)`IV‖CT`→STATUS(0x21) 1 mot big-endian
(2 valeurs distinctes, sens caché), SUBMIT(0x30)→FLAG(0x31)/NOPE(0x32). AES-128-CBC, clé per-instance.

## Résolution — Vaudenay CBC padding oracle
- Pièges framing : `length` compte les **mots** (64 o → `20 00`), checksum couvre opcode+payload seulement.
- CT = 64 o = IV + **3 blocs** (plaintext 48 = 32 ascii + bloc de padding `0x10`×16).
- Calibration oracle : VERIFY(vrai CT) → **STATUS=1 = padding OK** ; byte flip dans l'avant-dernier
  bloc → **STATUS=0 = padding KO**.
- Vaudenay standard par bloc : blob testé = `C'(16)‖Cj(16)` (C' = IV du bloc), récupère `D(Cj)` octet
  par octet, puis `Pj = D(Cj) XOR C_{j-1}` (vrai bloc précédent). Garde anti-faux-positif à pad=1.
- **Parallélisé sur 12 connexions TLS** (256 essais/position répartis) → ~1-2 min.
- Token rec' = `SESSION_48a68348087828796cb1c2c3` (32 o), strip PKCS#7 (3ᵉ bloc = padding plein) → SUBMIT.

Script : `solve_padding_oracle_lite.py` (mettre HOST/PORT de l'instance).

## Flag
`NCTF{af5a8ead6fe7485f4ff5b86c}`
