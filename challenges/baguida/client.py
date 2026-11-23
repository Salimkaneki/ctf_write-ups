#!/usr/bin/env python3
"""Tiny protocol client for the Baguida seal desk (handout helper)."""
import socket
import sys


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1345
    s = socket.create_connection((host, port))
    fh = s.makefile("rb")
    for _ in range(5):
        line = fh.readline()
        if not line:
            break
        sys.stdout.write(line.decode(errors="replace"))
    sys.stdout.flush()
    for line in sys.stdin:
        s.sendall(line.encode())
        reply = fh.readline()
        if not reply:
            break
        sys.stdout.write(reply.decode(errors="replace"))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
