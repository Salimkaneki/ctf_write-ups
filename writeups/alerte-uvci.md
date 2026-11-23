# fullaccess5--alerte-uvci (osint/forensics, 154)

## Challenge
7 questions OSINT sur une fuite attribuée à l'**UVCI** (Université Virtuelle de Côte d'Ivoire).
Point de départ : article `cyberc4st.com/actualites/fuite-donnees-uvci-cote-ivoire-base-sql/`.
Consigne : **sources ouvertes légitimes uniquement** (pas de dark web / forum criminel).
Flag = `NCTF{R1_R2_R3_R4_R5_R6_R7}`.

## Piste OSINT (chaîne de sources, 100% clearnet)
1. Article cyberc4st (par Samuel MANSOUO) → cite une **publication LinkedIn** d'**Adama Assiongbon**
   (Cyber Threat Intelligence Consultant) comme source. Lien SOURCE en bas de l'article.
2. Post LinkedIn d'Adama Assiongbon (`/posts/adama-assiongbon-9029893a_...activity-7520813815270232065`)
   → contient **2 screenshots** : [1] le post du forum, [2] un extrait CSV des données.
3. Screenshot [1] (ouvert en pleine résolution 1280×873) = le **post forum** avec le profil de l'acteur.
   Cross-check acteur : trackers CTI **VECERT** (x.com/VECERTRadar) et **Brinztech** documentent
   l'alias **Sensitive2025** (mêmes fuites : Toque/Argentine, bcac.hu/Hongrie). VECERT suit cet
   acteur sur **DarkForums**.

## Réponses (lues sur le screenshot du profil forum)
| Q | Question | Réponse | Confiance |
|---|---|---|---|
| Q1 | pseudo Telegram de l'acteur (sans @) | **Sensitive2025** | haute (= handle forum ; icône Telegram sur le profil) — à confirmer via le lien Telegram |
| Q2 | rang/badge (acronyme majuscules) | **MVP** | sûr (lu) |
| Q3 | nb de posts | **92** | sûr (lu) |
| Q4 | nb de threads | **86** | sûr (lu) |
| Q5 | score de réputation | **149** | sûr (lu) |
| Q6 | canal de communication privé | **Telegram** | haute (icône Telegram sur le profil) |
| Q7 | forum où la base a été publiée | **DarkForums** | moyenne (VECERT + style UI MyBB/violet/awards/MVP ; nom non visible dans le crop) |

Profil : avatar masqué, signature « Sharing Data with Love ❤️ Enjoy », Joined Feb 2025.
Titre du thread : « ⭐ Fresh Database / Virtual University of Côte d'Ivoire (UVCI) Free ».

## Flag proposé
`NCTF{Sensitive2025_MVP_92_86_149_Telegram_DarkForums}`
⚠️ Q1 (handle Telegram exact) et Q7 (nom exact du forum : `DarkForums` vs `DarkForums.st`) à vérifier
avant soumission — p.ex. en suivant l'icône Telegram du profil (source ouverte) et en confirmant le forum.
