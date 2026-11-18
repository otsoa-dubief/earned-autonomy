# Anchors of the commits cited in the registrations (PLAN_SUITE T48, 17/11/2026)

The working repository is not published (its history contains confidential files). For each commit cited on OSF, this table gives the git hash of each public folder or file at that commit. Git hashes depend only on content, so anyone can recompute them on the published snapshot (`git rev-parse HEAD:<path>` in the published repository, or `git hash-object` for a file) and check that the published code is the frozen one. A folder that changed after the cited commit has a different hash; for those, the cited version is not in the snapshot, and the comparison column says so.

| commit | role | path | hash at that commit | same in the published snapshot? |
|---|---|---|---|---|
| e82fb54 | priority record 7ju3c (package built from this commit) | `banc` | `3e6091167b26732b9596a51325f20dd8bb969a17` | no (changed later) |
| e82fb54 | priority record 7ju3c (package built from this commit) | `simulation/tests` | `f4e8fee2f2415c96a0b362ae8b310c8e4dbfdf6d` | yes |
| e82fb54 | priority record 7ju3c (package built from this commit) | `REGLE.md` | `fc83105dd1614472e5c24b7f9b9f2f8a73c69d8f` | no (changed later) |
| e82fb54 | priority record 7ju3c (package built from this commit) | `PLAN_EXPERIENCE.md` | `39c765f8e2a7bc77bf2e1ac91bfb1f4d169f475d` | no (changed later) |
| e82fb54 | priority record 7ju3c (package built from this commit) | `JOURNAL_CHANGEMENTS.md` | `5da2ea5d74319f4045e0ed581d88132add23fadd` | no (changed later) |
| a8eb1aae | freeze tag gel-2026-11-09 (preregistration vycge) | `banc` | `bf7c6ba73460016d0942a9346e0f5c4204cfd6f7` | yes |
| a8eb1aae | freeze tag gel-2026-11-09 (preregistration vycge) | `gel` | `2173537fa1277b0b14126d05800bee0ad1757e33` | yes |
| a8eb1aae | freeze tag gel-2026-11-09 (preregistration vycge) | `simulation/rejeu` | `dcf6c17f5a3435512a2754672945497cac9d1cfd` | yes |
| a8eb1aae | freeze tag gel-2026-11-09 (preregistration vycge) | `simulation/tests` | `f4e8fee2f2415c96a0b362ae8b310c8e4dbfdf6d` | yes |
| a8eb1aae | freeze tag gel-2026-11-09 (preregistration vycge) | `REGLE.md` | `82d500e9c224913e0853609b3f8216c5ac7dfd98` | yes |
| a8eb1aae | freeze tag gel-2026-11-09 (preregistration vycge) | `PLAN_EXPERIENCE.md` | `3e3606b5e07190fb58fdc4b74e5a228a015c8d06` | yes |
| a8eb1aae | freeze tag gel-2026-11-09 (preregistration vycge) | `JOURNAL_CHANGEMENTS.md` | `b51f715d0c4b65a91855f253534cdd0c68c9b1bf` | no (changed later) |
| 7e951f2 | aborted first freeze (D0) | `banc` | `bf7c6ba73460016d0942a9346e0f5c4204cfd6f7` | yes |
| 7e951f2 | aborted first freeze (D0) | `gel` | `fcb10710ccd5e0e6e52c3ee28aabbcb25533fdf5` | no (changed later) |
| 7e951f2 | aborted first freeze (D0) | `simulation/rejeu` | `c05133f05a1d82f0b6a1e52b9d4b689f17c658f4` | no (changed later) |
| 7e951f2 | aborted first freeze (D0) | `simulation/tests` | `f4e8fee2f2415c96a0b362ae8b310c8e4dbfdf6d` | yes |
| 7e951f2 | aborted first freeze (D0) | `REGLE.md` | `82d500e9c224913e0853609b3f8216c5ac7dfd98` | yes |
| 7e951f2 | aborted first freeze (D0) | `PLAN_EXPERIENCE.md` | `3e3606b5e07190fb58fdc4b74e5a228a015c8d06` | yes |
| 7e951f2 | aborted first freeze (D0) | `JOURNAL_CHANGEMENTS.md` | `74cc729def7a6a89194022c8c9db3bb1be0d38ea` | no (changed later) |
| ee0df60 | draw done; first final-replay run | `banc` | `bf7c6ba73460016d0942a9346e0f5c4204cfd6f7` | yes |
| ee0df60 | draw done; first final-replay run | `gel` | `2173537fa1277b0b14126d05800bee0ad1757e33` | yes |
| ee0df60 | draw done; first final-replay run | `simulation/rejeu` | `dcf6c17f5a3435512a2754672945497cac9d1cfd` | yes |
| ee0df60 | draw done; first final-replay run | `simulation/tests` | `f4e8fee2f2415c96a0b362ae8b310c8e4dbfdf6d` | yes |
| ee0df60 | draw done; first final-replay run | `REGLE.md` | `82d500e9c224913e0853609b3f8216c5ac7dfd98` | yes |
| ee0df60 | draw done; first final-replay run | `PLAN_EXPERIENCE.md` | `3e3606b5e07190fb58fdc4b74e5a228a015c8d06` | yes |
| ee0df60 | draw done; first final-replay run | `JOURNAL_CHANGEMENTS.md` | `9486b0fdf5b21557bc9bee013354beb5350b2b59` | no (changed later) |
| 1a5b4c3 | failure and fix declared; second final-replay run | `banc` | `bf7c6ba73460016d0942a9346e0f5c4204cfd6f7` | yes |
| 1a5b4c3 | failure and fix declared; second final-replay run | `gel` | `2173537fa1277b0b14126d05800bee0ad1757e33` | yes |
| 1a5b4c3 | failure and fix declared; second final-replay run | `simulation/rejeu` | `dcf6c17f5a3435512a2754672945497cac9d1cfd` | yes |
| 1a5b4c3 | failure and fix declared; second final-replay run | `simulation/tests` | `f4e8fee2f2415c96a0b362ae8b310c8e4dbfdf6d` | yes |
| 1a5b4c3 | failure and fix declared; second final-replay run | `REGLE.md` | `82d500e9c224913e0853609b3f8216c5ac7dfd98` | yes |
| 1a5b4c3 | failure and fix declared; second final-replay run | `PLAN_EXPERIENCE.md` | `3e3606b5e07190fb58fdc4b74e5a228a015c8d06` | yes |
| 1a5b4c3 | failure and fix declared; second final-replay run | `JOURNAL_CHANGEMENTS.md` | `cf5bba4a10eb21c21975037b70f2991505ab0787` | no (changed later) |

## Full history, kept encrypted

The complete working history (all branches and tags, `git bundle --all`, 17 November 2026) is kept by the author, encrypted (AES-256, OpenSSL, PBKDF2). It can be opened for a reviewer who asks. SHA-256 of the bundle before encryption: `4a9a675fc5af5e34f33d91b35f5a751b4dea4817609f0f7327ed3f30c145084c`; of the encrypted file: `326342d95da0a9dc2489e17629dce4c1108063b1b63b72cb259fb7366618c65a`.

## Withheld review files

Four review files dated 4 November 2026 are not in this snapshot: they concern the earlier, separate field study and quote its confidential figures. Their git blob hashes at the freeze commit (`git ls-tree gel-2026-11-09 revues/`), unchanged since the first commit:

| file | git blob |
|---|---|
| `revues/dossier_relecteur_2026-11-04.md` | `1cf74c66c70335d85a18862787f03cbc6b161786` |
| `revues/note_terrain_2026-11.md` | `0e6a5a352698e0c2bbee89cddc2cb6f7076d704a` |
| `revues/plan_2026-11-04.md` | `4557802e2bc5ce3a1e46ce4b77a5f785e2fb9245` |
| `revues/plan_2026-11-04_verification.md` | `8d8f250f04132f62da9268f5bb924decd637f5f3` |

Because these files are withheld, the hash of the whole `revues/` folder quoted in the OSF READMEs cannot be recomputed on this snapshot; it can be checked on the full history, kept encrypted by the author.
