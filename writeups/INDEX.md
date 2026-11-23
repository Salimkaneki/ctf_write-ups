# INDEX — NCTF26 finale (équipe Hawk Eye)

> **Point d'entrée unique.** Une ligne par challenge → la **fiche canonique** à lire, le **solveur**, le **flag**, le **statut**.
> En cas de doublon, lire **seulement** la fiche de la colonne « Fiche ». Les fichiers redondants sont listés en bas (§ Doublons).
> Mis à jour : 2026-11-20.

## Légende
✅ résolu & write-up OK · 🟡 flag proposé à confirmer · 🧰 exploit prêt (instance à relancer) · ⏸ en cours/bloqué · ⚠️ attention (leurre)

---

## CLOUD
| Challenge | Statut | Flag | Fiche | Solveur |
|---|---|---|---|---|
| série `*-prefix` (×9) | ✅ | voir fiche | `cloud-prefix-series.md` | `solve_prefix.py` |
| artifacts-imds | ✅ | `NCTF{8780ec8e1de2dbc00e5dec33}` | `imds-series.md` (+`artifacts-imds.md` détail) | `solve_imds.py` |
| billing-imds | ✅ | `NCTF{6160286625f026849a85dc5e}` | `imds-series.md` | `solve_imds.py` |
| **cdn-imds** ⚡first blood | ✅ | `NCTF{d7265367bf2f3a4cd1c7d318}` | `imds-series.md` | `solve_imds.py` |
| backup-imds | ✅ | `NCTF{d8ef5a755ecd3fc83fb4b23b}` | `backup-imds-oidc-cloud.md` | — |
| backup-oidc | ✅ | `NCTF{dea010e84499df6e317ad60a}` | `backup-imds-oidc-cloud.md` | — |
| spiffe-mtls-ghost (187) | ✅ | `NCTF{984c1274da61f760a5b29dea}` | `spiffe-mtls-ghost.md` | `challenges/spiffe-ghost/exploit.py` |
| artifacts-envexec / -presign | ⏸ | — | `artifacts-envexec-presign-WIP.md` | — |

## CRYPTO
| Challenge | Statut | Flag | Fiche | Solveur |
|---|---|---|---|---|
| fast-enough (509) | ✅ | `NCTF{aa2eba38db8805c1ba58305c}` | `fast-enough-crypto.md` | `challenges/fast-enough/solve_fast_enough.py` |
| yeye | ✅ | `NCTF{ae0f02cfa7e7024142f1f257}` | `yeye.md` | `solve_yeye.py` |
| commit-bias | ✅ | `NCTF{c0mmit_r3v34l_but_th3_dr4ws_w3re_l1n34rly_l1nk3d}` | `commit-bias.md` | `challenges/commit-bias/solve_commit_bias.py` |
| twister-tell | ✅ | `NCTF{mt19937_untempered_then_the_future_is_yours}` | `twister-tell.md` | `challenges/twister-tell/solve_twister.py` |
| enye | ✅ | `NCTF{34f210d4836dae5e0fa1b9bb}` | `enye.md` | `solve_enye.py` |
| agbale | ✅ | `NCTF{ca163ab8817d9f7ee27990c1}` | `agbale.md` | `solve_agbale.py` |
| sokode-crypto (500) | ✅ | `NCTF{f1a9537c67a9315917205968e9493ad0}` | `sokode-crypto.md` | `solve_sokode.py` |
| atike | ⏸ (hint) | — | — | `solve_atike.py` / `solve_atike_forge.py` |

## REVERSE
| Challenge | Statut | Flag | Fiche | Solveur |
|---|---|---|---|---|
| crc-forge | ✅ | `NCTF{crc32_le4ks_ev3ry_byt3}` | `crc-forge.md` | `challenges/crc-forge/solve_crc_forge.py` |
| pyc-ghost | ✅ | `NCTF{marsh4l_unp1ckl3d_th3_c0de}` | `pyc-ghost-reverse.md` | — |
| ebpf-verifier-mirage (275) | ✅ | `NCTF{77ad08bc7abee9a3de785d69}` | `ebpf-verifier-mirage.md` | `ebpf_client.py` |

## WEB
| Challenge | Statut | Flag | Fiche | Solveur |
|---|---|---|---|---|
| série `boazak--<ville>` (×9) | ✅ | voir fiche | `boazak-web-series.md` | — |
| boazak--akloa-rendus (SSRF) | ✅ | `NCTF{a9692000faea8ec0a035939e}` | `akloa-rendus.md` | — |
| boazak--ando-rapports | ✅ | `NCTF{91fe189a8a46192487746070}` | `boazak--ando-rapports.md` | — |
| bridged-deser | ✅ | `NCTF{53229fb635cde50c21761717}` | `bridged-deser.md` | — |
| boazak--aneho (hard) | ⏸ | — | `boazak--aneho-PROGRES.md` | — |
| boazak--amlame (300, 0 solve) | ⏸ | — | `amlame-PROGRES.md` | — |
| hackusman--tablenest (hard) | ⏸ | — | `tablenest-PROGRES.md` | — |

## FORENSICS
| Challenge | Statut | Flag | Fiche | Solveur |
|---|---|---|---|---|
| flooz-piège (500) | ✅ | `NCTF{service-flooz@…_TA0001_1}` | `flooz-piege.md` | — |
| flux-obscur | ✅ | `NCTF{…_SOC-7734-FLUX}` (le **vrai**) | `flux-obscur.md` | — |
| perfect (wifi/TLS keylog) | ✅ | `NCTF{3ph3m3r4l_but__k3yl0g_1n_dns__pfs_d3f34t3d}` | `perfect-wifi-tls-keylog.md` | — |

## OSINT
| Challenge | Statut | Flag | Fiche | Solveur |
|---|---|---|---|---|
| alerte-uvci (154) | 🟡 | `NCTF{Sensitive2025_MVP_92_86_149_Telegram_DarkForums}` (Q1/Q7 à confirmer) | `alerte-uvci.md` | — |

---

## ⚠️ Doublons à ranger (même challenge, 2+ fichiers)

| Challenge | ✅ Garder (canonique) | 🗑️ Redondant | État |
|---|---|---|---|
| fast-enough | `fast-enough-crypto.md` | `fast-enough.md` | ✔️ **rangé** dans `_doublons/` |
| pyc-ghost | `pyc-ghost-reverse.md` | `pyc-ghost.md` | ✔️ **rangé** dans `_doublons/` |
| akloa-rendus | `akloa-rendus.md` | `boazak--akloa-rendus.md` | à ranger (fichier coéquipier → accord avant de déplacer) |
| backup cloud | `backup-imds-oidc-cloud.md` | `backup-imds.md`, `backup-oidc.md` | à ranger (coéquipier) |
| **flux-obscur** | `flux-obscur.md` | **`flux-obscur-forensics.md`** | ⚠️ **le `-forensics` contient le flag LEURRE** (`…CLASSIFIED`, CVE-2021-44228) — **NE PAS soumettre** ; à ranger (coéquipier) |

> `_doublons/` : dossier d'archive (rien n'est supprimé — pas de git ici). Mes propres doublons y sont déjà.
> Les fichiers des coéquipiers ne sont **pas** déplacés sans leur accord ; ils sont juste signalés ici.

### Fichiers « récap de série » (à GARDER — ce ne sont pas des doublons)
`cloud-prefix-series.md`, `boazak-web-series.md`, `imds-series.md`, `offline-crypto-prng-trio.md` —
chacun résume plusieurs challenges ; utiles pour le jury. Les fiches individuelles restent la référence détaillée.

### Fichiers de pilotage
`PROCESSES.md` (méthode par flag, pour défendre la soumission) · `RESULTATS-SESSION.md` (journal) · `INDEX.md` (ce fichier) · `../README.md` (explication « grand public » pour le jury).
