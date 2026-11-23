# boazak--yeye (crypto, 50) — hash length extension

## Challenge
**Catégorie :** crypto  **Instance :** HTTP  **Auteur :** KodjoDoDjango
> Le portefeuille « Yeye » signe ses paiements avec un MAC maison `SHA256(secret || data)`.
> Forger un paiement valide pour `user=admin` sans connaître le secret.
> Entrées : `GET /challenge` → `{mac, msg}` ; `GET /pay?msg=<hex>&mac=<hex>`.

## Faille — length extension (MAC = H(secret || msg))
Un MAC construit comme `SHA256(secret||msg)` est vulnérable : l'état interne de SHA-256 après
avoir absorbé `secret||msg` est exactement le `mac` publié. On peut donc **reprendre** le hash
et continuer à hacher des octets supplémentaires, ce qui calcule le MAC de
`secret || msg || padding_glue || suffixe` sans connaître `secret`.

- `msg0 = "amount=1000&user=guest"`, `mac0` fourni.
- Suffixe ajouté : `&user=admin` → au parsing querystring, **le dernier `user=` l'emporte** → admin.
- On ne connaît pas `len(secret)` → on **brute-force** la longueur 0..64 ; une seule valide.

### Détail transport (le vrai piège)
`/pay` attend `msg` en **hexadécimal**, pas en texte. C'est obligatoire : le *glue padding*
de SHA-256 contient `0x80`, des `0x00` et la longueur sur 8 octets — des octets non-UTF-8 qui
ne survivent pas dans un paramètre texte. En hex, le serveur reconstitue les octets exacts.
(La paire d'origine en `?msg=<texte urlencodé>` renvoie « bad » ; en hex → `{"paid":true}`.)

Ici le secret faisait **28 octets**. Solveur : `python3 -I solve_yeye.py <URL>` (SHA-256 pur +
reprise d'état, soumission `/pay?msg=<forgé.hex()>&mac=<mac étendu>`).

## Leçon
Ne jamais authentifier avec `H(secret||message)` : utiliser **HMAC**.

## Flag
`NCTF{ae0f02cfa7e7024142f1f257}`
