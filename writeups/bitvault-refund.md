# bitvault-refund (web, 275) — RÉSOLU

## Challenge
Exchange BitVault. But : faire que `balance > deposited` (jamais possible honnêtement) → flag
dans `GET /api/v1/wallet`. API : open payout (réserve principal+fee), **reprice** (RBF : baisse
le fee, la différence est rebatée au solde), scrap (annule, rend le principal).
Fee band [20000,25000].

## Bug — reprice idempotent-cassé (double/n-rebate)
`POST /api/v1/payouts/<id>/reprice {"rebate_to_sat":F}` rebate `fee - F` au solde MAIS **ne met
jamais à jour le `network_fee_sat` stocké** (reste la valeur d'ouverture). → chaque reprice
recalcule le rebate depuis le fee d'origine et **re-crédite** la même différence.

Exploit :
1. `POST /api/v1/payouts {"sats":50000,"network_fee_sat":25000}`.
2. Répéter `POST /payouts/<id>/reprice {"rebate_to_sat":20000}` → +5000 au solde à chaque appel.
3. ~15 reprices → `balance_sat > deposited_sat` → `"overfunded":true` + flag.
   (« you minted money out of fee rebates »).

## Flag
`NCTF{d461331e81f474e1e333133c}`
