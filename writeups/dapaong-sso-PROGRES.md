# boazak--dapaong-sso (web, 100) — PROGRÈS (XSW OK, livraison dashboard bloquée)

## Challenge
SSO SAML du BNAT. Flux : `/` → `/saml/init` → `/idp/sso?relay=/dashboard` (IdP simulé) →
POST SAMLResponse à `/saml/acs`. But : accéder au « document confidentiel » (admin) sur `/dashboard`.

## Établi / réussi
- **IdP login à email LIBRE** : form avec email (défaut demo@bnat.tg) + **PoW**
  `sha256(challenge+nonce).startswith('0000')` (brute trivial). → on obtient une assertion signée
  pour **admin@bnat.tg** mais **role=USER**.
- Assertion signée RSA-SHA256, **cert X509 embarqué** dans KeyInfo. La `<ds:Reference>` n'a
  **pas de DigestValue** (format custom) ; la signature couvre **l'assertion** (modifier hors-assertion
  passe, modifier le role → « Signature RSA invalide »).
- **XSW RÉUSSI** : dupliquer l'assertion (role **USER→ADMIN**, sans signature, ID `_evil...`) et la
  placer **AVANT** l'assertion signée originale (variant A ; le wrap variant C marche aussi).
  → `POST /saml/acs` renvoie `{"name_id":"admin@bnat.tg","role":"ADMIN","token":"<64hex>"}`.
  (ACS valide la signature sur l'assertion originale, mais lit name_id/role sur la 1ère = evil.)

## Blocage
Le **token** renvoyé par l'ACS **n'authentifie PAS `/dashboard`** : testé Authorization Bearer/raw,
~40 noms de cookie, query params, headers X-Role/X-Remote-User → toujours `{"auth":"requise"}`
(réponse identique avec/sans token → `/dashboard` ne lit ni le token ni Authorization).
App **sans aucun Set-Cookie** sur tout le flux. ACS ne **fetch pas** `profile_url` (SSRF testé via
webhook = 0 hit). Le flag (document confidentiel) est côté `/dashboard` (GET only) ou renvoyé si la
session stockée est ADMIN.

## Pistes restantes (besoin source)
- Peut-être le token stocke role=USER (assertion signée) alors que l'ACS AFFICHE ADMIN (1ère assertion)
  → trouver le variant XSW qui met ADMIN dans la **session/token**, pas juste l'affichage.
- Ou mécanisme de session `/dashboard` non identifié (cookie signé Flask attendu, jamais posé).
- PoW: `sha256(challenge+nonce)` 4 zéros hex ; email libre à l'IdP.

## Flag
(non obtenu — role=ADMIN obtenu à l'ACS, reste à ouvrir /dashboard)
