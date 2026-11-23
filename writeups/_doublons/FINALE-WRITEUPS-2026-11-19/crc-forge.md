# crc-forge (reverse/crc32, 50)

## Challenge
**Catégorie :** reverse / crc32  **Auteurs :** hibris, Clawd  **Fichier :** `chall` (ELF x86-64 strippé, PIE).
**Offline, aucune exécution** (analyse 100% statique).
> Le binaire lit un flag et répond « checksums match » / « mismatch ». Les caractères du flag
> **ne sont pas dans le fichier** — seulement leurs checksums. Retrouver le flag accepté.

## Reverse (désassemblage `objdump -d`)
- Lit argv[1] (ou stdin), `strlen` doit valoir **0x1c = 28** → flag de 28 caractères.
- Boucle `i = 0..27`, table de 28 cibles uint32 à `.rodata:0x2060`.
- Checksum par caractère = **CRC32 réfléchi** (poly `0xEDB88320`) avec :
  - **init = ~i** (NOT de l'index — d'où « pas dans le fichier » : chaque octet a sa propre init),
  - traitement bit-à-bit de l'octet `flag[i]`,
  - **xorout = 0xFFFFFFFF** (`not eax`),
  - comparé à `target[i] = *(u32*)(0x2060 + 4*i)`.

Pseudo-code par caractère :
```
reg = ~i & 0xffffffff
for 8: reg = (reg>>1) ^ (POLY if reg&1 else 0)      # rounds sur l'init
r = (flag[i] ^ reg) & 0xffffffff
for 8: r = (r>>1) ^ (POLY if r&1 else 0)            # rounds sur l'octet
checksum = ~r & 0xffffffff
```

## Faille
Un CRC32 par **octet** est trivialement inversible : 256 essais par position (bijection pour un
octet). Chaque `flag[i]` est récupéré indépendamment → brute-force 28×256.
Solveur : `challenges/crc-forge/solve_crc_forge.py`.

## Flag
`NCTF{crc32_le4ks_ev3ry_byt3}`
