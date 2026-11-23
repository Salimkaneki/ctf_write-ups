# boazak--be (web / .git exposé + zip crack, id 457)

**Flag (finale) :** `NCTF{8ebb2e7dda5bc95d3011b2c3}`  —  **mdp zip : `chloedev`**

## Contexte
« dépôt git abandonné » : `/.git/` est exposé en prod.

## Exploitation
1. `.git/HEAD` + `.git/logs/HEAD` → 4 commits :
   Initial → *Added encrypted backup file* → *added debug logs* → *cleaned up debug files*.
2. Dump récursif des objets git (commit→tree→blob) depuis `/.git/objects/xx/yyyy` :
   - `debug.log` = « Debug mode enabled » (leurre, pas de mdp)
   - `backup.zip` (blob) = ZIP **chiffré ZipCrypto**, STORED, contient `flag.txt` (31 o).
3. Crack du mot de passe : brute ZipCrypto sur rockyou (vérif octet de contrôle + CRC)
   → **`chloedev`** → `unzip -P chloedev backup.zip` → flag.

## Outils
- Parser d'objets git maison (zlib.decompress, format `type\0body`).
- Déchiffreur ZipCrypto Python (ou `fcrackzip -D -p rockyou`, ou `zip2john`+john).
  `zip2john`/`fcrackzip` absents de la box → brute Python (≈9M essais avant hit).

## Note
Le flag est dans l'**historique** git même après « cleanup » — toujours dumper tous les commits.
