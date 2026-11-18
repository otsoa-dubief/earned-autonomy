# Vérification adverse des fiches de lecture (4 nov. 2026)

Méthode : sources re-téléchargées (HTML AWS, PDF arXiv Feng et DeepMind, HTML Anthropic x2 + annexe PDF, PDF Jøsang, XML PMC Hobbs, Europe PMC et Crossref pour les métadonnées). Calculs refaits en Python pur (SPRT exact par programmation dynamique, Bêta exact par binomiale, Clopper-Pearson). Aucune fiche modifiée.
Verdicts : C = confirmée, I = inexacte, X = introuvable.

## 1. aws_autonomie_graduee (texte intégral annoncé)
| Affirmation | Verdict | Preuve |
|---|---|---|
| Fenêtre de 50 actions ; poids 25/20/20/20/15 ; sécurité = plancher indépendant, valeur non donnée | C | « The scoring engine », tableau |
| Paliers 0-40 / 41-70 / 71-90 / 91-100, départ à T1, 2 outils visibles | C | « The tier system » |
| Hystérésis : +5 pour monter, descente au plancher de la plage ; « 96 pour T4, descendre à 90 » | C pour 96. Imprécis pour 90 | Texte : « demotion happens at the range floor itself », plancher de T4 = 91, pas 90. La lecture « 90 » est une interprétation non signalée comme telle (elle l'est pour 96 seulement) |
| Rétrogradation immédiate si sécurité sous plancher ou injection ; un cran ou T1 non précisé | C | « Demotion is immediate » ; « the agent moves down » |
| Barrière de livraison : tout changement de consigne/config/outil ; un seul appel non autorisé en cas adverse fait échouer ; « last known stable version » | C | « The delivery gate » |
| Taux de rejets plafonne la sécurité (30 % -> 70) ; arrêt d'urgence Cedar deny-all ; minimum sur la chaîne de délégation ; pénalité x2 de la fausse assurance ; honeypots sur trajectoire d'outils | C | « Production monitoring and recovery », « pre-execution layer » |
| Pas de résultat de terrain, « starting template » | C | Conclusion |
Fiche fiable. Seule réserve : « descendre à 90 ».

## 2. feng_niveaux_autonomie (texte intégral annoncé)
| Affirmation | Verdict | Preuve |
|---|---|---|
| Ordre L1 opérateur, L2 collaborateur, L3 consultant, L4 approbateur, L5 observateur | C | §3.1-3.5, Table 1 |
| Certificat = niveau maximal, pour (specs + environnement), délivré par un tiers (UK AISI, METR, entreprises), fondé sur agent privé + « autonomy case » | C | §4, §4.2 |
| Renouvellement : changement « peut » invalider ; procédure accélérée si changement mineur | C | §4.2 « Certificate renewal » |
| Évaluation assistée : seuil T non fixé ; jusqu'à 5 tours pour classer L1 ; classement par journal d'implication | C | §5 |
| Questions ouvertes L4 (approbation-tampon, agent mal aligné qui exploite le désengagement, savoir quand demander) ; L5 : seul contrôle = interrupteur d'arrêt | C | §3.4, §3.5 |
| v2 du 28/07/2025, pas de v3 | C | Page arXiv : v1 14 juin, v2 |
| « PDF 14 pages » ; « Tableau 1 absent du texte extrait, non lu » | I | Le PDF fait 16 pages ; le Tableau 1 est à la p. 16 (après la bibliographie). Il confirme les descriptions de la §3 (L4 : « User may specify conditions for seeking approval before agent operates », « failure or high-risk state ») |
Fiche fiable. La « question ouverte » sur le Tableau 1 est levée par cette vérification.

## 3. deepmind_delegation (texte intégral annoncé, avec réserve de coupures)
| Affirmation | Verdict | Preuve |
|---|---|---|
| Réversibilité : exemples (trade, supprimer une base, envoyer un mail externe) « stricter liability firebreaks, steeper authority gradients » | C | §2.2 (i) |
| §4.4 : choix de la réponse « ultimately governed by the task's reversibility » ; irréversible + critique = arrêt ou escalade humaine ; amortissement des mises à jour de réputation, délais avant ré-enchère | C | §4.4 |
| §4.2 : niveau d'autonomie « should not be static » | C | §4.2 |
| §4.6 : réputation = historique public vérifiable ; confiance = seuil privé contextuel ; « portfolio of signed, context-specific credentials » plutôt qu'un score | C | §4.6, Table 3 |
| §4.7 : droits permanents si faible criticité + forte réversibilité (réputation au-dessus d'un seuil) ; juste-à-temps + approbation humaine sinon ; disjoncteurs algorithmiques | C | §4.7 |
| §4.8 : erreur découverte après coup, même hors fenêtre de contestation = mise à jour rétroactive de la réputation | C | §4.8 dernier paragraphe |
| §5.1 : friction contextuelle sans fatigue d'alarme ; §5.3 : planchers de sûreté non contournables | C | §5.1, §5.3 |
| Rien sur le changement de version/modèle du délégué | C | Recherche « model update/new model/fine-tun/retrain » : seules occurrences hors sujet |
| Flux de surveillance L0-L3 ; 11 caractéristiques de tâche | C | §6.1 ; §2.2 (a)-(k) |
Fiche fiable. v1 unique, 12/02/2026 : C.

## 4. anthropic_mesurer_autonomie (texte intégral annoncé, annexe « en entier »)
| Affirmation | Verdict | Preuve |
|---|---|---|
| Auto-approbation ~20 % (<50 sessions) -> >40 % (~750) ; comptes inscrits après le 19/09/2025 ; unité = session | C | §3 + légende Figure 2 |
| Interruptions 5 % (~10 sessions) / ~9 % des tours | C | §3 + légende Figure 3 |
| 87 % / 67 % d'implication humaine (borne haute, note 10) ; 80 % garde-fous, 73 % humain, 0,8 % irréversible (note 14) | C | §5 + notes. À noter : la note 14 écrit « 80 % upper bound on direct human oversight » alors que 80 % est le chiffre des garde-fous ; la fiche le range avec raison comme borne haute, la source se contredit |
| « Plus de deux fois plus » : intro (que les humains n'interrompent) vs corps (que sur tâches minimales) | C | Intro et §4 : divergence réelle |
| Tableau 1 : 35/21/13/12/11 % et 32/17/7/5 % | C | Table 1 |
| Médiane 45 s ; P99,9 <25 -> >45 min ; interne 5,4 -> 3,3 interventions | C | §2 |
| Annexe : 998 481 appels (corrigé du 995 621 le 19/02) ; 1 400 classements sur 200 appels ; 99,0/99,0/99,0/100/90,5/77,5/88,0 % ; humain-dans-la-boucle 100 % / 46 % ; 98,72 % confiance >= 8 ; Claude Code 97,5 % (195/200), 98,5 % (n=201), 164/200 | C | Annexe, Table A1/A2, §Stop reason |
| « Annexe de 8 pages » lue en entier | I | Le PDF de l'annexe fait 29 pages (prompts inclus). Le contenu cité existe bien, mais la taille annoncée est fausse : ne pas écrire « lue en entier » sans l'avoir relue |
Fiche fiable sur les chiffres.

## 5. anthropic_auto_mode (texte intégral annoncé)
| Affirmation | Verdict | Preuve |
|---|---|---|
| « users accept 93% of them anyway » ; ni période ni population | C | §How it works ; aucune précision dans la page |
| Tableau : FPR 8,5 % -> 0,4 % (n=10 000) ; FNR 6,6 % -> 17 % (n=52) ; FNR 1,8 % -> 5,7 % (n=1 000) | C | §Results |
| Règle « 3 consecutive denials or 20 total » = refus du classifieur ; sans `claude -p`, le processus s'arrête | C | §Deny-and-continue |
| Classifieur Sonnet 4.6, deux étages, aveugle au raisonnement ; >20 règles de blocage en 4 groupes ; modification de sa propre config de permissions dans « Degrade security posture » | C | §How it works, §Block rules |
| Comparaison : « arguably a regression » vs approbation manuelle attentive ; Opus 4.6 system card §6.2.1 et §6.2.3.3 ; publié le 25/03/2026, John Hughes | C | Page |
| Variante « tool-calls-only » : FNR le plus bas mais perd l'ancrage ; inclure texte assistant + résultats dégrade la perf | C | §Design decisions |
| IC 17 % sur 52 : « ≈ 8 % à 30 % » | C | Clopper-Pearson recalculé : 9/52 = 17,3 %, IC 95 % [8,2 % ; 30,3 %] |
Fiche fiable.

## 6. tencate_confiance_supervision (annoncée inaccessible, résumé 2020 seul)
| Affirmation | Verdict | Preuve |
|---|---|---|
| Métadonnées 2020 (Acad Med 95(11):1662-1669) et 2005 (Med Educ 39(12):1176-1177), DOI | C | Crossref, Europe PMC |
| Accès : résumé seul, pas de plein texte, 2005 sans résumé | C | Europe PMC : isOpenAccess N, inEPMC N, 2005 abstract = None |
| Contenu « lu » : ordinal, décisions discrètes, ad hoc vs sommatif, rétrospectif vs prospectif avec estimation du risque | C | Résumé 2020 : exactement ces points |
| Contenu présenté comme lu au-delà du résumé ? | Non | Aucun niveau d'échelle ni critère de décision cité. Les limites de l'analogie (stagiaire/agent) sont du raisonnement de l'auteur de la fiche, balisé comme tel |
Fiche honnête.

## 7. lee_see_confiance (annoncée inaccessible, résumé seul)
| Affirmation | Verdict | Preuve |
|---|---|---|
| Métadonnées (Hum Factors 46(1):50-80, PMID 15151155) | C | Europe PMC |
| Contenu du résumé (revue sous 5 angles, confiance guide la dépendance, modèle conceptuel de la dynamique) | C | Résumé |
| Contenu de seconde main présenté comme lu | Non, mais fuite mineure | Les définitions calibration/résolution/spécificité sont marquées « si les définitions du rapport se confirment » : correct. En revanche la question ouverte « le « but » n'est pas observable dans un journal » s'appuie sur la triade performance/processus/but, que la fiche dit elle-même non vérifiée |
Fiche honnête, une phrase à baliser.

## 8. bainbridge_ironies (annoncée inaccessible, aucun contenu)
| Affirmation | Verdict | Preuve |
|---|---|---|
| Métadonnées (Automatica 19(6):775-779, DOI) | C | Crossref : titre, vol. 19, n° 6, pp. 775-779 ; pas de résumé |
| Aucun contenu rapporté | C | Confirmé : rien de seconde main présenté comme lu |
Fiche honnête. (Strauch 2018 cité comme piste : existe, non lu, signalé tel quel.)

## 9. wald_test_sequentiel (annoncée inaccessible ; calculs refaits)
Références : Annals Math. Stat. 16(2):117-186, DOI 10.1214/aoms/1177731118 : C (Crossref ; la fiche disait « de mémoire », c'est juste). Aucun contenu présenté comme lu dans Wald : honnête.
Recalcul (p0 = 2 %, p1 = 10 %, alpha = beta = 5 %) :
| Affirmation | Verdict | Preuve |
|---|---|---|
| ln 19 = 2,944 ; succès -0,0852 ; échec +1,6094 ; 1 échec = 18,9 succès | C | Recalculé |
| 34,58 -> 35 succès depuis zéro ; 53,5 -> 54 après 1 échec | C | Recalculé |
| Rejet depuis zéro : 2 échecs ; 1 ne suffit pas (1,83) | C | 1,83 recalculé |
| Risques exacts : rejet à tort 2,97 % (p=2 %), acceptation à tort 4,89 % (p=10 %) | C | DP : 2,97 % et 4,89 % |
| Taille moyenne : 54,6 (p=2 %), 38,3 (p=10 %), 76,7 (p=5 %), 54 % accepté | C | DP : 54,58 ; 38,30 ; 76,66 ; 54,3 % |
| « Après 100 succès, LLR = -8,5 : il faudrait 7 échecs (+11,3) pour atteindre ln A » | I | Il faut 7,12 échecs, donc **8**. Avec 7 : LLR = +2,75 < 2,944 |
| Remise à zéro partielle : LLR -2,9 -> -1,47 ; 17 succès de plus ; « 1 échec ne rétrograde pas, **2 échecs oui** » | I (partie rétrogradation) | -1,47 + 2 x 1,609 = +1,75 < 2,944 : pas de rejet. Il faut **3** échecs (+3,36). 17 succès : C |
| Remède « plancher à ln B − 1 échec » : « 35 succès restent nécessaires, et **2 échecs rapprochés rétrogradent toujours** » | I | Depuis un plancher à ln B : (2,944+2,944)/1,609 = 3,66, soit **4** échecs. Depuis ln B − 1 échec (-4,55) : 4,66, soit **5** échecs. « 2 échecs » n'est vrai que depuis LLR = 0 (départ neutre). Le « 35 succès nécessaires » n'a pas de sens depuis un plancher situé sous ln B (l'agent est déjà promu) |
| « Ce que ça corrige » : « 1 échec ne révoque pas, 2 échecs rapprochés oui » | I | Idem : vrai depuis zéro seulement ; pour un agent promu (LLR = ln B) il faut 4 échecs sans succès intercalaire |

## 10. josang_reputation_beta (texte intégral annoncé)
| Affirmation | Verdict | Preuve |
|---|---|---|
| Bled 2002, 15th Bled Conf., 17-19 juin, 14 p. | C | PDF |
| alpha = r+1, beta = s+1 ; E = (r+1)/(r+s+2) ; exemple 7/1 -> Beta(8,2), E = 0,8 | C | §2.1-2.2, éq. (2)-(5) |
| Combinaison par addition, indépendance exigée (ne pas compter deux fois la même fonction) | C | §2.4 |
| Oubli §2.6 : facteur lambda, récursif, **appliqué à r et s**, par retour reçu ; « selon la rapidité de changement attendue » | C | §2.6 éq. (12)-(13) |
| Retour fractionnaire (r,s) de poids r+s ; (0,0) sans poids ; centralisé, identité non traitée | C | §2.7, conclusion |
| Tableau Bêta : E, P(q<10 %), borne 95 % (35/0, 30/0, 28/0, 35/1, 15/0, 15/1) | C | Recalcul exact : 2,70/97,75/7,98 ; 3,12/96,18/9,21 ; 3,33/95,29/9,81 ; 5,26/89,64/12,19 ; 5,88/81,47/17,07 ; 11,11/51,82/25,01 |
| 28 succès pour P >= 95 % | C | min r = 28 |
| « 1 échec repousse à environ 50 succès » | I | Minimum exact : **44** succès (s=1) |
| « P(q>10 %) >= 50 % donne un déclencheur rapide (ici r=15, s=1 : 48 %) » | I (exemple) | 48 % < 50 % : l'exemple cité ne déclenche pas. Avec 15/1 le seuil de 50 % n'est pas franchi |
| Plafond 1/(1−lambda) : 20 / 50 / 100 ; plancher d'échec 4,5 % / 1,9 % / 0,98 % | C | Recalculé |
| 30 succès puis 1 échec, lambda = 0,98 : r = 22,3, s = 1, E = 7,9 %, P = 71 % | C | r = 22,27 ; E = 7,91 % ; P = 71,3 % |
| r 30 -> 15 : P = 96,2 % -> 81,5 % ; ~13 succès de plus | C | 81,47 % ; 28−15 = 13 |

## 11. hobbs_priors_commensurables (texte intégral annoncé)
| Affirmation | Verdict | Preuve |
|---|---|---|
| PMC4007051 = Hobbs, Sargent, Carlin, Bayesian Analysis 7(3):639-674, 2012 ; DOI 10.1214/12-BA722 | C | Crossref |
| Hobbs 2011 = Biometrics 67(3):1047-1056, PMC3134568, non lu | C | Europe PMC |
| Prior N(mu0, 1/tau) ; tau grand = emprunt fort ; bornes eta dans [0,05 ; 10] ; sans borne tau -> infini | C | §2.1, §2.3.1 |
| ~83 % de masse du prior de Hobbs 2011 à eta < 0,05 ou > 10 | C | §1 / §2.3.2 |
| Pas de forme fermée Bêta-binomiale ; logistique + Metropolis ; commensurate power prior non étudié (coût de calcul) | C | §4.1.1 ; §1.1 |
| Biais de direction inconnue (Pocock 1976) ; simulations H <= 3, n0 = 60, n = 180 ; « subjective » | C | §2.1, §3, §2.3.2 |
| Calculs a0 (30,3 / 92,6 / 74,9 / 56,5 % ; 68,6 / 92,6 / 85,7 / 75,8 % ; 89,1 / 97,7 / 99,5 %) | C | Recalculés à 0,1 point près |
| « Analogue simple, de moi, non de l'article » | C | Honnêtement balisé |

## Corrections à apporter

### Graves (changent la règle ou le cadre)
1. **wald** : l'affirmation « 2 échecs rapprochés rétrogradent toujours » (remède du plancher) est fausse. Depuis un LLR plafonné à ln B il faut 4 échecs ; depuis ln B − 1 échec, 5. Elle contredit « se perd vite » du CADRE si on la prend pour acquise. Corriger aussi la phrase « à ajouter dans le rapport » (« 1 échec ne révoque pas, 2 échecs oui ») : vrai depuis zéro seulement, pas pour un agent déjà promu. Recalculer le plancher à choisir pour que la rétrogradation arrive en N échecs voulus.
2. **wald** : après remise à zéro partielle (a0 = 0,5, LLR -1,47), il faut 3 échecs pour rejeter, pas 2. Même famille d'erreur.

### À corriger
3. **wald** : « il faudrait 7 échecs » -> 8 (7,12 arrondi à l'entier supérieur).
4. **josang** : « 1 échec repousse à environ 50 succès » -> 44 (minimum exact pour P(q<10 %) >= 95 %).
5. **josang** : l'exemple « r=15, s=1 : 48 % » censé illustrer un déclencheur P(q>10 %) >= 50 % ne le déclenche pas ; reformuler (seuil de 45 % ou autre exemple).
6. **anthropic_mesurer** : « annexe de 8 pages lue en entier » -> le PDF fait 29 pages. Corriger ou relire.
7. **feng** : « 14 pages » -> 16 pages ; le Tableau 1 est lisible (p. 16) ; supprimer la question ouverte correspondante.

### Mineurs
8. **aws** : « descendre se fait à 90 » : le texte dit « au plancher de la plage » (91 pour T4) ; signaler que c'est une lecture.
9. **lee_see** : baliser « le but n'est pas observable dans un journal » comme dépendant de la triade performance/processus/but, non vérifiée.
10. **anthropic_mesurer** : noter que la note 14 attribue « 80 % » à la supervision humaine alors que 80 % est la part des garde-fous (incohérence de la source, la fiche a raison d'en faire une borne haute).

## Compte rendu
- 11 fiches vérifiées contre les sources primaires re-téléchargées ; aucune citation déformée, aucun chiffre de source faux sur les 8 fiches de sources en ligne (AWS, Feng, DeepMind, Anthropic x2, Jøsang, Hobbs) ni sur les chiffres Anthropic/AWS.
- Aucune des trois fiches « inaccessible » (ten Cate, Lee & See, Bainbridge) ne présente de seconde main comme lue ; une phrase de Lee & See à baliser.
- Wald : références justes ; 2 erreurs de calcul qui touchent la règle (vitesse de rétrogradation, remède du plancher) : seules corrections graves.
- Jøsang : 2 erreurs chiffrées (44 et non ~50 ; exemple 48 % qui ne déclenche pas). Tous les autres calculs Bêta et Hobbs confirmés.
- Clopper-Pearson 17 % de 52 : [8,2 ; 30,3] confirmé ; SPRT (35, 54, 2,97 %, 4,89 %, ASN) confirmés.
- Deux erreurs de taille de document (annexe Anthropic 29 p., Feng 16 p.) sans effet sur les chiffres.
- Divergence source à garder : intro vs corps d'Anthropic sur « plus de deux fois plus » (réelle) ; note 14 sur 80 %.
- Verdict global : fiches utilisables ; corriger Wald avant de fixer le plancher dans la règle.
