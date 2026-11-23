# pyc-ghost (reverse/python, 50)

## Challenge
**Catégorie :** reverse / python  **Auteurs :** hibris, Clawd  **Fichier :** `vault.pyc` (bytecode Python 3.11).
**Offline, pas d'exécution** (désassemblage statique).
> Module Python compilé qui demande le flag et répond « correct »/« nope ». Le texte du flag
> n'est pas dans le fichier. Retrouver le flag accepté.

## Reverse
`vault.pyc` est du bytecode **Python 3.11** (magic 3495). Hôte en 3.12 → désassemblage avec
**xdis** (`pip install xdis` dans un venv ; `pydisasm vault.pyc`). Le docstring + les constantes
donnent tout :

- `DATA[i] = flag[i] XOR keystream[i]` (DATA = 32 octets embarqués).
- keystream = **LCG** : `SEED=4919`, `MUL=1103515245`, `ADD=12345`, `MASK=0x7fffffff`.
- Générateur `_ks` : `x=SEED; for _ in range(n): x=(x*MUL+ADD)&MASK; yield (x>>16)&255`
  (mise à jour **avant** le yield, octet = bits 16..23).

## Résolution
Reconstruire la keystream et XORer DATA :
```
x=SEED
for i in range(32): x=(x*MUL+ADD)&MASK; ks=(x>>16)&255; flag[i]=DATA[i]^ks
```

## Flag
`NCTF{marsh4l_unp1ckl3d_th3_c0de}`
