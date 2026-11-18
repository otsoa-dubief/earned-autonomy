# Repli sur la référence et seuil de « données suffisantes » : SPIBB, Seldonian/HCPI, conforme (CRC, LTT, Mondrian), abstention sélective

Notes de recherche, 6 novembre 2026. Sources primaires lues en texte intégral (PDF arXiv / PMLR / Science, plus annexes) sauf mention contraire. Les citations entre guillemets sont des extraits courts du texte source. Les calculs signalés « calcul personnel » sont à moi (approximation de Poisson), pas aux auteurs.

## 1. SPIBB et variantes : ensemble bootstrappé, choix de N∧, garantie, sensibilité

### Takeaway
SPIBB copie la politique de référence (baseline) sur toute paire (état, action) vue moins de N∧ fois et n'optimise que sur le reste. La garantie (amélioration ζ-approchée avec probabilité 1−δ) est exacte mais numériquement vide aux valeurs réellement utilisées : la théorie demande des N∧ de l'ordre du million (Scholl et al.) ou de plus de 10 millions (Wienhöft et al.), alors qu'en pratique on prend N∧ ≈ 5–20, choisi par recherche sur grille en simulation et jugé sur le CVaR (moyenne des 1 % ou 10 % pires exécutions). Plus N∧ est grand, plus l'algorithme est conservateur. Trop bas, il devient légèrement non sûr sur les petits jeux de données. La sécurité tient sur une large bande au-dessus d'un petit plancher.

### Cited Findings
**SPIBB original (Laroche, Trichelair, Tachet des Combes, ICML 2019, arXiv 1712.06924 v5)**
- Ensemble bootstrappé : B est « the set of state-action pairs with counts smaller than N∧ ». Πb-SPIBB impose π_spibb(a|x) = π_b(a|x) pour (x,a) ∈ B, puis fait une itération de politique contrainte à Πb dans le MDP du maximum de vraisemblance. L'algorithme 1 (projection gloutonne) donne la masse des actions non bootstrappées à l'action de Q maximal — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Variante Π≤b-SPIBB : π(a|x) ≤ π_b(a|x) sur B (éq. 10). Elle est « even more efficient in practice » mais « does not come with safety guarantees » — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Théorème 2 : π_spibb est une amélioration ζ-approchée sûre avec probabilité 1−δ, où ζ = (4V_max/(1−γ))·sqrt((2/N∧)·log(2|X||A|2^|X|/δ)) − ρ(π_spibb, M̂) + ρ(π_b, M̂) — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Statut de N∧ : « N∧ is not a property of the dataset, but a hyper-parameter of the algorithm ». Il faut le choisir « large enough to ensure safety and small enough to ensure improvement ». La borne de Petrik et al. (2016, Thm 8), fondée sur le compte minimal, donne ‖e‖∞ = 2 dans toutes leurs expériences, d'où « a trivial bound » — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Principe : SPIBB « improves the baseline when it can guarantee improvement and falls back on the baseline when the uncertainty is too high ». Les auteurs parlent d'un algorithme « knows-what-it-knows », « pessimistic » — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Mode d'échec évité : avec une baseline qui joue rarement certaines actions, « even in big datasets, some state-action pairs are observed only once or twice ». Le RL de base exploite alors ces « chimaeras ». SPIBB n'a pas le droit de « jump to conclusions without sufficient proof » — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Protocole de choix des hyperparamètres :
  - |D| ∈ {10, 20, 50, 100, 200, 500, 1000, 2000} trajectoires (plus 5000 et 10000 en gridworld) ;
  - évaluation par la moyenne et le X%-CVaR (« mean performance over the X% worst runs ») ;
  - recherche sur grille pour les concurrents, valeurs retenues δ_hcpi = 0,9, δ_rob = 0,1, κ_adj = 0,003.
  — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Gridworld 5×5 :
  - comparatif avec N∧ = 5 ;
  - avec N∧ = 20, les algorithmes sont « more conservative and therefore safe, while still achieving near optimality on big datasets » ;
  - « the bigger the N∧, the more conservative SPIBB gets » ;
  - l'amélioration est sûre « at the slight exception of Πb-SPIBB with a low N∧ on 10-trajectory datasets ».
  — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Données collectées par une politique uniforme (et non par la baseline) : les SPIBB « fail to be completely safe when N∧ ≤ 10 and |D| ≤ 20 » — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- MDP aléatoires (|X| = 50, |A| = 4, N∧ = 10) :
  - baseline mauvaise (η = 0,1) : « SPIBB algorithms are too conservative for small datasets but catch up on the bigger ones » ;
  - baseline forte (η = 0,9) : en 1%-CVaR, « all fail to be safe but the SPIBB algorithms » ;
  - carte de chaleur en fonction de N∧ : légèrement non sûr « when N∧ gets too low », puis « the red stains disappear » quand N∧ augmente.
  — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- SPIBB-DQN (pseudo-comptes par similarité euclidienne, 300 exécutions, jeux de 10k, 20k et 30k transitions) :
  - N∧ = 0 (DQN classique) dégrade la baseline et obtient le pire 10%-CVaR ;
  - SPIBB-DQN améliore la moyenne pour N∧ ≥ 1, et le 10%-CVaR pour N∧ ≥ 8.
  — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Méthodes calibrées sur la théorie et donc toujours en repli : Robust MDP et RaMDP « depend on a safety test that always failed in our experiments ». Robust MDP « always fall back on the baseline when the dataset is under 50,000 trajectories » — [Laroche et al. 2019, annexe B.2](https://arxiv.org/pdf/1712.06924)
- La meilleure valeur de HCPI trouvée par la grille, retenue pour le texte principal, est δ_hcpi = 0,9. Les auteurs notent que la confiance est alors très faible : « 0.1 for δhcpi = 0.9, and even null for δhcpi = 1 » — [Laroche et al. 2019, annexe B.2.2](https://arxiv.org/pdf/1712.06924)

**Soft-SPIBB (Nadjahi, Laroche, Tachet des Combes, ECML-PKDD 2019, arXiv 1907.05079)**
- Fonction d'erreur dérivée de Hoeffding : e_P(x,a) = sqrt((2/N_D(x,a))·log(2|X||A|2^|X|/δ)). Contrainte : Σ_a e(x,a)·|π(a|x) − π_b(a|x)| ≤ ε pour tout état x. C'est un budget local d'écart, pondéré par l'incertitude — [Nadjahi et al. 2019](https://arxiv.org/pdf/1907.05079)
- Remarque 3 : Πb-SPIBB est le cas particulier où e = ∞ sur B et e = 2 ailleurs. Les auteurs critiquent SPIBB, qui « relies on a binary decision-making and may be too conservative » — [Nadjahi et al. 2019](https://arxiv.org/pdf/1907.05079)
- Sensibilité :
  - Approx-Soft-SPIBB « behaves more smoothly with respect to its hyper-parameter, its optimal value being in interval [0.5,2] » ;
  - RaMDP, à l'inverse, a un effet de seuil : pour κ_adj ≥ 0,0035 il devient sur-conservateur au point de ne plus viser le but ;
  - Soft-SPIBB n'est « slightly unsafe only with η = 0.9 and less than 20 trajectories ».
  — [Nadjahi et al. 2019](https://arxiv.org/pdf/1907.05079)
- Choix de N∧ pour SPIBB comparé : « The mean performance improves as the safety decreases. We choose N∧ = 10 […] because it seems to offer the best compromise » — [Nadjahi et al. 2019, annexe B.2](https://arxiv.org/pdf/1907.05079)
- Cas limites : N∧ = 0 ou ε = +∞ donne un DQN classique ; N∧ = ∞ ou ε = 0 donne « a copy of the baseline ». Il a fallu 300 exécutions, « necessary to obtain reasonable estimates of algorithms' safety ». Approx-Soft-SPIBB-DQN est « less sensitive than SPIBB-DQN » à son hyperparamètre. Le théorème a une dépendance cubique en l'horizon (Remarque 4) — [Nadjahi et al. 2019](https://arxiv.org/pdf/1907.05079)

**Analyses ultérieures**
- Scholl, Dietrich, Otte, Udluft (arXiv 2208.00724, 2022) montrent que la revendication de sûreté prouvée de Soft-SPIBB « does not hold » : leur Assumption 1 est fausse pour tout 0 < γ < 1. Ils proposent Adv-Approx-Soft-SPIBB, prouvé sûr, et Lower-Approx-Soft-SPIBB, heuristique et meilleur empiriquement. Ils concluent que « huge amounts of data are necessary such that the safety bounds become useful in practice » — [Scholl et al. 2022](https://arxiv.org/pdf/2208.00724)
- Hyperparamètres retenus par recherche sur grille, « solely optimized for performance without considerations of the safety guarantees » :
  - Πb-SPIBB et Π≤b-SPIBB : N∧ = 10 (MDP aléatoires), N∧ = 7 (Wet Chicken) ;
  - R-MIN : N∧ = 3 ;
  - Approx-Soft-SPIBB : ε = 2 et ε = 1 (δ = 1).
  — [Scholl et al. 2022](https://arxiv.org/pdf/2208.00724)
- N∧ théorique pour une borne utile (Wet Chicken : |S| = 25, |A| = 5, V_max ≈ 20, γ = 0,95, borne inférieure −8, δ = 0,05) : **N∧ = 1 832 114**. La politique produite « would always be the behavior policy unless there are far more than 10,000,000 observations ». Πb-SPIBB est donc exclu de leur expérience à bornes utiles — [Scholl et al. 2022](https://arxiv.org/pdf/2208.00724)
- Dans la même expérience :
  - DUIPI reproduit la baseline jusqu'à 50 000 pas, puis donne des bornes utiles dès 500 000 pas ;
  - Adv-Approx-Soft-SPIBB est « very sensitive to changes in ε », alors que δ a « a weaker effect ».
  — [Scholl et al. 2022](https://arxiv.org/pdf/2208.00724)
- Wienhöft, Suilen, Simão, Dubslaff, Baier, Jansen (« More for Less », arXiv 2305.07958 ; IJCAI 2023, lieu non vérifié dans le texte consulté) :
  - la borne de compte minimal « often turns out to be too large for practical applications of SPI, it is instead turned into a hyperparameter » ;
  - N∧_SPIBB = 32·V_max²/(ζ²(1−γ)²)·log(2|S||A|2^|S|/δ), qui croît linéairement en |S| ;
  - leurs bornes (MDP à deux successeurs, fonction bêta incomplète inverse) croissent seulement en log |S|.
  — [Wienhöft et al. 2023](https://arxiv.org/pdf/2305.07958)
- Même ainsi, « even for small MDPs (e.g., |S| = 100) we still need over 10 million samples per state-action pair » pour 1−δ = 0,9 et ζ = 0,1, « which is infeasible in practice » — [Wienhöft et al. 2023](https://arxiv.org/pdf/2305.07958)
- Leur protocole :
  - N∧_SPIBB est pris comme hyperparamètre, on en déduit ζ, puis le N∧ plus petit qui donne le même ζ ;
  - 1000 répétitions, moyenne et CVaR à 10 % et 1 % ;
  - la méthode Beta commence à améliorer la politique de comportement avec des jeux « about half the size compared to SPIBB » sur le Gridworld.
  — [Wienhöft et al. 2023](https://arxiv.org/pdf/2305.07958)
- Simão, Laroche, Tachet des Combes (AAMAS 2020, arXiv 1909.05236), avec une baseline estimée par maximum de vraisemblance :
  - la garantie gagne un terme d'erreur « that cannot be reduced by hyper-parameter settings ». Sinon, on pourrait « consider an empty dataset, pretend it was generated with an optimal policy and expect a safe policy improvement over it » ;
  - un hyperparamètre nul force la copie de la baseline (erreur nulle) ; un hyperparamètre infini donne l'optimum du MDP estimé, avec une erreur non bornée.
  — [Simão et al. 2020](https://arxiv.org/pdf/1909.05236)
- Même source, sur les données corrélées : la borne « depends on the number of trajectories, not the number of state-action visits, nor the total number of samples ». Même avec beaucoup d'échantillons tirés de peu de trajectoires, « the variance may still be high » — [Simão et al. 2020](https://arxiv.org/pdf/1909.05236)
- Même source, sur la borne de Petrik : elle décroît comme l'inverse de la racine du compte minimal par paire. Or Laroche et al. montrent que, même sur de très petites tâches, ce minimum est « almost always zero » — [Simão et al. 2020](https://arxiv.org/pdf/1909.05236)
- Filtre de densité analogue, PQL/MBS (Liu, Swaminathan, Agarwal, Brunskill, arXiv 2007.08202, NeurIPS 2020) :
  - ζ(s,a) = 1(μ̂(s,a) ≥ b), b étant « the only hyper-parameter » ;
  - b arbitre entre conservatisme (b grand : on reste à l'initialisation) et « unfounded optimism » (b = 0) ;
  - en discret, « b = n0/n where n0 is our prior for the number of samples we need for reliable distribution estimates », avec b = 10/taille d'échantillon dans leur exemple ;
  - « their hyper-parameter N∧ is analogous to b·n » ;
  - en continu, on prend un percentile de μ̂ ;
  - diagnostic a posteriori : si la fraction filtrée sous la politique apprise est trop grande, on relance avec un b plus petit ;
  - meilleur seuil parmi {0,005 ; 0,001 ; 0,0001}, et b plus grand quand les données sont moins diverses.
  — [Liu et al. 2020](https://arxiv.org/pdf/2007.08202)

### Inferences
- Dans SPIBB, N∧ compte des transitions servant à estimer une loi multinomiale de successeurs, dont l'erreur décroît en 1/sqrt(N). Pour un taux d'événements rares, l'échelle pertinente n'est pas un compte brut mais le **nombre d'erreurs attendu au niveau de la barre** (n_eff × barre). « N∧ = 10 écritures » n'a aucun sens à 1/20 000. On transpose donc la logique de SPIBB, pas sa valeur.
- La porte de SPIBB est construite sur des comptes de visites, non sur les résultats (récompenses). Elle ne regarde pas l'issue qu'elle va juger. Pour nous, la porte doit dépendre du volume (n_eff) et de la barre, jamais du nombre d'erreurs observées, sinon on introduit un biais de sélection.
- Tous les auteurs (Laroche, Nadjahi, Scholl, Wienhöft) reconnaissent que le seuil « théorique » est hors d'atteinte. Le seuil réellement employé est choisi en simulation (grille, plusieurs tailles de données, critère de queue CVaR). Pour un préenregistrement, l'équivalent défendable est de fixer le seuil avant les données, par simulation des courbes de décision sur des taux d'agents plausibles (0,1×, 1×, 10× la barre). C'est le cadre de simulation déjà utilisé dans le projet.
- Les résultats de SPIBB montrent un plancher (risque à N∧ bas et petit |D|) puis un plateau sûr où l'on paie en conservatisme. Le seuil n'a pas besoin d'être réglé finement s'il est au-dessus du plancher.
- Soft-SPIBB suggère une alternative continue : pondérer la preuve d'un type par sa précision plutôt que tout-ou-rien. Mais sa preuve était fausse (Scholl), donc prudence avec les variantes « douces » non vérifiées.
- Le point de Simão (garantie fonction du nombre de trajectoires) justifie de calculer n_eff au niveau de la tâche (grappe), comme le fait déjà la correction intra-tâche.

### Gaps
- Aucune source ne donne de règle non empirique pour fixer N∧. Les auteurs le traitent explicitement comme hyperparamètre.
- Le code officiel SPIBB et ses valeurs par défaut n'ont pas été consultés.
- Le lieu de publication de Wienhöft et al. (IJCAI 2023), celui de Liu et al. (NeurIPS 2020) et la version publiée de Scholl et al. (version étendue d'un article ICAART 2022) ne sont pas vérifiés dans le texte lu. Celui de Soft-SPIBB (ECML-PKDD 2019) est confirmé par la bibliographie de Wienhöft et al.

## 2. Seldonian et HCPI : la sortie « No Solution Found », le découpage des données, la confiance face à la taille d'échantillon

### Takeaway
Ces méthodes font de « pas assez de données » une **sortie explicite**, NSF (No Solution Found), distincte d'une solution, et reviennent à la solution existante en cas de NSF. Le test de sûreté porte sur une partie réservée des données (en général 80 %) avec une borne de haute confiance. Avec peu de données, NSF est fréquent. Les auteurs listent comme question ouverte la nécessité de dire si un NSF vient d'un manque de données ou de contraintes contradictoires, ce qui est exactement notre distinction entre « absence de preuve » et « preuve d'absence ».

### Cited Findings
- Schéma général (Thomas, Castro da Silva, Barto, Giguere, Brun, Brunskill, *Science* 366:999–1004, 2019) :
  - l'algorithme renvoie « either a solution θc or NSF (no solution found) » ;
  - les données sont coupées en D1 et D2 ; « Candidate Selection » choisit une solution sur D1 en anticipant le test ;
  - « Safety Test » vérifie sur D2, par test t de Student ou inégalité de Hoeffding, si la confiance est suffisante ; sinon, NSF.
  — [Thomas et al. 2019](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- Définition de NSF (matériel supplémentaire) : « there may not be sufficient data for any algorithm to ensure that the behavioral constraints are met ». L'algorithme « should return NSF when it is unable to find a satisfactory solution given the available data ». Si NSF, « we can revert to using the baseline solution » — [Thomas et al. 2019, suppl.](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- Garde-fou contre la paresse : « the algorithm that always returns NSF is trivially Seldonian ». L'objectif doit donc pénaliser NSF, et il faut chercher « a Seldonian algorithm that returns NSF less frequently » — [Thomas et al. 2019, suppl.](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- Coût des bornes sans hypothèse de loi (Hoeffding) : certains problèmes « might require an impractical amount of data ». D'où les algorithmes quasi-Seldonian (test t, bootstrap), plus serrés mais seulement approximativement valides — [Thomas et al. 2019, suppl.](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- Découpage des données :
  - régression équitable NDLR et QNDLR : « Partition D into D1 (20% of data) and D2 (80% of data) » ;
  - HCPI : « we place 1/5 of the trajectories in the training set and the remainder in the test set ».
  — [Thomas et al. 2019, suppl.](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf) ; [Thomas, Theocharous, Ghavamzadeh, ICML 2015](https://proceedings.mlr.press/v37/thomas15.pdf)
- Interaction entre taille du test et sélection : la sélection du candidat prend |D2| en entrée et prédit le résultat du test de façon conservatrice (« over-prediction »), car une sous-prédiction fait renvoyer NSF trop souvent. Dans l'algorithme général (Fig. S15), l'intervalle du test t est **doublé** pendant la sélection — [Thomas et al. 2019, suppl.](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- Questions ouvertes posées par les auteurs :
  - faire du découpage D1/D2 un problème d'arrêt optimal ;
  - savoir si le doublement suffit pour que la probabilité de NSF tende vers 0 quand les données croissent ;
  - « How can a Seldonian algorithm explain to the user why it returned NSF, e.g., do constraints appear to be conflicting, or is there just not enough data? »
  — [Thomas et al. 2019, suppl.](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- Contraintes impossibles : l'algorithme doit renvoyer NSF avec forte probabilité. Il « can effectively say "I cannot do that." » — [Thomas et al. 2019, suppl.](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- Petits échantillons : NDLR et QNDLR « may often return No Solution Found ». Les auteurs refusent d'abandonner les contraintes (« insufficient data does not require us use methods that do not provide guarantees »). Ils évoquent des variantes plus faibles, par exemple garantir qu'« a third party could not show negligence » : personne ne pourrait montrer avec haute confiance, sur ces données, que la solution viole le seuil. Ces variantes « can produce solutions with any amount of data, they do not provide satisfying guarantees » — [Thomas et al. 2019, suppl.](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- Résultats publiés : les figures montrent, en fonction de la quantité de données, « the probability that each algorithm returned a solution ». Les algorithmes non Seldonian renvoient toujours une solution. Les algorithmes Seldonian en renvoient « using a reasonable amount of data » et sont les seuls à respecter les contraintes de façon fiable — [Thomas et al. 2019](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- RL (dosage d'insuline) : la performance moyenne utilise la politique initiale quand l'algorithme renvoie NSF. C'est un repli explicite sur la référence — [Thomas et al. 2019, suppl., Fig. S25](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- HCPI (2015) :
  - « safe » signifie que la probabilité de proposer une politique sous ρ− est au plus δ ;
  - pour éviter le problème des comparaisons multiples, on réserve des données « only used for a single safety test » ;
  - en démarrage à froid (peu de trajectoires), l'approche naïve « has a tendency to overfit », produisant un candidat qui semble passer mais échoue au test ;
  - l'algorithme 4 renvoie « NO SOLUTION FOUND (NSF) or a (semi-)safe policy ».
  — [Thomas, Theocharous, Ghavamzadeh 2015](https://proceedings.mlr.press/v37/thomas15.pdf)

### Inferences
- La correspondance avec notre cadre :

  | Seldonian | Notre cadre |
  |---|---|
  | Test de sûreté (borne supérieure de haute confiance) | Critère « preuve » (borne supérieure à 95 %, jugée trop stricte) |
  | NSF | « Indéterminé » |
  | « Contraintes contradictoires » | « Rien à déléguer » (preuve que l'agent est au-dessus de la barre) |

  Les auteurs eux-mêmes demandent de distinguer les deux dernières lignes, ce qui soutient une sortie à trois valeurs plutôt que de fondre « pas assez de données » dans « rien à déléguer ».
- La « variante faible » (aucun tiers ne peut prouver la négligence) revient à demander qu'on ne puisse pas montrer, avec haute confiance, que le taux dépasse la barre. Elle produit une réponse avec n'importe quelle quantité de données mais garantit peu : c'est exactement notre échec actuel (toujours délégable quand 0 erreur faute d'écritures). Une porte d'observabilité redonne du sens à cette variante.
- « Au moins un type d'action » choisit le meilleur de plusieurs candidats et le juge sur les mêmes données. C'est la situation que HCPI évite en testant un seul candidat sur des données réservées. Sans correction (ordre fixé à l'avance, Bonferroni), la probabilité de déclarer délégable un mauvais agent croît avec le nombre de types qui passent la porte.
- Que la meilleure configuration de HCPI dans le banc SPIBB corresponde à une confiance de 0,1 montre ce que coûte en puissance une exigence de preuve stricte quand les données sont rares. C'est cohérent avec les 39–65 % observés dans le projet pour des agents à 0,1× la barre.

### Gaps
- Le paramètre par défaut de part de données réservée à la sûreté dans la boîte à outils Seldonian n'a pas été vérifié.
- Les probabilités de NSF en fonction de n n'ont pas été extraites en chiffres des figures du *Science* (elles sont seulement graphiques).

## 3. Prédiction conforme, contrôle conforme du risque et Learn-then-Test : taille minimale de calibration et groupes (Mondrian) trop petits

### Takeaway
Les méthodes conformes ont une condition intégrée qui vérifie si les données « voient » le niveau visé. Un ensemble non trivial exige n ≥ 1/α − 1 ; sinon le quantile est infini et l'ensemble prédit contient tout. Le contrôle conforme du risque (CRC) se replie sur λ_max, le réglage le plus conservateur, quand la contrainte est infaisable, c'est-à-dire n < B/α − 1. Learn-then-Test s'abstient quand aucun réglage n'est certifié. Pour les petits groupes, la calibration par classe (Mondrian) reste valide mais devient triviale sous 1/α − 1 exemples. Ding et al. envoient ces classes dans un « cluster nul » calibré sur l'ensemble poolé, en fixant le seuil de rareté à partir de n_α = 1/α − 1. Les résultats d'impossibilité montrent qu'une garantie sur tous les petits sous-groupes coûte autant qu'un niveau marginal beaucoup plus strict.

### Cited Findings
- Quantile conforme : q̂ = s_⌈(n+1)(1−α)⌉ « when α ≥ 1/(n+1) and q̂ = ∞ otherwise » ; « in the case q̂ = ∞, C(Xtest) = Y, so the coverage property is trivially satisfied » — [Angelopoulos & Bates, Gentle Introduction (arXiv 2107.07511)](https://arxiv.org/pdf/2107.07511)
- Taille de calibration en pratique :
  - la couverture conditionnelle au jeu de calibration suit Beta(n+1−l, l), avec l = ⌊(n+1)α⌋ ;
  - recommandation « about 1000 calibration points » (couverture typiquement entre 0,88 et 0,92 pour α = 0,1) ;
  - Table 1, n requis pour un écart ε à δ = 0,1 et α = 0,1 : 9 812 (ε = 0,005), 244 390 (ε = 0,001), et 2 491 pour ε = 0,01. Ce dernier rapprochement est reconstitué : le tableau a été mal extrait, mais la valeur est cohérente avec n ≈ (1,645·0,3/ε)².
  — [Angelopoulos & Bates](https://arxiv.org/pdf/2107.07511)
- CRC (Angelopoulos, Bates, Fisch, Lei, Schuster, arXiv 2208.02814) : λ̂ = inf{λ : (n/(n+1))·R̂_n(λ) + B/(n+1) ≤ α} ; « When the set is empty, we define λ̂ = λmax », le réglage le plus conservateur. La procédure est serrée à 2B/(n+1) près — [Angelopoulos et al., CRC](https://arxiv.org/pdf/2208.02814)
- Learn-then-Test (Angelopoulos, Bates, Candès, Jordan, Lei, arXiv 2110.01052) :
  - objectif (α, δ)-RCP : P(R(T_λ̂) ≤ α) ≥ 1−δ ;
  - « some risks cannot be controlled at every level α for every data-generating distribution; in such cases, we abstain from returning an RCP » ;
  - p-valeurs Hoeffding-Bentkus, contrôle du taux d'erreur familial (FWER) par test en séquence fixe ;
  - en classification sélective, borne binomiale exacte calculée sur n(T), le nombre d'exemples non abstenus.
  — [Angelopoulos et al., LTT](https://arxiv.org/pdf/2110.01052)
- Classes rares (Ding, Angelopoulos, Bates, Jordan, Tibshirani, NeurIPS 2023, arXiv 2306.09335) : en calibration par classe, « for any class y for which |I_y| < (1/α) − 1, we will have q̂_y = ∞ », et l'ensemble contient alors y quelles que soient les données — [Ding et al. 2023](https://arxiv.org/pdf/2306.09335)
- Repli par pooling, le « cluster nul » :
  - les classes sont regroupées en M clusters plus un cluster « null » destiné aux « rare classes that do not have sufficient data to be confidently clustered » ;
  - pour ces classes, on compare le score au quantile « that would be obtained from running STANDARD on the proper calibration set », c'est-à-dire le quantile marginal poolé ;
  - la garantie de couverture par cluster (Proposition 1) ne vaut que pour les clusters non nuls.
  — [Ding et al. 2023](https://arxiv.org/pdf/2306.09335)
- Seuil de rareté fondé sur la théorie : une classe va au cluster nul si |I1_y| < n_α, avec n_α = (1/min{α, 0,1}) − 1, parce que son quantile extrême « will not be finite ». Pour l'heuristique de réglage, n_α = 1/α − 1 est « the minimum sample size needed so that the finite-sample adjusted (1 − α)-quantile […] is finite (e.g., nα = 9 when α = 0.1) » — [Ding et al. 2023](https://arxiv.org/pdf/2306.09335)
- Heuristiques de réglage : ñ = max(n_min, n_α), γ = K/(75+K), M = ⌊γñ/2⌋. Elles visent au moins 2M exemples de clustering par classe et « at least 150 examples per cluster on average ». Les heuristiques « do not always choose the parameter values that yield the best performance » — [Ding et al. 2023](https://arxiv.org/pdf/2306.09335)
- Régimes empiriques :
  - moins d'environ 10 exemples par classe : seule la méthode STANDARD (poolée) est possible ;
  - 20 à 75 : CLUSTERED ;
  - plus de 75 : CLUSTERED, ou CLASSWISE si les classes sont équilibrées ;
  - au moins 100 dans la classe la plus rare : CLASSWISE ;
  - transition vers 20–40 exemples (score softmax) ou 50–100 (score RAPS) ;
  - « The boundaries between these regimes are not universal ».
  — [Ding et al. 2023](https://arxiv.org/pdf/2306.09335)
- Limite fondamentale (Barber, Candès, Ramdas, Tibshirani, arXiv 1903.04684) :
  - couverture conditionnelle approchée (1−α, δ)-CC : couverture ≥ 1−α pour tout sous-ensemble de masse P_X ≥ δ ;
  - elle est obtenue trivialement par une couverture marginale au niveau 1 − αδ, et leur Théorème 2 montre que toute méthode (1−α, δ)-CC n'est « essentially no better than this kind of trivial construction » en longueur d'intervalle ;
  - exemple : α = 0,05 et δ = 0,1 imposent des intervalles à 99,5 %.
  — [Barber et al. 2020](https://arxiv.org/pdf/1903.04684v2)
- Garanties par groupe dégradées pour les petits groupes (Jung, Noarov, Ramalingam, Roth, arXiv 2209.15145) : l'erreur de couverture conditionnelle au groupe g et au seuil v est bornée par sqrt(α / Pr[g(x)=1, f(x)=v]). Elle croît donc quand la masse du groupe diminue. La méthode de Barber et al. pour groupes chevauchants y est décrite ainsi : calibrer un seuil par groupe et prendre « the most conservative threshold among all groups x belongs to » — [Jung et al. 2022](https://arxiv.org/abs/2209.15145)

### Inferences
- n ≥ 1/α − 1 est le précédent ML le plus net d'une **porte d'observabilité indexée sur le niveau visé**. Elle équivaut à environ un dépassement attendu au niveau α parmi les points de calibration. Transposée à nos barres : n_eff ≥ 199, 1 999 et 19 999 écritures (faible, moyen, fort enjeu).
- Ding et al. fournissent un patron complet. On estime par strate quand la strate voit le niveau, on se replie sur une estimation poolée sinon. Le seuil combine un plancher théorique (n_α) et des régimes empiriques. Pour nous, le repli peut être « non délégable » (le choix SPIBB) ou une estimation poolée entre types, au prix d'une garantie seulement marginale, comme pour le cluster nul.
- Le repli de CRC sur λ_max équivaut à notre défaut conservateur (pas de délégation). L'abstention de LTT correspond à « indéterminé ».
- Barber et al. impliquent qu'exiger une preuve sur chaque petite strate (type à fort enjeu) coûte intrinsèquement autant qu'un niveau global beaucoup plus strict. Il n'existe pas de raccourci qui garantisse quelque chose de non trivial sur une strate qui ne contient pas assez de données à son niveau.

### Gaps
- Le traitement des petites catégories dans les écrits fondateurs de Vovk sur le Mondrian n'a pas été consulté.
- Les lieux de publication de Barber et al. et de Jung et al. ne sont pas vérifiés (seule la version arXiv a été lue).
- Aucune règle publiée de fusion de catégories Mondrian n'a été trouvée en dehors de Ding et al.

## 4. Classification sélective et abstention avec garanties par groupe quand certains groupes sont rares

### Takeaway
SGR certifie un risque maximal sur la région acceptée par la queue binomiale exacte, avec une correction de Bonferroni sur ⌈log2 m⌉ seuils essayés. La garantie est marginale sur les entrées acceptées, pas par groupe. Les risques cibles très faibles exigent beaucoup d'exemples acceptés. L'abstention peut aggraver les écarts entre groupes.

### Cited Findings
- SGR (Geifman & El-Yaniv, arXiv 1705.08500, 2017) :
  - entrées : risque cible r*, confiance δ, échantillon S_m ;
  - recherche dichotomique sur k = ⌈log2 m⌉ seuils de confiance, avec la borne b*_i = B*(r̂_i, δ/⌈log2 m⌉, g_i(S_m)), solution de l'équation de queue binomiale (Gascuel & Caraux 1992) ;
  - les auteurs la présentent comme « the tightest possible numerical generalization bound » dans ce cadre, plus serrée que les bornes analytiques de type Hoeffding ;
  - la garantie porte sur le risque conditionnel à l'acceptation, R(f|P_g).
  — [Geifman & El-Yaniv 2017](https://arxiv.org/pdf/1705.08500)
- Chiffres, avec δ = 0,001 :
  - CIFAR-10, environ 5 000 exemples pour SGR et 5 000 pour le test : r* = 0,01 donne un risque test de 0,0092, une couverture de 0,786 et une borne de 0,0099 ;
  - ImageNet (VGG-16, top-1), environ 25 000 exemples : r* = 0,02 donne une couverture d'environ 0,23.
  — [Geifman & El-Yaniv 2017](https://arxiv.org/pdf/1705.08500)
- LTT applique la même logique à la classification sélective : borne binomiale exacte sur le risque conditionnel, calculée sur n(T), le nombre de prédictions non abstenues — [Angelopoulos et al., LTT](https://arxiv.org/pdf/2110.01052)
- Jones, Sagawa, Koh, Kumar, Liang (ICLR 2021) : la classification sélective « can magnify existing accuracy disparities between various groups », et « increasing abstentions can even decrease accuracies on some groups » — [Jones et al. 2021](https://arxiv.org/abs/2010.14134)

### Inferences
- Calcul personnel : pour certifier r* avec 0 erreur, il faut (1−r*)^n ≤ δ', soit n ≥ ln(1/δ')/r*. Pour SGR sur CIFAR-10 (δ' = 0,001/13), r* = 0,01 exige environ 950 exemples acceptés sans erreur. C'est la même structure que la règle de trois (section 5). La taille requise croît en 1/r*.
- Pour nous, le « risque » d'un type d'action se certifie de la même façon. SGR plaide pour une borne binomiale exacte (Clopper-Pearson) plutôt que Hoeffding, et pour une correction de la recherche sur plusieurs seuils ou types (Bonferroni, séquence fixe).
- Jones et al. avertissent qu'un mécanisme d'abstention ou de repli calibré globalement n'assure rien de tel pour chaque strate. Une porte par type est donc nécessaire, pas seulement une règle globale.

### Gaps
- Aucune source primaire n'a été lue sur le *learning to defer* avec garanties par groupe pour des groupes rares.
- Aucune variante de SGR par groupe n'a été trouvée.

## 5. Précédents de portes d'observabilité ; absence de preuve et preuve d'absence

### Takeaway
Les précédents les plus proches de « ne faire confiance qu'où les données voient la barre » sont :
- le n ≥ 1/α − 1 conforme et le cluster nul de Ding ;
- le N∧ de SPIBB (compte brut) et le b = n0/n de PQL ;
- la règle de trois (0 événement sur n donne p ≤ 3/n à 95 %) ;
- les normes NCHS de publication des proportions : n effectif minimal de 30, critères de largeur d'intervalle, revue obligatoire des estimations à 0 événement.

La statistique classique insiste sur le fait que l'absence de preuve n'est pas une preuve d'absence.

### Cited Findings
- Règle de trois : si aucun événement n'est observé sur n essais, la borne supérieure de l'intervalle de confiance à 95 % vaut environ 3/n (puisque ln 0,05 ≈ −3). Référence : Hanley & Lippman-Hand, « If nothing goes wrong, is everything all right? Interpreting zero numerators », *JAMA* 1983;249(13):1743–1745 (seule la notice a été consultée) — [JAMA](https://jamanetwork.com/journals/jama/article-abstract/389714)
- Altman & Bland, « Absence of evidence is not evidence of absence », *BMJ* 1995;311:485. Appeler « négatif » un essai non significatif « wrongly implies that the study has shown that there is no difference ». L'exemple cité est un essai bien plus petit que prévu, alors qu'un calcul suggérait « that 1800 patients were needed ». Les intervalles de confiance des petites études sont « likely to be wide ». « We can never prove the absence of a relation » — [Altman & Bland 1995 (copie)](https://www.acsu.buffalo.edu/~wdmccall/os512d/EvidAbs.html) ; [BMJ](https://www.bmj.com/content/311/7003/485)
- NCHS, normes de présentation des proportions (Parker, Talih, Malec et al., *Vital Health Stat* 2(175), 2017) :
  - une proportion doit reposer sur un n et un n effectif d'au moins 30, sinon elle est supprimée ;
  - intervalle de Clopper-Pearson (Korn-Graubard pour les enquêtes complexes) ;
  - largeur absolue ≥ 0,30 : suppression ;
  - largeur absolue entre 0,05 et 0,30 avec largeur relative > 130 % : suppression ;
  - moins de 8 degrés de liberté : signalement pour revue.
  — [NCHS 2017](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- Mêmes normes, cas des zéros :
  - n_e = n / effet de plan ;
  - avec 0 événement, la variance estimée est nulle et « the effective sample size will be undefined » ; on utilise alors le n nominal pour le critère de taille et pour les intervalles ;
  - toute estimation à 0 événement doit être « flagged for statistical review » ;
  - l'observation de zéro événement peut pourtant « provide important information (e.g., in the context of rare health outcomes) ».
  — [NCHS 2017](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- Précédents ML déjà cités : porte n ≥ 1/α − 1 et cluster nul ([Ding et al. 2023](https://arxiv.org/pdf/2306.09335)) ; N∧ de SPIBB ([Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)) ; b = n0/n, « N∧ […] analogous to b·n » ([Liu et al. 2020](https://arxiv.org/pdf/2007.08202)).

### Inferences
- **Trois portes, une même échelle.** Soit c = n_eff × barre (nombre d'erreurs attendu au niveau de la barre) et k le multiple « clairement mauvais » (par exemple 10) :

  | Porte | Condition | Équivalence | Analogue |
  |---|---|---|---|
  | Preuve | c ≥ 3 | Seul seuil où 0 erreur peut prouver p ≤ barre à 95 % | Règle de trois, critère Seldonian / UCB |
  | Plancher conforme | c ≥ 1 | Environ n ≥ 1/barre − 1 | Ding, n_α |
  | Détectabilité | k × c ≥ 3, soit c ≥ 0,3 pour k = 10 | Borne à 95 % avec 0 erreur ≤ k × barre | Puissance de détecter un agent 10× pire |

  Calcul personnel, n_eff minimal par barre :

  | Porte | Faible (1/200) | Moyen (1/2 000) | Fort (1/20 000) |
  |---|---|---|---|
  | Détectabilité (c = 0,3) | 60 | 600 | 6 000 |
  | Plancher conforme (c = 1) | 200 | 2 000 | 20 000 |
  | Preuve (c = 3) | ≈ 600 | ≈ 6 000 | ≈ 60 000 |

- **Courbes de décision par type.** Calcul personnel, loi de Poisson sur n_eff (approximation qui ignore la surdispersion résiduelle). Règle « porte puis estimation ponctuelle » : délégable si e ≤ c. On donne la probabilité de « délégable » pour un agent dont le vrai taux vaut k × barre :

  | Règle | k = 0,1 | k = 0,5 | k = 1 | k = 2 | k = 10 |
  |---|---|---|---|---|---|
  | Ponctuelle, c = 0,3 | 0,970 | 0,861 | 0,741 | 0,549 | **0,050** |
  | Ponctuelle, c = 1 | 0,995 | 0,910 | 0,736 | 0,406 | 0,0005 |
  | Ponctuelle, c = 3 | 1,000 | 0,934 | 0,647 | 0,151 | ≈ 0 |
  | Borne à 95 % ≤ barre, c = 3 (passe seulement si e = 0) | 0,741 | 0,223 | 0,050 | 0,002 | ≈ 0 |
  | Borne à 95 % ≤ barre, c = 10 (e ≤ 4) | 0,996 | 0,440 | 0,029 | ≈ 0 | ≈ 0 |

  Sans porte, avec c = 0,03 (par exemple 600 écritures à 1/20 000), un agent à 10× passe avec probabilité e^(−0,3) ≈ 0,74 : c'est le défaut constaté dans le projet. Sous c = 3, la règle de la borne à 95 % ne déclare jamais rien de délégable.
- La porte de détectabilité réalise exactement « absence de preuve ≠ preuve d'absence ». On ne lit « 0 erreur » comme une preuve que si un agent clairement mauvais en aurait produit plusieurs. Elle équivaut à exiger que la borne supérieure à 95 % exclue le niveau « clairement mauvais », et non la barre elle-même. C'est une marge de type non-infériorité, moins stricte que la preuve.
- Les normes NCHS montrent qu'un seuil générique (n_eff ≥ 30, largeur absolue ≤ 0,05) ne convient pas aux événements rares. Une proportion nulle sur 1 000 passe le critère de largeur absolue sans rien dire d'une barre à 1/20 000. La porte doit donc être indexée sur la barre. Le NCHS rappelle aussi qu'avec 0 événement, un n_eff calculé à partir de la variance observée est indéfini. Pour nous, cela invite à calculer le n_eff de la porte à partir d'une corrélation intra-tâche ou d'un effet de plan fixé à l'avance (ou poolé sur l'ensemble des types), pas à partir des erreurs de la strate jugée.

### Gaps
- Aucun article ML formalisant explicitement une porte « événements attendus au seuil ≥ c » sous ce nom n'a été trouvé. Les analogues sont le plancher conforme, la règle de trois et les bornes binomiales de SGR et LTT.
- Le rapport RAND « Driving to Safety » (exposition nécessaire pour démontrer un taux rare sans défaillance) n'a pu être consulté (accès refusé, 403). Il n'est pas cité.
- Les normes NCHS concernent la publication de statistiques, pas une décision. L'analogie est structurelle.

## 6. Leçons pratiques : le repli est-il conservateur et bien calibré, et que coûte-t-il ?

### Takeaway
Dans les bancs d'essai, se replier sur la référence dans les strates à faible compte est conservateur et empiriquement sûr dès que le seuil dépasse un petit plancher. Ce n'est pas une calibration au sens strict : la garantie théorique est vide aux seuils pratiques, et la sûreté est établie par simulation sur des critères de queue.

Coûts connus :
- perte de puissance sur petits jeux, surtout quand la référence est mauvaise ;
- discontinuité (tout ou rien) et dépendance au seuil ;
- méthodes calibrées sur la théorie qui se replient toujours ;
- garanties non transférées aux sous-groupes.

Remèdes publiés : contraintes douces (Soft-SPIBB), bornes plus serrées (Wienhöft), pooling ou structure (Ding ; SPIBB factorisé), sortie NSF explicite, choix du seuil par simulation avec critère de pire cas.

### Cited Findings
- Perte de puissance : « SPIBB algorithms are too conservative for small datasets but catch up on the bigger ones » quand la baseline est mauvaise — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
- Méthodes calibrées sur la théorie qui se replient toujours :
  - Robust MDP se replie sur la baseline sous 50 000 trajectoires, et les tests de sûreté de RaMDP et Robust MDP « always failed » — [Laroche et al. 2019](https://arxiv.org/pdf/1712.06924)
  - Πb-SPIBB à N∧ théorique reproduirait toujours la baseline sous plus de 10 millions d'observations — [Scholl et al. 2022](https://arxiv.org/pdf/2208.00724)
- Effet de seuil :
  - le caractère tout-ou-rien de SPIBB « may be too conservative » ;
  - RaMDP bascule dans la sur-prudence au-delà de κ_adj ≈ 0,0035 ;
  - Soft-SPIBB est plus lisse, avec ε optimal dans [0,5 ; 2].
  — [Nadjahi et al. 2019](https://arxiv.org/pdf/1907.05079)
- Compromis explicite : « The mean performance improves as the safety decreases » (choix de N∧ = 10) — [Nadjahi et al. 2019](https://arxiv.org/pdf/1907.05079)
- Le seuil devient un hyperparamètre parce que la borne est trop grande. Resserrer les bornes divise environ par deux les données nécessaires pour commencer à améliorer — [Wienhöft et al. 2023](https://arxiv.org/pdf/2305.07958)
- Le repli doit être une vraie référence. Une baseline estimée ajoute une erreur irréductible : on ne peut pas « pretend it was generated with an optimal policy » — [Simão et al. 2020](https://arxiv.org/pdf/1909.05236)
- Les données corrélées comptent par trajectoire : la garantie dépend du nombre de trajectoires, pas du nombre de visites — [Simão et al. 2020](https://arxiv.org/pdf/1909.05236)
- L'abstention peut faire baisser la précision de certains groupes — [Jones et al. 2021](https://arxiv.org/abs/2010.14134)
- Pooling des strates rares en cluster nul (quantile marginal) : c'est un repli utile, mais il n'offre qu'une garantie marginale à ces strates — [Ding et al. 2023](https://arxiv.org/pdf/2306.09335)
- Sortie NSF explicite avec retour à la référence, et nécessité d'expliquer si NSF vient d'un manque de données ou d'un conflit — [Thomas et al. 2019, suppl.](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)

### Inferences
Implications pour notre condition de délégabilité :

1. **Remplacer « p̂_t ≤ barre_t » par « type t éligible ET p̂_t ≤ barre_t ».** L'éligibilité est une porte calculée sur le plan d'expérience (n_eff,t et barre_t), jamais sur les erreurs observées, comme le N∧ de SPIBB porte sur des visites et non sur des issues. Deux candidates principiées :
   - (a) **porte de détectabilité** : n_eff,t × k × barre_t ≥ 3, avec k = 10 pour coller au défaut constaté (« agents 10× au-dessus de la barre »). Elle borne à 5 % la probabilité de déclarer éligible-et-passant un type pour un agent à k × barre ;
   - (b) **plancher conforme** : n_eff,t × barre_t ≥ 1, plus strict, qui écarte quasi totalement les agents à 10× (0,0005) tout en laissant passer 99,5 % des agents à 0,1×.

   La preuve (borne à 95 % ≤ barre) reste le critère Seldonian. Elle est jugée trop stricte, et le calcul ci-dessus confirme son manque de puissance quand c est petit.
2. **Sortie à trois valeurs**, sur le modèle de NSF :
   - « Délégable » : au moins un type éligible passe ;
   - « Rien à déléguer » : au moins un type est éligible et aucun ne passe. On peut exiger en plus une borne inférieure > barre pour parler d'agent « clairement non fiable » ;
   - « Indéterminé » : aucun type éligible.

   Si le préenregistrement impose une sortie binaire, « Indéterminé » vaut « non délégable » (le repli SPIBB, CRC λ_max), mais il doit être rapporté à part. Sinon on confond à nouveau absence de preuve et preuve d'absence.
3. **Choix du seuil :**
   - (i) un plancher théorique indexé sur la barre (c = 1, le n_α conforme ; ou k·c = 3, la règle de trois au niveau « clairement mauvais ») ;
   - (ii) une validation par simulation des courbes de décision (taux 0,1×, 1×, 10×), avec critère de pire cas, comme pour N∧ dans SPIBB, Soft-SPIBB et chez Scholl et al. ;
   - (iii) un gel avant les données.

   Les résultats SPIBB suggèrent une faible sensibilité au-dessus du plancher, avec un coût en conservatisme.
4. **Multiplicité.** « Au moins un type » est une union. Il faut soit un ordre fixé à l'avance (séquence fixe, comme dans LTT), soit une correction (Bonferroni, comme SGR et HCPI), soit au minimum rapporter l'inflation du taux de fausse délégation avec le nombre de types éligibles.
5. **n_eff de la porte.** Il faut le compter au niveau de la tâche (Simão) avec une corrélation intra-tâche ou un effet de plan préenregistré ou poolé. À 0 erreur, une estimation de la corrélation propre à la strate est indéfinie (NCHS).
6. **Effet attendu.** Les types à fort enjeu seront souvent non éligibles (6 000 à 20 000 écritures effectives nécessaires selon la porte). La délégabilité d'une configuration reposera alors sur les types faible et moyen enjeu. « Rien à déléguer » redeviendra possible et retrouvera son sens : il signalera des agents que les données voient au-dessus de la barre.

### Gaps
- Aucune étude de référence ne mesure, hors des articles SPIBB, Scholl et Wienhöft, la sensibilité de N∧ sur une grande famille de domaines.
- Aucune source ne traite le cas « union sur strates » avec repli strate par strate. Les recommandations sur la multiplicité sont transposées de HCPI, SGR et LTT.
- Les courbes de décision ci-dessus sont des approximations de Poisson par type isolé. Elles ne remplacent pas la simulation du projet (plusieurs types, corrélation intra-tâche).
