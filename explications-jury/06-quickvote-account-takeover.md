# quickvote (web, 99) — account takeover par CSRF + flux « mot de passe oublié »

## Challenge
**Catégorie :** web  **Instance :** VPN (`https://10.100.45.101/`)  **Auteur :** is1d0r3
**Flag :** `NCTF{7417ad06526c5fdc17f53270}`

> « Changer son adresse email sur QuickVote, c'est en deux clics. Le faire pour quelqu'un
> d'autre sans lui demander, c'est le vrai challenge. »

## La faille
Sur `/settings`, deux formulaires :
- changement de **mot de passe** → protégé par un `csrf_token`,
- changement d'**email de récupération** (`POST /settings/recovery-email`) → **PAS de csrf_token**.

Un seul oubli de protection CSRF, mais sur l'endpoint qui gouverne le flux « mot de passe
oublié » → account takeover complet.

## Exploitation (chaîne en 4 étapes)
L'appli fournit tout le nécessaire :
- **« Héberger une page »** (`/upload`) → publie du HTML à une URL same-origin.
- **« Signaler un lien »** (`/report`) → un **bot admin connecté** ouvre l'URL soumise.
- **« Boîte mail »** (`/mailbox`) → montre les emails reçus à *mon* adresse de récupération.

1. J'héberge une page CSRF qui s'auto-soumet :
   ```html
   <form action="/settings/recovery-email" method="POST">
     <input name="new_email" value="hawk@hawk.test">
   </form><script>document.forms[0].submit()</script>
   ```
2. Je **signale** son URL → le bot admin l'ouvre → comme l'endpoint n'a pas de CSRF, **l'email
   de récupération de l'admin devient le mien** (same-origin + cookie admin).
3. `POST /forgot-password` avec `username=admin` → le lien de reset part vers mon adresse →
   il apparaît dans **ma** boîte mail (`/mailbox`).
4. Je suis le lien `/reset-password/<token>`, je fixe un nouveau mot de passe admin, je me
   connecte → **flag sur le dashboard admin**.

## Leçon (pour le jury)
> La protection CSRF doit couvrir **TOUS** les endpoints qui modifient un état sensible. Ici
> tout était protégé… sauf le changement d'email de récupération — or c'est précisément la
> clé du flux « mot de passe oublié ». Un seul formulaire oublié = prise de contrôle totale
> du compte admin.
