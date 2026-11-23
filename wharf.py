#!/usr/bin/env python3
"""
wharf.py — pilote le plugin team_instancer (le "wharf") de arena.ctf.tg
depuis le terminal, en respectant les 2 limites : 6 instances simultanees
ET ~6 requetes / 60 s. Lance-le avec -I :   python3 -I wharf.py <cmd>

Auth (tes secrets restent chez toi, exporte-les toi-meme avec '! export ...') :
  CTF_TOKEN   = Access Token CTFd  (Settings -> Access Tokens)   [essaye en 1er]
  CTF_COOKIE  = valeur du cookie 'session' (DevTools -> Application -> Cookies)
                -> chemin navigateur, recupere le CSRF nonce tout seul.
  Au moins l'un des deux. Si spawn/destroy echoue en Token, exporte le cookie.

Commandes :
  list                      instances actives (/mine)
  spawn   <challenge_id>    cree une instance, affiche l'URL direct
  destroy <challenge_id> --yes    detruit (DESTRUCTIF -> --yes obligatoire)

Options : --base URL (def https://arena.ctf.tg)  --max-req N  --window S
"""
import json, os, re, sys, time, urllib.request, urllib.error, argparse

STATE = os.environ.get("WHARF_STATE",
    "/tmp/claude-1000/-home-dell-Documents-ctf-finale/"
    "9c42d546-4044-43d7-860b-a8f84555d933/scratchpad/wharf_reqs.json")

def _load_hits():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return []

def _save_hits(hits):
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        with open(STATE, "w") as f:
            json.dump(hits, f)
    except Exception:
        pass

def throttle(max_req, window):
    """Token-bucket persistant : attend pour ne jamais depasser max_req/window."""
    now = time.time()
    hits = [t for t in _load_hits() if now - t < window]
    while len(hits) >= max_req:
        wait = window - (now - min(hits)) + 0.3
        print(f"[throttle] {len(hits)}/{max_req} req dans {window}s -> pause {wait:.1f}s",
              file=sys.stderr)
        time.sleep(max(wait, 0.1))
        now = time.time()
        hits = [t for t in _load_hits() if now - t < window]
    hits.append(now)
    _save_hits(hits)

def http(method, url, headers, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except urllib.error.URLError as e:
        return 0, str(e)

def csrf_nonce(base, cookie):
    throttle(args.max_req, args.window)
    st, html = http("GET", base + "/challenges",
                    {"Cookie": f"session={cookie}", "User-Agent": "wharf-cli"})
    m = re.search(r'csrfNonce["\']?\s*[:=]\s*["\']([0-9a-fA-F]+)', html)
    if not m:
        sys.exit(f"[!] CSRF nonce introuvable (status {st}). Cookie session valide ?")
    return m.group(1)

def build_headers():
    h = {"Content-Type": "application/json", "Accept": "application/json",
         "User-Agent": "wharf-cli"}
    tok, ck = os.environ.get("CTF_TOKEN"), os.environ.get("CTF_COOKIE")
    if not tok and not ck:
        sys.exit("[!] Exporte CTF_TOKEN et/ou CTF_COOKIE (voir l'entete du script).")
    if tok:
        h["Authorization"] = f"Token {tok}"
    if ck:
        h["Cookie"] = f"session={ck}"
        h["CSRF-Token"] = csrf_nonce(args.base, ck)
    return h

def pretty(status, text):
    try:
        return status, json.loads(text)
    except Exception:
        return status, text

def cmd_list(h):
    throttle(args.max_req, args.window)
    st, body = pretty(*http("GET", args.base + "/plugins/team_instancer/mine", h))
    print(f"[mine] HTTP {st}")
    print(json.dumps(body, indent=2, ensure_ascii=False) if isinstance(body, (dict, list)) else body)

def cmd_spawn(h, cid):
    throttle(args.max_req, args.window)
    st, body = pretty(*http("POST", args.base + "/plugins/team_instancer/spawn",
                            h, {"challenge_id": cid}))
    print(f"[spawn {cid}] HTTP {st}")
    if isinstance(body, dict):
        url = (body.get("connection", {}) or {}).get("url") or body.get("url")
        if url:
            print(f"  URL : {url}")
            print(f"  -> cold-start ~8s, puis : curl -s {url}")
        print(json.dumps(body, indent=2, ensure_ascii=False))
    else:
        print(body)

def cmd_destroy(h, cid):
    throttle(args.max_req, args.window)
    st, body = pretty(*http("POST", args.base + "/plugins/team_instancer/destroy",
                            h, {"challenge_id": cid}))
    print(f"[destroy {cid}] HTTP {st}")
    print(json.dumps(body, indent=2, ensure_ascii=False) if isinstance(body, (dict, list)) else body)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["list", "spawn", "destroy"])
    p.add_argument("challenge_id", nargs="?", type=int)
    p.add_argument("--yes", action="store_true", help="confirme un destroy")
    p.add_argument("--base", default="https://arena.ctf.tg")
    p.add_argument("--max-req", type=int, default=6)
    p.add_argument("--window", type=float, default=60.0)
    args = p.parse_args()

    headers = build_headers()
    if args.cmd == "list":
        cmd_list(headers)
    elif args.cmd == "spawn":
        if args.challenge_id is None:
            sys.exit("[!] spawn <challenge_id>")
        cmd_spawn(headers, args.challenge_id)
    elif args.cmd == "destroy":
        if args.challenge_id is None:
            sys.exit("[!] destroy <challenge_id> --yes")
        if not args.yes:
            sys.exit("[!] destroy est DESTRUCTIF : ajoute --yes pour confirmer.")
        cmd_destroy(headers, args.challenge_id)
