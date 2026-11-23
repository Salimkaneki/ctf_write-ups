# boazak--akloa-rendus (web, 100) — SSRF (bypass de port)

## Challenge
**Catégorie :** web  **Instance :** HTTP  **Auteur :** boazak
> Service « Akloa Rendus » avec un endpoint de rendu d'URL. (Résolu par la session voisine en
> Bash ; méthode ci-dessous.)

## Faille : SSRF avec allowlist sur le DOMAINE mais pas sur le PORT
L'endpoint **`GET /render?url=`** récupère l'URL **côté serveur** (SSRF). Il y a une
**allowlist**, mais qui ne filtre que le **domaine** (`docs.akloa.tg`, `media.akloa.tg`,
`static.akloa.tg`) — **pas le port**.

Un **indice en commentaire HTML** de la page traîne :
```html
<!-- internal healthcheck: docs.akloa.tg port 9191 -->
```
→ un service **interne** tourne sur `docs.akloa.tg:9191` et sert le flag.

## Exploitation
Le domaine `docs.akloa.tg` est autorisé → on garde le domaine mais on change le **port** vers
le service interne :
```
GET /render?url=http://docs.akloa.tg:9191/
```
Le service interne 9191 **sert le flag sur n'importe quel path** → le flag revient dans la réponse.

## Leçon (pour le jury)
> « Une allowlist SSRF doit valider **l'hôte ET le port** (et résoudre l'IP). Autoriser un
> domaine sans fixer le port laisse atteindre **tous les services internes** de cette machine. »

## Flag
`NCTF{a9692000faea8ec0a035939e}`
