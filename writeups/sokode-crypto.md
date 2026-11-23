# boazak--sokode-crypto (crypto, 500)

## Challenge
**Auteur :** BoazAK  **Catégorie :** crypto (medium)  **Offline** (fichiers fournis)
**Fichiers :** `challenge.txt` (params RSA + 16 télégrammes), `oracle.py` (module AES-128)
> SCADA ICS. Module de chiffrement des télégrammes + journal de comms « en mode dégradé »
> exfiltrés. **Retrouvez la clé** utilisée pour chiffrer les télégrammes.

## Analyse
`oracle.py` = AES-128/ECB **réimplémenté à la main** (S-box standard, key schedule standard).
Le « mode dégradé » (`parity_bit=1`) injecte **une faute d'un octet** dans l'état
**après ShiftRows du round 9, juste avant MixColumns** :
```python
state[_FAULT_ROW][_FAULT_COL] ^= _FAULT_VAL   # perturbation round 9
```
→ configuration exacte de la **DFA de Piret–Quisquater**.

`challenge.txt` fournit, pour 16 télégrammes : `PT`, `CT` (correct), `CT_FAULT` (fauté, même
PT/clé), et `FAULT_COL` (0-3, 4 télégrammes par colonne). Le bloc `RSA_N/E/C`
(« SESSION_KEY_WRAP ») est un **leurre** : N est divisible par 3 mais N/3 n'est pas premier,
pas de factorisation exploitable.

## Attaque (DFA)
Une faute 1 octet dans la colonne F avant MixColumns R9 se propage :
- MixColumns R9 → diffuse sur les 4 octets de la colonne F ;
- ShiftRows R10 → éclate ces 4 octets sur 4 colonnes de sortie.

Positions de sortie affectées (index = 4·c+r) pour la faute colonne F :
`[4F+0, 4((F-1)%4)+1, 4((F-2)%4)+2, 4((F-3)%4)+3]` — **vérifié** par `CT ⊕ CT_FAULT`
(col 0 → octets {0,7,10,13}, etc.).

Pour chaque colonne, on devine les 4 octets de **K10** (clé de dernier tour) : pour chaque
ligne d'injection `rr` et valeur de faute `e∈1..255`, la différence après MixColumns vaut
`e · M[:,rr]`, et doit vérifier
`SBOX⁻¹(CT[p]⊕k) ⊕ SBOX⁻¹(CT_FAULT[p]⊕k) = ΔMC[r]`.
L'intersection des candidats sur les 4 télégrammes d'une colonne donne les 4 octets uniques.
On reconstitue **K10** (16 octets), puis on **inverse le key schedule** AES pour la clé maître.

## Résultat (vérifié : AES(PT,clé)==CT pour les 16)
- K10 = `768ee1d4e9c443781da78876f5a122bc`
- **Clé maître = `f1a9537c67a9315917205968e9493ad0`**

Solveur : `python3 -I solve_sokode.py challenges/sokode-crypto/challenge.txt`.

## Flag
`NCTF{f1a9537c67a9315917205968e9493ad0}` (la clé AES-128 recouvrée)
