# pyc-ghost (reverse) — bytecode Python + keystream LCG

## Challenge
**Catégorie :** reverse  **Fichier :** `vault.pyc` (bytecode Python 3.11, magic `a70d0d0a`)
**Flag :** `NCTF{marsh4l_unp1ckl3d_th3_c0de}`

## Résolution — désassembler SANS exécuter
Fichier non fiable → on ne l'exécute pas. On charge le code object via `marshal` (header de
16 octets en py3.7+) et on le désassemble avec `dis` :

```python
import dis, marshal
code = marshal.loads(open('vault.pyc','rb').read()[16:])
dis.dis(code)
```

Le docstring crache tout le principe :
> « The flag is never stored in plaintext. DATA holds `flag[i] ^ keystream[i]`, where the
> keystream comes from a linear congruential generator seeded with SEED. »

Constantes + fonctions (désassemblées) :
```python
SEED, MUL, ADD, MASK = 4919, 1103515245, 12345, 2147483647   # 0x7fffffff
DATA = (35,2,93,126,214,144,42,42,66,158,25,83,5,44,8,182,
        154,253,26,56,4,224,139,52,163,227,114,138,235,161,100,234)

def _ks(n):                       # générateur de keystream (LCG type glibc rand)
    x = SEED
    for _ in range(n):
        x = (x*MUL + ADD) & MASK
        yield (x >> 16) & 255     # octet = bits 16..23 de l'état

def unlock():
    return bytes(d ^ k for d, k in zip(DATA, _ks(len(DATA))))
```

## Reconstruction du flag
On rejoue le LCG et on XOR avec `DATA` (aucune entrée utilisateur nécessaire) :
```python
def ks(n):
    x = 4919
    for _ in range(n):
        x = (x*1103515245 + 12345) & 2147483647
        yield (x >> 16) & 255
print(bytes(d ^ k for d, k in zip(DATA, ks(len(DATA)))))
# b'NCTF{marsh4l_unp1ckl3d_th3_c0de}'
```

## Leçon (pour le jury)
> Compiler en `.pyc` **ne cache rien** : `marshal` + `dis` révèlent tout le bytecode. Et un
> **LCG n'est pas un chiffrement** — graine et paramètres étant dans le binaire, le keystream
> se rejoue trivialement. XOR + PRNG faible = réversible.
