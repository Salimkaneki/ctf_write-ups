#!/usr/bin/env python3
"""Client TLS pour ebpf-verifier-mirage. Envoie du bytecode hex, renvoie la réponse."""
import socket, ssl, sys, time

HOST="7x2cx4bdkkc4ayfl.t.ctf.tg"; PORT=1337

def ins(op,dst=0,src=0,off=0,imm=0):
    return bytes([op&0xff, dst&0xff, src&0xff, off&0xff]) + (imm & 0xffffffff).to_bytes(4,'little')

def send(bytecode, timeout=12):
    """bytecode: bytes. Retourne la réponse texte du service."""
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    raw=socket.create_connection((HOST,PORT),timeout=timeout)
    s=ctx.wrap_socket(raw,server_hostname=HOST)
    s.settimeout(timeout)
    out=b''
    try:
        # lire éventuel prompt
        time.sleep(0.3)
        try:
            s.setblocking(False); out+=s.recv(4096)
        except Exception: pass
        s.setblocking(True)
        s.sendall(bytecode.hex().encode()+b'\n')
        time.sleep(0.4)
        while True:
            try:
                chunk=s.recv(4096)
                if not chunk: break
                out+=chunk
            except socket.timeout: break
            except Exception: break
    finally:
        s.close()
    return out.decode('utf-8','replace')

if __name__=='__main__':
    # test: MOV R0, 0x41 ; EXIT
    prog = ins(0xb7,0,0,0,0x41) + ins(0x95)
    print('prog hex:', prog.hex())
    print(send(prog))
