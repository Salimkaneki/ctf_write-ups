# Explications jury — solves de la session (finale NCTF26)

6 challenges résolus. Pour chacun : le **pitch 30 s** (à dire à l'oral), puis le détail
technique dans le fichier numéroté correspondant.

| # | Challenge | Catégorie | Flag |
|---|-----------|-----------|------|
| 01 | fast-enough | crypto | `NCTF{aa2eba38db8805c1ba58305c}` |
| 02 | spiffe-mtls-ghost | cloud | `NCTF{984c1274da61f760a5b29dea}` |
| 03a | backup-imds | cloud | `NCTF{d8ef5a755ecd3fc83fb4b23b}` |
| 03b | backup-oidc | cloud | `NCTF{dea010e84499df6e317ad60a}` |
| 04 | perfect | forensics | `NCTF{3ph3m3r4l_but__k3yl0g_1n_dns__pfs_d3f34t3d}` |
| 05 | pyc-ghost | reverse | `NCTF{marsh4l_unp1ckl3d_th3_c0de}` |

---

## 01 — fast-enough (crypto) · *filter generator cassé par algèbre*
**Pitch :** « Le serveur chiffre avec un registre à décalage de 80 bits et une fonction de
brouillage. On nous donne 4860 bits de sortie, on doit prédire les 64 suivants, 25 fois en
moins de 150 s. La fonction de brouillage a une faiblesse : elle admet un *annihilateur de
degré 2*. Du coup chaque bit observé devient une équation du second degré sur l'état secret.
On résout tout par élimination de Gauss et on reconstruit l'état en ~1 s par manche. »
**Mot-clé jury :** immunité algébrique faible → attaque de Courtois-Meier.
**À montrer :** le solveur passe les 25 manches en 32 s (budget 150 s).

## 02 — spiffe-mtls-ghost (cloud) · *deux gardes, deux identités*
**Pitch :** « Un portail de sécurité laisse entrer les services qui présentent un badge signé.
Deux bugs : (1) la clé pour signer les badges est écrite en clair dans le fichier de config
fourni → on fabrique un badge nous-mêmes ; (2) le badge contient une *liste* d'identités, et
le portique d'entrée regarde la PREMIÈRE pendant que le coffre regarde la DERNIÈRE. On met
deux identités (une sandbox, une admin) → les deux gardes sont contents, le coffre livre le
flag. »
**Mot-clé jury :** *confused deputy* + secret de signature public. (Piège évité : un CN précis
donnait un faux flag.)

## 03 — backup-imds & backup-oidc (cloud) · *deux classiques du cloud*
**Pitch imds :** « Le service va chercher des fichiers pour nous (SSRF). On l'oriente vers
l'API de métadonnées d'AWS (169.254.169.254), on vole les identifiants temporaires du rôle de
la machine, et on lit le fichier privé = flag. »
**Pitch oidc :** « Le jeton d'authentification est un JWT. Le serveur accepte l'algorithme
*none* : on se forge un jeton "admin" sans aucune signature, et l'API privilégiée nous donne
le flag. »
**Mots-clés jury :** SSRF→IMDS (vol de credentials IAM) ; JWT `alg=none` (jamais faire
confiance au champ alg).

## 04 — perfect (forensics) · *la forward secrecy trahie par le DNS*
**Pitch :** « On a une capture WiFi et le mot de passe du réseau. On déchiffre le WiFi : à
l'intérieur, du HTTPS (donc chiffré) + des requêtes DNS bizarres. Ces requêtes DNS
contiennent, encodée, la *clé de session TLS* (un malware l'exfiltrait octet par octet). On
reconstruit cette clé, on déchiffre le HTTPS, et on lit la valeur sensible du formulaire. »
**Mot-clé jury :** la *perfect forward secrecy* ne protège que si les clés restent secrètes ;
ici la clé fuyait par exfiltration DNS. Surveiller les sous-domaines hexadécimaux anormaux.

## 05 — pyc-ghost (reverse) · *le bytecode Python ne cache rien*
**Pitch :** « On nous donne un fichier Python compilé (.pyc). On le désassemble SANS
l'exécuter. Le flag n'est pas stocké en clair : c'est `flag = données ⊕ keystream`, et le
keystream vient d'un générateur pseudo-aléatoire faible (LCG) dont la graine est dans le
fichier. On rejoue le générateur, on refait le XOR, le flag sort. »
**Mot-clé jury :** compiler en .pyc ≠ protéger ; un LCG n'est pas un chiffrement.

---

### Fil rouge des 6 solves (pour conclure devant le jury)
Chaque faille vient d'une **confiance mal placée** :
- confiance en un secret qui est en fait public (spiffe, pyc-ghost),
- confiance en un contrôle unique contourné par un second chemin (spiffe 2 URIs, backup SSRF→IMDS),
- confiance en une primitive supposée sûre mais faible ou mal configurée (fast-enough filtre,
  oidc alg=none, perfect = clé TLS exfiltrée).
