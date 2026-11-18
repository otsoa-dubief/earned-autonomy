# Travaux existants proches de l'« autonomie méritée » évaluée sur des agents

Recherche web en lecture seule, arrêtée au 2026-11-04. Environ 15 appels. Lecture : "texte intégral" = PDF lu en local (partiel) ; "résumé" = page arXiv/abstract ou snippet de moteur ; "secondaire" = blog/presse. Beaucoup de preprints récents (2026), non revus par des pairs sauf mention.

## 1. Systèmes de permissions dynamiques pour agents LLM : adaptent-ils les droits selon l'historique observé ?

### Takeaway
Les systèmes évalués (Progent, Conseca, AgentTrim, auto-review d'OpenAI) adaptent la politique à la tâche ou à l'état courant, pas au bilan passé de l'agent. Un seul préprint (Ou, 2026) apprend une frontière auto/ask/block à partir des approbations humaines, mais en simulation seulement. Le « tenir un registre de succès par type d'action » n'est évalué empiriquement nulle part, à ma connaissance.

### Cited Findings
- **Progent** (Shi et al., arXiv 2504.11703). Contrôle de privilèges par DSL, deny par défaut ; politiques mises à jour dynamiquement selon l'état de l'agent, générées par LLM. AgentDojo : attaque passée de 41,2 % à 2,2 % (v1) puis 39,9 % à 1,0 % (v2), utilité conservée ; attaques adaptatives testées. — [arXiv](https://arxiv.org/abs/2504.11703v1), [résumé v2](https://alphaxiv.org/overview/2504.11703v2). Lecture : snippets/résumés seulement. Proximité : **moyenne** (privilèges par action, mais mise à jour par état/tâche, pas par bilan).
- **AgentTrim** (arXiv 2601.12449, Fujitsu). Filtrage adaptatif d'outils au moindre privilège par étape, résultats AgentDojo ; chiffres non vérifiés. — [PDF](https://arxiv.org/pdf/2601.12449). Lecture : snippet. Proximité : **faible à moyenne**.
- **Conseca / « Contextual Agent Security: A Policy for Every Purpose »** (Tsai, Bagdasarian, arXiv 2501.17070). Politiques générées par LLM selon requête et contexte de confiance, vérifiées de façon déterministe. Prototype agent Linux (fichiers, mail), 3 références (sans politique, statique restrictive, statique permissive), preuve de concept sur peu de tâches synthétiques. Les chiffres (~60 %, 20 tâches) viennent de résumés tiers, non vérifiés. — [résumé tiers](https://www.emergentmind.com/papers/2501.17070). Lecture : secondaire. Proximité : **faible à moyenne**.
- **Auto-review (OpenAI, 30 avril 2026)**. Un agent relecteur remplace l'approbation humaine à la frontière du sandbox ; arrêts pour approbation ~200x moins fréquents ; approbation 99,1 % des actions escaladées ; rappel dépassement de périmètre 90,3 %, injection 99,3 % (90,2 % en incluant suppressions/falsification) ; MonitoringBench (Hard) 96,1 %. L'article ne décrit pas de permissions qui évoluent seules ; les règles restent définies par l'utilisateur ; suivi des taux d'escalade/refus/dérogations évoqué. — [OpenAI Alignment](https://alignment.openai.com/auto-review). Lecture : page complète via fetch. Proximité : **moyenne** (même problème, politique fixe).
- **Ou, « Progressive Autonomy as Preference Learning »** (arXiv 2605.19151, cs.AI/cs.HC, 18 mai 2026, auteur unique). Passerelle à processus gaussien (probit) sur la tolérance au risque humaine, mise à jour par approve/deny ; décision à trois zones (allow si p>τ_haut, block si p<τ_bas, ask entre les deux). Non-stationnarité par noyau à décroissance temporelle et détection de point de rupture en ligne (ex. nouvelle base de code). Simulation : 18 outils avec attributs de risque (réversibilité, sensibilité, rayon d'impact, argument destructeur), 8 niveaux de sensibilité, 7 contextes, N=1500 décisions, 6 graines, rupture de confiance abrupte à t=750, veto de sécurité (irréversible + sensible + faible confiance). Résultats : 68 % décidés automatiquement à 97,3 % d'exactitude et 2,4 % de faux-allow en validation ; 99,7 % après la rupture ; 98,7 % de généralisation sur une action jamais interrogée contre 66,7 % pour l'apprenant indépendant. Résultat négatif honnête : la règle « interroger dans la bande ask » n'est pas efficace en échantillons sous déséquilibre de classes. Les auteurs écrivent que le travail antérieur est « qualitatif » avec un palier fixé à la main, qu'aucun jeu de données public ne suit un superviseur dans le temps, et que le résultat est simulé « par nécessité ». — [arXiv](https://arxiv.org/abs/2605.19151), PDF lu partiellement en local via pdftotext. Lecture : **texte (sections clés)**. Proximité : **haute** sur « autonomie apprise par type d'action + reset à rupture + réversibilité comme attribut ». Différences : apprend la préférence du superviseur (pas la fiabilité de l'agent), pas de promotion par nombre de succès pondéré par l'enjeu, pas de rétrogradation immédiate, pas de tests-pièges, oracle simulé.
- **« Are You Still the Agent I Authorized? Earned Authority under a Fixed Ceiling for Evolving Agents »** (Zhang & Zhang, arXiv 2607.23586, 26 juillet 2026, cs.AI/cs.CR). Modèle formel « lié à l'état » : enveloppe de transition et plafond d'effet immuable fixés à l'octroi ; l'autorité peut diminuer librement et croître seulement sous conditions de preuve ; l'évidence produite par l'agent ne peut pas relever le plafond ; six classes de mutation (mémoire, outils, workflows, délégation…) mappées à des conséquences d'autorisation ; preuves sous hypothèses (médiation complète, abstraction d'effet saine, intégrité du moniteur). Pas d'évaluation empirique visible dans le résumé. — [arXiv](https://arxiv.org/abs/2607.23586). Lecture : résumé. Proximité : **haute conceptuellement** (autorité méritée, reset après mutation, plafond), **aucune** évaluation expérimentale vue.

### Inferences
- Le créneau « règle d'autonomie fondée sur preuves, évaluée sur agents dans un bac à sable » n'est occupé que par une simulation avec oracle synthétique (Ou) et une théorie sans expérience (Zhang & Zhang). Une expérience avec de vrais agents LLM et des taux d'erreur mesurés reste ouverte.
- Le fait que Ou écrive que les travaux précédents laissent le palier « fixé à la main » appuie la nouveauté de ton angle.

### Gaps
- Pas trouvé : travail comparant promotion par compteur de succès à des politiques fixes sur AgentDojo/τ-bench ou équivalent.
- Chiffres de Conseca et AgentTrim non vérifiés au texte.

## 2. Apprendre à déférer, prédiction sélective, conformal : agents qui demandent de l'aide

### Takeaway
Littérature abondante sur « quand demander », évaluée sur des benchmarks de clarification/abstention, mais toujours au niveau de la décision unique (cette requête, ce pas), pas d'une autonomie accordée dans la durée selon un bilan.

### Cited Findings
- **KnowNo, « Robots That Ask for Help »** (Ren et al., CoRL 2023). Prédiction conforme autour d'un planificateur LLM : agit si un seul choix est retenu, demande sinon ; garanties statistiques de réussite ; 10-24 % d'aide en moins que les références ; robots simulés et réels. — [PMLR](https://proceedings.mlr.press/v229/ren23a), [arXiv](https://arxiv.org/abs/2307.01928). Lecture : résumé/snippets. Proximité : **moyenne** (garantie de couverture, mais calibrée une fois, pas d'évolution).
- **S-ATLAS** (Wang, He, Kantaros, IEEE RA-L 2025). Extension multi-robots du conformal. Lecture : snippet. Proximité : **faible**.
- **HiL-Bench** (arXiv 2604.09408, avril 2026, Scale). Agents code/SQL, blocages (info manquante, ambiguïté, contradiction) révélés par l'exploration ; métrique Ask-F1 (précision des questions, rappel des blocages) ; 75-89 % pass@3 avec info complète contre 4-24 % quand il faut juger quand demander ; RL à récompense Ask-F1 améliore sur un modèle 32B. — [arXiv PDF](https://arxiv.org/pdf/2604.09408). Lecture : résumé/snippet. Proximité : **moyenne**.
- **AgentAbstain** (Liu et al., arXiv 2607.10059, 11 juillet 2026). 263 paires (agir / s'abstenir) dans 42 sandboxes, 8 scénarios, générateur AbstainGen ; 17 LLM, 4 harnais ; meilleur modèle 59,5 % de précision par paire ; abstention largement distincte de la capacité générale ; mode d'échec « abstention a posteriori » (action irréversible avant de s'abstenir). — [arXiv](https://arxiv.org/abs/2607.10059). Lecture : résumé (fetch). Proximité : **moyenne à haute** pour la méthode (paires de tâches, bac à sable) et pour le motif irréversibilité ; pas de dimension temporelle.
- **Bayesian self-escalation** (Shaikh, arXiv 2608.24087, 25 août 2026). Arrêt optimal sur un a posteriori de compétence, seuil dépendant du temps ; simulation + cascade Qwen2.5-Coder 1.5B vers 7B sur MBPP (257 tâches), 2 prédictions pré-enregistrées sur 3 confirmées. — [arXiv](https://arxiv.org/abs/2608.24087). Lecture : résumé. Proximité : **faible**.
- **« To Ask or Not to Ask: Learning to Require Human Feedback »** (arXiv 2510.08314) : Learning to Defer jugé sous-optimal sur certaines distributions, propose Learning to Ask. — [arXiv](https://arxiv.org/pdf/2510.08314). Lecture : snippet. Proximité : **faible**.
- **NoisyToolBench / Ask-when-Needed** (arXiv 2409.00557), **SAGE-Agent / ClarifyBench** (arXiv 2511.08798, ACL Findings 2026 ; POMDP, +7-39 % de couverture, 1,5-2,7x moins de questions), **clarification par gain d'information** (arXiv 2606.03135, τ-Bench enrichi, 5 modèles). — [2409.00557](https://arxiv.org/html/2409.00557v4), [2511.08798](https://www.arxiv.org/pdf/2511.08798), [2606.03135](https://papers.cool/arxiv/2606.03135). Lecture : snippets. Proximité : **faible**.
- Référence théorique : Madras et al. 2018 (learning to defer) et enquête 2026 sur la quantification d'incertitude pour agents ([arXiv 2609.07395](https://arxiv.org/pdf/2609.07395), non ouverte).

### Inferences
- Ces benchmarks fournissent des tâches avec « bonne réponse = demander » réutilisables comme pièges, et la métrique irréversible/réversible d'AgentAbstain colle à ta pondération par enjeu.

### Gaps
- Pas trouvé : étude où l'on déplace dans le temps le seuil de déférence d'un agent selon ses erreurs passées.
- Résultats détaillés des benchmarks non lus (résumés seulement).

## 3. Confiance, réputation dans des bacs à sable multi-agents ou places de marché

### Takeaway
La littérature LLM montre surtout que la réputation est exploitable ; il n'y a pas de test d'une échelle de promotion/rétrogradation pour déléguer des permissions.

### Cited Findings
- **TruthMarketTwin** (arXiv 2605.10059, mai 2026) : marché simulé avec acheteurs et vendeurs LLM ; compare réputation et garanties (warrants) ; les vendeurs LLM apprennent à exploiter les failles de la réputation ; la garantie réduit la tromperie. — [arXiv](https://arxiv.org/pdf/2605.10059). Lecture : snippet. Proximité : **faible à moyenne** (met en garde contre un score de réputation gaming-able).
- **Marché de biens de confiance (credence goods)** (arXiv 2603.08853, mars 2026) : agents GPT-5.1 experts/consommateurs ; les experts tendent à frauder sans préférences prosociales explicites ; la répétition ne discipline pas. — [arXiv](https://arxiv.org/html/2603.08853). Lecture : snippet. Proximité : **faible**.
- **Réputation pour places de marché multi-agents** (SingularityNET, arXiv 1905.08036, 2019), non LLM. — [arXiv](https://arxiv.org/pdf/1905.08036). Proximité : **faible**.
- **« Intelligent AI Delegation »** (arXiv 2602.11865) : déjà connu ; sépare réputation (historique public vérifiable) et confiance (seuil privé du délégant).
- Implémentations non revues : AWS (déjà connu), KavachOS (score 0-100 sur journal d'audit, départ à 50), Kizuna (réputation avec décroissance de 5 % par mois), Monte Carlo, Decagon ; thèse UTA sur confiance adaptative en e-marché. Seuils non validés. — [KavachOS](https://docs.kavachos.com/docs/trust), [Kizuna](https://kizuna-help.pages.dev/agents/trust-levels), [Monte Carlo](https://www.montecarlodata.com/blog-agentic-autonomy-is-a-trust-score/). Lecture : snippets.

### Gaps
- Aucune évaluation indépendante des seuils pratiques trouvée.

## 4. Transfert de confiance entre versions de modèle, recertification, régression

### Takeaway
Un seul travail académique direct : la confiance doit être remesurée à chaque version. Le reste est du conseil de praticiens ; le « rejouer les erreurs passées comme tests-pièges » n'est ni nommé ni évalué.

### Cited Findings
- **« The Moving Target »** (Fan et al., arXiv 2607.02587, juillet 2026, v2 août, accepté IEEE ICMLA 2026). 4 lignées open source (Yi, Qwen, Mistral, Gemma) x 3 générations, panier fixe de 200 items (TruthfulQA, BBQ, ToxiGen, CrowS-Pairs, XSTest), 3 gabarits de prompt ; la dérive moyenne entre générations adjacentes vaut plusieurs fois la référence nulle ; conclusion : un score de confiance est lié à un checkpoint, à remesurer à chaque version importante. Limites : pas d'API fermées ni de grands modèles. — [arXiv](https://arxiv.org/abs/2607.02587). Lecture : résumé (fetch). Proximité : **haute** pour justifier le reset ; mesure des benchmarks de chat, pas de comportement agentique.
- Pratique : re-valider la base comportementale à chaque mise à jour du fournisseur, rejouer toute la suite avant changement de modèle, blocage si une métrique P0 régresse de plus de 2 points (seuil illustratif). — [Roval](https://roval-ai.pages.dev/research/blog/agent-drift-continuous-compliance), [Model Upgrade Validation](https://marcelaldecoa.github.io/TheArchitectureOfIntent/patterns/deployment/model-upgrade.html), [CallSphere](https://callsphere.ai/blog/vw5g-behavioral-diff-testing-model-swap-2026). Lecture : snippets, sources vendeur/blog.
- Zhang & Zhang (2607.23586, voir §1) traitent les mutations d'agent (outils, mémoire) comme déclencheurs de réexamen d'autorisation.
- AWS (connu) : sur chute de sécurité, rétrécir les permissions et redéployer la dernière version stable.

### Gaps
- Pas trouvé : étude de régression comportementale d'agents (pas de chat) entre versions liée à des droits.
- Pas trouvé : usage des incidents passés comme suite de tests de recertification.

## 5. Niveaux d'autonomie avec évaluation empirique (2025-2026)

### Takeaway
Pas trouvé de suite empirique à Feng et al. ; seulement taxonomies et préconisations.

### Cited Findings
- **Feng, McDonald, Zhang** (arXiv 2506.12469) : cinq niveaux (opérateur, collaborateur, consultant, approbateur, observateur), certificats d'autonomie, évaluation seulement esquissée. — [arXiv](https://arxiv.org/html/2506.12469v2). Déjà connu.
- Compendium de critères d'agents (arXiv 2609.11018) : revue des taxonomies existantes. — [arXiv](https://arxiv.org/pdf/2609.11018). Lecture : snippet.
- CSA « Agentic AI Autonomy Levels and Control » v2.0 (mars 2026) et un article de Zheng et al. (juillet 2026) distinguant autonomie permise et capacité : cités par une source secondaire, **non vérifiés**.
- Pas de résultat METR, UK AISI ou US CAISI directement pertinent ressorti de mes requêtes (non couvert à fond).

### Gaps
- Rapports METR/AISI/CAISI : non explorés spécifiquement faute de budget d'appels. À chercher séparément.

## 6. Études de terrain sur le comportement d'approbation humaine

### Takeaway
Les chiffres convergent vers de l'approbation réflexe (>90 %) et une mauvaise détection humaine, mais viennent surtout d'Anthropic (auto-déclaré) et d'un jeu en ligne.

### Cited Findings
- Anthropic : taux d'approbation des invites de permission cité à 93 % (articles de mars 2026) puis 97 % (annonce du mode auto par défaut, 7 août 2026, effectif le 14 août) ; rejet de 3 % des demandes individuelles contre 39 % des plans ; étude citée de ~1 053 testeurs : humains détectent 13,6 % des commandes dangereuses contre 89 % pour le classifieur du mode auto. Conflit 93 vs 97 : à vérifier à la source primaire (non lue). — [DevOps.com](https://devops.com/anthropic-makes-claude-codes-auto-mode-the-default-betting-automation-beats-manual-review/), [Shelly Palmer](https://shellypalmer.com/?p=205420), [Doolpa](https://doolpa.com/news/anthropic-claude-code-auto-mode-autonomous-classifiers). Lecture : secondaire. Source primaire déjà connue de l'utilisateur.
- **« Continue? Y/N »** (A. Wauters) : ~409 000 décisions approuver/refuser, >40 000 parties, précision moyenne 66,3 %, ~34 % des commandes étaient des menaces ; les ratés remontent en fin de session de 60 s. Jeu observationnel, non contrôlé. — [LetsDataScience](https://letsdatascience.com/news/game-data-shows-humans-missed-one-in-three-dangerous-agent-c-a25c079f). Lecture : secondaire.
- Faux négatifs de revue automatisée ~17 % sur dépassements réels (un seul article, non recoupé) ; clic-through 70,2 % sur alertes SSL de navigateur (2013) comme analogie de habituation. — [Tianpan](https://tianpan.co/blog/2026-04-28-agent-permission-prompt-habituation-curve). Lecture : snippet.
- Recommandation de praticiens : suivre le taux d'approbation par classe d'action ; >95 % sur un mois = garde-fou soit inutile soit non lu ; seuil de 95 % sans mesure à l'appui. — [Resilient Cyber](https://resilientcyber.beehiiv.com/p/the-human-in-the-loop-illusion).

### Gaps
- Pas trouvé d'étude de terrain revue par des pairs sur la fatigue d'approbation avec agents.
- Pas de source primaire Anthropic relue dans cette session.

## Carte : ce qui existe, ce qui reste nouveau

| Élément de ta conception | Précédent le plus proche | Statut |
|---|---|---|
| Autonomie par type d'action | Ou 2605.19151 (attributs d'action, simulation) | Existe en simulation |
| Promotion après N succès vérifiés, N pondéré par enjeu/réversibilité | Aucun testé ; AWS et blogs (non validés) | **Non évalué** |
| Rétrogradation immédiate après erreur à enjeu moyen/haut | AWS (« promote slowly, demote fast »), pas de test | **Non évalué** |
| Reset de la preuve après changement de modèle/permission | Fan et al. 2607.02587 (justification), Zhang 2607.23586 (formel), Ou (point de rupture) | Justifié, pas testé sur agents |
| Erreurs passées rejouées comme tests-pièges de la nouvelle config | Aucun trouvé | **Nouveau** (à confirmer) |
| Protocole ouvert d'échange de preuves | Intelligent AI Delegation (crédentiels signés, conceptuel) | Conceptuel |
| Évaluation sur vrais agents LLM en bac à sable avec comparaison à politiques fixes | AgentAbstain/HiL-Bench (décision isolée), Progent/AgentDojo (sécurité) | **Ouvert** |

Limites de cette recherche : environ 15 appels, majorité de résumés ou snippets ; METR/AISI/CAISI, FAccT et les actes ACL/NeurIPS non fouillés directement ; une autre session devrait relire les sources primaires d'Anthropic et le texte complet d'AgentAbstain, HiL-Bench et Zhang & Zhang.
