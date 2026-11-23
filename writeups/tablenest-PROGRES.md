# hackusman--tablenest (web, hard, 300) — PROGRÈS (bloqué)

## Challenge
Plateforme resto Flask+nginx. « espace client et une console interne. Un incident
touche les outils de l'équipe : enquêtez et récupérez le flag. » Instance per-team.
README = vide (pas de fichier). 0 solve au moment du test (2026-11-19 ~22h).

## Surface (complète, brute-force exhaustif)
Client : `/ /menu /products /product/<slug> /restaurants /basket (+add/remove/clear/checkout)
/login /register /logout /forgot-password /reset-password /profile /mailbox
/mailbox/message/<uuid> /contact /health`.
Console staff : **`/support/` `/support/tickets` `/support/tickets/<id>` `/support/customers`
`/support/reports`** → tous **403** « Internal tools are limited to staff accounts ».

## Mécaniques établies
- Session = **cookie Flask signé** `{"role":"customer","user_id":N}`. Secret **absent de
  rockyou** + wordlist clés dev ciblée → non crackable (pas la voie).
- Reset mot de passe : token = `secrets.token_urlsafe(32)` **aléatoire** (pas de point,
  non prévisible), livré dans la **mailbox du compte** (par destinataire, pas par demandeur).
  Token lié à l'email **côté serveur** (form = token+pw seulement).
- Mailbox **stricte par compte** (pas d'IDOR sur `/mailbox/message/<uuid>` : ownership OK).
  L'indice « Contacts added to an account are delivered separately » **n'a aucune UI/endpoint**
  correspondant → leurre probable (ou mécanique backend non déclenchable à l'aveugle).
- Oracle d'énumération via register (loc=/login=libre, sinon rejeté/pris). **Seul compte
  non-client existant = `support@tablenest.local`** (= la cible staff). `admin@`, `staff@`,
  `security@`… tous LIBRES.
- Normalisation email = lower+strip ; **non-ASCII (cyrillique/zero-width) REJETÉ par validation**
  (pas de repli homoglyphe exploitable). Dots et +tag = comptes distincts, **livraison exacte**
  (pas de collision mailbox).

## Prises testées et ÉCARTÉES
forge cookie Flask · prédiction/override token reset (`email`/`user_id` dans le POST) ·
IDOR message · SQLi login+search · mass-assignment `role/is_staff` (register ET profile) ·
bypass authz `/support/*` (casse, slash, `X-Original-URL`, `XFF`, verbes, OPTIONS) ·
injection destinataire forgot-password · exposition source/`.env`/git · multi-email register ·
SSTI dans `full_name` (Jinja **autoescape** → échappé) · remember-me cookie (inexistant) ·
email d'activation staff sur `@tablenest.local` (aucun) · routage vhost (edge rejette Host≠SNI) ·
changement d'email profil (ignoré) · mots de passe faibles support@.

## Piste bot XSS (testée, négative)
Beacons `<img>`/`<script>` → webhook.site dans tickets `/contact` (4 topics). **0 hit en ~8 min**
→ pas de bot joignable et/ou contenu échappé (cohérent avec autoescape). Instance recyclée ensuite.

## Reste à essayer (avec un indice ou idée neuve)
- Déclencheur réel de la mécanique « contacts » (si elle existe).
- Faille logique multi-étapes sur reset/mailbox non vue.
- Instance morte : respawn id 730 → recréer comptes (hawk@test.local / HawkEye!2026).

## Flag
(non obtenu)
