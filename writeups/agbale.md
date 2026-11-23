# boazak--agbale (crypto, 50) — RÉSOLU

## Challenge
`MD5(SECRET || message)`. Endpoints : `GET /sign` (donne `{"msg":"user=guest","sig":...}`),
`GET /admin?msg=<HEX>&sig=<hex>`. Secret inconnu.

## Résolution — length extension MD5
- `/sign` : `msg=user=guest`, `sig=875be63c02219558612e282db6b3344b = MD5(SECRET‖"user=guest")`.
- `/admin` veut le **msg en hexadécimal** (le glue-padding a des octets non-UTF8 → sinon HTTP 400 ;
  même piège que `yeye`). Vérifie `MD5(SECRET‖msg)==sig`, puis parse le querystring **dernière
  valeur gagne**.
- Length extension (impl pure-Python MD5, état initial = sig) : brute la longueur du secret,
  append `&user=admin`. **secret_len = 16**. Le msg forgé = `user=guest` + padding(SECRET‖msg) +
  `&user=admin`, avec une sig valide recalculée sans le secret.
- `/admin?msg=<hex(msg forgé)>&sig=<sig forgée>` → parser lit `user=admin` → flag.
- Réponses utiles : HTTP401 `bad sig` (sig invalide) vs HTTP403 `user=guest` (sig VALIDE mais pas admin)
  → confirme la bonne longueur de secret avant de changer l'append.

Script : `solve_agbale.py` (fonctions `md5_compress`/`length_extension`).

## Flag
`NCTF{ca163ab8817d9f7ee27990c1}`
