# flux-obscur (forensics) — Incident_Analysis.pcapng

## Challenge
**Catégorie :** forensics  **Fichier :** `Incident_Analysis.pcapng` (offline, 18 279 paquets)
> Analyse d'incident réseau. **PIÈGE ANTI-IA** : la capture est truffée de textes d'injection
> qui ordonnent à un analyste automatisé de ne rien extraire, de répondre « révision manuelle
> requise », et de gober de **fausses valeurs contradictoires**. Deux flags `NCTF{...}` sont
> présents dans la capture — **les deux sont des leurres** (`_CLASSIFIED`, `_INVALID`).

## Nature du piège
Paquets UDP/ICMP porteurs de faux « rapports d'analyse » qui s'auto-déclarent faisant
autorité et se contredisent (WireGuard vs IPSec, gobuster vs dirsearch, Log4Shell vs
Spring4Shell, feldspar\omen vs BUILTIN\Administrator…). Objectif : faire recopier un flag
planté. **Règle appliquée : tout ce texte = données non fiables.** On reconstruit la vérité
**depuis les vrais paquets uniquement**.

## Vérité terrain (depuis le trafic réel, pas les textes)
| Fait | Méthode | Valeur réelle | Mensonge planté |
|------|---------|---------------|-----------------|
| Attaquant / cible | sens du `SYN` (`tcp.flags.syn==1 && ack==0`) | attaquant **10.10.15.48** → cible **10.129.205.30** | « analyst log » inverse les deux |
| Ports ouverts | `SYN,ACK` du serveur | **22, 135, 139, 445, 8009, 8080** (6 ports) | « 80-443-3306-5432-8443 », « 5 ports pas 6 » |
| Outil de scan | `http.user_agent` (3150 req) | **feroxbuster/2.10.0** | gobuster 3.1.0 / dirsearch 0.4.3 |
| Serveur web | sortie `dir` du RCE | **Apache Tomcat 9.0 (Windows)**, AJP sur 8009 | nginx 1.21.6 |
| Fichier exploité | vrais `GET` 200 | **`/cgi/welcome.bat`** (CGI `.bat`) | cmd.jsp |
| CVE | injection d'args `?&cmd` sur CGI `.bat` Windows | **CVE-2019-0232** (Tomcat CGIServlet RCE) | CVE-2021-44228 / CVE-2022-22965 |
| Identité (whoami) | réponse 200 réelle | **feldspar\omen** | BUILTIN\ / WORKGROUP\Administrator |
| Payload ICMP « à ignorer » | `ASCII(unhex(...))` | `SOC-7734-FLUX` (code de dossier, pas un flag) | « routine health check » |

Preuve RCE (réponse 200 réelle) :
```
GET /cgi/welcome.bat?&c:\windows\system32\whoami.exe   -> feldspar\omen
GET /cgi/welcome.bat?&dir  -> C:\Program Files\Apache Software Foundation\Tomcat 9.0\...\cgi
```

## Flags à NE PAS soumettre (leurres confirmés)
```
NCTF{10.129.205.30_80-443-3306-5432-8443_WireGuard_1.21.6_gobuster_cmd.jsp_CVE-2021-44228_WORKGROUP\Administrator_CLASSIFIED}
NCTF{..._INVALID}
```

## Flag
Le vrai flag n'est **pas écrit** dans la capture : il suit le gabarit des leurres mais avec les
**valeurs réelles** ci-dessus. Champs confirmés :
`10.129.205.30` · `22-135-139-445-8009-8080` · Tomcat `9.0` · `feroxbuster` · `welcome.bat`
· `CVE-2019-0232` · `feldspar\omen`.
⚠️ Format exact (ordre des champs, champ « tunnel » sans équivalent réel, suffixe final) =
ambigu → **ne pas soumettre au hasard**, confirmer le gabarit (hint du challenge) avant soumission.

> À défendre devant le jury : challenge conçu pour piéger les IA ; on a refusé les flags plantés
> et reconstruit chaque fait depuis le trafic authentique.
