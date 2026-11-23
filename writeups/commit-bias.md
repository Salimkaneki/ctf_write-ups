# commit-bias (crypto, 50) — récurrence linéaire mod p (Berlekamp-Massey)

## Challenge
**Catégorie :** crypto  **Auteurs :** hibris, Clawd  **Fichiers :** `ledger.coinvault`, `SPEC.md`
**Offline.**
> Jeu « provably fair » CoinVault. Chaque round, le croupier *scelle* sa draw
> `C = SHA256(Y‖r)[:16]` puis l'*ouvre* (révèle `Y ∈ F_p`). 48 rounds ouverts + 1 round
> **vault** scellé mais jamais ouvert, dont la draw `Y_vault` dérive la clé XOR du flag.
> Retrouver `Y_vault`, desceller le blob, lire le flag.

## Faille — les draws ne sont pas aléatoires
Le croupier prétend un tirage équitable, mais les draws `Y_0..Y_47` suivent une
**récurrence linéaire mod p** (ici d'**ordre 7**). Avec 48 échantillons, on reconstruit la
récurrence et on **prédit `Y_48`** (la vault draw), ce qui casse l'équité.

## Résolution
1. Parser `p`, les 48 `Y_r`, et la ligne `VAULT|IDX=48|C=…|CT=…`. (`FE = ceil(bits(p)/8) = 32`.)
2. **Berlekamp-Massey sur F_p** appliqué à la suite `Y` → récurrence minimale d'ordre **L=7**
   (vérifiée sur les 48 termes). (Marche aussi sur les différences `ΔY` pour tuer une constante.)
3. Prédire `Y_48 = −Σ_{j=1..7} C[j]·Y_{48−j} mod p`.
4. **Vérifier** : `SHA256(Y_48.to_bytes(32)‖(48).to_bytes(4))[:16] == C_vault`. ✓
5. Desceller : `key = SHA256(Y_48.to_bytes(32))` ; keystream `= SHA256(key‖00000000)‖SHA256(key‖00000001)‖…` ;
   `flag = CT XOR keystream`.

Solveur : `solve_commit_bias.py` (BM maison sur GF(p)).

## Piège
Le commitment SHA-256 est solide (rien à casser côté hash). La faiblesse est **la génération
des draws** : un PRNG linéaire rend toute la suite — y compris le tirage « secret » du vault —
entièrement prédictible. Exactement ce que dit le flag.

## Flag
`NCTF{c0mmit_r3v34l_but_th3_dr4ws_w3re_l1n34rly_l1nk3d}`
