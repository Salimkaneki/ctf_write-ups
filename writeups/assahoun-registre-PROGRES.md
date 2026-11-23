# boazak--assahoun-registre (web, 199) — PROGRÈS (bloqué)

## Challenge
GraphQL (`/graphql`, auth Bearer). Introspection **truquée** (schéma figé : Query{me,user(id:Int)},
Mutation{register,login}, User{id,username,email}). « partage tout sauf ses secrets ».

## Établi
- Champ caché **`secretNote`** sur User (hors introspection) : trouvé en le demandant ;
  le resolver renvoie un **dict fixe** {id,username,email,secretNote} quels que soient les champs demandés.
- `register(username,password)` → id auto-incrémenté (admin = **id 1** seedé). `login` → token **32 hex aléatoire**
  (différent à chaque login, non forgeable, non dérivé de id/username).
- `me` → user du token. `user(id:N)` → **« Access denied: you can only view your own profile »** si N≠mon id
  (check AVANT fetch : id:0 → denied). Flag = `secretNote` de l'admin (id 1).
- Parser **regex strict** : seuls `me{}`, `user(id:N){}`, `register`, `login` ; tout le reste = « Unknown operation »
  (pas d'alias/batch, pas de variables, pas d'args en plus, pas de champs/mutations cachés).

## Écarté
SQLi login/username (paramétré), SQLi Bearer token (dict lookup), tokens spéciaux (vide/1/admin/null),
mass-assignment register, confusion d'args dupliqués, username numérique, brute pw admin (liste courte),
`me(id:1)` (arg ignoré), unauth user(id:1).

## Piste restante
Le bug doit être dans le **check d'accès** `N != current_user.id` (ou la résolution token→user).
Peut-être : race au seed pour être id 1, collision de token, ou un format de token/`user(id)` non testé.
Instance : register `hawk/pw123456` (id 2). Endpoint aussi annoncé sur `:8022/graphql`.

## Flag
(non obtenu — besoin de lire secretNote de l'user 1)
