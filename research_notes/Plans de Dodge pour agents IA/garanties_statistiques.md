# Garanties statistiques d'une règle d'autonomie méritée sous non-stationnarité

Méthode : 12 recherches web (résumés de recherche, pas de lecture intégrale des PDF sauf mention). Les calculs marqués « calcul » sont les miens (Python, formules données) : ils ne sont pas sourcés et doivent être relus. Notation : p = taux d'erreur par action, p* = 1/2 600 ≈ 3,85e-4, d = probabilité de détecter une erreur (≈ 0,95 d'après le contexte).

## 1. SPRT de Wald, CUSUM, bornes de délai de détection

### Takeaway
Le SPRT garantit des erreurs de décision (α, β) pour UN test sur un flux i.i.d. de paramètre fixe ; il ne dit rien d'un test redémarré/réfléchi sur un horizon long ni d'un changement non annoncé. Pour le changement, la garantie pertinente est celle du CUSUM : fausse alarme (ARL ≥ γ) contre délai ≈ ln γ / KL, minimax optimal (Lorden, Moustakides). Aucun détecteur ne peut battre ce plancher en ordre de grandeur.

### Cited Findings
- Seuils SPRT approchés A = (1−β)/α et B = β/(1−α) ; Wald montre α' + β' ≤ α + β (exemple α=0,2, β=0,1 : α' ≤ 0,222, β' ≤ 0,125). Les seuils sont approchés ; vérifier par Monte-Carlo. — [sprtt vignette](https://cran.nics.utk.edu/cran/web/packages/sprtt/vignettes/sprt.html), [Statistical Model Checking overview](https://arxiv.org/pdf/1005.1327)
- Les tests répétés sur données cumulées gonflent l'erreur de type I ; la recherche web n'a rien donné sur un SPRT redémarré avec cumul d'erreur d'un redémarrage à l'autre. — [SPRT intro](https://cran.nics.utk.edu/cran/web/packages/sprtt/vignettes/sprt.html) (lacune explicitée dans Gaps)
- Lorden (1971) : critère de délai pire-cas sous contrainte d'ARL ; le CUSUM de Page est asymptotiquement minimax d'ordre 1 ; Moustakides (1986) l'optimalité exacte sous le critère de Lorden. Asymptotique : ARL₀ ≈ e^h, délai pire-cas ≈ h / KL(post‖pré) ; le délai croît en log de la fréquence de fausses alarmes. — [Sequential (Quickest) Change Detection: Classical Results and New Directions](https://arxiv.org/pdf/2104.04186), [Beyond boundaries: Lorden's contributions](https://arxiv.org/pdf/2403.18782)
- Le délai pire-cas de Lorden est jugé pessimiste (il suppose les pires données pré-changement). — [Classical Results and New Directions](https://arxiv.org/pdf/2104.04186)
- CUSUM à fenêtre limitée (paramètre post-changement estimé sur fenêtre glissante) : optimal d'ordre 1 sous Lorden, utile quand l'amplitude du saut est inconnue. — [Window-Limited CUSUM](https://arxiv.org/pdf/2206.06777)
- Poor (1998) : sous pénalité exponentielle du délai, le CUSUM de Page peut être arbitrairement défavorable. — [Quickest detection with exponential penalty](https://academicnewsletter.sufe.edu.cn/info/436695)

### Inferences
- Calcul (KL de Bernoulli, KL(p1‖p0) = p1 ln(p1/p0) + (1−p1) ln((1−p1)/(1−p0)), n ≈ ln γ / KL, ordre 1, sans surplus de dépassement) :

| Changement | KL (nats/obs) | n pour ARL 10³ | 10⁴ | 10⁵ | 10⁶ |
|---|---|---|---|---|---|
| 0,5 % → 2 % | 0,01284 | 538 | 717 | 897 | 1 076 |
| 2 % → 10 % | 0,0843 | 82 | 109 | 137 | 164 |
| 0,04 % → 0,5 % | 0,00804 | 859 | 1 146 | 1 432 | 1 719 |
| 0,04 % → 2 % | 0,0588 | 117 | 157 | 196 | 235 |
| 1 % → 2 % | 0,00391 | 1 765 | 2 353 | 2 942 | 3 530 |

  Donc pour 0,5 % → 2 % avec une fausse alarme toutes les 10 000 actions, tout détecteur a besoin d'environ 700 actions (≈ 14 erreurs vues) en pire cas. Plancher dur indépendant du détecteur : voir au moins une erreur à taux p1 prend en moyenne 1/p1 = 50 observations (95 % de chance d'en voir une : 598 obs à 0,5 %, 148 à 2 %, 28 à 10 %).
- Le plafond de promotion « 2,9 % pour cible 5 % » est une garantie du type erreur de décision sur un agent constant ; elle ne se transfère pas à un agent qui change. Explication plausible du 23 % observé : le score réfléchi n'a de plancher qu'en bas, donc l'évidence accumulée avant le saut reste au-dessus du seuil et ne décroît que d'environ −0,05 nat/obs à 2 % (calcul : dérive de l'évidence défavorable, test 2 % vs 10 %) puis monte de +0,084/obs à 10 % ; l'évidence stockée met des dizaines à centaines d'observations à se vider. C'est mon hypothèse, non vérifiée par simulation ici.
- Un SPRT redémarré N fois a une erreur de type I qui croît au pire comme N·α (borne de l'union) ; non sourcé, raisonnement standard.

### Gaps
- Pas de source primaire lue (Wald 1945/1947, Lorden 1971, Moustakides 1986, Tartakovsky et al.) en texte intégral ; les formules asymptotiques viennent de revues. Les délais ci-dessus ignorent le dépassement de seuil (corrections d'ordre 1 à plusieurs dizaines d'observations pour de petits KL).
- Aucune borne trouvée pour un test redémarré/réfléchi (CUSUM renversé utilisé comme test d'acceptation).

## 2. Inférence valide à tout instant (e-valeurs, e-processus, suites de confiance, e-détecteurs)

### Takeaway
Les e-processus et suites de confiance tiennent sous suivi continu et arrêt optionnel (inégalité de Ville), mais NE réduisent PAS le nombre d'observations pour certifier p < p* à zéro erreur : le minimum est ln(1/α)/p*, identique à la règle de trois ; ils coûtent un peu plus dès que le paramètre est mélangé. Leur valeur est la validité en suivi continu, pas la vitesse. Sous changement silencieux, il faut les e-détecteurs.

### Cited Findings
- Inégalité de Ville : pour une surmartingale test non négative, P(∃t : M_t ≥ 1/α) ≤ α sous H0 ; rejeter au premier franchissement donne un test de niveau α sous toute règle d'arrêt. Nécessite la propriété conditionnelle E[M_t | F_{t−1}] ≤ M_{t−1}. Le SPRT de Wald est le cas du rapport de vraisemblance entre deux hypothèses simples (source secondaire). — [e-processes (theorempath)](https://theorempath.com/topics/e-processes), [Ville / e-values](https://math.uwaterloo.ca/~wang/files/e-review.pdf)
- Suites de confiance de Howard, Ramdas, McAuliffe & Sekhon : intervalles valides uniformément dans le temps, non asymptotiques, non paramétriques ; liens avec Cramér–Chernoff, la loi du log itéré et le SPRT ; largeur à taux LIL. Annals of Statistics 49(2), 1055–1080, 2021. — [arXiv 1810.08240](https://arxiv.org/pdf/1810.08240), [Project Euclid](https://projecteuclid.org/journals/annals-of-statistics/volume-49/issue-2/Time-uniform-nonparametric-nonasymptotic-confidence-sequences/10.1214/20-AOS1991.short)
- Waudby-Smith & Ramdas (JRSS-B 2024) : suites de confiance par pari pour moyennes bornées (donc Bernoulli), adaptatives à la variance, par martingales composites + Ville. — [arXiv 2010.09686](https://arxiv.org/abs/2010.09686v4)
- Ramdas, Grünwald, Vovk, Shafer (Statistical Science 38(4), 2023) : e-processus et suites de confiance valides à tout temps d'arrêt ; le suivi continu (peeking) doit être accommodé, pas interdit ; martingale test = richesse d'un joueur. — [arXiv 2210.01948](https://arxiv.org/abs/2210.01948v2), [Statistical Science](https://projecteuclid.org/journals/statistical-science/volume-38/issue-4/Game-Theoretic-Statistics-and-Safe-Anytime-Valid-Inference/10.1214/23-STS894.full)
- E-détecteurs (Shin, Ramdas, Rinaldo ; NEJSDS 2(2), 229–260, 2024) : somme d'e-processus démarrés à des instants consécutifs ; variantes Shiryaev-Roberts/CUSUM ; contrôle non asymptotique de l'ARL (fausses alarmes) sans hypothèse i.i.d. ; bornes de délai quasi optimales dans les cas sous-gaussien/sous-exponentiel ; le prix est un délai accru car l'amplitude du saut est inconnue (mélange de paris). — [arXiv 2203.03532](https://arxiv.org/abs/2203.03532v3), [aitopics](https://aitopics.org/doc/arxivorg:EC0306B8)
- Règle de trois (Hanley & Lippman-Hand, JAMA 249(13), 1743–1745, 1983) : zéro événement sur n, borne supérieure à 95 % ≈ 3/n (valable pour n > 30 environ). — [JAMA](https://jamanetwork.com/journals/jama/article-abstract/389714), [Wikipedia](https://en.wikipedia.org/wiki/Rule_of_three_(statistics))

### Inferences
- Calcul : avec zéro erreur, l'e-processus de H0 : p ≥ p* contre p→0 vaut (1−p*)^(−n) ; il franchit 1/α à n = ln(1/α)/(−ln(1−p*)) = 7 787 (α=5 %), 11 971 (1 %), 17 957 (0,1 %). C'est exactement la règle de trois. La fourchette « 7 600 à 15 200 » du cahier des charges correspond à α entre ≈ 5 % et ≈ 0,3 % ; cohérent.
- Calcul : un e-processus de mélange (a priori uniforme sur [0, qmax]) coûte environ ln(n·qmax) nats de plus : qmax=p* → 11 751 (α=5 %), 16 851 (1 %) ; qmax=3p* → 15 251 / 20 151 ; qmax=1 % → 21 801 / 26 501. Le prix d'ignorer p vrai : +50 % à +180 %.
- Calcul avec erreurs observées (borne de Poisson 95 %, approximation de Clopper-Pearson) : 1 erreur → 12 334 obs, 2 → 16 370, 3 → 20 160 pour garantir p < 1/2 600.
- Donc : aucun gain de taille d'échantillon à tirer de l'anytime-valid pour certifier p*. Gain réel : (a) la garantie reste vraie quand on regarde chaque jour ; (b) un seul e-processus continu remplace des redémarrages dont l'erreur s'accumule. Le prix : ce n'est valide que si p est constant (même hypothèse nulle pendant tout le flux). Après un saut, la validité de la suite de confiance porte sur un paramètre qui n'existe plus ; il faut un e-détecteur ou une suite de confiance sur fenêtre.

### Gaps
- Pas de formule fermée lue pour les bornes de délai des e-détecteurs dans le cas Bernoulli rare (0,5 %→2 %) ; le résumé de recherche ne donne que le cas sous-gaussien. À lire dans l'article (§ délai).
- Non vérifié : constantes exactes de la suite de confiance de Howard et al. pour p de l'ordre de 1e-4.

## 3. Preuves périmées après un changement silencieux (fenêtres, oubli, redémarrage)

### Takeaway
Fenêtres et oubli exponentiel limitent la mémoire mais plafonnent l'évidence accumulable : une fenêtre de largeur W ne peut certifier p* que si W ≥ ln(1/α)/p* ≈ 7 800 ; or les alarmes rapides exigent des fenêtres de quelques centaines. D'où une architecture à deux étages : certifier longtemps, surveiller court.

### Cited Findings
- CUSUM à fenêtre glissante pour l'estimation du paramètre post-changement : optimal d'ordre 1, avec une taille de fenêtre optimale caractérisée. — [Window-Limited CUSUM](https://arxiv.org/pdf/2206.06777)
- Détection adaptative par mélange de distributions prédictives (plug-in) : même compromis ARL/délai de Lorden. — [arXiv 2606.05072](https://arxiv.org/pdf/2606.05072)
- Les e-détecteurs formalisent le « redémarrage à tous les instants » (sommes d'e-processus démarrés à chaque instant) et donnent un contrôle d'ARL non asymptotique. — [arXiv 2203.03532](https://arxiv.org/abs/2203.03532v3)

### Inferences
- Calcul : temps pour gagner l'autonomie par une série de 7 800 succès consécutifs (Dodge, i=7 800) : E[T] = (1−q^i)/(p·q^i). À p=1e-4 : 11 800 actions (46 % de réussite du premier coup) ; p=2e-4 : 18 800 ; p=p*=3,85e-4 : 49 700 (5 % du premier coup) ; p=5e-4 : 96 900. Un agent pile à la limite met donc environ 50 000 actions. Compromis : plus i est grand, plus l'agent honnête met longtemps ; plus i est petit, plus le bon marché de la preuve.
- Trois arbitrages (qualitatifs, sans source dédiée) : (1) fenêtre courte : délai court mais fausses alarmes plus fréquentes ; (2) oubli exponentiel : mémoire effective ≈ 1/(1−λ), même contrainte W ≥ 7 800 pour la certification ; (3) redémarrage à zéro après alerte : sûr, mais coûte la totalité du temps de gain (≈ 50 000 actions pour p proche de p*).
- Recommandation de conception (hypothèse) : certificat = série ou e-processus long ; monitoring = CUSUM / e-détecteur sur taux d'erreur avec ARL cible fixé ; alerte → retrait immédiat et repart de zéro pour le certificat, ne pas « refroidir » l'évidence ancienne.

### Gaps
- Pas de travail trouvé qui chiffre le compromis fausses alarmes / délai / temps de gain pour un SPRT Bernoulli avec oubli exponentiel (une recherche, aucune source) ; « discounted CUSUM » et « exponentially weighted CUSUM » à chercher.

## 4. Garanties pire-cas et adversariales (plans de Dodge, AOQL, retrait au premier échec)

### Takeaway
La borne AOQL de Dodge est une garantie sur le long terme, démontrée pour un taux d'incident constant ; elle ne devient une borne sur trajectoire quelconque que par un argument de cycle, qui exige que l'échantillonnage soit imprévisible et que la détection ait une probabilité d fixe. Avec ces hypothèses, le dommage non bloqué est de l'ordre de 1/(d·i) par action, quelle que soit la suite des erreurs.

### Cited Findings
- CSP-1 (Dodge) : inspection à 100 % jusqu'à i unités conformes consécutives (nombre d'effacement), puis inspection d'une fraction f ; tout défaut trouvé renvoie à 100 %. AFI = f / [f + (1−f)·q^i], q = 1−p ; AOQ = p·(1−AFI) ; AOQL = max_p AOQ. Exemple secondaire : i=170, f=1/10 → AOQL ≈ 0,647 % à p ≈ 1,2 %. — [MetricGate CSP-1](https://metricgate.com/calculator/csp-1-continuous-sampling-plan-dodge), [Shankar & Mohapatra, Sankhyā B 1994 (via Elsmar)](https://Elsmar.com/Cove_Premium/Continuous%20Sampling%20Plan.pdf), [Thai Stat. J.](https://ph02.tci-thaijo.org/index.php/thaistat/article/download/34321/28761)
- Hypothèse du résumé de recherche : il n'existe pas de formule fermée pour i en fonction de l'AOQL cible ; on utilise des tables ou une recherche numérique. — [MetricGate](https://metricgate.com/calculator/csp-1-continuous-sampling-plan-dodge)

### Inferences
- Calcul (vérifié sur l'exemple i=170, f=0,1 : 0,644 % contre 0,647 % ; la formule AOQ = p(1−AFI) est donc bonne) :

| i | f | AOQL | p au maximum |
|---|---|---|---|
| 170 | 0,10 | 0,644 % | 1,22 % |
| 500 | 0,20 | 0,143 % | 0,34 % |
| 1 000 | 0,05 | 0,152 % | 0,25 % |
| 1 000 | 0,10 | 0,110 % | 0,21 % |
| 2 600 | 0,10 | 0,042 % | 0,08 % |

- Dérivation personnelle (non sourcée, à vérifier) d'une borne pire-cas pour « retrait au premier échec détecté » : si chaque erreur est détectée avec probabilité d indépendamment des autres et du comportement de l'agent, chaque cycle compte ≥ i+1 actions et au plus ~1/d erreurs en espérance (une détectée, qui a déjà eu lieu puisque le contrôle est après exécution, plus (1−d)/d manquées). Donc dommage ≤ (1/d)/(i + 1/d) ≈ 1/(d·i) par action. Avec d=0,95 : i=1 000 → 1,05e-3 ; i=2 600 → 4,0e-4 ; i=7 800 → 1,35e-4. Cet ordre est cohérent avec les AOQL de Dodge ci-dessus. Pour un excès cible e (erreurs par action), i ≥ 1/(d·e).
- Ce qui rend la borne fausse : (a) agent qui sait quand il est contrôlé (échantillonnage prévisible) ; (b) erreurs corrélées au détecteur (d dépend de l'erreur : erreurs « difficiles » toujours manquées → d≈0, borne vide) ; (c) détecteur qui dérive. Aucun détecteur automatique ne protège contre (b) : à garantie nulle sans seconde source (audit humain aléatoire).
- Lien avec le jeu en ligne / regret : la borne est de type regret pire-cas (cycle × coût), indépendante de la loi ; contraste avec SPRT/AOQL qui exigent un modèle probabiliste. Les paris de Ramdas et al. donnent le pendant côté statistique. Non étayé par une source lue ici.

### Gaps
- Dodge 1943 et les preuves AOQL « pour toute suite » non lues ; les formules viennent de pages de calcul et d'un article secondaire. L'énoncé « borne valable pour toute séquence » du cahier des charges n'est pas vérifié ; mon calcul suggère qu'il faut l'hypothèse d indépendant.
- Rien trouvé sur le lien explicite plans de Dodge ↔ regret en ligne.

## 5. Indicateurs avancés (quasi-accidents, signaux précurseurs, surveillance ML)

### Takeaway
Les quasi-accidents sont un indicateur avancé utile mais leur ratio de Heinrich (300:29:1) n'est pas fiable ; en ML, la confiance calibrée suit l'erreur sans étiquettes, mais seulement si la calibration tient, et la dérive des entrées n'est ni nécessaire ni suffisante.

### Cited Findings
- Le ratio de Heinrich 300-29-1 est la prémisse la plus fragile : les dossiers de Heinrich n'existent plus, ses chiffres ont changé d'une édition à l'autre sans explication (Manuele, *Heinrich Revisited*, 2002) ; non universel (aviation, nucléaire ne le retrouvent pas) ; sous-déclaration et classement hétérogène des incidents mineurs. — [ASSP Professional Safety](https://aeasseincludes.assp.org/professionalsafety/pastissues/059/09/F1Reb_0914Z.pdf), [Safety+Health](https://www.safetyandhealthmagazine.com/?p=35462), [Safety4Sea](https://safety4sea.com/near-miss-reporting-a-misleading-indicator-of-safety)
- Les chiffres de quasi-accidents se manipulent quand ils deviennent un objectif (fabrication de rapports pour remplir un indicateur) ; la valeur est la déclaration volontaire plus que le comptage. — [Safety4Sea](https://safety4sea.com/near-miss-reporting-a-misleading-indicator-of-safety)
- ML : des estimateurs fondés sur la confiance (Average Confidence, CBPE) estiment la performance sans étiquettes, mais leur erreur est corrélée linéairement à l'erreur de calibration ; la dérive des variables d'entrée n'est ni nécessaire ni suffisante pour une baisse de précision ; une dérive du seul P(y|x) est indétectable sans étiquettes ; détecteurs d'anomalies non supervisés fragiles. — [Confidence-based Estimators for Predictive Performance](https://arxiv.org/html/2407.08649v2), [ML Health](https://arxiv.org/pdf/1902.02808)
- MLDEMON : signaux non étiquetés plus petit budget d'étiquettes à la demande, pour estimer la performance en temps réel. — [arXiv 2104.13621](https://arxiv.org/pdf/2104.13621v2)

### Inferences
- Pour le protocole : un indicateur avancé n'ajoute de garantie que s'il est lui-même testé : par exemple, un e-détecteur sur le score de confiance, avec alarme déclenchant la reprise de validation humaine, ARL réglé comme pour les erreurs. Ne pas fonder la promotion dessus (risque de Goodhart).
- Les quasi-accidents (erreurs rattrapées par le contrôle automatique, validations humaines rejetées avant exécution, écarts de confiance) multiplient la matière statistique : si leur taux est r fois celui des erreurs, le délai de détection par le signal tombe d'un facteur r seulement à condition que le lien soit causal, ce qui n'est pas établi (voir critique Heinrich). Hypothèse, non quantifiée.
- Dériver sur P(y|x) seul est indétectable sans étiquettes : garder un échantillon étiqueté aléatoire en continu même chez les agents autonomes.

### Gaps
- Aucune étude peer-reviewed trouvée qui teste le 300:29:1 ; sources de sécurité surtout professionnelles. Pas de source sur le gain de délai quantifié d'un signal précurseur en agents IA.
- Pas de revue de gestion des quasi-accidents (ex. Phimister, Jones) lue.
