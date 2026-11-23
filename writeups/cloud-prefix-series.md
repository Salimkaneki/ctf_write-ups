# Série cloud `*-prefix` (9 challenges) — récap

## Explication simple (pour le jury)

🏠 **L'image : la clé oubliée sous le paillasson.**
Un immeuble de stockage avec deux zones : une **publique** (tout le monde entre et regarde)
et une **privée** (fermée, le flag est dedans, il faut un **badge**).

🔓 **La faille.** Quelqu'un a laissé **un mot de passe traîner dans la zone publique**. Avec
ce mot de passe on obtient le badge qui ouvre la zone privée. C'est une **erreur humaine**,
pas un bug compliqué.

🛠️ **Les 4 gestes :**
1. On regarde dans la zone publique → un fichier de notes traîne.
2. On l'ouvre → un **mot de passe** (`deploy_secret=AKIA…`) a été oublié dedans.
3. On échange ce mot de passe contre un **badge** (un rôle qui peut lire le privé).
4. Avec le badge, on entre dans la zone privée et on prend le flag.

🎯 **Le piège.** La porte privée n'est écrite sur **aucun plan** (« served by no route ») :
on ne peut pas lister le privé, il faut **deviner le nom du fichier** (`private/flag`).

🗣️ **Phrase pour le jury :**
> « La faille n'est pas sophistiquée : un mot de passe laissé par erreur dans un endroit
> public permet de monter en privilège et d'accéder aux données protégées. »

👉 Les **9 challenges** sont **le même immeuble avec une déco différente** → un seul script
les ouvre tous.

---

Même faille pour les 9 : object-store type S3 avec ACL par préfixe.
Chaîne : `/list?prefix=public/` → objet public qui fuit `deploy_secret=AKIA…`
→ `/assume?secret=…` donne un `role-…` (role **backup-restore**, lit `private/*`)
→ `/get?key=private/flag` avec header `X-Role-Token`.

Détail complet + pièges dans [registry-prefix.md](registry-prefix.md).
Solveur générique : `python3 -I solve_prefix.py <url_instance>` (warmup cold-start inclus).

## Spawn / destroy (contourne les 2 limites)
- **6 instances concurrentes max / équipe** ET **~6 requêtes / fenêtre** sur l'instancer.
- Méthode : `fetch('/plugins/team_instancer/spawn'|'/destroy', {method:'POST',
  headers:{'CSRF-Token':window.init.csrfNonce,...}, body:JSON.stringify({challenge_id})})`.
  L'URL d'instance est directement dans la réponse du spawn (pas besoin de polling).
- Cycle : spawn (≤2-3 d'un coup) → solve en Bash → destroy pour libérer les slots.

## Flags (finale — rotatés)
| Challenge | id | Flag |
|---|---|---|
| registry-prefix | 48 | `NCTF{b0122351c3b584bb44aed38d}` |
| queue-prefix | 45 | `NCTF{377bd20118578742b153a027}` |
| artifacts-prefix | 19 | `NCTF{56fab799d1a44772c15e90aa}` |
| backup-prefix | 22 | `NCTF{5769dc71092bebf2073169ee}` |
| billing-prefix | 25 | `NCTF{2e6197b9d9845d50fce9593d}` |
| cdn-prefix | 28 | `NCTF{9d93814254df4fd8ebb2d42b}` |
| gateway-prefix | 31 | `NCTF{a1f910fd4fc6d1400f14689b}` |
| identity-prefix | 35 | `NCTF{e25633ff4fcb4d739b23d869}` |
| metrics-prefix | 40 | `NCTF{fb4b060e439d6b437c9db7f4}` |
