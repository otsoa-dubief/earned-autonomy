# Inventaire des dépôts et plan de levée des embargos (PLAN_SUITE T42, 17/11/2026)

États lus le 17/11/2026 à 17:55 UTC par l'API d'OSF (`api.osf.io/v2/registrations/<id>/`), depuis la session d'Otsoa dans le navigateur d'Orca ; fichiers archivés lus par `…/files/osfstorage/`. Rien n'a été recopié d'une fiche.

| Dépôt | Type | Enregistré (UTC) | État | Fin d'embargo | Fichiers archivés (SHA-256) |
|---|---|---|---|---|---|
| OSF 7ju3c (antériorité) | Open-Ended | 2026-11-05 10:52:04 | privé, sous embargo | 2030-11-04 | depot_osf_2026-11-05.zip (77c7a11e…) |
| OSF vycge (préenregistrement) | OSF Preregistration | 2026-11-10 05:00:45 | privé, sous embargo | 2030-11-04 | depot_osf_2026-11-05.zip (77c7a11e…), depot_osf_2026-11-09.zip (4e32ba98…) |
| OSF cusv6 (gel des verdicts) | Open-Ended | 2026-11-14 08:17:47 | privé, sous embargo | 2030-11-04 | depot_osf_gel_verdicts_2026-11-14.zip (10c40d40…, version d'u26kr), depot_osf_gel_verdicts_final_2026-11-14.zip (f80ceb0e…), depot_osf_2026-11-05.zip, depot_osf_2026-11-09.zip |
| OSF u26kr | Open-Ended | 2026-11-14 06:44:26 | **retiré** (withdrawn) | – | – (seule une page de retrait reste publique) |
| Zenodo 10.5281/zenodo.24321214 (résultats) | Dataset | 2026-11-17 17:49:13 | fiche publique, fichiers sous embargo | 2030-11-04 | earned_autonomy_results_2026-11-17.zip (7e8f8a7d…) |

Remarque : un enregistrement OSF d'un projet archive tous les fichiers du projet présents à ce moment. cusv6 contient donc aussi le premier zip du gel (celui d'u26kr, avec des chevrons dans le résumé) ; c'est déclaré dans sa fiche et sans conséquence.

## Contrôle des paquets (17/11)

Les quatre zips archivés sur OSF sont identiques à leurs copies locales (mêmes SHA-256). Recherche par motif sur leur contenu décompressé : aucune vraie clé (motif `sk-ant-api…` : 0), aucun dossier `donnees/`, aucun fichier `.env` ni « scelle ». Les correspondances du premier filtre sont des noms de scripts (`banc/pilote_etape1.py`…), des sorties du pilote sur les tâches de développement (`simulation/rejeu/sorties_pilote`, déposées sciemment) et de fausses clés de test (`sk-ant-FAUSSE-CLE-DE-TEST-123456`). Aucune adresse ou donnée de tiers. Le paquet Zenodo a été contrôlé avant publication (`revues/2026-11-17_audit_brouillon_zenodo.md`).

## Ce qui devient public à chaque levée

- **7ju3c** : le résumé, la fiche et le zip d'antériorité (règle, plan en projet, journal, simulation, banc, rapports au 05/11).
- **vycge** : le formulaire de préenregistrement et le zip du gel (plan figé, code du banc et du moteur, simulations, rapports), plus le zip d'antériorité.
- **cusv6** : le manifeste du gel des verdicts, le plan du gel, la commande exacte du rejeu final, et les zips archivés ci-dessus.
- **Zenodo** : les fichiers du rejeu final, les analyses exploratoires, le journal du tirage (la fiche et sa description sont déjà publiques).
- Le **projet OSF bd4g5** lui-même reste privé tant qu'on ne le rend pas public séparément (question à trancher en T43 avec Q7).

## Gestes exacts, le jour J (T43, accord d'Otsoa ; irréversible)

1. Relire les pages d'aide d'OSF sur la levée d'embargo le jour même.
2. Pour chaque enregistrement choisi (Q7), sur sa page OSF, connecté : menu de l'enregistrement → « End embargo early » (ou équivalent) → confirmer. OSF envoie un courriel d'approbation à l'administrateur (Otsoa) : approuver. La levée prend effet après approbation (jusqu'à 48 h si non approuvée).
3. Lire l'état par l'API : `public: true`, `embargoed: false` ; ouvrir la page en fenêtre privée.
4. Zenodo : « Edit » → fichiers en « Public », embargo décoché, retirer de la description les mentions de l'embargo, ajouter le lien vers l'article → « Publish » ; vérifier le téléchargement anonyme et l'empreinte.
5. OSF : ajouter le DOI Zenodo comme ressource « Data » de vycge ; dans Zenodo, remplacer les adresses OSF par les DOI OSF (attribués à la levée).
6. Noter dates et états dans ce fichier et dans `SUIVI.md`.
