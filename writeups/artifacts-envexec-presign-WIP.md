# artifacts-envexec (270) & artifacts-presign (271) — EN COURS (black-box)

Deux clouds black-box (pas de source) passés par bc. Instances live après le fix WARP.

## artifacts-envexec (270)
`POST /invoke {fn, env}`. Root : functions=[greet,healthcheck], safe_env=[LOG_LEVEL,REGION].
- `REGION` est **reflété** dans la réponse (`region:"..."`) ; `LOG_LEVEL` sans effet visible.
- Clés hors allowlist = **silencieusement ignorées** (pas de rejet).
- `env` en **liste** `["K=V"]` → **500** (le code attend un dict).
- **Pas d'exécution shell** : REGION/LOG_LEVEL/fn avec `; sleep 5`, `$(sleep 5)`, backticks →
  **aucun délai** (timing ~0.3 s) → pas d'injection de commande classique, pas d'exec aveugle.
- Piste restante : le levier « env→exec » n'est ni shell-injection ni allowlist-bypass trivial.
  À tester : clé `REGION` avec valeur qui influence un **chargement** (ex. un fn qui fait
  `import`/`eval`/template avec REGION), ou un **3ᵉ endpoint** non documenté, ou `fn` pointant
  vers un artefact déployé (lien avec presign 271 ?).

## artifacts-presign (271)
Root : `/presign?key=uploads/<name>`→PUT signé ; `/put?key=&exp=&sig=` (body=objet) ;
`/get?key=...` ; `/deploy` → « runs hooks/postdeploy ». (presign/deploy = **GET**.)
- bc : `/presign` signe **n'importe quelle clé** (bypass du préfixe `uploads/`), put/get OK,
  mais `/deploy` renvoie toujours `hook:"none"` même après écriture de `hooks/postdeploy`
  → **deploy lit un store séparé** de get/put.
- Pistes restantes : clé exacte attendue par deploy (`hooks/postdeploy.sh` ? extension ?),
  format/contenu du hook (shebang ?), ou étape de « promotion » entre le store d'upload et le
  store lu par deploy ; vérifier les params de `/deploy` et la signature attendue.

## État
Non résolus — analyse en cours. Les deux reflètent le thème « artifacts » (registre/déploiement).
