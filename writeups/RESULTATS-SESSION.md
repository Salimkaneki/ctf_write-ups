# Résultats session (Claude ctf-finale-d5) — NCTF26 finale, 2026-11-19

## ✅ Résolus — 9 flags web (série boazak--), vérifiés en direct
| Challenge | id | Flag | Faille | Write-up |
|-----------|----|------|--------|----------|
| agoe | 452 | `NCTF{e3d0e63f14d63b4489f4f532}` | batch IDOR (ids=[moi,admin]) | boazak--agoe.md |
| tsevie | 469 | `NCTF{6af2911c862115e9327c858c}` | LFI /api/note?file=/proc/self/environ | boazak--tsevie.md |
| akodessewa | 454 | `NCTF{69f599c438329642fbb05b4a}` | mass assignment register | boazak--akodessewa.md |
| kande | 460 | `NCTF{5cccbb9757646180a674d2c3}` | config merge admin=true | boazak--kande.md |
| be | 457 | `NCTF{8ebb2e7dda5bc95d3011b2c3}` | .git exposé + crack zip (chloedev) | boazak--be.md |
| vogan | 470 | `NCTF{3477daa63b62b83dc574cca9}` | YAML RCE + oracle d'erreur | boazak--vogan.md |
| atakpame | 456 | `NCTF{9db3ec32d980bd45848d898b}` | command injection (name) | boazak--atakpame.md |
| togbi | 467 | `NCTF{7bf81884cfbd023b49935d93}` | JWT RS256→HS256 (sign2n + gmpy2) | boazak--togbi.md |
| mono | 484 | `NCTF{5439f1780e0f2cef76b261d5}` | backend /admin-flag direct | boazak--mono.md |

## ⏸ Parkés / bloqués (raison)
- **Série isid0r3** (carnet 491, curfew 492, + bibliotech 490, lockstep/nexero/proformat/linkcard) :
  **mur anti-automatisation** — captcha sur login ET inscription, `SECRET_KEY` Flask fort
  (flask-unsign a épuisé rockyou sur curfew). Nécessite un HUMAIN pour franchir le captcha
  (login+register) puis me passer le cookie authentifié → je ferais l'escalade post-auth
  (carnet = forge JWT via JWKS exposé).
- **koutammakou 462** (web, hard) : Zip Slip en écriture seule, pas de primitive de lecture
  simple du flag (nginx bloque ../, symlinks non suivis) — parké.
- **doublepeel** (stego clavier, local) : zone gauche sûre (`1234/qwe/asd/zxc`), zone droite
  ambiguë (halo). 9 candidats dans `scratchpad/doublepeel_candidats.txt`. Se tranche avec une
  photo plus droite de la moitié droite.

## ⏳ En attente de slot d'instance (quota équipe 6/6)
- **agent-tool-abuse 374** (AI) + CHAINS vaultboard/pipeline — à spawner dès qu'un slot se libère.

## 🚫 À NE PAS faire
- **« Prends le contrôle de ctf.tg »** (défi #1 qualifs, défacement prod) : caduc (équipe déjà
  en finale, défi abandonné → droits clos), et risque sur l'infra de jeu en pleine finale.

## Méthode (rappel)
Spawn via navigateur (team_instancer, csrfNonce) → solve en Bash/curl sur `https://<rand>.t.ctf.tg/`
→ flag rendu, humain soumet. Flags souvent dans la var d'env `FLAG` ou un fichier `/flags/flag.txt`.

## ✅ Session ctf-finale (2ece) — 2026-11-19 après-midi — 2 flags crypto
| Challenge | id | Flag | Faille | Write-up |
|-----------|----|------|--------|----------|
| oxdefault--fast-enough | 509 | `NCTF{aa2eba38db8805c1ba58305c}` | filter-LFSR 80b, attaque algébrique AI=2 (annihilateurs deg2 → linéarisation GF(2)) | fast-enough.md |
| boazak--yeye | 416 | `NCTF{ae0f02cfa7e7024142f1f257}` | hash length extension `SHA256(secret‖msg)`, msg en hex, +`&user=admin` (secret=28o) | yeye.md |

### ⏸ atike (398, crypto 50) — decrypt OK, /check bloqué
Padding oracle Vaudenay OK → target décrypte en `permission:admin@corp.io` (solve_atike.py, 48 workers,
early-stop, fix oracle 429→retry). MAIS `/check` veut un plaintext précis inconnu : admin/superadmin/root
forgés (CBC-R, solve_atike_forge.py) → tous « no » 403. Pas de source fournie, pas d'endpoint spec.
→ en attente du hint 40pts (validé par Salim) ; bloqué par Chrome offline + pas de token.
Instance du moment : h7x75kywhlcrbghi.t.ctf.tg (reste joignable en Bash).

### Notes instancer (compte partagé Mr Mevtr très disputé)
spawn/destroy via fetch CSRF OK ; instances tuées/recyclées par coéquipiers en pleine résolution
→ solver doit finir vite. URLs lisibles seulement à l'écran (filtre JS bloque cookie/query ; ne PAS
contourner par encodage — classifier « undermining oversight »). Lire l'URL via screenshot/zoom de la modale.

### ✅ commit-bias (53, crypto 50) — OFFLINE, Berlekamp-Massey
Fichiers `ledger.coinvault`+`SPEC.md`. Draws `Y_r∈F_p` liées par récurrence linéaire ordre 7 →
BM sur F_p prédit `Y_48` (vault, jamais ouvert) → commit match → `key=SHA256(Y48)`, keystream
SHA256-CTR, XOR CT. Flag=`NCTF{c0mmit_r3v34l_but_th3_dr4ws_w3re_l1n34rly_l1nk3d}`. Solveur
`challenges/commit-bias/solve_commit_bias.py`.

### 🟡 alerte-uvci (759, osint 154) — flag proposé (2 champs à confirmer)
OSINT clearnet : article cyberc4st → LinkedIn (Adama Assiongbon) → screenshot post forum.
`NCTF{Sensitive2025_MVP_92_86_149_Telegram_DarkForums}` (Q2-Q5 lus ; Q1/Q6/Q7 à confirmer).

### ✅ twister-tell (89, crypto 50) — OFFLINE, MT19937 untemper
624 sorties → untemper (point fixe) → setstate index 624 → keystream mots 32-bit big-endian → XOR
flag.enc. Flag=`NCTF{mt19937_untempered_then_the_future_is_yours}`. Solveur
`challenges/twister-tell/solve_twister.py`.

### ✅ crc-forge (183, reverse 50) — OFFLINE, static reverse
ELF strippé : CRC32 réfléchi par octet, init=~index, xorout=0xffffffff, 28 cibles à .rodata:0x2060.
Brute-force 28×256. Flag=`NCTF{crc32_le4ks_ev3ry_byt3}`. Solveur `challenges/crc-forge/solve_crc_forge.py`.

### ✅ pyc-ghost (188, reverse 50) — OFFLINE, xdis + LCG
vault.pyc (py3.11) désassemblé via xdis. DATA[i]^LCG keystream ((x>>16)&255, SEED=4919,
MUL=1103515245, ADD=12345, MASK=0x7fffffff). Flag=`NCTF{marsh4l_unp1ckl3d_th3_c0de}`.

### ✅ spiffe-mtls-ghost (652, cloud 187) — SVID multi-URI forgery
Seed HMAC leaké dans bundle_config.json → forge SVID. Ingress check uris[0] (sandbox),
Vault check uris[-1] (vault-controller) → SVID multi-URI passe les 2 (confused deputy).
Flag=`NCTF{984c1274da61f760a5b29dea}`. Exploit `challenges/spiffe-ghost/exploit.py`.

### ✅ artifacts-imds (17, cloud 449) — SSRF→IMDS→rôle
/fetch?url= = SSRF ; pointer 169.254.169.254/.../backup-role → token ; /objects/flag +
X-Role-Token → flag=`NCTF{8780ec8e1de2dbc00e5dec33}`. Variantes backup/billing/cdn-imds identiques.
Script `solve_imds.py <url>`.

### ✅ billing-imds (23, cloud 500) + cdn-imds (26, cloud 500) — même chaîne SSRF→IMDS
Identique à artifacts-imds (solve_imds.py). billing=`NCTF{6160286625f026849a85dc5e}`,
cdn=`NCTF{d7265367bf2f3a4cd1c7d318}` (cdn-imds était 0-solve → first blood potentiel).
