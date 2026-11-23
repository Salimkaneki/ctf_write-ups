# boazak--mono (web / SSRF proxy, id 484)

**Flag (finale) :** `NCTF{5439f1780e0f2cef76b261d5}`

## Contexte
« Site accessible via un proxy maison qui relaie vers un backend interne. Le flag est sur
le backend, route `/admin-flag`, normalement inaccessible de l'extérieur. »

## Résolution (instance finale)
Sur l'instance fournie, `GET /admin-flag` renvoie **directement** le flag ; la racine
affiche « Backend home » → le backend interne est joignable sans contourner le proxy.
```bash
curl -s $INSTANCE/admin-flag    # -> NCTF{...}
```

## Si le backend n'est PAS exposé (vrai scénario SSRF)
Le proxy relaie selon un paramètre d'hôte/URL ou le Host. Chercher :
- un param `?url=` / `?host=` / `?target=` sur la racine ou `/proxy`,
- un en-tête `Host:` ou `X-Forwarded-Host` qui sélectionne le backend,
- forcer le proxy à requêter `http://backend-interne/admin-flag`.
(Non nécessaire ici — accès direct.)
