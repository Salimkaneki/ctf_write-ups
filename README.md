# NCTF26 — Finale — Les challenges expliqués simplement

Ce document explique, **avec des images simples**, les challenges qu'on a résolus.
Objectif : pouvoir les **raconter au jury sans jargon**.

Pour chaque challenge tu trouveras :
- 🏠 **L'image** (une comparaison de la vie courante)
- 🔓 **La faille** (le problème, en mots simples)
- 🛠️ **Ce qu'on a fait** (les étapes)
- 🎯 **Le piège** (le leurre qu'il fallait éviter)
- 🗣️ **La phrase à dire au jury**

Les détails techniques (commandes) sont dans le dossier [`writeups/`](writeups/).

---

# PARTIE 1 — Les challenges "cloud"

## A. La série `*-prefix` (9 challenges identiques)

🏠 **L'image : la clé oubliée sous le paillasson.**
Imagine un immeuble de stockage avec deux zones :
- une zone **publique** où tout le monde peut entrer et regarder,
- une zone **privée**, fermée, où se cache le flag. Il faut un **badge** pour y entrer.

🔓 **La faille.**
Quelqu'un a laissé **un mot de passe traîner dans la zone publique**. Avec ce mot de passe,
on obtient le badge qui ouvre la zone privée. C'est une **erreur humaine**, pas un bug
compliqué.

🛠️ **Ce qu'on a fait (4 étapes) :**
1. On regarde dans la zone publique → on trouve un fichier de notes qui traîne.
2. On ouvre ce fichier → dedans, un **mot de passe** (`deploy_secret=AKIA…`) a été oublié.
3. On échange ce mot de passe contre un **badge** (un "rôle" qui a le droit de lire le privé).
4. Avec le badge, on entre dans la zone privée et on prend le flag.

🎯 **Le piège.**
La porte de la zone privée n'est écrite sur **aucun plan** : si on demande "montre-moi la
liste du privé", on nous répond non. Il faut **deviner le nom du fichier** (le plus logique :
`private/flag`).

🗣️ **À dire au jury.**
> « La faille n'est pas sophistiquée : c'est un mot de passe laissé par erreur dans un
> endroit public, qui permet de monter en privilège et d'accéder aux données protégées. »

👉 Les **9 challenges** (registry, queue, billing, cdn, gateway, identity, metrics,
artifacts, backup) sont **le même immeuble avec une déco différente** → un seul script les
ouvre tous.

| Challenge | Flag |
|---|---|
| registry-prefix | `NCTF{b0122351c3b584bb44aed38d}` |
| queue-prefix | `NCTF{377bd20118578742b153a027}` |
| artifacts-prefix | `NCTF{56fab799d1a44772c15e90aa}` |
| backup-prefix | `NCTF{5769dc71092bebf2073169ee}` |
| billing-prefix | `NCTF{2e6197b9d9845d50fce9593d}` |
| cdn-prefix | `NCTF{9d93814254df4fd8ebb2d42b}` |
| gateway-prefix | `NCTF{a1f910fd4fc6d1400f14689b}` |
| identity-prefix | `NCTF{e25633ff4fcb4d739b23d869}` |
| metrics-prefix | `NCTF{fb4b060e439d6b437c9db7f4}` |

---

## B. `ebpf-verifier-mirage` (le plus technique, 300 points)

🏠 **L'image : le vigile qui ne compte pas comme le processeur.**
Il y a un coffre-fort de 64 cases. Devant, un **vigile** contrôle chaque ordre qu'on donne,
pour être sûr qu'on ne va pas fouiller **au-delà** des 64 cases autorisées.

🔓 **La faille : le vigile et l'exécutant ne font pas le même calcul.**
On donne un ordre du genre "divise ce nombre par un facteur énorme".
- **Le vigile croit :** « ça donne forcément zéro, donc il ira à la case 0, c'est sans
  danger » → il laisse passer.
- **Le processeur, en vrai,** a une règle bizarre : pour ce facteur précis, il **ne change
  rien** → le nombre reste intact.

Résultat : le vigile pense qu'on va à la case 0, mais en réalité on va **où on veut**, même
**en dehors** du coffre. C'est une **fuite de mémoire**.

🛠️ **Ce qu'on a fait.**
On lit les cases une par une, y compris celles interdites.

🎯 **Le piège.**
La case 0 contient un **faux flag** (un leurre). Le **vrai flag** est à la **case 64**, juste
après la limite autorisée — exactement là où seule notre astuce permet d'aller.

🗣️ **À dire au jury.**
> « Le gardien faisait confiance à son propre calcul théorique, mais le matériel ne calcule
> pas pareil. Cette différence entre la théorie du contrôleur et la réalité du processeur
> ouvre une fuite de mémoire. » (C'est une vraie classe de bugs du noyau Linux.)

**Flag** : `NCTF{77ad08bc7abee9a3de785d69}`

---

# PARTIE 2 — Le challenge "crypto"

## `sokode-crypto` (500 points) — casser AES grâce à une erreur provoquée

🏠 **L'image : deviner la serrure en provoquant un défaut.**
Une machine chiffre des messages avec une serrure très solide (AES, incassable en force
brute). Mais on nous donne, pour 16 messages : le message en clair, le chiffré **correct**,
et un chiffré **abîmé** (fabriqué en introduisant volontairement une petite erreur dans la
machine).

🔓 **La faille.**
En comparant un chiffré **correct** et le même chiffré **abîmé par une erreur minuscule et
bien placée**, on peut **remonter petit à petit à la clé secrète**. C'est une attaque connue
(dite « par faute »).

🛠️ **Ce qu'on a fait.**
Pour chaque petite erreur, on compare les deux versions, on en déduit un morceau de la clé,
et de morceau en morceau on reconstruit **toute la clé secrète**. On vérifie : avec cette
clé, nos 16 chiffrés correspondent bien. **La clé elle-même est le flag.**

🎯 **Le piège.**
Le fichier contenait aussi un gros bloc "RSA" qui ressemblait à la vraie cible → c'était un
**leurre**, sans rapport avec la solution.

🗣️ **À dire au jury.**
> « AES est incassable de face. Mais en provoquant une petite erreur contrôlée dans la
> machine et en comparant avec le chiffré normal, on reconstruit la clé morceau par morceau. »

**Flag** : `NCTF{f1a9537c67a9315917205968e9493ad0}` (c'est la clé retrouvée)

---

# PARTIE 3 — Les challenges "web" (série boazak, 9 villes)

Chaque ville = **une faille web différente**. Voici chacune en une image simple.

| Ville | L'image simple | Ce qu'on a fait | Flag |
|-------|----------------|-----------------|------|
| **agoe** | Le videur vérifie seulement la **1ʳᵉ personne** de la file | On demande nos données **puis** celles de l'admin dans la même requête ; le contrôle ne regarde que la 1ʳᵉ → la note secrète de l'admin passe. | `NCTF{e3d0e63f14d63b4489f4f532}` |
| **tsevie** | On demande un fichier, le site **ne vérifie pas lequel** | On demande un fichier système au lieu d'une note → il contient le flag. | `NCTF{6af2911c862115e9327c858c}` |
| **akodessewa** | Le formulaire d'inscription **accepte n'importe quel champ** | À l'inscription, on ajoute en douce "je suis admin" → on devient admin. | `NCTF{69f599c438329642fbb05b4a}` |
| **kande** | Les réglages **fusionnent** ce qu'on envoie, sans vérifier | On envoie "admin = vrai" → le réglage est accepté → accès admin. | `NCTF{5cccbb9757646180a674d2c3}` |
| **be** | Le code source (dossier `.git`) a été **laissé en ligne** | On récupère l'historique du code → un fichier `.zip` protégé y est caché → on casse son mot de passe → flag. | `NCTF{8ebb2e7dda5bc95d3011b2c3}` |
| **vogan** | Le serveur **lit trop naïvement** ce qu'on lui envoie (il peut exécuter du code) | On le pousse à provoquer une erreur dont **le message d'erreur contient le flag**. | `NCTF{3477daa63b62b83dc574cca9}` |
| **atakpame** | Le serveur **colle notre texte dans une commande** | On glisse une commande cachée qui lit le fichier du flag et le réaffiche. | `NCTF{9db3ec32d980bd45848d898b}` |
| **togbi** | Un **laissez-passer signé** qu'on arrive à **re-fabriquer** | On reconstruit la clé publique du serveur et on s'en sert pour forger un laissez-passer "super-admin". | `NCTF{7bf81884cfbd023b49935d93}` |
| **mono** | Une porte de service censée être **cachée** ne l'était pas | On demande directement la page secrète `/admin-flag` → flag. | `NCTF{5439f1780e0f2cef76b261d5}` |

**Les 2 réflexes à citer :**
- Souvent le flag est rangé dans les **variables du serveur** → dès qu'on peut lire un
  fichier, on lit le fichier spécial qui les affiche.
- Quand le site ne répond rien d'utile, **un message d'erreur peut trahir le secret**
  (cas de **vogan**).

**Les plus impressionnantes à mettre en avant :** **togbi** (on re-fabrique un laissez-passer
signé — de la cryptographie) et **vogan** (on fait parler le serveur par ses erreurs).

---

# Synthèse pour le jury (ta conclusion)

- **Cloud** : 10 flags. De l'erreur humaine réaliste (mot de passe oublié) à une faille
  pointue du cœur de Linux (le vigile vs le processeur).
- **Crypto** : on a cassé AES, non pas de force, mais en provoquant une erreur et en
  comparant — méthode élégante, vérifiée de bout en bout.
- **Web** : 9 failles différentes, un vrai tour d'horizon des erreurs classiques des sites.
- **Fil rouge** : on a **repéré les leurres** (faux flag, faux fichier, faux RSA) à chaque
  fois → ça prouve qu'on a vraiment compris, et pas juste copié une solution.
# ctf_write-ups
