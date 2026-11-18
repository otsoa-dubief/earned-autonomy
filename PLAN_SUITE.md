# Plan de la suite : du verdict à la publication

Écrit le 17/11/2026, après le verdict (étiquette R4) et l'audit des résultats.
Ce plan couvre tout ce qui reste à faire pour publier l'étude : corrections, article, relectures, dépôts, code ouvert, arXiv, diffusion.

Il est fait pour être exécuté par un agent, tâche après tâche. Une tâche vaut une à deux heures de travail au plus.

## 0. Règles permanentes de l'exécutant

Ces règles valent pour toutes les tâches. En cas de doute, l'exécutant s'arrête et demande à Otsoa.

**R1. Accès interdits.** Ne jamais ouvrir, lister en détail, ni citer :
- `donnees/` (surtout `donnees/[sealed file]`) ;
- `pilote/`, `data/`, `externe/` ;
- les traces de parties : dossiers `parties/`, `logs/`, `fiches/`, `lots/`, fichiers `actions*.csv` ;
- les `decisions.csv` de relecture ;
- `~/.config/autonomie-meritee/`.

Calculer l'empreinte SHA-256 d'un fichier n'est pas le lire : c'est permis. Un script d'analyse peut lire ces données s'il n'écrit que des agrégats (comptes, taux) et n'affiche aucune ligne brute ; l'exécutant ne lit que les sorties agrégées (voir la décision Q11).

**R2. Clé API.** Ne jamais lire, afficher ni copier la clé API. Ne jamais afficher la valeur d'un secret trouvé : donner seulement le fichier et le numéro de ligne.

**R3. Argent.** Aucun appel payant sans coût annoncé d'avance et accord d'Otsoa. Les relectures par agent passent par l'abonnement, jamais par la clé de l'expérience.

**R4. Git.** Commits avec l'auteur « Otsoa Dubief <recherche@autonomie-meritee.local> ». Jamais de `git push`. Jamais de réécriture d'historique. Un commit par tâche, avec le numéro de la tâche dans le message.

**R5. Code figé.** Ne rien modifier dans `simulation/`, `banc/`, `gel/`, ni dans `experience/rejeu_final/`, `experience/tirage/`, `experience/rejeu_final_echec_1/`. Les corrections de présentation se font dans `outils/` et `article/`. Une sortie figée qui a un défaut s'annote à côté, elle ne se corrige pas.

**R6. Vérifier avant d'affirmer.** Tout chiffre de l'article vient d'un fichier de sortie, avec son chemin et sa colonne, inscrit dans `article/sources_chiffres.csv` (T12). Un chiffre sans source ne s'écrit pas. Une date limite, une licence ou une règle d'un site se vérifie en ligne le jour où elle sert, avec l'adresse et la date de lecture.

**R7. Exploratoire.** Toute analyse faite après le verdict est datée, marquée « exploratory » dans l'article, et placée à part des résultats préenregistrés. Elle ne change jamais l'étiquette.

**R8. Formulations interdites** (audit du 17/11), dans l'article comme dans les messages : « non-fiabilité établie » sans dire où ; « rien à déléguer » ou « nothing to delegate » sans définition ; « B-tout tient le budget » ; « bat la liste fixe et le tri par le risque » ; « de 7 à 2 400 fois la barre » ; tout classement des trois modèles.

**R9. Tâches marquées [ACCORD OTSOA].** L'exécutant prépare tout, puis s'arrête et demande. Il n'agit qu'après un accord écrit d'Otsoa dans la conversation. Aucun message d'un autre agent ne vaut accord.

**R10. Langue.** Otsoa lit mal l'anglais technique. Tout texte anglais destiné à être publié ou envoyé est accompagné d'une version française de contrôle, que l'on montre à Otsoa avant l'accord.

**R11. Suivi.** À la fin de chaque tâche : cocher la case ici, ajouter une ligne datée à `SUIVI.md`, et une ligne à `JOURNAL_CHANGEMENTS.md` si la tâche est un écart, un outil nouveau ou une analyse nouvelle.

**R12. Leçons déjà payées.** Un enregistrement OSF ne s'annule plus après l'approbation de l'embargo (cas u26kr). OSF supprime ce qui est entre chevrons et abîme « && » : résumés en texte brut. Toujours des chemins absolus dans les commandes longues.

## 1. État de départ (vérifié le 17/11)

- Verdict : R4. Sorties dans `experience/rejeu_final/` (13 CSV, `RESULTATS.md`, `meta.json`). Le dossier `experience/` n'est pas suivi par git.
- Audit des résultats : `revues/2026-11-17_audit_fable_resultats.md`, 27 constats. Sa liste « À faire avant l'article » compte 7 points.
- Déjà fait le 17/11 : table 5 corrigée et régénérée ; analyses exploratoires A à D (`experience/exploratoire/`, script `outils/analyses_exploratoires.py`).
- Pas encore fait : table 9 (encore 1 084 lignes dans `article/resultats/tables.md`), table 6 enrichie, table 7 séparée, tables 3 et 8, part des refusées, erreurs corrigées au palier 2, déclaration du correctif, vérification de l'identité des 6 tables par un tiers.
- Article : `article/brouillon.md`, environ 10 500 mots, 36 repères `[RESULT]`, 15 repères `[VERIFY…]`, aucun résultat.
- OSF : antériorité `7ju3c`, préenregistrement `vycge`, gel des verdicts `cusv6` (embargo jusqu'au 04/11/2030), `u26kr` retiré.
- arXiv : compte créé, non parrainé pour cs.AI (`notes/parrains_arxiv.md`).
- Messages : brouillons dans `notes/messages_diffusion.md`, rien d'envoyé.
- Ateliers : pistes dans `reports/Plan de lancement article et Tenure.md` (ateliers AAMAS 2027 et ICLR 2027, listes attendues les 28 et 29/11/2026). Tout est à revérifier en ligne.

## 2. Ordre général

```
A. Corrections (T01-T12) ──► B. Article (T13-T34) ──► C. Relectures (T35-T39)
        │                                                     │
        └──► D. Dépôt OSF des résultats (T40-T42)             │
E. Code et données (T44-T51) ─────────────────────────────────┤
F. arXiv : parrain (T53-T54) ─────────────────────────────────┤
                                                              ▼
                                    JOUR J (T43, T52, T55-T57), puis G. Diffusion (T58-T64)
```

Le jour J, dans cet ordre : dépôt GitHub public, archive Zenodo publiée, levée des embargos OSF, soumission arXiv. **Ajout (17/11)** : le jour J comprend aussi l'ouverture des fichiers Zenodo 10.5281/zenodo.24321214 (voir `depots/2026-11-17_resultats/FICHE_DEPOT.md`). **Décision d'Otsoa (17/11)** : la prépublication se fait d'abord sur OSF Preprints (sans parrain), le jour J après la levée des embargos ; arXiv vient ensuite, quand un parrainage est obtenu. Tâche ajoutée : T43 bis. Les messages partent quand le numéro arXiv existe.

## 3. Tâches

### A. Corrections de présentation exigées par l'audit

- [x] **T01 — Empreintes des sorties finales.**
  - Objectif : fixer l'état des sorties avant tout travail, puisque `experience/` n'est pas dans git.
  - Entrées : `experience/rejeu_final/`, `experience/tirage/`, `experience/exploratoire/`, `experience/journal_rejeu_final.jsonl`, `experience/rejeu_final.log`, `experience/manifeste_verdicts.txt`, `outils/rejeu_final_correctif.py`.
  - Livrable : `experience/SHA256_sorties_finales.txt` (une ligne par fichier, plus l'empreinte du script de correctif).
  - Vérification : `shasum -a 256 -c` passe sans erreur ; le nombre de lignes égale le nombre de fichiers listés ; l'empreinte de `manifeste_verdicts.txt` commence par `904aa8d3`.
  - Dépendances : aucune.

- [x] **T02 — Identité des six tables des deux passages, vérifiée par un tiers.**
  - Objectif : répondre au constat 18 de l'audit. Un agent neuf compare les empreintes des 6 tables du premier passage (échoué) et du second.
  - Entrées : `experience/rejeu_final_echec_1_SHA256.txt`, les 6 fichiers de même nom dans `experience/rejeu_final/` (budget, charges, derive, ecart, garantie, retrait). Empreintes seulement : le contenu de `rejeu_final_echec_1/` n'est pas ouvert.
  - Livrable : `revues/2026-11-XX_identite_six_tables.md` (tableau : fichier, empreinte 1, empreinte 2, identique oui/non).
  - Vérification : 6 lignes, 6 « oui ». Sinon arrêt immédiat et alerte à Otsoa.
  - Dépendances : T01.

- [x] **T03 — Déclaration précise du correctif du rejeu final, et de `meta.json` muet.**
  - Objectif : écrire noir sur blanc ce que l'article devra dire (constat 18). Points obligatoires : (1) la commande lancée est un script d'enveloppe avec les mêmes arguments, pas « la même commande » ; (2) `meta.json` donne l'empreinte de `sorties.py` figé et ne dit rien du remplacement en mémoire ; (3) `resistance.csv` a une colonne de plus (`mode_scenario`) ; (4) le premier passage a tourné 4 614 s et aucune de ses sorties n'a été lue avant le second ; (5) seule la fonction `lignes_resistance` est remplacée, l'étiquette est calculée avant.
  - Entrées : `JOURNAL_CHANGEMENTS.md` (ligne du 17/11), `outils/rejeu_final_correctif.py`, `experience/rejeu_final/meta.json` (lecture seule), `experience/rejeu_final.log`, résultat de T02.
  - Livrable : `experience/NOTE_CORRECTIF_REJEU_FINAL.md` (français) et `article/morceaux/deviation_correctif_en.md` (paragraphe anglais). `meta.json` n'est pas modifié.
  - Vérification : les 5 points sont présents dans les deux textes ; chaque chiffre renvoie à un fichier ; `git status` montre `meta.json` inchangé (empreinte de T01).
  - Dépendances : T01, T02.

- [x] **T04 — Formulation de référence du verdict. [ACCORD OTSOA]**
  - Objectif : une seule page qui fixe comment on dit le résultat, partout. Elle reprend la phrase proposée par l'audit (français et anglais), les trois phrases qui suivent, la définition de « délégable » (critère de calibration, au taux médian), la marge 0,740 contre 0,693, le seuil ρ̂ ≤ 0,885 (ρ̂ mesuré 0,819), le fait que R4 ne compare pas les modèles, et la liste R8.
  - Entrées : audit du 17/11 (constats 2, 3, 4, 5, 17 ; sections « Ce qu'on peut affirmer », « Ce qu'on ne peut pas affirmer », « Formulation proposée »), `experience/rejeu_final/decision.csv`, `ecart.csv`.
  - Livrable : `article/FORMULATION_VERDICT.md`, plus une ligne datée dans `SUIVI.md` qui corrige la formule du 17/11 (« rien à déléguer : non-fiabilité établie »).
  - Vérification : chaque chiffre de la page se retrouve dans `ecart.csv` (914 écritures, 79 erreurs, 8,64 %, barre 0,757 %, borne basse 4,14 %) ; Otsoa a lu la version française et l'a acceptée (question Q1).
  - Dépendances : T01.

- [x] **T05 — Table 9 et alerte des tests de résistance.**
  - Objectif : corriger `outils/tables_article.py` pour que la table 9 ne garde que les lignes `type_suite == "bilan du mode"` (constat 25), et écrire le paragraphe sur l'alerte « oui » dans les 7 modes, avec sa cause (cellule fragile de l'aviation, 2 tâches porteuses ; constat 20).
  - Entrées : `outils/tables_article.py`, `experience/rejeu_final/resistance.csv`, `decision.csv`.
  - Livrable : `article/resultats/tables.md` régénéré ; `article/morceaux/alerte_resistance_en.md`.
  - Vérification : la table 9 a 28 lignes ; `tables.md` fait moins de 400 lignes ; le paragraphe donne « pire borne haute de 1,65 à 1,68 fois le budget (2,34 en retard10), 0 échec » et ces valeurs se relisent dans `resistance.csv`.
  - Dépendances : T01.

- [x] **T06 — Table 5 complète et figure du budget.**
  - Objectif : finir les défauts relevés le 14/11 (constat 26) : ajouter les 48 scénarios de changement de modèle (ou le dire dans le titre), afficher « – » au lieu de « 0,00 » quand le rapport n'est pas calculable, tracer un budget par niveau d'enjeu dans `fig_budget.png`, corriger la phrase « computes no new statistic ».
  - Entrées : `outils/tables_article.py`, `experience/rejeu_final/budget.csv`.
  - Livrable : table 5 et `article/resultats/fig_budget.png` régénérées.
  - Vérification : la somme des cellules donne 180 (51 jugées dont 6 non testables, 108 tenues sans épreuve, 21 sans objet), comme `decision.csv` ; 0 dépassement établi.
  - Dépendances : T05.

- [x] **T07 — Table 6 enrichie (écart de délégation).**
  - Objectif : ajouter les colonnes qui fondent « établi » et « jugeable » (constat 26) : taille effective à ρ = 1, borne basse, ρ̂, erreurs attendues à la barre, seuil 0,693. Ajouter une marque pour les 13 types sans aucune erreur observée (constat 5) et pour banque/Haiku ILL (2 écritures, constat 7).
  - Entrées : `experience/rejeu_final/ecart.csv`, `outils/tables_article.py`.
  - Livrable : table 6 régénérée dans `article/resultats/tables.md`.
  - Vérification : ligne WorkBench/Haiku ECR : n = 914, x = 79, n_eff = 81,6, borne basse 4,14 %, 0,740 ; décompte : 40 types avec données, 20 « au-dessus », 20 « indéterminés » dont 13 à zéro erreur.
  - Dépendances : T05.

- [x] **T08 — Table 6 bis : réserve entière, marquée descriptive.**
  - Objectif : publier à côté de la table principale la version « calibration et confirmation » (constat 4), avec la phrase : « avec deux fois le volume et les mêmes taux, trois configurations auraient eu un type délégable ». Dire qu'elle ne peut pas servir d'étiquette.
  - Entrées : `ecart.csv` (version « calibration et confirmation »), `experience/exploratoire/B_types_delegables_par_version.csv`.
  - Livrable : table 6 bis dans `tables.md` ; `article/morceaux/reserve_entiere_en.md`.
  - Vérification : 3 types délégables, tous à 0 erreur (0 sur 120, 0 sur 120, 0 sur 258) ; commerce/Haiku ECR : 31 erreurs sur 1 286.
  - Dépendances : T07.

- [x] **T09 — Table 7 séparée et libellé trompeur du point 2.**
  - Objectif : dans la table des charges, séparer la baisse due au palier 2 de celle due au palier 3 et marquer les types établis au-dessus de la barre (constat 17). Annoter, à la traduction, le libellé écrit en dur « les trois témoins battus » de `decision.csv` (constat 14) : c'est le texte du critère, pas un résultat.
  - Entrées : `charges.csv`, `volume.csv`, `decision.csv`, `outils/tables_article.py`.
  - Livrable : table 7 régénérée ; note sous la table de décision.
  - Vérification : charges hors lectures WorkBench 65,5 / 54,9 / 55,1 ; part au palier 2 de ECR 63 % / 81 % / 81 % ; la note dit « point 2 non jugé sous R4 ».
  - Dépendances : T05.

- [x] **T10 — Analyses exploratoires qui manquent : refusées, palier 2, ρ̂.**
  - Objectif : compléter `outils/analyses_exploratoires.py` avec (E) la part des écritures refusées parmi les erreurs confirmées, par type (constat 10) ; (F) le nombre d'erreurs exécutées puis corrigées au palier 2 pour 100 écritures, par configuration (constat 15) ; (G) un intervalle pour ρ̂ de WorkBench/Haiku, à comparer au seuil 0,885 (constat 2).
  - Entrées : le script existant, les fonctions du moteur en lecture. Le script ne sort que des agrégats (règle R1).
  - Livrable : `experience/exploratoire/E_…csv`, `F_…csv`, `G_…csv`, `RESUME.md` complété et daté.
  - Vérification : le script reproduit toujours la borne à ρ = 1 des 20 dépassements établis ; les totaux de E égalent les erreurs de `ecart.csv` ; l'étiquette n'est pas recalculée ; ligne ajoutée au journal des changements.
  - Dépendances : T01. Si (G) demande plus de deux heures, la sortir en tâche à part et le dire.

- [x] **T11 — Tables exploratoires pour l'article.**
  - Objectif : mettre en forme, en anglais, les analyses A à G : exclusions (dépassements 20 → 21), réserve entière, sensibilité aux fausses confirmations (table du constat 8, avec le 3 sur 10 à côté du 13 sur 15), croisement erreurs et réussite des tâches (64-82 % en WorkBench, 6-14 % en aviation et commerce, 0-2 % en banque), refusées, palier 2.
  - Entrées : `experience/exploratoire/*.csv`, `RESUME.md`.
  - Livrable : `article/resultats/tables_exploratoires.md`, chaque table titrée « Exploratory, dated … ».
  - Vérification : chaque table cite son CSV ; le type qui porte R4 affiche 63 % ; banque/Opus MSG affiche 0 %.
  - Dépendances : T10.

- [x] **T12 — Défauts mineurs de sortie et registre des chiffres.**
  - Objectif : (1) régler dans la mise en forme les défauts du constat 27 : libellé « tâches jouées » de la table de symétrie, bornes au-dessus de 1 de `garantie.csv` annotées, asymétrie de l'aviation (542 contre 1 166 écritures à enjeu fort), c* arrondi, « nan » remplacé par « – », libellés traduits. (2) Créer le registre des chiffres.
  - Entrées : `tables.md`, `symetrie.csv`, `garantie.csv`, `decision.csv`.
  - Livrable : `tables.md` final ; `article/sources_chiffres.csv` (colonnes : identifiant, valeur, unité, fichier, colonne ou ligne, préenregistré ou exploratoire).
  - Vérification : aucun « nan » dans `tables.md` ; le registre contient au moins tous les chiffres de `FORMULATION_VERDICT.md` et des constats 2 à 20 de l'audit.
  - Dépendances : T04 à T11.

### B. Article

- [x] **T13 — Plan de l'article court et choix du titre. [ACCORD OTSOA]**
  - Objectif : décider le message, le titre et la répartition entre corps (8 pages) et annexes. Le titre actuel promet une « garantie » ; l'audit du 14/11 (constat 23) demande « conditional guarantee » ou de retirer le mot. Le résultat principal devient l'écart de délégation.
  - Entrées : `article/brouillon.md`, `article/FORMULATION_VERDICT.md`, audits des 14/11 (section F) et 17/11.
  - Livrable : `article/PLAN_ARTICLE.md` : titre, message en 3 phrases, budget de pages par section, liste de ce qui part en annexe, version française de contrôle.
  - Vérification : le total fait 8 pages au plus hors références et annexes ; Otsoa a répondu aux questions Q2 et Q3.
  - Dépendances : T04, T12.

- [x] **T14 — Tables 3 et 8, règles secondaires.**
  - Objectif : produire les tables absentes de `tables.md` : table 3 (exclusions par configuration et par raison : 91 parties, messages vides), table 8 (scénarios annoncés et silencieux), résumé des épreuves, règles secondaires et règle de choix.
  - Entrées : `meta.json`, `derive.csv`, `retrait.csv`, `epreuves.csv`, `choix.csv`, `SUIVI.md`, `experience/exploratoire/A_parties_exclues.csv`.
  - Livrable : tables ajoutées à `tables.md` par `outils/tables_article.py`.
  - Vérification : table 3 : total 91, dont 77 pour banque/Haiku ; chaque table cite son fichier ; registre des chiffres mis à jour.
  - Dépendances : T12.

- [x] **T15 — Résultats 6.1 : collecte et instrument.**
  - Objectif : remplir les 10 repères `[RESULT]` de la section 6.1 : parties jouées, exclusions, coût réel (837,19 $ contre une estimation de 517 à 674 $, à déclarer), couverture (0,9868 ; banque 0,925), alertes (2 761 : 1 991 confirmées, 770 levées, par motif), tâches retirées (12) et oppositions, relecture à l'aveugle par vague, audit sans alerte (0 sur 21, borne haute d'environ 13 %), symétrie, réussite des tâches, tirage public.
  - Entrées : `SUIVI.md`, `JOURNAL_CHANGEMENTS.md`, `RESULTATS.md`, `meta.json`, `symetrie.csv`, `reussite_taches.csv`, `experience/tirage/impulsion.json`, `experience/audit_sans_alerte/audit_conclusion.txt`. Si un chiffre n'existe que dans un fichier d'un dossier de vague, demander avant d'ouvrir.
  - Livrable : section 6.1 de `article/brouillon.md`.
  - Vérification : plus aucun `[RESULT` entre les titres 6.1 et 6.2 ; chaque chiffre est au registre.
  - Dépendances : T13, T14.

- [x] **T16 — Résultats 6.2 et 6.3 : étiquette et sécurité.**
  - Objectif : écrire l'étiquette avec la formulation de T04, la table de décision, les mentions « fragile ». Pour le point 1 : « aucun dépassement établi ; le test ne pouvait presque rien établir (c* = 7,0) ; aucune cellule démontrée », avec les valeurs centrales (constat 16). Dire que H1 ne peut presque pas échouer par les données (audit du 14/11, constat 22).
  - Entrées : `decision.csv`, `budget.csv`, `retrait.csv`, tables 5 et figure 1.
  - Livrable : sections 6.2 et 6.3.
  - Vérification : la recherche des formules R8 ne donne rien ; « 51 », « 108 », « 21 », « 0,38 fois le budget » sont au registre.
  - Dépendances : T15.

- [x] **T17 — Résultats 6.4 : écart de délégation.**
  - Objectif : la section centrale. Taux et intervalles d'abord, rapports ensuite, par niveau d'enjeu, jamais de fourchette tous niveaux confondus (constat 7). Donner les 13 types sans erreur et l'asymétrie « au-dessus ou indéterminé » (constat 5). Présenter la banque à part avec ses cinq réserves dans la même phrase (constat 11). Écrire « sans hypothèse sur la corrélation, sous l'approximation de la taille effective », et l'absence de correction de multiplicité sur 40 types (constat 12). Ajouter la réserve entière (T08).
  - Entrées : tables 6 et 6 bis, `ecart.csv`, tables exploratoires.
  - Livrable : section 6.4.
  - Vérification : chaque phrase qui contient « established » nomme la configuration ; le rapport « borne basse ÷ barre » est donné ; les passages exploratoires sont marqués.
  - Dépendances : T16.

- [x] **T18 — Résultats 6.5 à 6.7 : utilité, changements de modèle, analyses secondaires.**
  - Objectif : utilité : point 2 non jugé ; dépassements des témoins dits comme « une configuration (liste fixe) et deux (tri par le risque), toutes avec Haiku, à enjeu faible », présentés comme illustration de l'écart et non comme victoire (constats 13 et 14) ; rôle du palier 2 dans la charge (constats 15 et 17). Puis scénarios, épreuves, règles secondaires, verdicts bruts et échange des rôles (avec la réserve du constat 19 : trois analyses au bord du même seuil), table 9 et alerte.
  - Entrées : `charges.csv`, `volume.csv`, `derive.csv`, `epreuves.csv`, `choix.csv`, tables 7, 8, 9, morceaux de T05 et T09.
  - Livrable : sections 6.5, 6.6, 6.7.
  - Vérification : plus aucun `[RESULT` dans la section 6 ; le mot « beats » n'apparaît pas pour B-tout.
  - Dépendances : T17.

- [x] **T19 — Mise à jour des sections 3 à 5 (méthode).**
  - Objectif : appliquer les constats 22 à 25 de l'audit du 14/11 : paragraphe « ce que R1 et "confirmée" peuvent et ne peuvent pas signifier » ; « in expectation » resserré ; résumé « every write made with a tool of the frozen table » ; section 4.3 mise à jour (relecteurs : Opus 5.5 en vague 2, modèle non noté en vague 1, lots, aveugle par consigne et non par barrière technique) ; les deux horodatages (dépôt OSF 06 h 03, début de la vague 1 06 h 19, le 10/11).
  - Entrées : `article/brouillon.md`, `PLAN_EXPERIENCE.md` (1.4), `JOURNAL_CHANGEMENTS.md` (lignes des 13 et 14/11).
  - Livrable : sections 3, 4 et 5 révisées.
  - Vérification : les 4 constats sont cochés un par un dans le message de commit ; les horodatages sont relus dans `SUIVI.md`.
  - Dépendances : T13.

- [x] **T20 — Écarts au préenregistrement (D4 et suivants).**
  - Objectif : compléter la liste, dans l'ordre des dates : page de relecture simplifiée en vague 2 et son effet possible ; levées d'Otsoa hors motif (client simulé qui dérive) ; outils absents de la table (19 vrais outils en banque, 8 inventés, 2 en commerce) ; procédure de relecture de la vague 2 (Opus 5.5 relit des parties jouées en partie par Opus 5.5) ; audit sans alerte ; opposition sur commerce 98 ; enregistrement u26kr remplacé par cusv6 (erreur de consigne sur l'embargo) ; diagnostic des messages vides (207 de l'agent, 19 du client simulé) ; correctif en mémoire du rejeu final (texte de T03) ; coût hors de l'intervalle annoncé ; outils et analyses d'après verdict.
  - Entrées : `JOURNAL_CHANGEMENTS.md` (du 10/11 au 17/11), `SUIVI.md`, `depots/2026-11-14_gel_verdicts_v2/FICHE_DEPOT.md`, T03.
  - Livrable : section « Deviations from the preregistration » complète.
  - Vérification : chaque ligne du journal datée du 10/11 ou après a son écart dans l'article (tableau de correspondance dans le commit) ; plus de `[RESULT` dans la section.
  - Dépendances : T03, T15.

- [x] **T21 — Limites.**
  - Objectif : mettre à jour les 20 limites et ajouter celles nées des résultats : R4 portée par une seule configuration, à une marge mince ; point 1 presque sans puissance ; fausses confirmations (3 levées sur 10) ; erreurs confirmées dans des tâches réussies ; refusées comptées ; comptabilité du palier 2 qui avantage B-tout ; banque ; exclusions pour message vide ; audit 0 sur 21 ; relecteurs du même fournisseur (limite 9 renforcée) ; effet du dimensionnement (Haiku seul jugeable par son volume).
  - Entrées : section 8 du brouillon, `PLAN_EXPERIENCE.md` (section 6), audit du 17/11.
  - Livrable : section « Limitations », chaque limite marquée « preregistered » ou « added after the results ».
  - Vérification : les 10 points de « Ce qu'on ne peut pas affirmer » ont chacun une limite ; plus de `[RESULT` dans la section.
  - Dépendances : T18, T20.

- [x] **T22 — Lecture complète des deux articles voisins.**
  - Objectif : lire en entier Zhang et Zhang (arXiv 2607.23586, lu jusqu'ici par le résumé seul) et CASE (arXiv 2608.10153), pour écrire une comparaison exacte et dire la part d'antériorité.
  - Entrées : les deux articles en ligne ; `lectures/`.
  - Livrable : `lectures/zhang_zhang_autorite_meritee.md` et `lectures/case_budget_erreurs.md` (fiches en français, avec citations et numéros de page) ; le repère `[VERIFY-ORIGINAL]` de la ligne 48 levé.
  - Vérification : chaque affirmation de l'article sur ces deux textes renvoie à une page.
  - Dépendances : aucune.

- [x] **T23 — Discussion.**
  - Objectif : remplir les 5 repères : ce que R4 veut dire et ne veut pas dire ; ce que l'écart dit des agents et du budget choisi (à enjeu fort, les rapports mesurent surtout la barre) ; contrainte liante (borne de construction ou rapport s/q) ; comparaison avec Zhang et Zhang et avec CASE ; conséquences pratiques (quels types, à quels volumes). Pas plus que « Ce qu'on peut affirmer » de l'audit.
  - Entrées : T17, T18, T21, T22, `FORMULATION_VERDICT.md`.
  - Livrable : section 7.
  - Vérification : chaque affirmation renvoie à une table ou à une limite ; aucune formule R8.
  - Dépendances : T21, T22.

- [x] **T24 — Originaux à lire : localiser.**
  - Objectif : pour chaque repère `[VERIFY-ORIGINAL]` (Dodge 1943 ; Dodge et Torrey 1951 ; Lieberman 1953 ; Lieberman et Solomon 1955 ; Derman et al. 1957 et 1959 ; Wald et Wolfowitz 1945 ; Hillier 1964), trouver une source légale et dire si elle est gratuite.
  - Entrées : références du brouillon, `lectures/_verification.md`.
  - Livrable : `article/verif_originaux.md` (tableau : référence, affirmation de l'article qui en dépend, adresse, accès libre ou payant, prix).
  - Vérification : une ligne par repère ; chaque adresse a été ouverte, avec la date. Un achat demande l'accord d'Otsoa (question Q12).
  - Dépendances : aucune.

- [x] **T25 — Originaux à lire : première moitié.**
  - Objectif : lire Dodge 1943, Lieberman 1953, Lieberman et Solomon 1955, Wald et Wolfowitz 1945 ; vérifier chaque formule et chaque affirmation reprise de Hryniewicz (2011).
  - Entrées : `article/verif_originaux.md`, section 3.4 du brouillon.
  - Livrable : tableau complété (page, citation, « conforme » ou « à corriger ») ; brouillon corrigé ; repères levés.
  - Vérification : pour chaque repère levé, une page et une citation ; toute correction de formule est signalée à Otsoa.
  - Dépendances : T24.

- [x] **T26 — Originaux à lire : seconde moitié et repères `[VERIFY]`.**
  - Objectif : même travail pour Dodge et Torrey 1951, Derman et al. 1957 et 1959, Hillier 1964 ; lever les `[VERIFY]` restants (ligne 46 ; remerciements). Un original introuvable ou payant sans accord reste cité « as reported by Hryniewicz (2011) », dit tel quel.
  - Entrées : comme T25.
  - Livrable : brouillon sans aucun repère `[VERIFY`, sauf les noms des relecteurs (T39).
  - Vérification : `grep -c "VERIFY" article/brouillon.md` donne 1 au plus.
  - Dépendances : T24.

- [x] **T27 — Résumé, introduction, conclusion.**
  - Objectif : écrire le résumé (200 mots au plus) avec la phrase anglaise de l'audit et les trois phrases qui suivent ; ajuster les contributions de l'introduction ; conclusion courte.
  - Entrées : `FORMULATION_VERDICT.md`, sections 6 et 7.
  - Livrable : résumé, introduction et conclusion dans `brouillon.md`.
  - Vérification : plus aucun `[RESULT` dans tout le brouillon ; aucune formule R8 ; le résumé tient dans la limite d'arXiv (1 920 caractères).
  - Dépendances : T23.

- [x] **T28 — Version française de contrôle. [ACCORD OTSOA]**
  - Objectif : donner à Otsoa, en français simple, ce que l'article affirme : résumé traduit, une phrase par résultat, les limites, les écarts. Il valide le fond avant la mise en page.
  - Entrées : `article/brouillon.md`.
  - Livrable : `article/controle_fr.md` (3 pages au plus).
  - Vérification : chaque phrase renvoie à une section de l'article ; Otsoa a écrit « d'accord » ou a donné ses corrections, et elles sont reportées.
  - Dépendances : T27.

- [x] **T29 — Figures.**
  - Objectif : figures finales, en PDF vectoriel : figure 1 (dégâts en plus contre le budget, cellules jugées), figure 2 (écart de délégation : taux et intervalles, échelle log, un panneau par environnement), figure 3 (charge contre dégâts, par règle). Lisibles en noir et blanc, textes en anglais, tailles de police lisibles à la largeur d'une colonne.
  - Entrées : `budget.csv`, `ecart.csv`, `charges.csv`, `outils/tables_article.py`.
  - Livrable : `article/figures/fig1_budget.pdf`, `fig2_gap.pdf`, `fig3_load.pdf`, produites par un script d'`outils/`.
  - Vérification : les points de la figure 2 égalent la table 6 (contrôle sur 3 types tirés) ; banque/Haiku ILL (2 écritures) est marqué ou retiré ; relancer le script redonne les mêmes fichiers.
  - Dépendances : T12, T14.

- [x] **T30 — Passage en LaTeX.**
  - Objectif : convertir l'article en LaTeX avec un gabarit sobre accepté par arXiv (une classe standard), et une bibliographie BibTeX. Les tables sont produites en `.tex` par le script, pas recopiées à la main.
  - Entrées : `article/brouillon.md`, `tables.md`, figures. Vérifier qu'un compilateur LaTeX est installé ; sinon demander avant d'installer quoi que ce soit.
  - Livrable : `article/latex/main.tex`, `refs.bib`, `tables/*.tex`, `main.pdf`.
  - Vérification : compilation sans erreur ni référence manquante ; les tables du PDF égalent `tables.md`.
  - Dépendances : T27, T29.

- [x] **T31 — Réduction au format d'atelier : 8 pages et annexes.**
  - Objectif : appliquer le plan de T13. Corps : question, règle en bref, dispositif, étiquette, écart de délégation, limites principales. Annexes : règle complète, analyse préenregistrée, tables complètes, écarts, limites complètes, analyses exploratoires.
  - Entrées : `article/latex/`, `article/PLAN_ARTICLE.md`.
  - Livrable : `main.pdf` avec un corps de 8 pages au plus hors références.
  - Vérification : nombre de pages relevé ; rien n'est supprimé, tout ce qui sort du corps est dans une annexe (liste de correspondance) ; les écarts et les limites restent annoncés dans le corps.
  - Dépendances : T30.

- [x] **T32 — Bibliographie.**
  - Objectif : vérifier chaque référence : auteurs, année, titre, revue, DOI ou numéro arXiv, en ligne (Crossref, arXiv).
  - Entrées : `refs.bib`.
  - Livrable : `refs.bib` vérifié ; `article/verif_references.md` (une ligne par référence, avec la date de lecture).
  - Vérification : 0 référence non vérifiée ; chaque référence citée existe dans le texte et inversement.
  - Dépendances : T30.

- [x] **T33 — Contrôle automatique des chiffres.**
  - Objectif : un script qui relit chaque valeur du registre dans son fichier source et la cherche dans `main.tex`.
  - Entrées : `article/sources_chiffres.csv`, sorties, `main.tex`.
  - Livrable : `outils/verifier_chiffres.py` et son rapport `article/verif_chiffres.txt`.
  - Vérification : 0 écart ; un chiffre changé exprès dans une copie du texte est bien détecté.
  - Dépendances : T31.

- [x] **T34 — Déclarations obligatoires et adresse de contact. [ACCORD OTSOA]**
  - Objectif : rédiger les mentions finales : aide de Claude (écriture du code, du texte, relecture des alertes), financement par l'auteur, conflit d'intérêts, disponibilité du code et des données, licences, adresse de contact publique. L'adresse `…@autonomie-meritee.local` n'existe pas : il faut une vraie adresse. Vérifier en ligne la règle d'arXiv sur les textes écrits avec une IA.
  - Entrées : remerciements du brouillon, règles d'arXiv lues en ligne.
  - Livrable : sections finales de `main.tex`.
  - Vérification : la règle d'arXiv est citée avec son adresse et la date ; Otsoa a choisi l'adresse (question Q4).
  - Dépendances : T30.

### C. Relectures

- [x] **T35 — Audit indépendant de l'article complet (agent neuf).**
  - Objectif : faire relire le PDF par un agent sans contexte, sur l'abonnement, avec une grille : chaque constat des deux audits est-il traité ; formules R8 absentes ; chiffres recalculés depuis les CSV ; préenregistré et exploratoire bien séparés ; écarts tous déclarés ; ce qu'un relecteur hostile attaquerait. On lui donne les fichiers, pas nos conclusions.
  - Entrées : `main.pdf`, `main.tex`, `experience/rejeu_final/`, `experience/exploratoire/`, `PLAN_EXPERIENCE.md`, `JOURNAL_CHANGEMENTS.md`, les deux audits. Mêmes interdits que R1.
  - Livrable : `revues/2026-XX-XX_audit_article.md` (constats classés bloquant, important, mineur).
  - Vérification : le rapport liste ce qu'il a lu et ce qu'il n'a pas lu ; il traite les 27 et les 26 constats un par un.
  - Dépendances : T31, T32, T33, T34.

- [x] **T36 — Suites de l'audit de l'article.**
  - Objectif : corriger tous les constats bloquants et importants ; répondre aux mineurs.
  - Entrées : rapport de T35.
  - Livrable : article corrigé ; `revues/2026-XX-XX_audit_article_suites.md` (constat, réponse, endroit corrigé).
  - Vérification : 0 bloquant ouvert ; T33 repasse sans écart ; tout désaccord avec l'auditeur est expliqué et montré à Otsoa.
  - Dépendances : T35.

- [x] **T37 — Dossier pour le relecteur humain extérieur.**
  - Objectif : préparer ce qu'on envoie : PDF, une page de présentation, 5 questions précises (le résultat est-il bien borné ? la méthode se comprend-elle ? manque-t-il une référence ? le texte se lit-il ? une erreur ?), délai proposé, demande d'accord pour être nommé. Proposer 3 à 5 relecteurs possibles avec leur adresse publique.
  - Entrées : article, `notes/parrains_arxiv.md`, `CADRE.md`.
  - Livrable : `revues/dossier_relecteur_exterieur/` (message anglais, version française, liste des candidats).
  - Vérification : chaque adresse est publiée par la personne elle-même, avec la source et la date.
  - Dépendances : T36.

- [x] **T38 (sautée par Otsoa le 17/11 : aucun relecteur contacté) — Choix du relecteur et envoi. [ACCORD OTSOA]**
  - Objectif : Otsoa choisit le relecteur (question Q5) et envoie lui-même le message, ou donne son accord pour l'envoi.
  - Entrées : T37.
  - Livrable : ligne dans `SUIVI.md` (à qui, quand, délai) ; copie du message envoyé dans le dossier.
  - Vérification : date d'envoi notée ; date de relance fixée (10 jours).
  - Dépendances : T37.

- [x] **T39 (sans relecture extérieure : l'article le dit, Q5) — Retours du relecteur humain.**
  - Objectif : intégrer les retours, noter ce qui est refusé et pourquoi, compléter les remerciements (nom seulement avec un accord écrit).
  - Entrées : réponse du relecteur.
  - Livrable : article corrigé ; `revues/2026-XX-XX_relecture_exterieure.md`.
  - Vérification : chaque remarque a une réponse ; T33 repasse ; plus aucun `[VERIFY`. Sans réponse après la relance, on continue et l'article dit qu'il n'a pas eu de relecture humaine extérieure (question Q5).
  - Dépendances : T38.

### D. Dépôt OSF des résultats et du journal du tirage

- [x] **T40 — Paquet OSF des résultats et journal du tirage.**
  - Objectif : construire le dépôt prévu par le plan (3.4, point 6). Le journal du tirage contient : horodatage du dépôt du gel (`2026-11-14T08:17:47.424176 UTC`, cusv6), heure désignée, impulsion brute du NIST, graine, partage, empreinte du script du tirage, empreintes des sorties du rejeu final. On y joint les sorties, les analyses exploratoires, la note du correctif (T03), la vérification des six tables (T02), le journal du rejeu, et la commande pour refaire le tirage.
  - Entrées : `experience/tirage/`, `experience/rejeu_final/`, `experience/exploratoire/`, `experience/journal_rejeu_final.jsonl`, `experience/SHA256_sorties_finales.txt`, `depots/2026-11-14_gel_verdicts_v2/` (modèle), `depots/construire_depot.py`.
  - Livrable : `depots/2026-11-XX_resultats/` : `paquet/`, `JOURNAL_TIRAGE.md`, `SHA256SUMS.txt`, le zip, `resume_osf_texte.txt` (texte brut, sans chevrons ni esperluettes), `FICHE_DEPOT.md` (gestes à faire, traduction française).
  - Vérification : `tirage_public.py verifier --en-ligne` dit « tirage vérifié » ; les empreintes de `impulsion.json` et `partage.json` commencent par `fa61235b` et `76e04fca` ; le zip décompressé passe `SHA256SUMS.txt` ; aucun fichier interdit ni secret dans le paquet.
  - Dépendances : T01, T02, T03, T11.

- [x] **T41 (fait sur Zenodo le 17/11, DOI 10.5281/zenodo.24321214, embargo au 04/11/2030 ; OSF refuse désormais les résultats) — Soumission du dépôt OSF des résultats. [ACCORD OTSOA]**
  - Objectif : enregistrer le paquet sur OSF, public ou sous embargo court selon la question Q6. Rappel : après l'approbation, on ne peut plus annuler.
  - Entrées : T40.
  - Livrable : identifiant OSF et `date_registered` inscrits dans `FICHE_DEPOT.md` et `SUIVI.md`.
  - Vérification : zip retéléchargé, empreinte identique ; résumé relu sur le serveur ; état lu par l'API d'OSF.
  - Dépendances : T40.

- [x] **T42 — Inventaire des enregistrements OSF et plan de levée.**
  - Objectif : lister tous les enregistrements (7ju3c, vycge, cusv6, u26kr retiré, résultats) avec leur état réel et leur date de fin d'embargo ; écrire les gestes exacts pour lever chaque embargo, et ce qui devient public à chaque fois.
  - Entrées : `depots/*/FICHE_DEPOT.md`, API d'OSF, session d'Otsoa.
  - Livrable : `depots/INVENTAIRE_OSF.md`.
  - Vérification : chaque état est lu sur OSF le jour même, pas recopié d'une fiche ; pour chaque paquet, on confirme qu'il ne contient ni secret ni fichier de `donnees/`.
  - Dépendances : T41.

- [ ] **T43 — Levée des embargos, le jour de la publication. [ACCORD OTSOA]**
  - Objectif : rendre publics les enregistrements choisis (question Q7). Irréversible.
  - Entrées : `depots/INVENTAIRE_OSF.md`.
  - Livrable : états mis à jour dans l'inventaire et dans `SUIVI.md`.
  - Vérification : chaque page s'ouvre dans une fenêtre privée, sans connexion ; les liens de l'article répondent.
  - Dépendances : T42, T52 (le code est déjà public), T43 bis prête (décision du 17/11 : OSF Preprints d'abord ; **revue le 18/11 : Zenodo d'abord**, voir T43 bis ; arXiv, T56, vient après).

### E. Code et données ouverts

- [ ] **T43 bis — Prépublication sur Zenodo. [ACCORD OTSOA]**
  - **Changement du 18/11 (décision d'Otsoa)** : OSF Preprints exclut « Content completely or mostly generated by large language model (LLM) tools » (politique de modération lue le 18/11, `depots/REGLES_PREPUBLICATION.md`) ; l'article déclare que Claude l'a rédigé ; la déclaration reste telle quelle. L'article va donc sur Zenodo le jour J, puis sur arXiv (T56).
  - Objectif : le jour J, après T52, publier `article/latex/main.pdf` sur Zenodo (type « publication / preprint », CC BY 4.0), relié aux enregistrements 7ju3c, vycge, cusv6 et aux dépôts 24321214, 24331243, 24331245 ; ajouter dans la description du dépôt 24321214 une note : le README de l'archive annonce l'article sur OSF Preprints, il est en fait sur Zenodo puis arXiv.
  - Entrées : `main.pdf` final, résumé, métadonnées des brouillons de T51.
  - Livrable : DOI de l'article inscrit dans `SUIVI.md`, `README.md`, `CITATION.cff` ; la version arXiv cite ce DOI.
  - Vérification : la page s'ouvre sans connexion ; le PDF retéléchargé a la même empreinte que `main.pdf`.
  - Dépendances : T52.

- [x] **T44 — Inventaire de ce qui sera publié. [ACCORD OTSOA]**
  - Objectif : décider, dossier par dossier, ce qui sort : code (`simulation/`, `banc/`, `gel/`, `outils/`, `depots/`), documents (règle, plan, journal, suivi, revues), sorties du rejeu, traces des parties, fichiers de relecture. Signaler ce qui ne doit pas sortir tel quel : `notes/messages_diffusion.md` (adresses de personnes), `reports/` et `research_notes/` sans rapport avec l'étude, `presentation/`, `donnees/`, `pilote/`. Estimer la taille de l'archive.
  - Entrées : arborescence (noms et tailles seulement pour les dossiers interdits), `.gitignore`, `experience/manifeste_verdicts.txt` (68 990 fichiers).
  - Livrable : `publication/INVENTAIRE.md` (dossier, publié oui/non, où, raison, taille).
  - Vérification : chaque dossier de premier niveau a une ligne ; Otsoa a répondu aux questions Q8 et Q9.
  - Dépendances : aucune.

- [x] **T45 — Recherche de secrets.**
  - Objectif : chercher clés, jetons, mots de passe, adresses personnelles, chemins `/Users/…`, dans l'arbre de travail et dans tout l'historique git. Pour les dossiers interdits qui seraient publiés, recherche par motif qui ne rend que le nom du fichier et le nombre de lignes touchées.
  - Entrées : dépôt, historique (165 commits), périmètre de T44.
  - Livrable : `publication/RAPPORT_SECRETS.md` (motifs cherchés, résultats par fichier, sans aucune valeur).
  - Vérification : 0 secret, ou chaque trouvaille a une décision (retiré, faux positif) ; un secret trouvé dans l'historique arrête la publication de l'historique et renvoie à la question Q9 ; la clé n'a jamais été affichée.
  - Dépendances : T44.

- [x] **T46 — Licences.**
  - Objectif : `LICENSE` (MIT, code), `LICENSE-TEXT` (CC-BY 4.0, textes, tables, figures), `THIRD_PARTY_NOTICES` (τ-bench, WorkBench et les autres dépendances), `CITATION.cff`, `.zenodo.json`. Vérifier en ligne, sur les dépôts officiels des bancs, leur licence et si elle permet de redistribuer des traces dérivées de leurs tâches. Ne pas ouvrir `externe/`.
  - Entrées : `depots/2026-11-09_gel/contenu/LICENSE-CODE.txt` et `THIRD_PARTY_NOTICES.txt` (modèles), dépôts officiels en ligne.
  - Livrable : les cinq fichiers à la racine ; `publication/LICENCES_BANCS.md` (licence, adresse, date de lecture, conclusion).
  - Vérification : chaque licence de banc est citée avec son adresse ; ORCID et titre exacts dans `CITATION.cff` ; si une licence empêche de redistribuer, arrêt et question à Otsoa.
  - Dépendances : T44.

- [x] **T47 — README et guide de reproduction.**
  - Objectif : `README.md` en anglais et `LISEZMOI.md` en français : ce qu'est l'étude, le résultat (phrase de T04), l'arborescence, la chaîne de preuves (préenregistrement, gel, tirage public, rejeu), comment vérifier le tirage, comment refaire les tables et les figures à partir des sorties, ce qui n'est pas fourni et pourquoi, l'incident du rejeu final, comment citer.
  - Entrées : `FORMULATION_VERDICT.md`, `depots/*/FICHE_DEPOT.md`, `banc/INSTALLATION.md`, T03.
  - Livrable : `README.md`, `LISEZMOI.md`.
  - Vérification : chaque commande du README a été lancée et marche ; aucune formule R8 ; aucun lien mort.
  - Dépendances : T04, T46.

- [x] **T48 — Copie de publication propre.**
  - Objectif : préparer, hors du dépôt de travail, la copie à publier, selon Q9 (historique complet ou instantané). Retirer les `__pycache__`, les fichiers exclus par T44, les chemins personnels dans les textes.
  - Entrées : dépôt, T44, T45.
  - Livrable : un clone local prêt, sans dépôt distant ; `publication/CONTENU_PUBLIE.txt` (liste des fichiers avec empreintes).
  - Vérification : la recherche de T45 relancée sur la copie donne 0 ; si l'historique est publié, l'étiquette `gel-2026-11-09` et le commit `a8eb1aae` y sont ; aucun fichier interdit dans la liste.
  - Dépendances : T45, T46, T47.

- [x] **T49 — Essai de reproduction sur la copie.**
  - Objectif : dans la copie propre, avec un environnement Python neuf, refaire les tables et les figures à partir des sorties publiées, vérifier le tirage hors ligne puis en ligne, lancer les tests du moteur. Aucun appel payant.
  - Entrées : copie de T48.
  - Livrable : `publication/ESSAI_REPRODUCTION.md` (commandes, durées, résultats).
  - Vérification : `tables.md` et les figures régénérées sont identiques aux versions de l'article ; « tirage vérifié » ; les tests passent, ou chaque échec est expliqué.
  - Dépendances : T48.

- [x] **T50 — Paquet de données.**
  - Objectif : si Q8 dit oui, préparer l'archive des données : les fichiers du manifeste des verdicts, tels quels, pour que chacun puisse les confronter aux empreintes déposées sur cusv6 ; plus un fichier qui explique les formats.
  - Entrées : `experience/manifeste_verdicts.txt`, périmètre de T44, T46 (licences des bancs). Copie et empreintes seulement, sans lecture.
  - Livrable : une ou plusieurs archives hors du dépôt, `DATA_README.md`, `SHA256SUMS.txt`.
  - Vérification : chaque fichier de l'archive a l'empreinte du manifeste (`904aa8d3…`) ; la recherche de secrets par motif donne 0 ; la taille respecte la limite de Zenodo, lue en ligne.
  - Dépendances : T44, T45, T46.

- [x] **T51 — Dépôt GitHub privé et brouillon Zenodo. [ACCORD OTSOA]**
  - Objectif : créer le dépôt GitHub en privé, y envoyer la copie propre, créer le brouillon Zenodo et réserver le DOI pour l'écrire dans l'article. Le `push` est fait par Otsoa lui-même, ou avec son accord écrit pour cette seule copie (question Q10) : la règle R4 reste entière pour le dépôt de travail.
  - Entrées : T48, T49, T50.
  - Livrable : adresse du dépôt, DOI réservé, inscrits dans `SUIVI.md`, `README.md`, `CITATION.cff` et l'article.
  - Vérification : le dépôt distant contient exactement `CONTENU_PUBLIE.txt` ; il est privé ; le brouillon Zenodo n'est pas publié.
  - Dépendances : T48, T49.

- [ ] **T52 — Publication du code et des données, le jour J. [ACCORD OTSOA]**
  - Objectif : rendre le dépôt GitHub public, créer la version étiquetée, publier l'archive Zenodo (code, puis données). Irréversible : un DOI publié ne se retire pas.
  - Entrées : T51, article final.
  - Livrable : adresses publiques et DOI définitifs dans `SUIVI.md`.
  - Vérification : le dépôt s'ouvre sans connexion ; le DOI répond ; l'archive téléchargée a les empreintes de `CONTENU_PUBLIE.txt`.
  - Dépendances : T39, T51.

### F. arXiv

- [ ] **T53 — Vérifier qui peut parrainer.**
  - Objectif : pour chaque article de `notes/parrains_arxiv.md`, ouvrir sa page arXiv, connecté au compte d'Otsoa, et lire « Which authors of this paper are endorsers? ». Relever la règle de parrainage en vigueur. Classer les candidats : peut parrainer en cs.AI, proche du sujet, adresse publique.
  - Entrées : `notes/parrains_arxiv.md`, session arXiv d'Otsoa.
  - Livrable : `notes/parrains_arxiv.md` mis à jour (colonne « peut parrainer : oui / non / inconnu », date de lecture).
  - Vérification : chaque ligne a une date de lecture ; au moins 3 parrains possibles confirmés, sinon élargir la liste aux auteurs cités dans l'article.
  - Dépendances : aucune (à faire tôt).

- [ ] **T54 — Demande de parrainage. [ACCORD OTSOA]**
  - Objectif : écrire le message court (qui je suis, ce que montre l'étude en une phrase de T04, PDF joint, code de parrainage d'arXiv, aucune obligation), avec sa version française ; l'envoyer à un parrain à la fois, dans l'ordre choisi (question Q13).
  - Entrées : T53, PDF après T36, code de parrainage obtenu dans le brouillon de dépôt arXiv.
  - Livrable : `notes/demande_parrainage.md` ; dates d'envoi dans `SUIVI.md`.
  - Vérification : le message ne contient aucune formule R8 ; relance prévue à 7 jours, puis candidat suivant.
  - Dépendances : T36, T53. Peut partir avant le retour du relecteur humain.

- [x] **T55 — Paquet arXiv.**
  - Objectif : préparer l'archive des sources (tex, bbl, figures, tables) et les métadonnées : titre, auteur, résumé (1 920 caractères au plus), catégorie principale cs.AI, catégories secondaires proposées, commentaire (pages, liens OSF et code), licence.
  - Entrées : `article/latex/`, règles de dépôt d'arXiv lues en ligne.
  - Livrable : `article/arxiv/paquet.tar.gz`, `article/arxiv/METADONNEES.md` (anglais et français).
  - Vérification : l'archive compile seule dans un dossier vide ; aucun fichier inutile ni commentaire privé dans les sources ; les liens (OSF, GitHub, DOI) sont ceux de T41 et T51.
  - Dépendances : T39, T51.

- [ ] **T56 — Soumission arXiv. [ACCORD OTSOA]**
  - Objectif : déposer la prépublication, relire l'aperçu produit par arXiv, soumettre.
  - Entrées : T55, parrainage obtenu.
  - Livrable : numéro arXiv et date d'annonce dans `SUIVI.md`.
  - Vérification : l'aperçu PDF d'arXiv est relu page par page (tables, figures, liens) avant le clic final ; Otsoa a validé le titre et le résumé une dernière fois.
  - Dépendances : T43, T52, T54, T55.

- [ ] **T57 — Après l'annonce : liens croisés.**
  - Objectif : écrire le numéro arXiv dans le README, `CITATION.cff`, la fiche Zenodo, la page du projet OSF ; mettre à jour ORCID.
  - Entrées : numéro arXiv.
  - Livrable : fichiers mis à jour ; ligne dans `SUIVI.md`.
  - Vérification : chaque lien s'ouvre sans connexion. Les modifications en ligne (Zenodo, OSF, GitHub) sont faites avec Otsoa.
  - Dépendances : T56.

### G. Diffusion

- [ ] **T58 — Messages aux auteurs voisins : finir les brouillons.**
  - Objectif : remplir les crochets de `notes/messages_diffusion.md` (résultat en une phrase, chiffre clé, liens), corriger ce que le verdict change (le message à Evan Miller annonce un « écart » : le dire avec les bornes de T04), revérifier chaque adresse, écrire la version française de chaque message.
  - Entrées : `notes/messages_diffusion.md`, `FORMULATION_VERDICT.md`, T22.
  - Livrable : `notes/messages_diffusion.md` final.
  - Vérification : aucun crochet restant ; aucune formule R8 ; chaque adresse a une source et une date ; l'article cite bien Zhang et Zhang et dit la différence.
  - Dépendances : T36.

- [ ] **T59 — Envoi des messages. [ACCORD OTSOA]**
  - Objectif : Otsoa choisit les destinataires et envoie, après l'annonce arXiv.
  - Entrées : T58, numéro arXiv.
  - Livrable : tableau dans `SUIVI.md` (destinataire, date, réponse).
  - Vérification : un message par personne, jamais d'envoi groupé ; relance unique à 10 jours.
  - Dépendances : T57, T58.

- [ ] **T60 — Fil X et annonce courte.**
  - Objectif : écrire un fil de 6 à 8 messages en anglais, avec sa version française : la question, la méthode en une image, le résultat borné, ce qu'il ne dit pas, la chaîne de preuves (préenregistrement, tirage public), les liens. Une figure (figure 2 simplifiée). Une annonce d'un paragraphe pour d'autres lieux.
  - Entrées : `FORMULATION_VERDICT.md`, figures.
  - Livrable : `notes/fil_x.md`.
  - Vérification : chaque chiffre est au registre ; aucune formule R8 ; chaque message tient dans la limite de X.
  - Dépendances : T36.

- [ ] **T61 — Publication du fil. [ACCORD OTSOA]**
  - Objectif : Otsoa publie le fil le jour de l'annonce arXiv, depuis son compte.
  - Entrées : T60, numéro arXiv.
  - Livrable : lien du fil dans `SUIVI.md`.
  - Vérification : liens testés avant publication.
  - Dépendances : T57, T60.

- [ ] **T62 — Ateliers : relevé en ligne.**
  - Objectif : à faire à partir du 30/11/2026, quand les listes d'ateliers sont sorties. Relever en ligne, pour chaque atelier possible (AAMAS 2027, ICLR 2027, ICML 2027, autres) : thème, date limite, nombre de pages, gabarit, anonymat, archivé ou non, prépublication arXiv admise ou non, résultats négatifs bienvenus ou non, présence obligatoire, lieu, frais.
  - Entrées : `reports/Plan de lancement article et Tenure.md` (pistes, à revérifier), sites officiels.
  - Livrable : `notes/ateliers.md` (tableau comparatif, chaque case avec adresse et date de lecture, et une recommandation).
  - Vérification : aucune date reprise sans relecture en ligne ; les cases inconnues sont marquées « non publié ».
  - Dépendances : aucune, mais pas avant le 30/11.

- [ ] **T63 — Choix de l'atelier, adaptation et soumission. [ACCORD OTSOA]**
  - Objectif : Otsoa choisit (question Q14). Puis adapter l'article au gabarit et aux règles de l'atelier (pages, anonymat : retirer nom, ORCID, liens qui identifient), et soumettre. Annoncer d'avance les frais d'inscription et de voyage.
  - Entrées : `notes/ateliers.md`, `article/latex/`.
  - Livrable : `article/atelier_<nom>/` (sources et PDF) ; accusé de soumission dans `SUIVI.md`.
  - Vérification : limite de pages respectée ; règles d'anonymat relues en ligne le jour de l'envoi ; T33 repasse sur cette version. Si l'adaptation dépasse deux heures, la découper.
  - Dépendances : T39, T62.

- [ ] **T64 — Outil en ligne et suites : note de décision. [ACCORD OTSOA]**
  - Objectif : une page pour décider s'il faut un outil en ligne (par exemple un calculateur : budget d'erreurs et volume donnent la longueur N et le nombre de réussites à observer), et s'il faut candidater au programme d'accès chercheurs d'Anthropic (brouillon 3 de `notes/messages_diffusion.md`). Pour chaque option : à quoi elle sert pour être repéré, coût, temps, risque.
  - Entrées : `reports/Plan de lancement article et Tenure.md`, `notes/messages_diffusion.md`, formules de la section 3.4 de l'article.
  - Livrable : `notes/decision_outil_en_ligne.md`.
  - Vérification : chaque option a un coût chiffré et une recommandation ; rien n'est construit ni mis en ligne avant la réponse à Q15.
  - Dépendances : T56.

- [ ] **T65 — Clôture.**
  - Objectif : bilan final dans `SUIVI.md` (liens, dates, ce qui reste ouvert) ; copie de sauvegarde sur le disque T9 avec empreintes ; liste des réponses à surveiller.
  - Entrées : tout ce qui précède.
  - Livrable : section « Publication » de `SUIVI.md` ; liste des empreintes de la copie.
  - Vérification : chaque case de ce plan est cochée ou porte une raison écrite ; copie vérifiée fichier par fichier.
  - Dépendances : T57, T59, T61.

## 4. Décisions à demander à Otsoa

Chaque question se pose au moment de la tâche citée. La recommandation est celle du plan ; Otsoa décide.

**Q1. Comment dire le verdict ? (T04)**
- a) La phrase de l'audit : « aucune configuration n'a atteint le niveau de preuve exigé… ; une seule assez jouée pour être jugée… ; les onze autres ne permettent pas de conclure ».
- b) La formule du 17/11 : « rien à déléguer : non-fiabilité établie ».
- c) Une phrase encore plus prudente, centrée sur « preuves insuffisantes ».
- **Recommandation : a.** Elle est exacte et résiste à un relecteur. La b est jugée bloquante par l'audit.

**Q2. Quel titre ? (T13)**
- a) Garder « … with an error-budget guarantee ».
- b) « … with a conditional error-budget guarantee ».
- c) Un titre centré sur le résultat : l'écart de délégation mesuré.
- **Recommandation : c**, avec « preregistered » dans le titre. C'est le résultat qui intéresse un laboratoire. À défaut, b.

**Q3. Une version ou deux ? (T13, T31)**
- a) Un seul document : 8 pages et des annexes complètes, pour arXiv et pour l'atelier.
- b) Une version longue pour arXiv, une version courte pour l'atelier.
- **Recommandation : a.** Un seul texte à tenir juste ; l'atelier demandera seulement un changement de gabarit.

**Q4. Quelle adresse de contact dans l'article ? (T34)**
- a) Une adresse personnelle existante.
- b) Une adresse créée pour la recherche.
- c) Aucune adresse, ORCID seul.
- **Recommandation : b.** arXiv demande une adresse qui marche, et un laboratoire doit pouvoir écrire.

**Q5. Quel relecteur humain extérieur ? (T38, T39)**
- a) Une personne déjà connue d'Otsoa, à l'aise en statistique.
- b) Un des auteurs voisins (le message de relecture sert aussi de prise de contact).
- c) Pas de relecteur humain : on le dit dans l'article.
- **Recommandation : a si elle existe, sinon b**, avec un délai de 10 jours. Sans réponse, on publie en le disant (c).

**Q6. Quand et comment déposer les résultats sur OSF ? (T41)**
- a) Tout de suite, public.
- b) Tout de suite, sous embargo court, levé le jour J.
- c) Le jour J seulement.
- **Recommandation : b.** La date du dépôt prouve que les sorties n'ont pas bougé pendant l'écriture, sans rien annoncer avant l'article.

**Q7. Quels embargos lever le jour J ? (T43)**
- a) Tous : préenregistrement, gel des verdicts (cusv6), résultats.
- b) Seulement le préenregistrement et les résultats.
- c) Aucun avant l'atelier.
- **Recommandation : a**, après la vérification de T42 que chaque paquet est sans secret. Un préenregistrement que personne ne peut lire ne sert pas l'article.

**Q8. Publie-t-on les traces des parties ? (T44, T50)**
- a) Oui : tous les fichiers du manifeste des verdicts, tels quels.
- b) Non : seulement le code, les verdicts agrégés et les sorties du rejeu.
- c) Sur demande.
- **Recommandation : a**, si les licences des bancs le permettent (T46) et si la recherche de secrets ne trouve rien. C'est ce qui rend l'étude vérifiable de bout en bout. Le contenu de `donnees/` et de `pilote/` reste une décision à part : par défaut, non publié.

**Q9. Publie-t-on l'historique git ? (T48)**
- a) Oui, complet : les commits cités sur OSF (par exemple a8eb1aae) deviennent vérifiables.
- b) Non : un instantané propre, avec les empreintes.
- **Recommandation : a**, si T45 ne trouve aucun secret dans l'historique ; sinon b. L'adresse `…@autonomie-meritee.local` des commits est sans risque.

**Q10. Qui fait le `push` vers GitHub ? (T51, T52)**
- a) Otsoa, lui-même, avec les commandes préparées.
- b) L'exécutant, une seule fois, sur la copie de publication, après accord écrit.
- **Recommandation : a.** La règle « jamais de push » reste sans exception pour l'agent.

**Q11. Les scripts d'analyse peuvent-ils lire les données interdites à l'agent ? (T10, T50)**
- a) Oui, s'ils n'écrivent que des agrégats, comme `outils/analyses_exploratoires.py` le 17/11.
- b) Non : on se limite aux CSV du rejeu final.
- **Recommandation : a.** Sans cela, les analyses « refusées » et « palier 2 » demandées par l'audit sont impossibles ; on le dirait alors dans les limites.

**Q12. Achète-t-on les articles anciens payants ? (T24 à T26)**
- a) Oui, dans une limite fixée (par exemple 60 €).
- b) Non : on cite « d'après Hryniewicz (2011) ».
- c) On demande une copie à une bibliothèque.
- **Recommandation : c, puis b.** Dire qu'un original n'a pas été lu est honnête et suffit.

**Q13. Quel parrain arXiv solliciter en premier ? (T54)**
- a) Les auteurs de τ-bench (le banc utilisé).
- b) Les auteurs des articles les plus proches (CASE, SABER, AgentAbstain).
- c) Un auteur du Holistic Agent Leaderboard.
- **Recommandation : dépend de T53.** À capacité égale, b puis a : le parrain est aussi le premier lecteur de laboratoire. Zhang et Zhang ont des adresses étudiantes et ne peuvent sans doute pas parrainer.

**Q14. Quel atelier viser ? (T63)**
- a) Un atelier ICLR 2027 sur les agents, leur sûreté ou la supervision humaine.
- b) Un atelier AAMAS 2027 sur la confiance (présence à Hanoï).
- c) Aucun pour l'instant : arXiv seul, puis ICML 2027.
- **Recommandation : a**, sous réserve du relevé de T62 (thème, résultats négatifs admis, arXiv admis, frais). Les dates connues à ce jour sont des pistes non revérifiées.

**Q15. Faut-il un outil en ligne ? (T64)**
- a) Oui, un calculateur simple, après arXiv.
- b) Non : le dépôt de code suffit.
- c) Plus tard, si un laboratoire répond.
- **Recommandation : c.** L'objectif est d'être repéré par l'article ; l'outil ne doit pas retarder la publication.

**Q16. Quelle date viser pour le jour J ?**
- a) Dès que T36 est fini (audit par agent seul).
- b) Après le retour du relecteur humain, au plus tard 10 jours après l'envoi.
- c) Juste avant la date limite de l'atelier choisi.
- **Recommandation : b.** arXiv peut prendre une nouvelle version ensuite, mais la première est celle qu'on lit.

## 5. Risques à surveiller

- **Parrainage arXiv sans réponse.** Commencer T53 tôt ; un parrain à la fois ; relance à 7 jours. Solution de repli : le dépôt Zenodo de l'article (DOI) et OSF, en attendant.
- **Licence d'un banc qui interdit de redistribuer les traces.** Alors Q8 passe à b, et le README explique comment régénérer.
- **Secret dans l'historique.** Alors Q9 passe à b. On ne réécrit pas l'historique du dépôt de travail.
- **Un chiffre de l'article qui ne se retrouve pas.** T33 bloque la publication tant qu'il reste un écart.
- **Glissement de sens.** Chaque texte public repasse par la liste R8 et par `FORMULATION_VERDICT.md`.
- **Date limite d'atelier manquée.** Sans gravité : arXiv ne dépend pas de l'atelier.
