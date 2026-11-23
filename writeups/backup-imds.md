# backup-imds (cloud, id 20) — SSRF → IMDS → role token

## Challenge
**Catégorie :** cloud  **Instance :** par équipe, HTTP  **Résolu par :** ctf-finale-bc (session coordonnée)

## Résolution (résumé)
Service exposant une fonctionnalité qui va chercher une URL côté serveur (SSRF). On pointe la
requête vers le **service de métadonnées de l'instance (IMDS)**
`http://169.254.169.254/...` pour récupérer les **credentials de rôle** (token temporaire),
puis on s'en sert pour lire le secret protégé.

Chaîne type :
```
SSRF (param url/fetch) -> http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>
                       -> AccessKey/SecretKey/Token
-> utiliser le token pour accéder à la ressource privée -> flag
```

## Flag
`NCTF{d8ef5a755ecd3fc83fb4b23b}`
