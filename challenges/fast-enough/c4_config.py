# -*- coding: utf-8 -*-
"""Parametres PUBLICS du chiffrement (identiques a chaque round/connexion ;
seul l'etat initial du LFSR est secret et tire au hasard a chaque round)."""

L = 80                      # longueur du LFSR
POLY_INT = 1377573749490194700300181   # polynome de retroaction (primitif)
TAPS = [0, 14, 32, 53, 76]  # positions des 5 taps du filtre
COEF = [2, 3, 4, 5, 8]      # coefficients de la combinaison entiere
CST = 19                    # constante additive
BYTE = 0                    # octet du digest dont on prend le LSB
NBITS = 4860                # bits de keystream fournis par round


def fb_taps():
    """Positions de retroaction : c_i = bit i de POLY_INT, pour i < L."""
    return [i for i in range(L) if (POLY_INT >> i) & 1]
