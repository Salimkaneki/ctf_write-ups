# fast-enough (crypto, ~509) — attaque algébrique sur filter generator (Courtois-Meier)

## Challenge
**Catégorie :** crypto  **Instance :** TLS netcat (`ncat --ssl {host} {port}`)
**Fichiers :** `c4_config.py`, `c4_proto.py`, `c4_oracle.py`
**Flag :** `NCTF{aa2eba38db8805c1ba58305c}`

> Oracle réseau. 25 rounds ; à chaque round le serveur donne **4860 bits de keystream**
> d'un chiffrement à flot et il faut **prédire les 64 bits suivants** — le tout en
> **moins de 150 s au total**. L'état initial du LFSR (80 bits) est secret et **tiré au
> hasard à chaque round**.

## Le chiffrement
Un **filter generator** classique :
- **LFSR de Fibonacci**, longueur `L = 80`, rétroaction linéaire donnée par `POLY_INT`.
  L'état avance : `s ← s[1:] + [⊕_{j∈FB} s[j]]`.
- **Sortie** : à chaque pas, 1 bit = `f(s[TAPS])` où `TAPS = [0,14,32,53,76]` (5 bits d'état)
  et `f(b) = SHA256( str(19 + 2·b0 + 3·b1 + 4·b2 + 5·b3 + 8·b4) )[0] & 1`.

`f` est une **fonction booléenne fixe de 5 bits** (table de vérité de 32 entrées), de **degré
algébrique 4**, équilibrée.

## La faille : immunité algébrique faible
Une fonction de 5 variables admet toujours un **annihilateur de degré ≤ 2** (théorie de
Courtois-Meier). On vérifie que `f` **et** `f+1` ont chacun un annihilateur `g` de degré 2 :
`g(x) = 0` partout où `f(x) = 1` (resp. `= 0`).

Conséquence : pour **chaque bit de sortie** `z_t`,
- si `z_t = 1` : `g_f(taps_t) = 0`,
- si `z_t = 0` : `g_{f+1}(taps_t) = 0`.

Comme les 5 bits de taps au temps `t` sont des **formes linéaires** des 80 bits d'état
initial (le LFSR est linéaire), chaque équation `g(taps_t)=0` est une **équation de degré 2**
en les 80 inconnues.

## Résolution — linéarisation + Gauss GF(2)
On traite chaque produit `x_a·x_b` comme une nouvelle variable : `80 + C(80,2) = 3240`
inconnues. Avec 4860 équations (> 3240) → système surdéterminé, résolu par **élimination de
Gauss sur GF(2)** (lignes bit-packées en `uint64`, XOR vectorisé numpy).

- Le rang obtenu est 3239/3240 (nullité 1) → **2 candidats** ; on lève l'ambiguïté en
  **régénérant un préfixe de keystream** et en gardant celui qui colle.
- On récupère l'**état initial exact**, puis on fait tourner le chiffrement en avant pour
  produire les **64 bits** demandés.

Performance : pré-calcul des formes linéaires et des lignes d'équations **une seule fois**
(hors horloge serveur, ~8 s), puis **~1,1 s par round**. Total 25 rounds ≈ **32 s** ≪ 150 s.

## Le détail qui tue (nullité 1)
Les 80 variables linéaires sont toutes pivotées, mais **une variable quadratique reste libre**
→ deux états possibles. On ne devine pas : on **vérifie** chaque candidat en recalculant les
premiers bits du keystream. Sans ça, l'état récupéré est faux 1 fois sur 2.

## Leçon (pour le jury)
> Dans un chiffrement à flot à filtre, une fonction de filtrage **non linéaire ne suffit pas** :
> si elle possède un **annihilateur de petit degré** (immunité algébrique basse), chaque bit
> observé devient une équation de degré 2 et **tout l'état secret se résout par algèbre
> linéaire**. Il faut une fonction à **haute immunité algébrique**.

## Fichier
`solve_fast.py` (auto-test offline 3/3 + client TLS). Flag : `NCTF{aa2eba38db8805c1ba58305c}`
