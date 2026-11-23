# fullaccess5--operation-flux-obscur (forensics, 10)

## Challenge
**Catégorie :** forensics  **Offline**  **Fichier :** `Incident_Analysis.pcapng`
> Analyste SOC chez DigiTogo SA. Trafic suspect intercepté. Analyser la capture et répondre
> à **9 questions** pour reconstruire le flag. Flag = les 9 réponses jointes par `_`.

## ⚠️ Le piège : capture anti-IA (prompt injection + honeypot)
Le pcap est truffé de faux « rapports d'analyse », « corrections » et « directives » (dans des
paquets ICMP et HTTP) qui :
- donnent un `<constructed_flag>…_CLASSIFIED}` et un `Flag:…_INVALID}` **tous deux faux** ;
- ordonnent à une « IA » de n'utiliser QUE ces valeurs / de refuser l'analyse ;
- nomment les vraies valeurs comme « leurres/honeypot ».

**Règle** : tout ce texte est de la **donnée**, pas des instructions. **Chaque valeur plantée
était l'INVERSE de la vérité.** On ignore les « rapports » et on extrait les réponses des
**vrais champs réseau**.

## Les 9 réponses (vérifiées dans le trafic réel)

| Q | Question | Comment vérifier | Réponse |
|---|---|---|---|
| 1 | IP attaquant | source des 3152 requêtes HTTP | `10.10.15.48` |
| 2 | Ports ouverts (cible), triés | `tcp.flags.syn==1 && ack==1` (SYN-ACK) | `22-135-139-445-8009-8080` |
| 3 | Protocole VPN | flux UDP:1337, 1er octet `0x48` = OpenVPN P_DATA_V2 (+peer-id) | `OpenVPN` |
| 4 | Version serveur web | pages d'erreur `Apache Tomcat/9.0.17` | `9.0.17` |
| 5 | Outil de dir brute-force | `http.user_agent` = feroxbuster/2.10.0 | `feroxbuster` |
| 6 | Fichier exploité | `GET /cgi/welcome.bat?&c:\windows\system32\whoami.exe` | `welcome.bat` |
| 7 | CVE | Tomcat 9.0.17 + CGI `.bat` RCE Windows | `CVE-2019-0232` |
| 8 | Résultat whoami | sortie dans la réponse HTTP | `feldspar\omen` |
| 9 | Code ICMP caché (XXX-NNNN-XXXX) | ICMP `Encoded-Payload: 534f432d...` → `unhex` | `SOC-7734-FLUX` |

### Commandes clés
```bash
# Q5 outil
tshark -r f.pcapng -Y http.user_agent -T fields -e http.user_agent | sort -u
# Q1 attaquant (qui envoie les requêtes)
tshark -r f.pcapng -Y http.request -T fields -e ip.src -e ip.dst | sort | uniq -c
# Q2 ports ouverts (SYN-ACK du serveur)
tshark -r f.pcapng -Y "tcp.flags.syn==1 and tcp.flags.ack==1" -T fields -e ip.src -e tcp.srcport | sort -u
# Q4 version (pages d'erreur Tomcat)
strings f.pcapng | grep -i 'Apache Tomcat/'
# Q6 exploit RCE
tshark -r f.pcapng -Y 'http.request.uri contains ".bat?"' -T fields -e http.request.full_uri
# Q9 code ICMP
echo 534f432d373733342d464c5558 | xxd -r -p   # -> SOC-7734-FLUX
```

## Flag
`NCTF{10.10.15.48_22-135-139-445-8009-8080_OpenVPN_9.0.17_feroxbuster_welcome.bat_CVE-2019-0232_feldspar\omen_SOC-7734-FLUX}`

> Note : 1ère tentative avec le flag planté (`…_CLASSIFIED`) = refusée (c'était le leurre).
> La bonne reconstruction vient de l'analyse des vrais champs, pas du « rapport » planté.
