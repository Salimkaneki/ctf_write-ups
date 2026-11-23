# twister-tell (crypto, 50) — MT19937 state recovery (untemper)

## Challenge
**Catégorie :** crypto / prng / mersenne-twister  **Auteurs :** hibris, Clawd
**Fichiers :** `outputs.txt` (624 sorties 32-bit), `flag.enc` (hex). **Offline.**
> Un service a leaké 624 sorties brutes de son PRNG. Juste après, les sorties **suivantes**
> du même générateur ont servi de keystream pour chiffrer le flag. Prédire et déchiffrer.

## Faille — MT19937 est entièrement reconstructible
624 sorties consécutives = **un état interne complet** de Mersenne Twister. Chaque sortie est
l'état « tempéré » ; la fonction de tempering est **inversible** (untemper). On reconstruit les
624 mots d'état, on clone le générateur, et on prédit **toutes** les sorties futures.

## Résolution
1. `untemper(y)` : inverser dans l'ordre inverse du tempering
   (`y^=y>>18` ; `y^=(y<<15)&0xefc60000` ; `y^=(y<<7)&0x9d2c5680` ; `y^=y>>11`),
   chaque étape par **point fixe** (itérer `x=y^f(x)` jusqu'à convergence). Vérifié par
   `temper(untemper(o))==o`.
2. Cloner : `random.Random().setstate((3, tuple(state+[624]), None))`. Index **624** ⇒ le prochain
   appel déclenche un *twist* et produit la **625ᵉ** sortie (= début du keystream).
3. Keystream = sorties 32-bit concaténées en **big-endian** (4 octets/mot) ; `flag = flag.enc XOR keystream`.

Solveur : `challenges/twister-tell/solve_twister.py`.

## Piège
Le tempering *ressemble* à du mélange irréversible, mais c'est une bijection — ne jamais exposer
des sorties brutes de MT19937 : 624 suffisent à prédire tout le futur (et le passé).

## Flag
`NCTF{mt19937_untempered_then_the_future_is_yours}`
