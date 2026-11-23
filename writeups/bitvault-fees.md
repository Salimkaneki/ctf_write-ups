# bitvault-fees (web, 275) — RÉSOLU

## Challenge
Programme VIP BitVault : le fee tier dépend du **maker volume roulant 30j**. Atteindre
**obsidian** (≥ 1,000,000) débloque `GET /api/v1/vault/obsidian-desk` (flag). Collatéral de
départ ~25000 ; une commande ne peut locker plus que le disponible.
API : `POST /ladder/post {side,notional}`, `POST /ladder/pull {order_id}`.

## Bug — volume non décrémenté au pull
`post` ajoute `notional` à `rolling_volume_30d` et locke le collatéral.
`pull` **libère le collatéral mais ne retire PAS le notional du volume**.
→ chaque cycle post+pull (notional = collatéral dispo = 25000) ajoute 25000 au volume, à coût nul.

Exploit : boucler ~40-45× `post {"side":"bid","notional":25000}` puis `pull {order_id}` →
volume ≥ 1,000,000 → tier `obsidian` → `GET /api/v1/vault/obsidian-desk` → flag.

## Flag
`NCTF{3862b02de9026d9bbe12c682}`
