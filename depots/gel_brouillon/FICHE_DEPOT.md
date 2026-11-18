# Dépôt du gel sur OSF (préparé le 09/11, gel fait le 09/11)

**Gel fait le 9 novembre 2026** (résultats ci-dessous). Reste le dépôt sur OSF, par Otsoa. Ordre : plan, 7, étape 8, points 1 à 5.

## Les gestes, dans l'ordre

1. Feu vert d'Otsoa après sa relecture finale (contrôle 4, pièce 9).
1 bis. **Statuts ouverts** (audit avant le gel, O1) : Otsoa tranche chaque « Proposé » du plan et de `REGLE.md` (Décidé tel quel, à modifier, à retirer) ; on retire « PROJET » de `PLAN_EXPERIENCE.md` (l. 1 et 3), de `REGLE.md` (l. 3) et le `statut` de `simulation/rejeu/config_rejeu.json` ; commit. Tout cela **avant** `--tirer-g0`.
2. `simulation/.venv/bin/python gel/manifeste.py --apercu` : seul empêchement attendu, « G0 n'est pas tirée ».
3. `gel/manifeste.py --tirer-g0`, puis écrire la valeur **à l'endroit prévu** : la ligne juste sous la puce « une graine maîtresse G0, tirée par `secrets.randbits(64)` au gel et écrite dans le plan figé » (5.5, point 4, vers la l. 504), au format exact `     - valeur tirée au gel : G0 = <valeur>`. Le contrôle refuse la valeur écrite ailleurs, deux fois ou fausse (test `gel/tests/test_manifeste.py`). Puis commit : **ce commit est celui que `GEL.json` nommera** (`GEL.json.commit` désigne le commit de G0, pas celui du manifeste).
4. `gel/manifeste.py --ecrire`, puis commit de `gel/`. Le manifeste compte alors **1 310 fichiers** : les 1 306 de l’aperçu du 09/11 au soir, plus `gel/GEL.json` et les **3** fichiers d’environnement (`simulation`, `tau2-bench`, `WorkBench`). *Corrigé le 09/11 au gel : la fiche en comptait 2 par erreur.* Si `paquets()` échoue en route, il laisse un `gel/environnements/` partiel : on le relance (rien n'est commité tant que l'étape ne finit pas).
5. `gel/manifeste.py --verifier` : code de sortie 0.
6. Étiquette git annotée sur le commit de `gel/`, par exemple `gel-<AAAA-MM-JJ>`. **Sauvegarde de l'étiquette** (rien n'est poussé) : `git bundle create ../autonomie-meritee_gel-<AAAA-MM-JJ>.bundle --all` hors du dépôt, puis copie sur un second support d'Otsoa ; noter le SHA-256 du bundle ici.
7. Paquet : `python3 depots/construire_depot.py --type gel --commit <sha> --etiquette <étiquette> --date "<d Month YYYY>" --dossier depots/<AAAA-MM-JJ>_gel`. Le script refuse un commit sans GEL.json ni manifeste, une étiquette qui ne désigne pas le commit, une G0 non tirée et toute entrée du dépôt ni incluse ni citée. Le zip se refait à l'identique (dates et ordre fixés, test `depots/tests/`).
8. Contrôles avant d'emballer, comme le 05/11 : aucune clé, aucune mention de [company], de [company] ni de [company] dans les fichiers inclus, licences des bancs tiers, tests passés sur le commit extrait. Tests du script : lancer `depots/tests` seul (`pytest depots/tests`), **pas** `pytest depots` : l'ancienne extraction de `depots/2026-11-05_anteriorite/contenu/`, ignorée par git, contient ses propres tests, qui échouent hors de leur dépôt (3 échecs).
9. OSF, projet https://osf.io/bd4g5/ : Otsoa glisse le zip dans *OSF Storage* ; registration ; embargo ; soumission après son feu vert.
10. Noter ici et dans `SUIVI.md` : le lien, **le SHA-256 du zip réellement déposé** (celui lu sur le serveur d'OSF avant la soumission, comme le 05/11), celui de `gel/MANIFESTE_SHA256.txt` et celui du bundle.

## Modèle de registration (décidé par Otsoa le 09/11)

- **Préenregistrement** : formulaire structuré complet, **OSF Preregistration**, avec le plan figé en pièce jointe. Réponses champ par champ : `FORMULAIRE_OSF_PREREG.md`.
- **Embargo** : le même que le 05/11, jusqu'au 04/11/2030, levable plus tôt.
- `presentation/` reste hors du dépôt. Les trois sorties archivées qui portent un chemin personnel sont déposées telles quelles.

## Métadonnées (en anglais)

**Title** : Earned autonomy for AI agents: preregistration of the frozen experiment plan (<d Month YYYY>)

**Description** : Preregistration of a confirmatory experiment on earned autonomy for AI agents: frozen plan, rule specification, replay engine and benchmark instrumentation, frozen at a git tag before any confirmatory data are collected. Builds on the priority record https://osf.io/7ju3c/ (5 November 2026).

**Licence** : CC-BY 4.0 (comme le 05/11) ; code sous MIT ; fichiers tirés des bancs sous leur licence MIT d'origine.

**Subject** : Physical Sciences and Mathematics / Computer Sciences / Artificial Intelligence and Robotics.

**Tags** : AI agents ; earned autonomy ; human oversight ; delegation ; AI safety ; agent evaluation ; error budget ; preregistration ; tau-bench ; WorkBench ; offline replay.

**Summary** : Preregistration, on <d Month YYYY>, of the confirmatory experiment of the project "Earned autonomy for AI agents". The project asks which open protocol would let any organisation delegate progressively to an AI agent, per type of action, on verified evidence, with guarantees that can be checked and revoked. The attached archive (<zip>, SHA-256 <sha zip>) is extracted from git commit <sha>, tag <étiquette>. It contains the frozen experiment plan, the rule and its dated decisions, the change log, the replay engine and simulations that compute the verdict, the benchmark instrumentation, the freeze manifest (gel/MANIFESTE_SHA256.txt, SHA-256 <sha manifeste>) and literature reports; the other files of the repository are committed by their git hashes only (README_DEPOT.md). Master seed G0 = <G0>. Documents: CC BY 4.0; code: MIT; files derived from tau-bench 2.0 and WorkBench remain under their MIT licenses. Code and documents were written with the help of Claude (Anthropic), under the author's direction.


## Résultats du gel (9 novembre 2026)

- G0 = **9879107140414210923**, tirée une seule fois et écrite dans le plan : commit `6c6dd66`.
- **Gel avorté** : un premier manifeste (commit `7e951f2`) et son étiquette locale, jamais sortis de la machine, sont abandonnés. Deux tests du périmètre vérifiaient l'état d'avant le gel (« G0 non tirée ») et échouaient depuis le tirage. Ils sont corrigés (`9fffe67`, `cb9cbce`), les sorties du gel avorté sont retirées (`6e89b45`) sans réécrire l'historique, et G0 est inchangée. Journal : ligne du 09/11, nuit.
- Gel : commit de base `cb9cbce` (c'est lui que nomme `GEL.json.commit`), manifeste au commit **`a8eb1aa`**, **1 310 fichiers** ; SHA-256 de `gel/MANIFESTE_SHA256.txt` : `88715a0d790cd5228b6a247b8e10b74d2c1c1ea022d47fbc9386949e263b9600`. `--verifier` : conforme. Suite complète au commit du gel : 1 128 réussis et 1 échec attendu, code de sortie 0.
- Étiquette annotée **`gel-2026-11-09`**, sur `a8eb1aae06d237ff094933f30d4a9ddf045d4898`.
- Bundle de sauvegarde : `ROOT_gel-2026-11-09.bundle` (17 173 219 octets), SHA-256 `5978946e7b3aec1c8d8e9cbabbc194b29d386a0f9fddd7e369adc9adb0a1db1a`. Il contient **tout** le dépôt, `donnees/` compris : à garder privé, à copier sur un second support d'Otsoa. Le bundle du gel avorté est mis de côté, pas supprimé : `ROOT_gel-2026-11-09_AVORTE-7e951f2.bundle`.
- Paquet : `depots/2026-11-09_gel/depot_osf_2026-11-09.zip` (16 280 478 octets, 420 fichiers extraits), SHA-256 **`4e32ba989c0f572242d1e52a9787d25a1f8129934a015b7527b6a1f663f6dcc6`**.
- Contrôles d'avant emballage : aucune clé, hors la fausse clé des tests `sk-ant-FAUSSE-CLE-DE-TEST-123456` (comme le 05/11) ; aucune mention de [company], [company], [company], [company] ni [company] ; `LICENSE-CODE.txt` et `THIRD_PARTY_NOTICES.txt` présents (licences MIT des bancs).
- **Contrôle du paquet par les tests** : **le test complet se fait sur le dépôt à l'étiquette** (ci-dessus : 1 128 réussis, 1 échec attendu). Lancés dans le paquet extrait, 1 029 tests passent, et les 54 échecs viennent tous de fichiers absents par construction : 46 de `pilote/` (engagé par son empreinte seulement) et 8 des bancs (7 fichiers de `externe/tau2-bench`, 1 `git rev-parse` dans `externe/tau2-bench`), qu'on obtient en clonant les bancs aux commits notés dans `GEL.json`. Aucun autre échec.
- **Dépôt OSF, 10/11/2026 à 05 h 00 UTC** : https://osf.io/vycge/ (OSF Preregistration, privée, embargo jusqu'au 04/11/2030, approuvée). Zip glissé dans *OSF Storage* du projet bd4g5 avant la soumission ; SHA-256 lu sur le serveur d'OSF avant la soumission : `4e32ba989c0f572242d1e52a9787d25a1f8129934a015b7527b6a1f663f6dcc6` (16 280 478 octets), identique au paquet ; relu dans l'archive de la registration après la soumission, identique. L'archive contient aussi le zip du 05/11 (`77c7a11e…`), présent dans le stockage du projet.
- Texte déposé : `depots/2026-11-09_gel/FORMULAIRE_OSF_DEPOSE.md` (copie exacte, lue sur le serveur ; 23 réponses identiques à la version finale). Le brouillon `FORMULAIRE_OSF_PREREG.md` a été corrigé avant la soumission, après trois relectures indépendantes contre le plan figé.
