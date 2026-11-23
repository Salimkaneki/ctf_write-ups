# cdn-oidc (cloud, 500) — RÉSOLU

Identique à billing-oidc : `/token` → id_token HS256 `{"groups":["users"]}`.
Forge **alg:none** avec `{"sub":"guest","groups":["platform-admin"]}`, signature vide →
`/admin/flag` + `Authorization: Bearer` → flag.

Voir `billing-oidc.md` pour le détail. Toute la famille `*-oidc` = même attaque alg:none.

## Flag
`NCTF{619cbcd3782125c2d5bf0025}`
