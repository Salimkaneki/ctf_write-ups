# boazak--aneho (web / hard, id 455) — PROGRÈS (non résolu)

Chaîne trouvée en black-box, bloquée au dernier pas (sandbox).

## Étape 1 — SQLi auth bypass → admin ✅
`POST /login` username injectable. `username=admin' OR '1'='1` & password=x → connecté
en **admin** (session Flask `{"is_admin":1,"user_id":1,"username":"admin","ward_slot":"WARD-ALPHA-913"}`).
NB: commentaires `--`/`#` et UNION ne passent pas (re-check password côté SQL), mais oracle
booléen OK : `zzz' OR ((CONDITION) AND username='admin') OR 'a'='b`.

## Étape 2 — SSTI (Jinja2 sandboxé) dans /admin ✅
`GET /admin?name={{7*7}}` → "Welcome 49". Helper exposé : `read_note(slot)` (= `read_ward_note`).
Page admin : "Sandbox is active — dangerous calls are blocked".

## Reconnaissance (oracle SQLi) ✅
- DB = **1 seule table `users`** (pas de table notes/memo/flag/ward).
- Users seedés : id1 admin (WARD-ALPHA-913), id2 guest (WARD-GUEST-000). Rien d'autre.
- Le flag n'est ni dans users, ni dans sqlite_master.sql.

## Mur ❌
- `read_note(slot)` : slots valides `WARD-[A-Z]+(-[0-9]+)?` (fullmatch, pas de traversal).
  Les notes sont des **fichiers** ("pickled notes are now restricted" sur le dashboard).
  Brute des slots thématiques (ICU/ER/FLAG/INCIDENT/…) = "No clinical memo". Slot probablement
  instance-random → non trouvable sans fuite.
- `SECRET_KEY` Flask **fort** (flask-unsign a épuisé rockyou) → pas de forge de session.
- Sandbox Jinja2 **bloque tous les dunders** (`__class__`/`__globals__`/`|attr`/concat) → pas
  d'évasion triviale.

## Pour finir (pistes)
1. **Évasion SandboxedEnvironment** via un gadget (objet exposé avec méthode non-dunder menant
   à l'exécution) — à chercher avec la source.
2. **Primitive pickle** : read_ward_note unpickle les notes (RestrictedUnpickler). Trouver un
   point d'écriture de note (import admin ?) → pickle malveillant bypassant la restriction.
3. Fuir le slot de la note-flag (listing du dossier notes/ via une des deux voies ci-dessus).
