# boazak--amlame (web, 300, 0 solve) — PROGRÈS (vuln confirmée, sink à préciser)

## Challenge
Node app derrière nginx. Index: « POST /api/profile (JSON) pour vos préférences,
GET /api/report pour l'export. » Énoncé: « préférences d'affichage JSON puis exporter un
rapport. Un rapport bien configuré commence par un bon profil. » Instance 679.

## Établi
- `POST /api/profile` = merge JSON **récursif** dans un profil global (echo le profil fusionné,
  accumulé entre requêtes, pas de cookie). `GET /api/report` → toujours `<pre>rapport-standard</pre>`.
- **PROTOTYPE POLLUTION CONFIRMÉE** (app Node/JS) : `{"__proto__":{"k":"v"}}` pollue
  **Object.prototype globalement** — preuve : un sous-objet frais (`nest`) hérite des clés polluées.
  `__proto__` disparaît de l'echo, `constructor` reste clé propre = signature JS.
- Le rapport ne reflète AUCUNE clé testée (~250 noms EN+FR+hyphénés : template/report/type/format/
  name/kind/gabarit/modele/... en valeur-chaîne marqueur → rien).
- **Valeur OBJET en pollution → CRASH de l'app** (`{"__proto__":{"type":{...},...}}` → instance
  « introuvable »). Probablement casse un interne framework (clé type/... lue par Express), ou
  un sink `path.join(dir, cfg.KEY)` qui throw sur objet mais retombe en silence sur chaîne invalide.
- LFI tenté (traversées `../../etc/passwd`, `/flag`, `package.json`, `server.js`, avec/sans ext)
  via pollution de 25 clés → aucune fuite. Soit mauvaise clé, soit extension ajoutée, soit sink ≠ readFile.
- Pas d'autre endpoint (/api/profile, /api/report seulement).

## Hypothèse de travail
Le rapport lit une clé précise du profil/config (héritée via proto) et fait un `readFile`/`path.join`
→ **LFI vers le flag** (ou sélection de template → SSTI). Reste à trouver : le **nom exact de la clé**
et le **format du chemin** (base dir + extension éventuelle). Gadget EJS/child_process RCE testé (webhook) → 0 callback.

## Blocages pratiques
- **Instances très instables** (compte partagé Mr Mevtr : tuées en minutes ; mes valeurs-objet les crashent).
  Garder les tests en **valeurs chaîne uniquement**. URL change à chaque respawn.
- Respawn : fetch `/plugins/team_instancer/spawn` {challenge_id:679}.

## Flag
(non obtenu — vuln prototype pollution confirmée, sink à finaliser)
