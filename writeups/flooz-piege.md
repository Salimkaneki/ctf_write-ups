# fullaccess5--operation-flooz-piege (forensics, 500)

## Challenge
**Catégorie :** forensics  **Offline**  **Fichier :** `remboursement_flooz.eml`
> Analyste SOC/Blue Team chez DigiTogo SA. Un employé compta reçoit un faux « remboursement
> Flooz » de 75 000 FCFA prétendant venir de Moov Africa Togo, l'invitant à confirmer son
> numéro + code PIN sur un portail. Il transmet l'email brut sans cliquer. **Mission :**
> analyser le courriel et retrouver **8 artefacts**. Flag = `NCTF{1_2_3_4_5_6_7_8}`.

## Méthode
Tout se lit dans les **en-têtes** (`Received`, `Authentication-Results`, `From`) et le
**corps HTML** (lien du bouton). Rien à deviner, rien d'externe.

```bash
python3 -c "import email;m=email.message_from_file(open('remboursement_flooz.eml'));\
print('\n'.join('%s: %s'%(k,' '.join(v.split())) for k,v in m.items() \
if k in ('From','Received','Authentication-Results')))"
# liens du corps :
python3 -c "import email,re;m=email.message_from_file(open('remboursement_flooz.eml'));\
[print(a) for p in m.walk() if p.get_content_type()=='text/html' \
for a in re.findall(r'href=[\"\x27]?(https?://[^\"\x27 >]+)',p.get_payload(decode=True).decode())]"
```

## Les 8 artefacts

| # | Question | Réponse | Source |
|---|---|---|---|
| 1 | Email expéditeur réel | `service-flooz@moov-africa.tg` | `From:` |
| 2 | IP publique réelle (vers 1er relais) | `102.67.41.83` | `Received: from vps-8471.hostzone.net (102.67.41.83)` |
| 3 | SPF au MX final `mx.digitogo.tg` | `fail` | `Authentication-Results: mx.digitogo.tg; spf=fail (sender IP is 102.67.41.83)` |
| 4 | DKIM au MX final | `none` | même ligne : `dkim=none` |
| 5 | Nom d'hôte réel émetteur | `vps-8471.hostzone.net` | 1er `Received` externe |
| 6 | Domaine de hameçonnage (bouton) | `moov-flooz-remboursement.secure-pay.top` | `href` du bouton d'action (HTML) |
| 7 | Tactique MITRE ATT&CK (phishing) | `TA0001` (Initial Access) | hameçonnage → tactique Initial Access |
| 8 | Secondes entre 1er et 2e relais | `1` | `09:17:33` → `09:17:34` (chaîne `Received`) |

### Chaîne Received (du + ancien au + récent)
```
vps-8471.hostzone.net (102.67.41.83)  -> mail-gw.digitogo.tg   09:17:33   (1er relais)
smtp-relay.moov-africa.tg [41.207..]  -> mail-gw.digitogo.tg   09:17:34   (2e relais, inséré)
mail-gw.digitogo.tg (10.0.1.5)        -> mx.digitogo.tg        09:17:35
```
Q8 = 34 − 33 = **1 s**.

## Indicateurs de compromission (pourquoi c'est du phishing)
- **IP réelle** = un VPS random `102.67.41.83` (hostzone.net), pas Moov.
- **SPF=fail / DKIM=none / DMARC=fail** au MX final → expéditeur **usurpé**.
- **Lien piégé** : domaine sosie `secure-pay.top` (sous-domaine `moov-flooz-remboursement`).
- Faux `Received` de `smtp-relay.moov-africa.tg` inséré pour paraître légitime.

## Flag
`NCTF{service-flooz@moov-africa.tg_102.67.41.83_fail_none_vps-8471.hostzone.net_moov-flooz-remboursement.secure-pay.top_TA0001_1}`

### Variantes si refusé
- #6 : `secure-pay.top` (domaine racine) au lieu du FQDN complet.
- #7 : `T1566` (technique Phishing) au lieu de la tactique `TA0001`.
