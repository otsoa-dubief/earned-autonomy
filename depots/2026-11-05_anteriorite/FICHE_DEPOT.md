# Dépôt d'antériorité sur OSF, 5 novembre 2026

Décision d'Otsoa (QCM du 05/11, fin de matinée) : un premier dépôt sous embargo, avec les fichiers publiables et les empreintes du reste. Ce n'est pas le préenregistrement : le plan figé sera déposé à part (gel visé le 18/11).

## Résultat

- **Soumis le 05/11/2026 à 10 h 52 UTC (11 h 52 à Paris)** : https://osf.io/7ju3c/ (modèle Open-Ended Registration).
- État lu par l'API d'OSF juste après : privé, `embargo_end_date` 2030-11-04, `pending_embargo_approval` vrai (courriel d'approbation à Otsoa ; sans action, approbation automatique au bout de 48 heures), archivage terminé.
- Fichier archivé : identifiant OSF `6aec5f29a9238a8535ca360c`, SHA-256 `77c7a11efde14855462b8f7a0026b88155e39697b70f8c4389fde2591aebce73`, vérifié sur le serveur avant la soumission.
- Brouillon et fichier préparés par Claude dans le navigateur d'Orca ; fichier glissé par Otsoa (le navigateur tourne sur son MacBook Air) ; soumission par Claude après le feu vert d'Otsoa.

## Le paquet

- Fichier : `depot_osf_2026-11-05.zip` (6 681 477 octets, hors git). Il se refait avec `python3 depots/construire_depot.py --commit e82fb54ff24ddedba990c8d94d2ef23dbbe722f4 --dossier depots/2026-11-05_anteriorite`.
- SHA-256 : `77c7a11efde14855462b8f7a0026b88155e39697b70f8c4389fde2591aebce73`.
- *Note du 09/11 (audit avant le gel, O2)* : le zip déposé ne se refait pas octet pour octet. Il a été construit avant que le script fixe les dates et l'ordre des fichiers, et ses fichiers générés portaient la date de construction. L'objet reproductible est le manifeste : `contenu/MANIFEST_SHA256.txt` et `contenu/README_DEPOT.md` se refont à l'identique depuis le commit (test `depots/tests/`). Le SHA-256 du zip se note tel que déposé (`77c7a11e…`). Depuis le 09/11, une reconstruction donne un zip stable, qui n'est pas celui du dépôt : `e44f1985…` construit à l'heure de Paris (Europe/Paris), puis, depuis que le zip est écrit en UTC (contre-vérification de l'audit), `f408a788ab586cbd7103b3dabc65b67e8262e1f01842dd71001b8221fd64549d`, quel que soit le fuseau de la machine.
- Les versions précédentes ne valent plus : `166925aa…` (sans licence), puis `3c10a187…` (sans les mentions des bancs tiers, et avec un chemin de session dans une note).
- Extrait du commit `e82fb54ff24ddedba990c8d94d2ef23dbbe722f4` (arbre `64de79b0757db720414a6d79d5241006a070a117`).
- Contenu :
  - `REGLE.md`, `PLAN_EXPERIENCE.md` (projet), `JOURNAL_CHANGEMENTS.md`, `simulation/`, `banc/`, `reports/` : 149 fichiers ;
  - `README_DEPOT.md` (en anglais, avec un résumé en français) ;
  - `LICENSE-CODE.txt` (licence MIT du code) ;
  - `THIRD_PARTY_NOTICES.txt` (licences MIT de τ-bench et de WorkBench, avec la liste des fichiers qui en sont tirés) ;
  - `MANIFEST_SHA256.txt`.
- Exclus, engagés seulement par leur empreinte git (liste dans le README) : `ATTENTE.md`, `CADRE.md`, `SUIVI.md`, `donnees/`, `lectures/`, `notes/`, `pilote/`, `research_notes/`, `revues/`.
- Contrôles faits avant d'emballer :
  - aucune clé (seulement le nom de la variable et la fausse clé des tests) ;
  - aucune mention de [company], de [company] ni de [company] dans les fichiers inclus (« Hermes » n'apparaît que comme outil d'agents) ;
  - les seules adresses électroniques sont les données fictives de WorkBench ;
  - les fichiers tirés des bancs gardent leur licence MIT d'origine, avec ses mentions ;
  - 534 tests passés sur le commit extrait.

## Les gestes sur OSF

1. Téléverser le zip dans *Files*, *OSF Storage* du projet https://osf.io/bd4g5/. Le navigateur d'Orca tourne sur le MacBook Air : c'est Otsoa qui glisse le fichier.
2. Registration : modèle **Open-Ended Registration**, brouillon `https://osf.io/registries/drafts/6aec5ccb4bdc69c98280bc38/`.
3. *Register*, **Enter registration into embargo**, date de fin le 4 novembre 2030 (4 ans au plus), puis *Submit*.
4. OSF peut envoyer un courriel d'approbation (48 heures) ; la date retenue reste celle de la soumission. Ne pas toucher aux fichiers du projet avant la fin de l'archivage.
5. Noter le lien de la registration dans `SUIVI.md`.

Rappels (aide d'OSF, vérifiée le 05/11) :
- une registration ne se modifie ni ne se supprime ; un retrait laisse visibles le titre, les auteurs et le DOI ;
- pendant l'embargo, la page affiche « introuvable » à tous les autres ;
- l'embargo se lève tout seul à la date choisie, ou plus tôt sur demande.

## Métadonnées (en anglais)

**Title** : Earned autonomy for AI agents: priority record of the working state (5 November 2026)

**Description** : Priority record of the working state of the project on 5 November 2026: rule specification and dated design decisions, draft (not frozen) experiment plan, exploratory simulation and its results, instrumentation code for the public benchmarks used (tau-bench 2.0, WorkBench). Not the preregistration: the frozen experiment plan will be registered separately, before any confirmatory data are collected.

**Licence** (choix d'Otsoa, QCM du 05/11) : CC-BY 4.0 dans le champ d'OSF ; code (`banc/`, `simulation/`) sous licence MIT ; fichiers tirés des bancs sous leur licence MIT d'origine. Elle ne pourra plus changer sur cette registration. Otsoa garde tous ses droits d'auteur : rien ne l'empêche d'en tirer un plugin Hermes sous la licence de son choix.

**Subject** : Physical Sciences and Mathematics / Computer Sciences / Artificial Intelligence and Robotics.

**Tags** : AI agents ; earned autonomy ; human oversight ; delegation ; AI safety ; agent evaluation ; error budget ; tau-bench ; WorkBench ; offline replay.

**Summary**

Priority record of the working state, on 5 November 2026, of the project "Earned autonomy for AI agents". The project asks which open protocol would let any organisation delegate progressively to an AI agent, per type of action, on verified evidence, with guarantees that can be checked and revoked. The attached archive (depot_osf_2026-11-05.zip, SHA-256 77c7a11efde14855462b8f7a0026b88155e39697b70f8c4389fde2591aebce73) contains the rule specification and dated design decisions, the draft (not frozen) experiment plan, the exploratory simulation (E1) and its results, the instrumentation code for the public benchmarks used (tau-bench 2.0, WorkBench), the change log after the pilot (development tasks only), and literature reports. It is extracted from git commit e82fb54ff24ddedba990c8d94d2ef23dbbe722f4; other files of the project repository are committed by their git hashes only (see README_DEPOT.md in the archive). Documents: CC BY 4.0; code: MIT; files derived from tau-bench 2.0 and WorkBench remain under their MIT licenses (THIRD_PARTY_NOTICES.txt). This is not the preregistration of the experiment: the frozen plan will be registered separately, before any confirmatory data are collected. Code and documents were written with the help of Claude (Anthropic), under the author's direction.

## Après le dépôt (05/11, vers 17 h 30)

- Embargo approuvé par Otsoa à 17 h 00 (historique du projet) : la registration affiche « embargoed until Mon Nov 04 2030 ».
- Deux liens de lecture du projet, créés par Otsoa à 17 h 03 (anonyme) et 17 h 04, supprimés à sa demande ; l'API d'OSF n'en liste plus aucun.
- Fiche du **projet** (osf.io/bd4g5, privé) remplie à sa demande, par l'API d'OSF depuis sa session : description de recherche (en anglais), les 10 mots-clés, les 3 disciplines et la licence CC-BY 4.0 (2026, Otsoa Dubief), comme sur la registration. La registration elle-même n'a pas été modifiée.
