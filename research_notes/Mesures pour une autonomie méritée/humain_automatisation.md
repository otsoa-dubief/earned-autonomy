# Mesures issues de la recherche humain-automatisation pour accorder/retirer l'autonomie d'un agent IA

Date des notes : 2026-11-04. Méthode : recherche web (résumés/abstracts ; PDF intégraux rarement ouverts). Légende : [LU] = page primaire ouverte ; [RÉSUMÉ] = abstract/notice biblio seulement ; [SEC] = source secondaire ; [NON VÉRIFIÉ] = à ne pas citer sans contrôle. Les passages « Inférences » sont miens, pas des résultats publiés.

## 1. Taxonomies de niveaux/types d'automatisation et critères de choix par fonction

### Takeaway
Sheridan & Verplank (1978) donnent l'échelle de niveaux ; Parasuraman, Sheridan & Wickens (2000) y ajoutent 4 types de fonctions (acquisition, analyse, décision, action) et des critères d'évaluation (conséquences sur la performance humaine d'abord ; fiabilité et coût des erreurs ensuite). La méta-analyse d'Onnasch et al. (2014) montre le compromis central : plus d'automatisation = meilleure perf. de routine mais pire reprise en cas de panne. Pour les agents LLM, Feng et al. (2025) proposent 5 niveaux définis par le rôle de l'humain, et l'idée de « certificat d'autonomie ».

### Cited Findings
- Sheridan & Verplank (1978), « Human and Computer Control of Undersea Teleoperators », rapport MIT Man-Machine Systems Lab, contrat N00014-77-C-0256 ; couvre le contrôle humain en fonction du degré d'automatisation, de l'intégration capteur-commande et des exigences de tâche [RÉSUMÉ] — [NTRL ADA057655](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA057655.xhtml). Le détail exact des 10 niveaux n'a PAS été relu dans l'original (seuls niv. 1, 2, 8 vus via PetroWiki [SEC]) : [PetroWiki](https://petrowiki.spe.org/Levels_of_automation).
- Parasuraman, Sheridan & Wickens (2000), « A model for types and levels of human interaction with automation », IEEE Trans. Systems, Man, Cybernetics Part A 30(3):286-297, DOI [10.1109/3468.844354](https://doi.org/10.1109/3468.844354) [RÉSUMÉ via notices biblio] : 4 classes de fonctions (acquisition d'information, analyse, sélection de décision, mise en œuvre de l'action), chacune sur un continuum manuel-automatique. Critère primaire = conséquences de performance humaine (charge mentale, conscience de la situation, complacence, déqualification) ; critères secondaires = fiabilité de l'automatisation et coût des conséquences décision/action. Source du résumé : [BibBase](https://bibbase.org/network/publication/parasuraman-sheridan-wickens-amodelfortypesandlevelsofhumaninteractionwithautomation-2000) et recherche (échelle 1-10 non relue dans l'original).
- Onnasch, Wickens, Li & Manzey (2014), « Human Performance Consequences of Stages and Levels of Automation: An Integrated Meta-Analysis », Human Factors 56(3):476-488 (DOI non vérifié) [RÉSUMÉ] — [notice TU Berlin](https://depositonce.tu-berlin.de/items/7df9879f-d77b-4f2b-8760-f0e3d174ca67/full) : 18 expériences ; DOA plus haut = bénéfice en routine, dégradation quand l'automatisation échoue (« lumberjack effect »), effet le plus marqué en franchissant la frontière analyse -> sélection d'action. Contesté/nuancé en 2020 : Wickens, Onnasch, Sebok & Manzey, « Absence of DOA Effect but No Proper Test of the Lumberjack Effect » — [notice](https://edoc.hu-berlin.de/items/3f552834-54c7-4b6c-8744-0d0d19553fc2/full).
- Feng, McDonald & Zhang (2025), « Levels of Autonomy for AI Agents », arXiv:2506.12469 (v1 14 juin 2025, v2 28 juil. 2025) [LU abstract] — [arXiv](https://arxiv.org/abs/2506.12469) : 5 niveaux par rôle de l'utilisateur (Operator/Collaborator/Consultant/Approver/Observer selon les sources ; la page ne détaille pas, ordre de la page : Observer, Approver, Consultant, Collaborator, Operator listé « par autonomie croissante » -> incohérence d'ordre entre sources, à vérifier dans le PDF). Thèse : le niveau d'autonomie est un choix de conception distinct de la capacité et de l'environnement ; propose des « certificats d'autonomie » et des premières idées d'évaluation.
- Kaber & Endsley (2004), Theoretical Issues in Ergonomics Science 5(2):113-153 [RÉSUMÉ] — [notice BibBase](https://bibbase.org/network/publication/kaber-endsley-theeffectsoflevelofautomationandadaptiveautomationonhumanperformancesituationawarenessandworkloadinadynamiccontroltask) : niveaux bas = meilleure perf. ; niveaux intermédiaires = meilleure conscience de la situation ; la durée du cycle d'allocation adaptative influence surtout charge subjective et tâche secondaire, peu la perf. primaire/SA.

### Inferences
- Le choix du niveau devrait être par fonction ET par type d'action (lecture/analyse vs action sortante), pas global par agent : la frontière analyse -> action est celle où les coûts de panne explosent (Onnasch 2014).
- Critère « coût de l'erreur/réversibilité » (PSW 2000, critère secondaire) est directement lisible dans les logs (type d'outil, irréversible oui/non) ; la fiabilité est mesurable par fonction, pas par agent.
- Le niveau « Approver » (valider chaque action) n'est pas un niveau sûr par défaut s'il dégénère en clic automatique (voir §3, §6).

### Gaps
- Liste exacte des 10 niveaux de Sheridan & Verplank non vérifiée dans l'original (rapport DTIC/NTIS non ouvert).
- Pas relu : texte intégral de PSW 2000 ; ordre/appellation exacte des 5 niveaux de Feng et al.

## 2. Confiance dans l'automatisation : définition, mesure, calibration

### Takeaway
Lee & See (2004) : la confiance guide la dépendance quand la complexité empêche de tout comprendre ; la bonne cible est la confiance *appropriée* (calibration, résolution, spécificité), pas la confiance maximale. Les questionnaires (Jian et al. 2000) mesurent l'attitude ; les mesures comportementales (dépendance/reliance, conformité/compliance, échantillonnage de l'information) sont les seules lisibles dans des logs, mais leur interprétation est débattue.

### Cited Findings
- Lee & See (2004), « Trust in Automation: Designing for Appropriate Reliance », Human Factors 46(1):50-80, DOI [10.1518/hfes.46.1.50_30392](https://doi.org/10.1518/hfes.46.1.50_30392) [RÉSUMÉ] — [PubMed](https://pubmed.ncbi.nlm.nih.gov/15151155/) : trois composantes de la confiance appropriée = calibration (confiance vs capacité réelle), résolution (la confiance varie-t-elle avec la capacité réelle ?), spécificité (confiance différenciée par fonction/contexte/dans le temps) [SEC sur les trois noms : [arXiv 2311.06305 revue systématique](https://arxiv.org/pdf/2311.06305)] ; bases de la confiance = finalité, processus, performance [SEC] ; mésusage (sur-dépendance) vs désusage (rejet).
- Jian, Bisantz, Drury & Llinas (2000), « Foundations for an Empirically Determined Scale of Trust in Automated Systems », Int. J. Cognitive Ergonomics 4(1):53-71 ; rapport AFRL-HE-WP-TR-2000-0102 [RÉSUMÉ] — [DTIC ADA395339](https://apps.dtic.mil/sti/pdfs/ADA395339.pdf) : échelle issue d'une analyse en grappes de mots (12 facteurs). Non validée par les auteurs eux-mêmes ; biais positif relevé : Gutzwiller et al. (2019), « Positive bias in the Trust in Automated Systems Survey? » — [notice](https://www.sciencegate.app/document/10.1177/1071181319631201).
- Hoff & Bashir (2015), Human Factors 57(3):407-434, DOI [10.1177/0018720814547570](https://doi.org/10.1177/0018720814547570) [RÉSUMÉ] — [notice](https://experts.illinois.edu/en/publications/trust-in-automation-integrating-empirical-evidence-on-factors-tha/) : revue systématique 2002-2013 (101 articles, 127 études) ; trois couches : confiance dispositionnelle, situationnelle, apprise.
- Compliance vs reliance (Meyer 2004) : deux réponses comportementales à une alerte binaire (suivre le signal / s'abstenir de précautions en l'absence de signal) [SEC] — [Berlin, Measures of Reliance and Compliance](https://depositonce.tu-berlin.de/items/1abacf5b-8cb9-47cf-971d-d737176d3622/full). Débat : Dixon, Wickens & McCarley (2007) trouvent les deux non indépendantes ; Chancey et al., Human Factors 59(3):333-345 (en ligne 2016, papier 2017) : fausses alarmes -> compliance, omissions -> reliance, mais concluent que le paradigme ne reflète pas deux types de confiance [SEC] — [Chancey notice](https://cir.nii.ac.jp/crid/1361137045748632832).
- Revue systématique « Fostering appropriate trust in human-AI interaction » (arXiv 2023) [SEC, non lue] — [arXiv:2311.06305](https://arxiv.org/pdf/2311.06305). Bibliométrie 24 ans de recherche sur la confiance dans l'IA — [arXiv:2309.09828](https://arxiv.org/pdf/2309.09828) [titre vu seulement].

### Inferences (mesures dans les logs d'agent)
- Questionnaire : seulement ponctuel (Jian = biaisé, non validé) ; pas pour piloter en continu.
- Comportemental, lisible dans les logs : (a) taux d'acceptation par catégorie d'action = proxy de dépendance, mais SANS lecture de qualité ; (b) taux d'acceptation conditionnel à la qualité *réelle* de la proposition (nécessite un étalon : résultat vérifié a posteriori) = calibration/résolution au sens Lee & See ; (c) variation du taux d'acceptation entre catégories (spécificité). Avec 1 refus sur 83, la résolution est non estimable : si les propositions erronées sont rares, un humain qui valide tout paraît « bien calibré » sans l'être.
- Calcul perso (Wilson 95 %) : 1 refus / 83 -> taux de refus 1,2 % [intervalle env. 0,2 % à 6,5 %] : trop large pour distinguer un contrôle efficace d'un contrôle inexistant.

### Gaps
- Seuils chiffrés de « bonne calibration » : aucun consensus trouvé.
- Lee & See : texte intégral non lu par moi (copies : [OSU](https://csel.eng.ohio-state.edu/productions/intel/research/trust/Lee%20%26%20See%20Trust%20Review.pdf), [Aalto](https://mycourses.aalto.fi/pluginfile.php/1903876/course/section/223217/Lee%20and%20See%20-%202004%20-%20Trust%20in%20Automation%20Designing%20for%20Appropriate%20Rel.pdf)) ; définitions de calibration/résolution/spécificité à vérifier mot à mot.
- DOI de Jian 2000 et d'Onnasch 2014 non confirmés ici.

## 3. Complaisance et biais d'automatisation : détection, signaux de validation « tampon »

### Takeaway
Parasuraman & Manzey (2010) : complaisance et biais d'automatisation sont des manifestations qui se recoupent, centrées sur l'attention, présentes chez novices ET experts, non supprimées par la pratique. Détection classique = échantillonnage de l'information (le superviseur vérifie-t-il les sources ?) et erreurs d'omission/commission face à une aide fautive. Les signaux « validation tampon » (taux ~100 %, temps de réponse court) sont des indices plausibles mais aucune source trouvée ne fixe un seuil validé.

### Cited Findings
- Parasuraman & Manzey (2010), « Complacency and Bias in Human Use of Automation: An Attentional Integration », Human Factors 52(3):381-410, DOI [10.1177/0018720810376055](https://doi.org/10.1177/0018720810376055) [RÉSUMÉ] — [PubMed](https://pubmed.ncbi.nlm.nih.gov/21077562/) ; [TU Berlin](https://depositonce.tu-berlin.de/items/0c787d91-6021-480b-a333-009e0d1d0092/full) : complaisance surtout sous charge multi-tâche ; biais d'automatisation = erreurs d'omission et de commission avec aides imparfaites ; modèle intégré personnel/situationnel/automatisation.
- Bahner, Hüper & Manzey (2008), « Misuse of automated decision aids: Complacency, automation bias and the impact of training experience », Int. J. Human-Computer Studies 66:688-699 [SEC, non relu] : complaisance mesurée par l'échantillonnage d'information (proportion de paramètres pertinents consultés) comparée entre ceux qui commettent/ne commettent pas une erreur de commission, reproduit dans PM 2010 — [recherche, voir ConfCore](https://core.ac.uk/download/187203048.pdf). Compagnon : Bahner, Elepfandt & Manzey (2008) : faire vivre des pannes d'automatisation à l'entraînement réduit la complaisance envers la fonction d'alarme et les erreurs d'omission, mais pas les erreurs de commission [SEC, même source de recherche].
- Moray & Inagaki, « Attention and complacency », Theoretical Issues in Ergonomics Science 1(4):354-365 (daté 2000 ou 2001 selon les listes) [SEC] — [revue Frontiers 2019](https://www.frontiersin.org/articles/10.3389/fpsyg.2019.00225/pdf) : complaisance définissable seulement par comparaison du comportement d'échantillonnage à celui d'un « observateur rationnel » ; définir la complaisance par l'erreur est critiqué comme circulaire.
- Buçinca, Malaya & Gajos (2021), « To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI in AI-assisted Decision-making », Proc. ACM HCI 5(CSCW1), arXiv [2102.09692](https://arxiv.org/abs/2102.09692) [RÉSUMÉ] — [page Harvard](https://www.eecs.harvard.edu/~kgajos/papers/2021/bucinca2021trust.shtml) : 199 participants ; les « cognitive forcing functions » (ex. forcer à décider avant de voir l'avis de l'IA, délai) réduisent la sur-dépendance mais sont les moins appréciés ; bénéfice plus grand pour fort Need for Cognition (équité).
- Passi & Vorvoreanu (2022), « Overreliance on AI: Literature Review », Microsoft Research MSR-TR-2022-12 (~60 articles : développement, mesure, conséquences, mitigation) [SEC] — [MSR](https://www.microsoft.com/en-us/research/?p=854967) ; suivis : MSR-TR-2024-7 (GenAI, ~50 articles) et MSR-TR-2025-4 (certaines mitigations peuvent se retourner contre l'objectif) — [MSR 2025](https://www.microsoft.com/en-us/research/?p=1133469). Non lus en détail.

### Inferences (signaux de tampon dans les logs d'approbation)
Aucun seuil publié trouvé ; indicateurs candidats, à calibrer sur données propres :
- Taux d'approbation proche de 100 % (ici 82/83 = 98,8 %) : NON discriminant seul, car un agent bon produit aussi ce taux ; à lire conjointement avec la proportion de propositions réellement défectueuses (Bahner : l'humain n'est « complaisant » que si ses vérifications diminuent alors que l'automatisation reste faillible).
- Délai de réponse : temps entre notification et clic, comparé au temps de lecture plausible du contenu (longueur du texte/diff). Distribution (médiane, part < N secondes), dérive dans le temps, variance par catégorie d'action.
- Accès au contenu : ouverture du détail/déroulé avant clic (équivalent log de l'échantillonnage d'information, la mesure de Bahner/Moray).
- Rafales : approbations en lot, plusieurs clics en < 1 s, approbations hors heures de bureau.
- Épreuves de vigilance injectées (« canaris ») : proposition volontairement défectueuse insérée à fréquence faible et connue du système ; taux de détection = mesure directe de la complaisance (analogue des mesures d'omission/commission), à éthiquement cadrer et à ne pas l'appeler « incident ».
- Le taux d'acceptation de ~93 % dans Claude Code (Anthropic, mars 2026) montre que ce niveau est typique sans protocole : voir §6.

### Gaps
- Aucune source trouvée donnant un seuil validé de temps de réponse ou de taux d'approbation pour classer un approbateur comme « tampon ».
- Bahner 2008 et Moray & Inagaki : textes non lus.

## 4. Ironies of Automation (Bainbridge 1983) et implications pour l'approbation humaine

### Takeaway
Bainbridge : automatiser la majorité de la tâche laisse à l'humain les cas les plus durs et l'empêche de garder la compétence/vigilance pour les exercer. Appliqué aux agents : l'approbation d'actions rares et presque toujours justes est le cas typique de supervision de vigilance qui se dégrade.

### Cited Findings
- Bainbridge (1983), « Ironies of Automation », Automatica 19(6):775-779, DOI [10.1016/0005-1098(83)90046-8](https://doi.org/10.1016/0005-1098(83)90046-8) [SEC : biblio concordante, texte non lu par moi] — [copie PDF gwern](https://gwern.net/doc/sociology/technology/1983-bainbridge.pdf) ; [Wikipédia](https://en.wikipedia.org/wiki/Ironies_of_Automation). Thèse : l'automatisation peut accroître les difficultés de l'opérateur ; l'humain est chargé de ce qui n'est pas automatisable. Retrospective citée : ~1800 citations en 2016 (Strauch).
- Effet lumberjack (Onnasch 2014, cf. §1) : plus d'automatisation -> pire reprise en cas de panne [RÉSUMÉ] — [notice](https://depositonce.tu-berlin.de/items/7df9879f-d77b-4f2b-8760-f0e3d174ca67/full).

### Inferences
- Les mécanismes classiques (vigilance, perte de compétence, sortie de la boucle) prédisent que la qualité de l'approbation baisse avec la durée d'une série de réussites : mesure longitudinale à suivre (délai, ouverture du contenu, détection de canaris) plutôt que taux de refus.
- Un humain qui n'est jamais mis en situation d'exercer le jugement (aucune proposition ambiguë) ne peut pas reprendre la main quand il faut : prévoir des exercices/bascules régulières en manuel (idée à confronter aux « cognitive forcing » de Buçinca).
- Je n'ai pas relu le texte de Bainbridge : les points ci-dessus (vigilance, déqualification) viennent de ma connaissance du texte, à vérifier dans la copie PDF.

### Gaps
- Textes de suivi de Bainbridge (retrospectives IEEE/ACM) non ouverts.

## 5. Automatisation adaptative : déclencheurs et métriques

### Takeaway
La littérature distingue l'automatisation *adaptable* (l'opérateur décide de déléguer) et *adaptative* (le système ajuste le niveau). Déclencheurs classiques : événements critiques, mesure de performance de l'opérateur, modèle de l'opérateur, mesure physiologique, méthodes hybrides.

### Cited Findings
- Taxonomie des déclencheurs attribuée à Parasuraman et al. (1992) : événements critiques, performance de l'opérateur, modélisation de l'opérateur, physiologie, hybrides ; Scerbo (1996) pour le modèle d'événements critiques [SEC] — [Bailey et al., NASA NTRS](https://ntrs.nasa.gov/api/citations/20040084079/downloads/20040084079.pdf). Auteurs de Parasuraman 1992 non confirmés par cette recherche.
- Les événements critiques ignorent les ressources disponibles de l'opérateur [SEC, même source] ; les mesures physiologiques ne dépendent pas des réponses visibles [SEC].
- Revue citée dans un rapport OSTI : seuls deux mécanismes améliorent la performance de façon constante en laboratoire — délégation initiée par l'opérateur (délégation hiérarchique de tâches) et mesure EEG d'engagement [SEC] — [OSTI 1165505](https://www.osti.gov/biblio/1165505).
- Kaber & Endsley (2004) : la fréquence/durée des cycles d'adaptation pèse sur charge subjective et tâche secondaire (cf. §1).

### Inferences
- Pour un protocole d'autonomie « méritée » : l'équivalent de l'adaptable = l'organisation délègue explicitement (octroi) ; l'équivalent de l'adaptatif = retrait automatique sur déclencheur. Déclencheurs transposables aux logs : événements critiques (incident, bloc de garde-fou franchi/évité de justesse), performance de l'agent (taux de blocs automatiques, retours en arrière), état de l'humain (charge d'approbations par heure, rafales). Le déclencheur « physiologique » n'a pas d'équivalent ; remplaçable par signaux d'engagement (délai, ouverture du contenu).
- Cycles trop fréquents d'octroi/retrait coûtent en charge (Kaber & Endsley) : prévoir hystérésis (seuil de retrait plus sensible que seuil d'octroi, durée minimale).

### Gaps
- Pas de source primaire lue sur Scerbo 1996 / Parasuraman 1992 (références exactes à retrouver). Aucune étude appliquée à des agents LLM trouvée sur ce point.

## 6. Travaux 2023-2026 sur agents LLM : calibration, sur-dépendance, fatigue d'approbation

### Takeaway
Les données publiques récentes confirment le phénomène (utilisateurs acceptent ~93 % des invites ; l'auto-approbation augmente avec l'expérience tout en s'accompagnant de plus d'interruptions) et les premières modélisations traitent la capacité de l'humain comme une ressource finie. Aucune validation expérimentale humaine du « seuil de fatigue » trouvée.

### Cited Findings
- Anthropic (25 mars 2026), « Claude Code auto mode » [LU] — [anthropic.com/engineering/claude-code-auto-mode](https://www.anthropic.com/engineering/claude-code-auto-mode) : « les utilisateurs acceptent 93 % [des invites] de toute façon » ; l'approbation systématique mène à la fatigue d'approbation (les gens cessent de prêter attention) ; classifieurs à deux étages (taux de faux positifs 0,4 % sur n=10 000 trafic interne ; premier étage seul 8,5 % ; faux négatifs 17 % sur actions « trop zélées » réelles) ; repli sur l'humain après 3 refus consécutifs ou 20 refus au total. (Chiffre 97 % cité par des sources secondaires non retrouvé dans la source primaire : écarter.)
- Anthropic (18 févr. 2026), « Measuring AI agent autonomy in practice » [LU] — [anthropic.com/research/measuring-agent-autonomy](https://www.anthropic.com/research/measuring-agent-autonomy) : auto-approbation intégrale ~20 % des sessions pour <50 sessions, >40 % vers 750 sessions ; interruptions ~5 % des tours (~10 sessions) vs ~9 % (expérimentés) ; interventions humaines par session 5,4 -> 3,3 (usage interne, août-déc.) ; durée de tour médiane ~45 s, 99,9e percentile >45 min ; l'agent s'arrête pour demander plus de deux fois plus souvent que l'humain n'interrompt sur tâches complexes ; classifications générées par Claude, non vérifiables manuellement ; Claude Code seul, surtout génie logiciel. Utile comme jeu de métriques d'autonomie observée (durée de tour, taux d'auto-approbation, taux d'interruption, arrêts initiés par l'agent), pas comme preuve de bonne supervision.
- Turan (8 juin 2026), « Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human », arXiv [2606.08919](https://arxiv.org/abs/2606.08919) [LU abstract] : fatigue du relecteur modélisée comme croissant avec la charge d'escalade ; accord inter-relecteurs sur le risque modéré (kappa de Fleiss = 0,52 sur 125 actions étiquetées) ; sécurité réalisée en U inversé selon le taux d'escalade (trop d'escalades peut dégrader la sécurité) ; attaque par inondation. Résultats de simulation/modélisation, étude humaine à venir (non validé sur des relecteurs humains). Auteur unique, preprint.
- Feng et al. 2025 (cf. §1) : niveaux et « certificats d'autonomie » — [arXiv](https://arxiv.org/abs/2506.12469).
- Autres preprints cités par une source secondaire, NON OUVERTS : arXiv 2505.11579 (Dimensional Governance), 2506.12482 (TAO), 2510.09781 (Safiron), 2601.10156 (ToolSafe) — [NON VÉRIFIÉ].
- Sur-dépendance IA : Buçinca et al. 2021 ; Passi & Vorvoreanu 2022 ; MSR 2024/2025 (cf. §3).

### Inferences
- Le pilote (98,8 % d'approbations, 1 refus ; 702 blocs automatiques ; 17 incidents) est cohérent avec le ~93 % d'Anthropic : l'indicateur « nombre d'approbations/de refus » est peu informatif, il mesure surtout la sélectivité de l'agent à ne demander que les cas faciles.
- Les 702 blocs automatiques sont l'indicateur le plus riche : ils mesurent la fréquence à laquelle l'agent tente des actions hors cadre. Un taux de blocs par tâche (702/216 ≈ 3,25) en baisse = apprentissage ou contournement ? Besoin de les classer (tentative légitime / dangereuse / bruit).
- Mesures candidates dérivables des logs, avec leur famille d'origine : durée de tour et arrêts initiés par l'agent (Anthropic 2026) ; part des actions par catégorie de réversibilité (PSW 2000, Onnasch) ; délai d'approbation et ouverture du contenu (Moray, Bahner) ; détection de canaris (Parasuraman & Manzey) ; charge d'approbation par heure et rafales (Turan) ; hystérésis (Kaber & Endsley).

### Gaps
- Aucune étude à pairs sur l'approbation de *plans/actions d'agents LLM* avec mesure du temps de réponse trouvée en cette session ; recherche limitée (une requête arXiv sur ce thème).
- Revue systématique 2023 (arXiv 2311.06305) et bibliométrie 2023 (arXiv 2309.09828) non lues.
- Non traité : travail 2024-2026 sur la calibration de la confiance des utilisateurs envers des assistants LLM (expressions d'incertitude, etc.) — non cherché faute de budget d'outils.
