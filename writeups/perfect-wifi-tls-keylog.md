# oxdefault--perfect (misc/forensics, 500) — WPA2 + keylog TLS exfiltré par DNS

## Challenge
**Catégorie :** misc (forensics réseau)  **Fichiers :** `capture.pcapng`, `wifi-psk.txt`
**Flag :** `NCTF{3ph3m3r4l_but__k3yl0g_1n_dns__pfs_d3f34t3d}`

> Un poste s'est connecté au portail interne via HTTPS pendant qu'une capture sans fil
> tournait. Le réseau Wi-Fi est connu (`wifi-psk.txt`), le reste est dans `capture.pcapng`.
> Le formulaire soumis contenait une valeur sensible : retrouvez-la.

`wifi-psk.txt` : SSID `OfficeWiFi`, PSK `C0ffee-Br34k-99` (WPA2-PSK / CCMP).

## Résolution (3 couches à décortiquer)

### 1) Déchiffrer le WiFi WPA2
La capture contient le handshake 4-way (4 EAPOL) + 38 trames data chiffrées CCMP.
```
airdecap-ng -e OfficeWiFi -p 'C0ffee-Br34k-99' capture.pcapng   # -> capture.pcapng-dec
```
→ 38/38 paquets WPA déchiffrés. Le trafic en clair = **DNS (20) + TLS (6)**, pas de HTTP :
le portail est bien en HTTPS, donc le formulaire est chiffré par TLS.

### 2) Le keylog TLS exfiltré par DNS (le vrai twist)
Les requêtes DNS sont suspectes :
```
0.434c49454e545f52414e444f4d20356136373266.exfil.telemetry-sync.net
1.3863616666363336336363383038653535633264.exfil.telemetry-sync.net
... (jusqu'à 8)
```
Chaque label hex, concaténé **dans l'ordre des index**, puis décodé en ASCII, donne :
```
CLIENT_RANDOM 5a672f8caff6363cc808e55c2db6a50fb1e4ae6789a9175dabaf93524a9cbe14 7f7432963a0b1928...fb8b7be27e0cad4b87f0a44b3e47a61092b5fa18
```
C'est exactement le **format SSLKEYLOGFILE** (`CLIENT_RANDOM <client_random> <master_secret>`).
Un implant exfiltrait la clé de session TLS octet par octet via DNS.

### 3) Déchiffrer le TLS et lire le formulaire
```
# keys.log contient la ligne CLIENT_RANDOM ...
tshark -r capture.pcapng-dec -o tls.keylog_file:keys.log -Y http.request \
       -T fields -e http.file_data
```
Le POST `/portal/submit` (application/x-www-form-urlencoded) révèle :
```
action=submit & user=operator &
note=maintenance window approved\nNCTF{3ph3m3r4l_but__k3yl0g_1n_dns__pfs_d3f34t3d}
```

Le suite de chiffrement était `0xc02f` = ECDHE_RSA_AES128_GCM → **PFS**. Impossible à casser
par la clé privée serveur... sauf que le **master secret lui-même a fuité par DNS**.

## Leçon (pour le jury)
> La *perfect forward secrecy* ne protège une capture que si les **clés de session restent
> secrètes**. Ici un implant recopiait la clé TLS dans des requêtes DNS : en déchiffrant
> d'abord le WiFi (PSK connu), on récupère cette clé et on lit le HTTPS en clair. Surveiller
> les **exfiltrations DNS** (sous-domaines hex anormaux) est essentiel.

## Outils
`airdecap-ng` (WPA2) + `tshark -o tls.keylog_file` (TLS). 100 % offline.
