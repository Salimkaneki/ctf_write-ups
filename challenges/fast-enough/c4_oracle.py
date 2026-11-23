# -*- coding: utf-8 -*-
"""
C4 -- oracle chronometre (serveur). A chaque connexion :
  - K rounds ; a chaque round un etat initial FRAIS et aleatoire du LFSR ;
  - le serveur envoie NBITS bits de keystream ;
  - le joueur doit renvoyer les PREDICT_M bits de keystream SUIVANTS ;
  - tout faux, ou depassement du budget total DEADLINE secondes -> deconnexion.
Les K rounds reussis dans le temps imparti -> le flag.

Params du chiffrement : voir c4_config (publics). Seul l'etat est secret/frais.
"""
import os, sys, time, secrets
import c4_config as C
from c4_proto import FilterLFSR

K = 25                 # nombre de rounds
PREDICT_M = 64         # bits a predire par round
DEADLINE = 150.0       # budget total (s) par connexion
FLAG = os.environ.get("FLAG", "NCTF{PLACEHOLDER_c4_flag}")


def make_cipher():
    return FilterLFSR(C.L, C.fb_taps(), C.TAPS, C.COEF, C.CST, C.BYTE)


def run_session(inf, outf, rng=secrets.SystemRandom()):
    def send(s):
        outf.write(s + "\n"); outf.flush()
    cip = make_cipher()
    send("== C4 stream oracle ==")
    send(f"params: L={C.L} poly={hex(C.POLY_INT)} taps={C.TAPS} "
         f"coef={C.COEF} cst={C.CST} byte={C.BYTE}")
    send(f"rounds K={K}, per round: {C.NBITS} keystream bits -> predict next "
         f"{PREDICT_M} bits. Budget {DEADLINE:.0f}s total.")
    t0 = time.time()
    for rnd in range(1, K + 1):
        state = [rng.randrange(2) for _ in range(C.L)]
        full = cip.keystream(state, C.NBITS + PREDICT_M)
        given = full[:C.NBITS]; nxt = full[C.NBITS:]
        send(f"[round {rnd}/{K}] " + "".join(map(str, given)))
        line = inf.readline()
        if not line:
            return False
        ans = line.strip()
        if time.time() - t0 > DEADLINE:
            send("timeout"); return False
        if ans != "".join(map(str, nxt)):
            send("wrong"); return False
        send("ok")
    send("FLAG: " + FLAG)
    return True


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "0"))
    if port == 0:
        # mode stdio (xinetd/socat) : une session sur stdin/stdout
        run_session(sys.stdin, sys.stdout)
        return
    import socketserver

    class H(socketserver.StreamRequestHandler):
        timeout = DEADLINE + 30

        def handle(self):
            inf = self.rfile_text(); outf = self.wfile_text()
            try:
                run_session(inf, outf)
            except Exception:
                pass

        def rfile_text(self):
            return _TextWrap(self.rfile)

        def wfile_text(self):
            return _TextWrapW(self.wfile)

    class S(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    print(f"listening on {host}:{port}", file=sys.stderr)
    S((host, port), H).serve_forever()


class _TextWrap:
    def __init__(self, raw): self.raw = raw
    def readline(self):
        return self.raw.readline().decode("utf-8", "replace")


class _TextWrapW:
    def __init__(self, raw): self.raw = raw
    def write(self, s): self.raw.write(s.encode())
    def flush(self): self.raw.flush()


if __name__ == "__main__":
    main()
