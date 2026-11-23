# -*- coding: utf-8 -*-
"""Chiffrement a flot : filter generator sur un LFSR de Fibonacci.
A chaque pas, t bits de taps sont combines en un entier, hache (SHA-256), et on
sort le bit de poids faible d'un octet du digest."""
import hashlib


class FilterLFSR:
    def __init__(self, L, fb_taps, filt_taps, coef, cst, byte_idx):
        self.L = L
        self.fb = list(fb_taps)        # positions XORees pour la retroaction
        self.P = list(filt_taps)       # positions des taps du filtre
        self.coef = list(coef)
        self.cst = cst
        self.byte = byte_idx

    def filter_bit(self, taps):
        val = self.cst + sum(c * int(b) for c, b in zip(self.coef, taps))
        return hashlib.sha256(str(val).encode()).digest()[self.byte] & 1

    def keystream(self, state, n):
        """state : liste de L bits. Renvoie n bits de sortie."""
        s = list(state)
        out = []
        for _ in range(n):
            out.append(self.filter_bit([s[p] for p in self.P]))
            fbbit = 0
            for j in self.fb:
                fbbit ^= s[j]
            s = s[1:] + [fbbit]
        return out
