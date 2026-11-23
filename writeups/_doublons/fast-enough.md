# fast-enough (crypto, id 509) — filter-generator LFSR, immunité algébrique

## Challenge
**Catégorie :** crypto  **Résolu par :** ctf-finale-bc (solveur validé offline)

## Résolution (résumé)
Générateur par **filtrage** : un LFSR de 80 bits, filtré par une fonction booléenne `F`.
`F` a une **immunité algébrique = 2** → il existe des **annihilateurs de degré 2**
(ex. `F=1 ⇒ x4·(x1⊕x3)=0`). On linéarise sur les **monômes quadratiques** de l'état,
le système GF(2) se réduit à un **noyau de dimension 1** → on retrouve l'**état exact** du LFSR,
puis on prédit les 64 bits demandés.

Perf : ~1 s/round, 25 rounds en ~32 s (`solve_fast_enough.py`).

## Flag
`NCTF{aa2eba38db8805c1ba58305c}`
