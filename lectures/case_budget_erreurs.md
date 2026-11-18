# Fiche de lecture : Telukunta, Lilis, Baron, cadre CASE, budget d'erreurs et autonomie

## 1. Référence
- **Auteurs** : Srinivas Telukunta (Cornell University, Johns Hopkins University), Georgios Nektarios Lilis (Cornell University), Lucio Baron (AI71).
- **Titre** : « The CASE Framework: A Multi-Disciplinary Control Architecture for Governing Enterprise Agentic AI », arXiv 2608.10153 [cs.AI].
- **Version** : **v1 seule** (soumise le 10 août 2026 ; la page de garde du PDF porte « August 12, 2026 »). Pas de v2 : la page de résumé ne liste que [v1] et `/abs/2608.10153v2` renvoie 404 (vérifié le 17 novembre 2026).
- **Licence** : CC BY 4.0. Code et données annoncés : https://github.com/srinivastelukunta/case_framework_arxiv_codes
- **Accès** : texte intégral lu (PDF v1, 34 pages, texte extrait avec pdftotext ; sections 1 à 10, annexes A et B, références). Pagination ci-dessous = pagination du PDF (identique à celle imprimée). Les figures n'ont pas été vues en image, seulement leur texte extrait.
- **Nature** : cadre conceptuel de gouvernance d'agents en entreprise, avec trois études empiriques sur sources publiques (incidents, outils, déploiements). Pas d'expérience sur les agents eux-mêmes.

## 2. Ce que propose l'article, section par section
**Résumé et §1 (p.1-3).** Thèse : la gouvernance des agents est « four problems, not one » (p.1), chacun avec une science établie. CASE = Control theory (agent seul), complex Adaptive systems (collectifs), Supervisory cybernetics (équipes humain-agent), Engineering operations (flottes). Le résumé place le budget d'erreurs dans la couche 4 : « extending error budgets to decision quality so autonomy becomes a controlled variable » (p.1). Six contributions listées (p.2-3).

**§2 Littérature (p.3-5).** Cinq courants : contrôle, systèmes adaptatifs complexes, cybernétique, AgentOps/SRE, modèles de maturité. §2.4 : « reliability for an agent includes decision quality, task completion fidelity, and cost-per-operation bounds, not merely availability » (p.5). §2.5 : les modèles de maturité existants (dont les « autonomy ladders from copilots to orchestrated multi-agent ecosystems ») sont dits « process maturity models » (p.5). Aucune citation d'Anthropic, de Feng et al., de Zhang et Zhang, ni du CSP de Dodge.

**§3 Nouveautés N1 à N7 (p.5-7).** N5 est la nôtre : « We extend the SRE error budget from availability to decision quality and close the loop by modulating autonomy level against remaining budget (Equations (6) and (7)). » (p.6). Les auteurs bornent leur revendication : « is, to our knowledge, new as a stated governance mechanism » (p.6). N4 : indice de maturité non compensatoire (Éq. 9).

**§4 Le cadre (p.7-15).**
- 4.1 couche 1, boucle de contrôle par agent (Éq. 1), observabilité, contrôlabilité, stabilité, planification à horizon glissant, « gain scheduling » (« strictness should be scheduled by task risk class and input novelty, high-gain in unfamiliar regimes and relaxed in certified ones », p.8), vecteur d'erreur incluant « budget burn rate against Equation (6) » (p.8).
- 4.2 couche 2, collectifs : risque d'essaim (Éq. 2), facteur de branchement k < 1 comme « design target » (Éq. 3, p.9).
- 4.3 couche 3, supervision : loi de la variété requise, « Vhuman × G ≥ Vagents » (Éq. 5, p.9).
- 4.4 couche 4, opérations : voir §3 ci-dessous (Éq. 6 et 7, p.10).
- 4.5 couplage entre couches et « zero-touch deployment paradox » (Éq. 8, p.11).
- 4.6 inventaire de mécanismes (Tableau 3, p.12-15) : une ligne « Error-budget-modulated autonomy » (p.15).

**§5 Validation empirique (p.15-23).** Trois études : 62 incidents codés, 22 outils codés, 35 déploiements scorés. Détail au §5 de cette fiche.

**§6 Modèle de maturité CASE (p.23-25).** Niveaux L0 à L4 (Tableau 10, p.24), indice « bottleneck » M = α·m_min + (1−α)·m̄, α = 0,6 (Éq. 9, p.24).

**§7 Illustration ZTAD (p.25-27).** Architecture de déploiement « zero touch » en neuf étapes, tirée de plateformes de production à l'échelle Fortune 50. Trois leçons (couplage observé, paradoxe observé, mécanismes non exercés qui se dégradent, p.27). Aucune ne porte sur le budget d'erreurs.

**§8 à §10 (p.27-28).** Implications pour dirigeants, régulateurs (art. 14 du règlement IA de l'UE), éditeurs. Limites : « the formal apparatus is deliberately spare: Equations (1) through (9) state governance conditions rather than derive closed-form results » (p.28).

**Annexes (p.29-32).** A : grille d'évaluation (Tableaux 11-12), exemple chiffré ; recommandation de cadence « quarterly, aligned with error-budget review » (p.30). B : protocoles de codage ; les deux codeurs sont des modèles de langage (Claude Opus 4.8 et GPT-5.6, p.31-32).

## 3. Budget d'erreurs de décision et autonomie comme variable contrôlée
**Texte exact (§4.4, p.10).**
- Éq. 6 : « Define an agent service-level objective over a decision population and derive an error budget: B = (1 − SLO) × N_decisions », où « budget consumption counts hallucinated actions, scope violations, policy breaches, and cost overruns alongside conventional failures » (p.10).
- Éq. 7 : « The distinctive CASE move is to make autonomy itself a controlled variable modulated by remaining budget: expand autonomous scope while the budget is healthy, contract toward human review as it depletes, and halt expansion entirely on exhaustion: a(t) = g(B_remaining(t)), g monotone non-decreasing » (p.10).
- Principe de gouvernance : « autonomy is earned against a measured error budget rather than granted by approval memo » (p.11).
- Tableau 3, ligne « Error-budget-modulated autonomy » : « Budget dashboard by violation class; autonomy expansion approved against remaining budget » ; échec évité : « Autonomy granted by memo » (p.15).

**La fonction a(t) = g(budget restant) existe-t-elle telle quelle ?** Oui. Notre écriture est celle de l'Éq. 7, y compris « monotone non-decreasing ».

**g est-elle spécifiée ?** Non. Seule la monotonie est posée. Pas de forme, pas de seuils, pas de pente, pas de valeur de SLO. L'unité de a(t) (le « scope » autonome) n'est pas définie. Les auteurs assument cette sobriété : « the formal apparatus is deliberately spare » (p.28).

**Exigence de preuve, borne, N ?**
- Aucune exigence de preuve statistique. Aucune longueur de série de succès. Aucun intervalle de confiance, aucun test.
- Aucune borne sur les erreurs laissées passer par la délégation. Éq. 6 fixe un budget, elle ne dit pas combien de preuves exigent une promotion. Le seul « N » de l'Éq. 6 est la population de décisions (N_decisions), pas une longueur de série.
- Les seules bornes de l'article portent sur autre chose : k < 1 (« design target », p.9), inégalité de variété (p.9), plafonds de jetons/coût (Tableau 3, p.12).
- « Evidence » apparaît dans l'article au sens de pièces documentaires pour l'évaluation de maturité (« error-budget dashboards », Tableau 11, p.29), pas au sens d'une exigence statistique de promotion.

**Points d'incertitude internes à l'article.**
- « halt expansion entirely on exhaustion » (p.10) : g non décroissante donne a minimal quand B = 0 ; le texte ne dit pas si l'épuisement fige l'autonomie ou la ramène à zéro. Les deux lectures sont compatibles avec le texte.
- Le budget est compté en nombre d'erreurs, par « violation class » pour le tableau de bord (p.15). Aucune pondération par gravité ou réversibilité n'est décrite.
- Le niveau d'agrégation du budget n'est pas explicite : voir §6, point 7.

## 4. Les cinq niveaux : maturité de gouvernance ou niveaux d'autonomie ?
**Ce sont des niveaux de maturité de gouvernance.**
- « The CASE maturity model measures whether the correct science governs each scale of agency, which makes it a scientific maturity model rather than a process one. Five levels are defined by which layers are operational and coupled » (p.23).
- Niveaux (Tableau 10, p.24) : L0 Ad hoc, L1 Controlled, L2 Emergence-aware, L3 Requisite, L4 Autonomic. Le niveau d'une organisation se lit sur l'indice Éq. 9 (seuils 0,25 / 0,50 / 0,75 / 1,00, p.24), calculé à partir de scores par couche sur des grilles de classes de mécanismes (Tableau 12, p.30), à partir de pièces documentaires.
- Le niveau est celui d'une **organisation** (ou d'un déploiement), jamais d'un agent ni d'un type d'action.

**Nuance : l'autonomie y figure comme contenu et comme critère de sortie.**
- L1 : « bounded autonomy per agent » (p.24).
- Critère de sortie de L3 : « Autonomy modulated by live error budgets across the fleet (Eq. (7)) » (p.24).
- L4 : « Error-budget-modulated autonomy ... humans govern envelopes, not instances » (p.24).
- §8 : « the CASE maturity pathway offers a staging discipline for autonomy expansion » (p.27).
- Donc le niveau le plus haut suppose une autonomie modulée par le budget ; mais l'échelle elle-même ne décrit pas ce que fait l'humain ni ce que l'agent a le droit de faire.

## 5. Évaluation empirique
**Oui, mais elle ne teste pas le mécanisme budget-autonomie.** Trois études sur sources publiques (p.15-21) :
- Étude 1 : 62 incidents (AI Incident Database, rapports d'éditeurs). « 51 of 62 (82%) carry at least one secondary layer » (p.16). Part primaire L1 : 84 % (p.16).
- Étude 2 : 22 outils. Couverture complète L2 : 0 sur 22 (« no tool in the sample provides Full L2 coverage », p.17).
- Étude 3 : 35 déploiements. « every deployment falls in the composite L0 band » (p.19).

Ni l'Éq. 6, ni l'Éq. 7, ni la fonction g ne sont testées : aucune étude ne fait varier un budget ni ne mesure des erreurs avec ou sans modulation. Le seul lien est que « error-budget dashboards » sert de pièce justificative dans la grille de maturité (p.29).

**Portée déclarée.** « the studies are offered as validation of structure, not precise measurement of magnitude » (p.23). Limites : « independent multi-organization field application of the instrument is the appropriate test » (p.28), « controlled simulation of the coupling dynamics ... is a natural next step » (p.28), l'illustration « demonstrates feasibility, not generality » (p.28).

**Revendication d'usage en production** (non étayée par des données) : « every governance principle in Section 4 corresponds to a mechanism the authors have run, not only proposed » (p.7). Aucun chiffre sur le budget d'erreurs en exploitation n'est donné au §7.

## 6. Vérification point par point du brouillon (ligne 50, « Error budgets and autonomy »)
| # | Affirmation du brouillon | Verdict | Preuve |
|---|---|---|---|
| 1 | « Site-reliability engineering uses error budgets consumed over a window. » | **À nuancer** (porte sur le SRE, pas sur CASE) | CASE définit B sur « a decision population » (Éq. 6, p.10), pas sur une fenêtre de temps. Le « window » vient du SRE en général, que l'article ne détaille pas ; il ne faut pas lui attribuer. |
| 2 | CASE « extends the error budget to the quality of agent decisions » | **Exacte** | « extended from availability to decision quality » (p.10) ; N5 (p.6). Précision : la consommation compte aussi coûts et violations de politique (p.10). |
| 3 | CASE « makes autonomy a controlled variable » | **Exacte** | « make autonomy itself a controlled variable » (p.10) ; titre N5 « Autonomy as a controlled variable » (p.6). |
| 4 | « a(t) = g(remaining budget) with g non-decreasing » | **Exacte** | Éq. 7 : « a(t) = g(B_remaining(t)), g monotone non-decreasing » (p.10). |
| 5 | « expands while the budget is healthy, contracts toward human review as it depletes, and stops expanding on exhaustion » | **Exacte** | « expand autonomous scope while the budget is healthy, contract toward human review as it depletes, and halt expansion entirely on exhaustion » (p.10). |
| 6 | « The function g is left unspecified » | **Exacte** | Seule la monotonie est posée (p.10) ; « deliberately spare » (p.28). |
| 7 | « no evidence requirement or bound is derived » | **Exacte, à préciser** | Aucune exigence statistique ni borne sur les erreurs laissées passer (p.10, p.28). Risque d'ambiguïté : l'article parle de « evidence artifacts » pour la maturité (p.29-30), et il a d'autres bornes sans rapport (k < 1, p.9). Préciser le type de preuve et de borne. |
| 8 | « (Its five levels are a governance maturity model, not autonomy levels.) » | **À nuancer** | Exact sur la définition (« scientific maturity model rather than a process one », p.23 ; niveaux fondés sur les couches opérationnelles, p.23-24). Mais (a) les auteurs récusent « process maturity model » et se disent « scientific » ; (b) L1, L3 et L4 contiennent de l'autonomie (« bounded autonomy per agent », « Autonomy modulated by live error budgets », p.24) et §8 parle de « staging discipline for autonomy expansion » (p.27). |
| 9 | « In both CASE and our rule a budget drives autonomy » | **Exacte** | p.10, p.11, p.15. |
| 10 | « CASE modulates scope by the budget *remaining* at fleet level » | **À nuancer** | « Remaining » : exact (« remaining budget », p.10). « Fleet level » : soutenu par la couche 4 « automated fleet » (p.7) et le critère « across the fleet » (p.24), mais l'article ne dit nulle part que le budget est agrégé à l'échelle de la flotte plutôt que par agent : le vecteur d'erreur d'un agent contient son propre « budget burn rate » (p.8), L1 parle de « bounded autonomy per agent » (p.24), et le tableau de bord est « by violation class » (p.15). |
| 11 | « we *size* the evidence requirement N from the budget before any run, per action type » (contraste) | **Exacte pour ce qui est de CASE** | CASE n'a ni N, ni évidence requise, ni dimensionnement avant exécution (p.10). Une réserve : CASE fixe aussi un budget à l'avance (B = (1−SLO)×N_decisions, p.10), donc « from a budget set in advance » n'est pas ce qui nous distingue ; ce qui nous distingue est la dérivation d'une longueur de série à partir du budget. Éviter la collision de notation : leur N_decisions n'est pas notre N. |
| 12 | « per action type » comme point de différence | **À nuancer** | CASE n'a pas de budget par type d'action, mais a des notions voisines par classe : gain scheduling « by task risk class » (p.8), « Risk-scored action classes » pour les portes d'approbation (p.14), tableau de bord « by violation class » (p.15). Aucune n'est reliée à a(t). |

**Reformulation anglaise proposée pour le paragraphe (à valider)**
> **Error budgets and autonomy.** Site-reliability engineering uses error budgets. The CASE framework (Telukunta, Lilis and Baron, 2026, v1) extends the error budget to decision quality, B = (1 − SLO) × N_decisions over a decision population, and makes autonomy a controlled variable, a(t) = g(B_remaining(t)) with g monotone non-decreasing: autonomous scope expands while the budget is healthy, contracts toward human review as it depletes, and halts expanding on exhaustion. The function g is left unspecified. The authors derive no statistical evidence requirement, no run length and no bound on the errors that delegation lets through, and they report no test of the mechanism. Their five levels are a maturity model of the governance architecture, defined by which layers are operational and coupled, not levels of agent autonomy, although the upper levels presuppose budget-modulated autonomy. In both CASE and our rule a budget drives autonomy; the mechanism differs. CASE ties autonomy to the budget remaining, with no stated granularity (fleet, agent or action type); we derive the run length N required for promotion from a budget set in advance, per action type.

## 7. Part d'antériorité
**Ce que leur texte contient déjà de notre idée.**
- **Budget d'erreurs fixé à l'avance, relié à une population de décisions** : B = (1 − SLO) × N_decisions (p.10). Nous ne pouvons pas revendiquer l'idée d'un budget d'erreurs sur les décisions d'agents.
- **Autonomie pilotée par le budget** : Éq. 7, revendiquée comme nouvelle « to our knowledge » (N5, p.6). Notre brouillon l'attribue correctement.
- **Autonomie « gagnée » plutôt qu'accordée** : « autonomy is earned against a measured error budget rather than granted by approval memo » (p.11). Même formule que notre « earned autonomy », à citer.
- **Règle par classe** : strictness « scheduled by task risk class » (p.8) ; « Risk-scored action classes; synchronous approval only for high-consequence classes » (p.14) ; budget « by violation class » (p.15). C'est de la différenciation par classe de risque ou d'erreur, mais pas un niveau d'autonomie par type d'action gagné sur preuves.
- **Contraction vers la revue humaine** quand le budget baisse (p.10) : un recul gradué, proche de notre retrait mais non déclenché par une première erreur.
- **Retrait brutal ponctuel** : « Kill-and-quarantine on invariant violation detected in telemetry » (p.13) ; reversion automatique de code, prompts et politiques (p.14). C'est un coupe-circuit sur violation d'invariant, pas une règle de retrait d'autonomie à la première erreur d'un type.
- **Remise à zéro sur changement** : « coupled-layer certification renewed on every material change » (p.30, aussi p.24). C'est la logique de notre remise à zéro sur changement de configuration, mais au niveau de l'organisation.
- **Preuves documentaires et cadence d'examen** : revue trimestrielle « aligned with error-budget review » (p.30).

**Ce que leur texte ne contient pas.**
- Une longueur de série N tirée d'un budget : absente (p.10).
- Une règle de retrait à la première erreur : absente. La contraction est progressive avec le budget restant (p.10).
- Une garantie bornée sur les erreurs supplémentaires : absente. « Equations (1) through (9) state governance conditions rather than derive closed-form results » (p.28).
- Une exigence statistique de preuve pour promouvoir : absente. Les « evidence artifacts » sont documentaires (p.29).
- La spécification de g : absente (p.10).
- Un niveau d'autonomie par type d'action : absent. Les niveaux sont des niveaux de maturité d'organisation (p.23-24).
- Un test empirique du mécanisme (rejeu, simulation ou terrain) : absent (p.23, p.28).
- Une pondération des erreurs par gravité ou réversibilité dans le budget : absente (p.10).
- Une référence au CSP, aux plans d'échantillonnage ou à Zhang et Zhang : aucune (références p.32-34).

**Conséquence pour notre apport (telle que le brouillon la formule).** Rester sur « run length N derived from an error budget set in advance, a guarantee on the extra errors, and a preregistered measurement ». Ne pas écrire que l'usage d'un budget pour piloter l'autonomie est nouveau, ni que le suivi par classe l'est. La phrase « the mechanism differs » est juste à condition de préciser le granularité (non spécifiée chez eux) et de ne pas prétendre que CASE ignore tout budget fixé à l'avance.

## Questions ouvertes
- Les auteurs publient du code et des jeux de données (lien GitHub) : ils concernent les études 1 à 3, pas Éq. 7 ; non ouvert ici.
- Les références [12], [13], [16], [18], [25], [26] sont des préprints ou des revues sectorielles non lus ici ; [26] (SRE pour agents) pourrait contenir un budget d'erreurs de décision antérieur. À chercher à part.
