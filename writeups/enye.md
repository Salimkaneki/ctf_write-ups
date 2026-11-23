# boazak--enye (crypto, 50) — Bleichenbacher (BB'98)

## Challenge
**Catégorie :** crypto  **Instance :** HTTP  **Auteur :** boazak
> « Enye » = « oui, c'est ça » en éwé → l'**oracle oui/non**. Le serveur déchiffre le RSA que
> tu lui envoies et dit si le résultat est un **bloc PKCS#1 v1.5 valide** (`00 02 …`) ou non.
> Entrées : `GET /challenge` (donne `n`, `e`, `c`), `GET /oracle?c=<int>` (`{"valid":bool}`).

## Explication simple (pour le jury)

🔐 **L'image : le cadenas qui fait « bip » quand on approche la bonne forme.**
On a un message chiffré par RSA. On ne connaît **pas la clé privée**. Mais le serveur accepte
qu'on lui donne n'importe quel chiffré et nous répond **une seule info** : « le résultat
commence-t-il bien par `00 02` ? » (oui/non).

🧠 **La faille (Bleichenbacher, 1998).** Ce **unique bit** « oui/non », demandé des milliers de
fois avec des chiffrés multipliés astucieusement, suffit à **resserrer petit à petit**
l'intervalle où se trouve le message, jusqu'à **une seule valeur = le message en clair**.

🗣️ **Phrase pour le jury :**
> « Révéler ne serait-ce qu'un bit d'information sur le padding d'un déchiffrement RSA permet,
> en ~5000 requêtes, de récupérer tout le message sans jamais connaître la clé privée. »

🛡️ **La leçon :** c'est pour ça qu'on n'utilise **jamais** RSA PKCS#1 v1.5 pour du chiffrement
→ utiliser **RSA-OAEP** (ou mieux, de l'échange de clés moderne).

## Attaque (détail)
`n` = 1024 bits (k=128), `e=65537`. Le `c` fourni est déjà PKCS-conforme → `s0=1`, le message
`m` est dans `[2B, 3B)` avec `B = 2^(8·126)`.
1. **Étape 2a** : trouver le plus petit `s` tel que `oracle(c·sᵉ mod n)` = valide.
2. **Étapes 2b/2c** : affiner `s` (recherche linéaire si plusieurs intervalles, ciblée si un seul).
3. **Étape 3** : chaque « oui » **rétrécit l'intervalle** des valeurs possibles de `m`.
4. Quand l'intervalle = **1 valeur** → c'est `m`. Retirer le padding `00 02 PS 00` → le message.

Parallélisation : l'algo est séquentiel entre étapes, mais la **recherche de `s`** dans chaque
étape se teste par **fenêtres concurrentes** (48 threads) pour tenir la latence réseau.
Solveur : `python3 -I solve_enye.py` (→ 994 itérations, 5408 requêtes, convergence propre).

## Flag
`NCTF{34f210d4836dae5e0fa1b9bb}`
