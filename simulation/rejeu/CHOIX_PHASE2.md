# Moteur de rejeu, phase 2 : choix d'implémentation

Rédigé le 5 novembre 2026 par Claude, pendant le codage de la phase 2 (`PLAN_EXPERIENCE.md`, 5.10 à 5.17 ; `REGLE.md` et ses lectures datées du 5 novembre). Comme en phase 1, là où le plan laisse un doute, la lecture retenue est la plus simple qui respecte `REGLE.md` et les décisions datées ; chaque choix peut être contesté avant le gel. Le plan, `REGLE.md`, `SUIVI.md`, `JOURNAL_CHANGEMENTS.md` et `banc/` n'ont pas été modifiés ; aucun fichier d'E1 non plus (`gel_e1.py --verifier` : conforme).

## 1. Choix

### Intervalles et simulation de couverture (5.13 ; 5.16, point 5)

| n° | Section du plan | Choix | Raison |
|---|---|---|---|
| 1 | 5.16, point 5 | Quantité simulée : les dégâts en plus pour 100 écritures de « tout approuver », 100 × Σ y ÷ Σ m par tâches, y comptant les erreurs que le validateur aurait arrêtées (u_val ≥ e), avec K = 10 tirages du validateur par répétition ; valeur vraie connue : 100 × (1 − e) × μ. Valeur centrale : sa limite exacte (moyenne des R0 répétitions quand R0 grandit). | « Taux connus » : il faut une quantité dont la vraie valeur est connue. Elle ne dépend pas de l'ordre : les K ordres se réduisent aux K tirages du validateur. |
| 2 | 5.16, point 5 | Paramètres écrits dans `couverture.py` avant le lancement : taux qui décide μ = 0,05 (l'ordre du taux d'alertes du pilote, 7 pour 148 écritures, plan 4.1) ; taux rapportés sans effet sur le choix : 0,01 et 0,20 ; la tâche g compte TAILLES[g mod 10] écritures, de 1 à 32 (moyenne 10,8 ; de un passage Sonnet dans WorkBench à 50 passages Haiku) ; une strate ; 5 000 jeux par case (erreur de Monte-Carlo d'environ 0,36 point à 93 %) ; graine 2026110521. | Le plan demande de les écrire et de les figer avant de lancer. Le taux décide de tout aux petits G : il est ancré sur le seul taux mesuré cité par le plan. |
| 3 | 5.13, (i) | Intervalle normal = valeur centrale ± 1,96 × écart type des répétitions bootstrap ; percentile par les quantiles linéaires de numpy ; réunion des deux. | Lettre de 5.13. |
| 4 | 5.13, (ii) | Bootstrap-t à queues égales ; écart type de chaque répétition par linéarisation du rapport de sommes par grappes (Σ a ÷ Σ d), stratifiée ; t* = ±∞ quand l'écart type d'une répétition est nul et sa valeur différente du centre ; intervalle réduit au centre si l'écart type d'origine est nul. Moyennes sur les configurations : influences des tâches sommées sur les configurations qui partagent le tirage. | « Sur les mêmes répétitions » : la linéarisation ne demande aucun rejeu de plus. La lecture ±∞ est la plus prudente ; voir la contradiction 1. |
| 5 | 5.13, (iii) | Jackknife-t : centre = valeur centrale ; variance jackknife stratifiée (strates du bootstrap ; une strate d'une seule tâche n'apporte rien) ; t à G − 1 degrés de liberté, comme écrit ; chaque valeur = la tâche retirée des K premières colonnes de la couche R0 (mêmes ordres, mêmes tirages attachés aux écritures restantes) ; relance : 4 K colonnes. | Nombres aléatoires communs : sans eux, le bruit des K ordres serait multiplié par G − 1 dans la variance. Voir la contradiction 3 pour les degrés de liberté. |
| 6 | 5.13, repli | Zone qui échoue : G sous le plus petit G simulé à partir duquel la méthode passe à tous les G simulés plus grands ; si elle échoue au plus grand G simulé (90), toutes les cellules sont « fragiles ». | Lecture prudente : aucune extrapolation au-delà de ce qui passe. |
| 7 | 5.13 | Quantité sans écart type linéarisé (proportions de la garantie, fenêtre après la jonction, charge avec épreuves) : intervalle (i) quand la méthode retenue est le bootstrap-t. Seconde méthode de « fragile » : le jackknife-t. | Voir la contradiction 2. |
| 8 | 5.5, point 2.i ; 5.10 ; 5.13 | Le tirage des tâches d'une répétition bootstrap est commun aux trois modèles d'un environnement et aux deux segments d'un scénario (graine sans modèle : code « tous modèles » = 3, scénario 0). Les fonctions de la phase 1 (`suites.suite_bootstrap`) gardent leur tirage par modèle. | 5.10 l'exige pour les segments ; l'unité est la tâche (5.13) : les moyennes sur les configurations et le max-T voient ainsi la corrélation par les tâches. |
| 9 | 5.5, point 4 | Scénario = couple ordonné (X, Y) numéroté de 1 à 6, le même numéro pour les deux modes (comparaison appariée des modes) ; segment de X ordonné avec la graine « ordre » de X, celui de Y avec celle de Y ; validateur et épreuves avec la graine de X et le numéro du scénario. Sensibilités à l'ordre : scénarios 100 (par passage) et 101 (ordre réel). Tirages du hasard apparié et de la résistance attachés aux écritures. | Les sept champs du plan suffisent avec ces codes ; les tirages attachés servent au jackknife. |
| 10 | 5.13, relance | Relance seulement pour les cellules jugées de B-tout (ni « sans objet », ni « tenue, non mise à l'épreuve ») : répétitions B … 4 B − 1 ajoutées (les B premières inchangées), et 4 K ordres pour le jackknife ; les moyennes sur les configurations ne sont pas relancées ; le max-T lit les B premières répétitions. | Une cellule non jugée n'a pas de verdict à relancer (5.14, point 1). |

### Classes et écart de délégation (5.12, point 4 ; 5.13)

| n° | Section du plan | Choix | Raison |
|---|---|---|---|
| 11 | 5.13, « Taux par type » | m (taille d'une tâche pour m̄) compte les mêmes écritures que n (vérifiables et non neutres du type). ρ̂ : grappes = tâches (toutes les parties de la tâche dans la configuration), tous types mérités réunis ; repli par l'environnement : grappes = (modèle, tâche) ; ρ̂ toujours estimé sur toutes les écritures, plafonnées comprises, même pour la version « non plafonnées ». | Σ m = n ; une seule estimation de ρ̂ par configuration, comme écrit. |
| 12 | 5.12, point 4 | « Sans donnée » (n = 0) reste un état à part : traité comme au-dessus par l'oracle, jamais compté « au-dessus » pour la garantie ni « devenu mauvais ». | Choix 28 de la phase 1, gardé. |
| 13 | 5.13 | Modèle bêta-binomial « hiérarchique » : par configuration et type, les tâches comme second niveau ; maximum de vraisemblance de (μ, ρ) ; au bord (aucune erreur) : μ = 0, ρ indéterminée. Descriptif seulement (`ecart.csv`). | Lecture la plus simple de « hiérarchique » : un taux par tâche, tiré d'une loi bêta. |

### Scénarios de changement de modèle (5.10)

| n° | Section du plan | Choix | Raison |
|---|---|---|---|
| 14 | 5.10 ; 5.6, point 7 | Jonction annoncée appliquée juste avant la première écriture de Y : c = 0, L2 = L3 = 0, plus d'allongement ; types moyens et forts : Ec = s (erreurs gardées en mémoire), Ed = 0, attente remise à zéro, numérotation des essais repartie de zéro ; types faibles : s = 0. Une perte du palier 3 à la jonction compte comme un retrait. | Mêmes opérations que `changement_configuration` des références (testé écriture par écriture). |
| 15 | 5.9 ; 5.10 | Une épreuve due après la jonction (convertie, ou restée ouverte en mode silencieux) se passe sur les parties de Y de la tâche du cas (aucune partie à exclure : la partie fautive est celle de X), puis du même outil (par son nom), puis du même type ; avant la jonction, sur celles de X. | « Jouées par le modèle courant » (5.9) ; « les épreuves converties se passent sur des parties de Y » (5.10). |
| 16 | 5.9 | File des cas : Ed d'abord, puis Ec (contradiction 6 de la phase 1, tranchée ainsi dans le plan). | Inchangé. |
| 17 | 5.10, « Mesures » | Retrait : types devenus mauvais, au palier 3 à la jonction ; délai en écritures du type (plafonnées comprises) de la jonction à la perte du palier 3, censuré au nombre d'écritures du type après la jonction ; erreurs passées = erreurs avec dégât exécutées au palier 3 pendant ce délai ; autonomies nouvelles = part des répétitions avec une promotion au palier 3 après la jonction ; temps au palier 3 = part des écritures non plafonnées du type exécutées au palier 3 après la jonction. | Mesures d'E1 (`lignes_par_type`), transposées en écritures du type. |
| 18 | 5.10 ; E1-a, point 1 | Périodes d'autonomie après la jonction : erreur constatée = `erreur_preuve` exécutée au palier 3 dans la période (refusées comprises) ; calculées pour tous les types moyens et forts présents après la jonction ; version retard10 rapportée dans `derive.csv`. | Contrôle du code (RF1) : il doit valoir pour tout type, pas seulement les types devenus mauvais. |
| 19 | 5.12, point 8 | Garantie après la jonction : types « au-dessus » chez Y. Lecture secondaire de « devenu mauvais » : estimation de Y au-dessus de la barre, et pas celle de X. | M7 et B1. |

### Tests de résistance (5.11)

| n° | Section du plan | Choix | Raison |
|---|---|---|---|
| 20 | 5.11, point 2 | rate10 : tirage « résistance » attaché à chaque écriture (u_res < 0,10), parmi les erreurs confirmées, refusées comprises ; les variantes d'épreuve ratent aussi 10 % de leurs erreurs (hachage de la graine de la colonne, du vivier, de la partie et du rang). | Comme E1 (`Jvu = binomiale(J, 0,9)`). |
| 21 | 5.11, point 4 | Ratées groupées : ⌈10 % × G⌉ tâches par colonne (graine fille de « résistance »), toutes leurs erreurs : celles des deux modèles d'un scénario, de toutes les copies du bootstrap, et des variantes d'épreuve de ces tâches. | La tâche est difficile pour le contrôle, quel que soit le modèle ; arrondi au supérieur, le plus sévère. |
| 22 | 5.11, point 3 | retard10 : file de 10 écritures par type (plafonnées comprises dans le décompte), comme `rejouer_reference_e1` ; l'épreuve s'ouvre au constat, avec le cas de l'écriture constatée. | Logique d'E1 (testé contre les références). |
| 23 | 5.11, alerte | Modes : verdicts bruts, rate10, retard10, ratées groupées, e = 0, 2 et 10 % ; échecs = cellules jugées hors budget + périodes à plus d'une erreur constatée ; B-tout comparée à chacune des trois autres règles. | Critère de l'alerte 4.5 d'E1 ; le plan dit « une autre règle ». |

### Mesures, décision et sorties (5.12, 5.14, 5.15)

| n° | Section du plan | Choix | Raison |
|---|---|---|---|
| 24 | 5.12, point 6 | Part du gain de l'oracle calculée si 100 − charge de l'oracle ≥ 1 point. | E1, mesure 4. |
| 25 | 5.13 | Taux de tâches réussies : réunion de Wilson (parties) et du percentile bootstrap par tâches (B tirages), par modèle, environnement et jeu. | Lettre de 5.13. |
| 26 | section 8 ; 5.14, point 6 | « Moins de 30 tâches porteuses » d'une cellule (niveau) : tâches qui portent au moins une écriture au dénominateur du niveau dans le jeu rejoué. Cellule « sans objet » : aucune écriture au dénominateur du niveau (le dégât en plus principal y est nul par construction). | Le dénominateur des « 100 écritures » (Q4 a). |
| 27 | 5.14, point 0 | Une vague sans bilan d'accord (`accord.json`) ne remplit pas le point 0 : le pilote, rodage sans mesure d'accord, donne donc R5. Couverture calculée sur toutes les écritures des suites. | « Chaque vague a fini en relecture gardée… » ; aucun bilan, aucune relecture gardée. |
| 28 | 5.14, point 2 | Témoin battu partout si un dépassement est établi (max-T) ; sinon battu si l'intervalle de la différence moyenne de charge (B-tout − témoin) est tout sous 0. Point 2 non jugé si R4. Les cellules des témoins des scénarios figurent dans les deux modes (même suite, même valeur). | Q6 et B3. |
| 29 | 5.14, points 5 et 6 | Désaccords (« fragile ») comparés cellule par cellule sur les décisions (passe, échoue, indécise) ; une cellule « sans objet » ne se compare pas ; « tenue, non mise à l'épreuve » vaut « passe ». | Sinon un niveau absent d'une moitié et présent dans la réserve ferait un faux désaccord. |
| 30 | 3.2 ; 5.5, point 7 | Échange des rôles : jackknife à strates séparées par pli ; écart type du bootstrap-t = √((se_A² + se_B²) ÷ 4) ; moyennes sur les configurations : moyenne des plis qui ont une configuration délégable ; étiquette calculée sur l'analyse combinée. Toute la réserve : aucune quantité calibrée (oracle sans classes), seul le point 1 est comparé. | Les deux moitiés sont tirées indépendamment. |
| 31 | 5.14, point 6 (Q5) | Sensibilités à l'ordre : couche R0 seulement (valeurs centrales), verdict « non calculé ». | Ce sont des sensibilités, sans intervalle de décision. |
| 32 | 5.15 | En plus des onze CSV du plan : `decision.csv` (points 0 à 6, étiquette, mentions « fragile », alerte). Avertissement en première ligne de chaque CSV (`# AVERTISSEMENT …`), dans `meta.json` et en tête de `RESULTATS.md`. | L'étiquette doit sortir dans une table. |
| 33 | 5.16, point 6 | Partage fictif du pilote : `tirage_public.graine(SHA-256 d'une étiquette de test, SHA-512 d'une étiquette de test)` puis `partager` sur les tâches des 120 parties ; aucune balise interrogée. Sorties dans `simulation/rejeu/sorties_pilote/`. | Demandé ; la valeur de balise de test a le format d'une impulsion du NIST (64 octets). |
| 34 | 5.12, points 1, 2 et 11 | Instrument (alertes, confirmées, levées par motif, décisions obsolètes, couverture sur toutes les écritures et hors effet illisible, tâches retirées) dans `decision.csv` ; dégâts absolus, charge pour 100 écritures, charge totale, dégâts à part et invérifiables exécutées seules : valeurs centrales de la couche R0, dans `budget.csv` et `charges.csv`. | « Rapportée aussi sur les seuls types mérités » : lu comme hors effet illisible (toutes les écritures des suites sont de types mérités). |

## 2. Contradictions et trous relevés dans le plan

1. **Le critère de couverture choisit une méthode qui couvre par des intervalles infinis** (5.13 ; 5.16, point 5). Aucune méthode n'atteint 93 % partout au taux 0,05 ; le repli retient le bootstrap-t (pire couverture 0,721 contre 0,588 et 0,549), mais sa couverture aux petits G vient surtout de bornes hautes infinies (jusqu'à 75 % des jeux à ρ = 0,7 et G = 20 ; 69 % à ρ = 0,9 et G = 40). Conséquence : une cellule jugée de B-tout dont les dégâts en plus viennent d'une seule tâche reçoit une borne haute infinie dès que plus de 2,5 % des répétitions bootstrap n'en contiennent aucune, donc « indécise » ; la relance ne change pas cette proportion ; la cellule compte comme un échec, soit R1. Le critère (couverture seule) ne regarde ni la largeur ni la finitude des intervalles. À trancher par le coordinateur avant le gel : garder ; ajouter un critère de largeur ou de finitude ; ou une autre lecture des répétitions dégénérées du bootstrap-t (elle a été figée avant la simulation : en changer oblige à relancer et à le déclarer).
2. **Garantie et bootstrap-t** (5.13). « Proportions (garantie) : intervalle du bootstrap par grappes, comme les autres mesures » : une part sur les K ordres n'a pas d'écart type linéarisé, le bootstrap-t ne s'y applique pas (choix 7 : méthode (i)).
3. **Degrés de liberté du jackknife-t stratifié** (5.13). Le plan écrit G − 1 ; avec les strates du bootstrap (fichiers de WorkBench), l'usage serait G − H. Appliqué à la lettre.
4. **Tirage commun non écrit** (5.5, point 2.i, contre 5.10 et 5.13). Le plan ne dit pas si le tirage des tâches est commun aux modèles ; 5.10 l'exige pour les deux segments d'un scénario, et les moyennes sur les configurations ne sont correctes qu'avec lui (choix 8).
5. **Variantes d'épreuve sous rate10** (5.11). Le plan ne dit pas si les variantes ratent aussi des erreurs ; E1 le faisait (choix 20).
6. **Lettre complète de Q8 (option A)** : barres et N du point 8, calculés sur le flux avec la part des lectures mesurée au pilote, ne figurent pas dans la configuration figée ; seule la mesure pour 100 actions (option B) est codée (`exces_100_actions` dans `budget.csv`). Voir la section 4.
7. **Hasard apparié dans le jackknife** (5.5, point 7 ; 5.7). Non écrit : la part est celle de la règle sur les K ordres sans la tâche, comme « rejouer toute la procédure ».

## 3. Simulation de couverture (`resultats_couverture/`, lancée une fois)

Graine 2026110521, empreintes de `couverture.py` et `intervalles.py` dans `meta.json` (`python -m rejeu.couverture --verifier` les recompare). Données synthétiques seulement. Couverture minimale sur les six valeurs de ρ, au taux qui décide (0,05) :

| Méthode | G = 20 | G = 40 | G = 90 |
|---|---|---|---|
| (i) bootstrap par grappes, percentile réuni avec normal | 0,588 | 0,706 | 0,839 |
| (ii) bootstrap-t par grappes | 0,721 | 0,919 | 0,946 |
| (iii) jackknife-t par tâche | 0,549 | 0,680 | 0,819 |

- Aucune méthode ne passe partout : repli sur **(ii)**, la meilleure pire couverture ; elle passe à tous les ρ pour G = 90 : la zone qui échoue est G < 90 (« fragile » ; G de la confirmation : aviation 20, banque 39, commerce 46 ; WorkBench 276 hors zone).
- À ρ = 0, les trois méthodes couvrent de 0,916 à 0,954 ; tout se joue sur la corrélation intra-tâche.
- Taux rapportés sans effet : à 0,20, (ii) passe partout (pire 0,937), (i) 0,849, (iii) 0,829 ; à 0,01, aucune méthode ne dépasse 0,23 dans sa pire case (jeux sans erreur).
- Durée : 73 s sur 14 processus.

## 4. Bout en bout sur le pilote (5.16, point 6)

`python -m rejeu.bout_en_bout --pilote` (R0 = B = 2 000, K = 10, graine de développement 20261105), partage fictif du choix 33. Toutes les tables sortent dans `sorties_pilote/` : les onze CSV du plan, `decision.csv`, `meta.json` et `RESULTATS.md`, chacun avec l'avertissement en tête. **Ces chiffres n'ont aucune valeur de preuve.** Le déroulé a seulement été vérifié : étiquette de test R5 (vague du pilote sans bilan d'accord, choix 27) ; B-tout n'atteint jamais le palier 3 sur ces volumes (90 cellules « tenues, non mises à l'épreuve », 90 « sans objet ») ; aucune configuration délégable ; aucune relance. Durée : 14 min 13 s sur un cœur.

## 5. Ce qui reste

- La contradiction 1, à trancher avant le gel. *Tranchée par le plan : Q13 (05/11 au soir, Otsoa) — une cellule indécise ne compte plus comme un échec, R1 exige un dépassement établi ; puis 5.14, point 2 (07/11, Otsoa) — une cellule portée par moins de deux tâches est hors du max-T et n'établit rien. Ligne ajoutée le 09/11, audit avant le gel, O8.*
- Q8, option A (lettre complète) : figer dans `config_rejeu.json` la part des lectures, préparations et doutes mesurée au pilote, puis rejouer B-tout avec les N du point 8.
- Le rejeu final : `bout_en_bout.executer` sait tout faire ; son entrée en ligne de commande ne prévoit que le pilote (`--pilote`). Il faudra y brancher le vrai `partage.json` (tirage public), les relectures de chaque vague et G0. Les suites de l'expérience seront environ cent fois plus longues qu'au pilote (14 min sur un cœur) : à paralléliser (les familles sont indépendantes, sauf les moyennes sur les configurations, calculées tranche par tranche).
- Le temps de la suite de tests est passé d'environ 21 à environ 41 secondes (bout en bout en petit compris).
