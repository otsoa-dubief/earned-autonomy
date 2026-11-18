# Paquet de données (PLAN_SUITE T50, 18/11/2026)

Rien n'est envoyé à cette étape : brouillon Zenodo en T51, publication en T52 (accord d'Otsoa pour les deux).

- Construit par `outils/construire_paquet_donnees.py` dans `~/dev/autonomie-meritee-archives/paquet_donnees_2026-11-18/` ; copie vérifiée sur le disque T9 (`T9/autonomie-meritee/paquet_donnees_2026-11-18/`, `shasum -c` : tout OK).
- `earned_autonomy_data_2026-11-18.zip` : 928 873 781 octets, SHA-256 `10cc6719…7a3f6a` ; 68 990 fichiers, chacun relu dans l'archive et comparé au manifeste des verdicts (`904aa8d3…f88d`) : 0 écart ; chemins sous `experience/`. Durée : 74 s.
- Fichiers à déposer : le zip, `DATA_README.md`, `manifeste_verdicts.txt`, `LICENSE-TEXT`, `THIRD_PARTY_NOTICES`, `SHA256SUMS.txt` (6 fichiers, sous la limite de 100).
- Limite de Zenodo lue en ligne le 18/11 : 50 Go et 100 fichiers par enregistrement (help.zenodo.org/docs/deposit/create-new-upload/ ; about.zenodo.org/policies/). Le paquet fait 0,93 Go.
- Recherche par motif sur les 68 990 fichiers (noms de fichiers et décomptes seulement, aucun contenu affiché) : 0 pour le nom de la société, le nom commercial, l'adresse de l'auteur, `sk-ant-`, `ANTHROPIC_API_KEY=`, `scelle`, `donnees/` ; 1 803 fichiers avec `@gmail.com`, soit 24 adresses distinctes, toutes présentes dans les données des bancs (utilisateurs fictifs) ; 5 601 fichiers avec `/Users/`, tous sur le seul préfixe `/Users/Otsoa/dev/autonomie-meritee`.
- Les fichiers ne sont pas modifiés (ils gardent les empreintes du manifeste) ; d'où les chemins locaux laissés tels quels, signalés dans `DATA_README.md`.
