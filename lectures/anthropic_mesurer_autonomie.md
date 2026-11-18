> **Corrections après relecture indépendante (4 novembre, détail dans `_verification.md`)** : l'annexe technique fait 29 pages, pas 8 : l'étendue réelle de la lecture de l'annexe est à confirmer ; les chiffres vérifiés dans la fiche restent confirmés par la relecture.

# Anthropic, « Measuring AI agent autonomy in practice » (fiche de lecture)

## Référence
- Miles McCain, Thomas Millar, Saffron Huang, Jake Eaton, Kunal Handa, Michael Stern, Alex Tamkin, Matt Kearney, Esin Durmus, Judy Shen, Jerry Hong, Brian Calvert, Jun Shern Chan, Francesco Mosconi, David Saunders, Tyler Neylon, Gabriel Nicholas, Sarah Pollack, Jack Clark, Deep Ganguli (équipe Societal Impacts).
- « Measuring AI agent autonomy in practice », publié le 18 février 2026. https://www.anthropic.com/research/measuring-agent-autonomy
- Annexe PDF « Appendix to Measuring AI agent autonomy in practice », février 2026, corrigée le 19/02 (taille d'échantillon 995 621 devenue 998 481) : https://www-cdn.anthropic.com/files/4zrzovbb/website/55e4d2de6eb39b3a9259c3f74843f86b1a12e265.pdf
- **Accès : texte intégral lu** (page, notes de bas de page 1 à 16, annexe de 8 pages en entier : prompts, validation, méthode). Le titre de la page est « in practice » ; le rapport cite « Measuring AI agent autonomy » sans ce suffixe (sans conséquence).
- Note de méthode : l'outil de lecture a d'abord rendu des résumés ; le texte brut a ensuite été récupéré (HTML et PDF) et lu directement. Les chiffres ci-dessous viennent de ce texte brut.

## Ce que dit la source

### Méthode et données
- Définition d'agent : un système d'IA muni d'outils qui lui permettent d'agir (introduction, « Studying agents in the wild »). Unité d'analyse API : l'appel d'outil isolé.
- **Deux sources.** (1) API publique : échantillon aléatoire de **998 481 appels d'outil**, du 19 janvier au 2 février 2026 (annexe). Exclut les clients à rétention zéro et ceux dont l'usage n'est pas permis pour l'analyse agrégée. Chaque appel est classé par claude-sonnet-4-5, température 0,2, avec le prompt système et le contexte précédent. (2) Claude Code : sessions interactives, liées de bout en bout ; échantillons de 500 000 interruptions, 500 000 questions et 500 000 sessions sur la même période.
- **Comment les actions sont classées** (annexe) : un modèle attribue à chaque appel un risque 1-10, une autonomie 1-10, une complexité du but (5 niveaux), un type d'environnement, un impact (observation / mineur / intermédiaire / complet), la présence d'un humain dans la boucle, la **réversibilité** (facilement réversible / réversible avec effort / irréversible / sans objet), les garde-fous, l'architecture, une confiance 1-10. Les clusters sont des regroupements automatiques ; ceux sous un seuil de volume (appels ou clients) sont exclus (note 15).
- Les scores de risque et d'autonomie sont « des indicateurs comparatifs plutôt que des mesures précises » (note 13).

### Chiffres exacts avec leur définition
- **Durée de tour** (Claude Code) : médiane environ 45 s (entre 40 et 55 s sur quelques mois). Percentile 99,9 : de moins de 25 min (octobre 2025) à plus de 45 min (janvier 2026). Le texte parle aussi de ~42 min en comparaison avec METR. Baisse depuis mi-janvier (section 2).
- Interne Anthropic, août à décembre : taux de réussite sur les tâches les plus dures doublé, interventions humaines par session de 5,4 à 3,3 (section 2, note 7 : classement par Claude).
- **Auto-approbation** (section 3) : les nouveaux utilisateurs (moins de 50 sessions) utilisent l'auto-approbation complète dans **environ 20 % des sessions** ; **plus de 40 % vers 750 sessions**. L'unité est la session, pas l'action. Réserve : par défaut Claude Code exige l'approbation de chaque action, donc une partie de la hausse est un réglage de confort. Population : comptes inscrits après le 19 septembre 2025.
- **Interruptions** (section 3) : utilisateurs d'environ 10 sessions, **5 % des tours** interrompus ; utilisateurs expérimentés, **environ 9 % des tours**. Intervalle de Wilson 95 % dans la figure ; la courbe se stabilise peut-être, les intervalles s'élargissent aux fortes anciennetés.
- **Implication humaine selon la complexité** (API) : 87 % des appels de tâches minimales ont une forme d'implication humaine, contre 67 % pour les tâches très complexes. Cette estimation est une **borne haute** (note 10).
- **Arrêts initiés par l'agent** (section 4) : sur les tâches les plus complexes, Claude Code demande des précisions **plus de deux fois plus souvent que sur les tâches minimales**, et plus souvent que l'humain n'interrompt ; n = 500 000 sessions, IC 95 % inférieur à 0,9 % partout. Attention : l'introduction écrit « plus de deux fois plus souvent que les humains n'interrompent » ; le corps du texte écrit « plus de deux fois plus que sur les tâches minimales ». Les deux phrases ne disent pas la même chose. Aucun taux absolu n'est donné dans le texte.
- Raisons de l'arrêt par l'agent (tableau 1, classées par Claude, échantillon 500 000) : proposer un choix entre approches 35 %, recueillir un diagnostic 21 %, clarifier une demande vague 13 %, demander des accès 12 %, demander une approbation avant d'agir 11 %. Raisons des interruptions humaines : fournir un contexte ou une correction 32 %, agent lent ou bloqué 17 %, l'humain veut faire l'étape suivante 7 %, changer les exigences 5 %. Listes non exhaustives.
- **API publique, risque** (section 5, note 14) : **80 %** des appels viennent d'agents qui semblent avoir au moins un garde-fou (borne haute) ; **73 %** semblent avoir un humain dans la boucle (borne haute) ; **0,8 %** des actions semblent **irréversibles** (exemple : envoyer un mail à un client). Génie logiciel : près de 50 % des appels.
- Le texte ne publie ni taux de refus humain, ni taux d'erreur de l'agent, ni fréquence d'actions irréversibles réellement exécutées avec erreur.

### Qualité de la classification (annexe, validation manuelle)
- 1 400 classements sur **200 appels d'outil**, notés par l'équipe Societal Impacts (pas de vérité terrain indépendante, pas de matrice de confusion).
- Exactitude : risque 99,0 % et autonomie 99,0 % (à ±1 point), domaine 99,0 %, réversibilité 100 %, garde-fous présents 90,5 %, humain dans la boucle 77,5 %, complexité 88,0 %.
- **Humain dans la boucle** : quand le modèle dit « pas d'humain », il a raison à 100 % ; quand il dit « humain », il n'a raison que dans **46 %** des cas de l'échantillon (il prend des tours « Human » programmatiques pour un vrai humain). Échantillon biaisé par des transcriptions d'apprentissage par renforcement.
- **Réversibilité 100 %** mais l'échantillon est concentré sur « sans objet » et « facilement réversible » : signal limité sur les cas graves.
- **Garde-fous** : échantillon presque sans cas « sans garde-fou » ; plus de confiance sur la présence que sur l'absence.
- Claude Code : motif d'arrêt 97,5 % d'accord (195/200), complexité 98,5 % (n = 201). Les interruptions « humaines » sont rares dans l'échantillon validé (164 sur 200 tours terminés normalement).
- Confiance déclarée par le classifieur : 98,72 % des classements à 8 ou plus.

### Limites reconnues (section 6 « Limitations » et notes)
- Un seul fournisseur de modèle.
- Deux sources incomplètes : API sans sessions (appels isolés), Claude Code complet mais produit unique, surtout logiciel ; les résultats forts viennent de Claude Code et peuvent ne pas se généraliser.
- Classements faits par Claude, sans inspection manuelle possible (vie privée) ; des garde-fous peuvent exister hors de vue.
- Fenêtre de temps limitée (fin 2025 à début 2026).
- Échantillonnage par appel : les flux à nombreux appels sont surreprésentés.
- Pas de distinction production / évaluation : plusieurs clusters à haut risque semblent être des évaluations de sécurité ; des actions peuvent être simulées.
- Note 9 : le logiciel est facile à vérifier (on teste, on compare) ; dans les domaines où vérifier demande autant d'expertise que produire, le glissement vers la supervision pourrait être plus lent. Note 16 : idem pour droit, médecine, finance.
- Note 4 : l'autonomie « n'est pas une propriété fixe du modèle mais une caractéristique émergente d'un déploiement » (modèle, comportement de l'utilisateur, produit). Pas de définition formelle.

### Règles de retour à l'humain et recommandations (section 7)
- Pas de règle chiffrée de retour à l'humain. Recommandations : surveillance après déploiement, entraîner les modèles à reconnaître leur incertitude, donner aux utilisateurs une visibilité et des moyens simples d'intervenir, ne pas imposer de schéma d'interaction (par exemple approuver chaque action) ; viser « que les humains soient en position de surveiller et d'intervenir ».
- Citation : « effective oversight doesn't require approving every action but being in a position to intervene when it matters » (section 3).

## Ce que ça change pour notre règle (propositions, rien de décidé)
1. **Journaliser la réversibilité et l'impact de chaque action**, avec les mêmes catégories qu'Anthropic (observation / mineur / intermédiaire / complet ; facilement réversible / avec effort / irréversible / sans objet). Cela rend notre taxonomie comparable à la seule publication de terrain.
2. **Journaliser trois fois la relecture** : délai, ouverture du détail, décision. Anthropic ne mesure aucun de ces trois points ; cela correspond au trou à combler. L'unité « session en auto-approbation » est trop grossière pour notre rejeu.
3. **Séparer les arrêts de l'agent des interruptions humaines** dans nos journaux, avec le motif (choix entre approches, accès manquant, demande d'approbation, clarification). L'agent qui s'arrête de lui-même est un signal de sûreté à compter en positif, cohérent avec notre principe « un doute signalé ne coûte rien ».
4. **Relecture humaine** : le texte montre que l'humain qui approuve beaucoup n'est pas forcément inattentif (il interrompt plus avec l'expérience), mais sans mesure d'attention. Proposition : ne pas utiliser le taux d'acceptation seul comme preuve ; ajouter les interruptions en cours d'exécution et les corrections ultérieures.
5. **Marquer l'étiquetage comme automatique ou manuel** : la validation d'Anthropic (200 appels) montre qu'un classifieur surestime l'humain présent (46 % de justesse) et reste peu testé sur les actions graves. Si nous étiquetons les incidents par modèle, journaliser aussi un échantillon relu à la main.
6. **Retour à l'humain** : le texte ne fixe pas de seuil, il recommande de ne pas exiger l'approbation de chaque action. Notre règle peut s'inspirer de l'idée « être en position d'intervenir » : visibilité, arrêt simple, journal lisible.
7. **Baser les paliers sur l'ancienneté** est une pratique d'usage (20 % puis 40 % des sessions en auto), pas une règle de sûreté. Rien ici ne justifie un seuil en nombre de sessions.

## Ce que ça corrige dans le rapport
- **« 93 % »** : le chiffre n'est pas dans cette source ; il vient du billet auto mode. Voir la fiche `anthropic_auto_mode.md`.
- **« environ 20 % des sessions pour les nouveaux utilisateurs, plus de 40 % vers 750 sessions »** : exact. À préciser : « nouveaux » = moins de 50 sessions ; l'unité est la session en auto-approbation complète ; une partie du mouvement est un réglage de confort (le défaut impose l'approbation) ; comptes inscrits après le 19/09/2025.
- **« 5 % des tours chez les novices, 9 % chez les expérimentés »** : exact. À préciser : « novices » = environ 10 sessions ; le texte ne donne pas de nombre de sessions pour « expérimentés » ; l'unité est le tour.
- **« Ces classifications ont été générées par un modèle et ne sont pas vérifiables manuellement, ce qui en fait des ordres de grandeur »** : imprécis. Vrai pour risque, autonomie, réversibilité, humain, garde-fous (API) et pour les motifs d'arrêt. Mais l'annexe documente une validation manuelle de 200 appels (99 % sur risque et autonomie, 46 % de justesse quand le classifieur dit « humain présent »), et la limite exacte est que les données brutes ne peuvent pas être inspectées. Le texte ne dit pas comment sont calculés les taux d'auto-approbation et d'interruption ; ne pas les ranger sans vérification parmi les « classifications générées par un modèle ».
- **« arrêts initiés par l'agent, que la firme présente comme une propriété de sécurité »** : exact, mais incomplet : « plus de deux fois plus que sur les tâches minimales », avec des réserves explicites (peut-être pas aux bons moments, questions inutiles, effet du mode Plan).
- **Le chiffre « 0,8 % d'actions irréversibles »** (que la demande du chef de projet dit être dans le rapport) **n'apparaît pas dans le corps du rapport relu** ; il manque. Définition à ajouter : appels d'outil de l'API publique, classés par modèle, 998 481 appels, 19 janvier au 2 février 2026 ; exemple « envoyer un mail à un client » ; 80 % de garde-fous et 73 % d'humain sont des bornes hautes ; la validation de la réversibilité repose sur un échantillon peu risqué.
- **Absent aussi du rapport** : la publication est la seule à fournir des chiffres sur la répartition humain / agent dans l'arrêt, mais sans aucun taux de refus ni d'erreur. Le rapport dit à raison qu'on ne peut pas inférer la qualité de la relecture ; on peut ajouter que la source elle-même ne la mesure pas.
- Le rapport écrit « environ 20 % des sessions pour les nouveaux utilisateurs » sans dire que la période et le périmètre sont ceux de Claude Code interactif ; à ajouter.

## Questions ouvertes
- Comment sont mesurés exactement l'auto-approbation et le taux d'interruption (détection des marqueurs « [Request interrupted by user] » dans la transcription, d'après les prompts de l'annexe, mais non dit pour l'auto-approbation) ?
- La contradiction entre l'introduction et le corps sur « plus de deux fois plus » reste à lever ; à signaler aux auteurs ou à citer avec prudence.
- Les 0,8 % d'irréversible : quelle part vient de clusters simulés ou d'évaluations ? Le texte ne le dit pas.
- Aucune donnée sur les erreurs de l'agent par type d'action : notre rejeu apporterait précisément cela.
- Annexe disponible, mais pas de jeu de données ouvert : pas de reproduction possible.
