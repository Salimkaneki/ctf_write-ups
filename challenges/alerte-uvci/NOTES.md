# fullaccess5--alerte-uvci (OSINT, 227 pts, id 759)

Flag = NCTF{R1_R2_R3_R4_R5_R6_R7}

## Trail
1. Énoncé → article de départ : https://cyberc4st.com/actualites/fuite-donnees-uvci-cote-ivoire-base-sql/
2. Article → "publication LinkedIn d'Adama Assiongbon" (consultant CTI) + sous-domaine licences3.uvci.online
3. Post LinkedIn (activity-7520813815270232065) → 2 images :
   - capture du POST FORUM de l'acteur (profil + stats)
   - dump CSV (username,password,idnumber,firstname,lastname,email,...)

## Acteur (depuis la capture forum)
- Pseudo forum : **Sensitive2025** ("last modified by Sensitive2025")
- Signature : "Sharing Data with Love <3 Enjoy"
- Thread : "Fresh Database / Virtual University of Cote d'Ivoire (UVCI) Free", online university / www.licences3.uvci.online
- Acteur réel tracké par VECERT (@VECERTRadar sur X) et Brinztech (fuite bcac.hu, Toque Argentine)

## Réponses confirmées (depuis le profil forum de la capture)
- R2 (rang/badge, acronyme majuscules) = **MVP**
- R3 (posts)       = **92**
- R4 (threads)     = **86**
- R5 (reputation)  = **149**

## À trouver
- R1 pseudo Telegram  (icône Telegram présente dans le profil, handle non visible)
- R6 canal de communication privé
- R7 nom du forum cybercriminel (en-tête rogné sur la capture ; thème MyBB sombre/violet,
  rangs "MVP", "Hidden Content", titres préfixés d'une étoile → ressemble à DarkForums, À CONFIRMER)

Squelette : NCTF{R1_MVP_92_86_149_R6_R7}

## Pistes restantes pour R1/R6/R7
- 1 hint dispo (id 1551) — coûte des points, décision user
- chercher d'autres posts d'Adama Assiongbon (X/Medium/blog) nommant forum+Telegram
- identifier le forum par son thème sans le visiter

## MAJ — identification du forum
- R7 = **DarkForums** (darkforums.st). Preuve : DarkForums a les rangs VIP/MVP/GOD
  (MVP = rang payant ~40€), membres premium = accès à un "private leak channel".
  "MVP" sur la capture = ce rang. Sensitive2025 attesté y poster (alertes Brinztech
  NBGSPL / bcac.hu ; reports leakd.com/insecureweb sur DarkForums).
- Reste R1 (pseudo Telegram) + R6 (canal privé) — pointent vers le Telegram de l'acteur
  (icône Telegram dans le profil). Pas trouvés en sources publiques → hint (1551) probable,
  ou le handle = "Sensitive2025" (même pseudo), à CONFIRMER, ne pas soumettre au hasard.

Flag : NCTF{R1_MVP_92_86_149_R6_DarkForums}
