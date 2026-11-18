# Corrélation intra-tâche entre types d'écriture de prévalences très différentes : ICC latente, ICC observée, effet de plan

Conventions de cette note.
- **ρ_L** : ICC sur l'échelle latente d'un modèle à intercept aléatoire de tâche u_j ~ N(0, σ²). Logit : ρ_L = σ²/(σ² + π²/3). Probit : ρ_L = σ²/(σ² + 1).
- **ρ_obs** : ICC sur l'échelle observée 0/1, c'est-à-dire la corrélation de Pearson entre deux écritures d'une même tâche (du même type, sauf mention « croisée »). C'est elle, et elle seule, qui entre dans Deff = 1 + (m − 1)ρ_obs.
- **p** : prévalence marginale du type (taux d'erreur moyen sur les tâches). **m** : nombre d'écritures du type par tâche.
- Les sections « Inferences » contiennent mes propres calculs : intégration numérique (scipy `quad`) sur l'intercept aléatoire, avec β0 résolu pour que la prévalence marginale vaille exactement p. Contrôles : accord à 5 décimales avec la loi normale bivariée (probit) ; Monte-Carlo sur 400 000 tâches simulées pour la formule de dilution (§3). Ce sont des calculs sous modèle, pas des résultats publiés.
- Le défaut mesuré par le projet (ρ vrai 0,7 → estimation poolée 0,34–0,41, estimation par type 0,57–0,61) vient du brief, pas d'une source.

## 1. Échelle latente contre échelle observée : formules, et ce que la prévalence fait à l'ICC observée (1 %, 0,1 %, 0,01 %)

### Takeaway
À variance latente fixée, l'ICC observée, celle qui fait l'effet de plan, s'effondre quand la prévalence baisse. À ρ_L = 0,3 (logit), elle vaut 0,025 à 1 %, 0,0030 à 0,1 % et 0,0003 à 0,01 %, soit à peu près proportionnelle à p. À ρ_L = 0,7, elle vaut 0,23, puis 0,10, puis 0,034. En probit, la chute est plus lente (ρ_L = 0,3 : 0,046, puis 0,014, puis 0,004), et l'écart entre liens grandit avec la rareté. La conversion exacte est une intégrale : c'est la méthode B de Goldstein et al. 2002, implémentée dans QGglmm. En probit, elle a une forme fermée (normale bivariée). Les approximations de premier ordre (linéarisation, méthode delta, Dempster–Lerner, R_org de rptR) sous-estiment fortement l'ICC observée dès que la variance latente est grande. Elles surestiment donc n_eff.

### Cited Findings
- En binaire, la variance de niveau 1 dépend de l'espérance (« var(y_ij) = π_ij(1 − π_ij) »), et « the level 2 variance, σ²_u0, is measured on the logistic scale so is not directly comparable to this level 1 variance » ; dans ces modèles « the variance partitions are dependent on predictors associated with the individual observation » — [Goldstein, Browne & Rasbash 2002, prépublication PDF](https://bristol.ac.uk/media-library/sites/cmm/migrated/documents/pvmm.pdf) (publié dans *Understanding Statistics* 1(4):223–231).
- Méthode A (développement de Taylor au premier ordre, évalué en u = 0) : τ = σ²_u π²[1 + exp(Xβ)]⁻² / {σ²_u π²[1 + exp(Xβ)]⁻² + π(1 − π)}, avec π = exp(Xβ)/(1 + exp(Xβ)) — [Goldstein et al. 2002](https://bristol.ac.uk/media-library/sites/cmm/migrated/documents/pvmm.pdf).
- Méthode B (simulation) : tirer m ≈ 5000 valeurs u ~ N(0, σ̂²_u), calculer π* pour la valeur de x choisie, puis τ = v2/(v2 + v1) avec v2 = var(π*) et v1 = E[π*(1 − π*)]. « The advantage of method B is that it does not involve any approximation » — [Goldstein et al. 2002](https://bristol.ac.uk/media-library/sites/cmm/migrated/documents/pvmm.pdf).
- Méthode C (modèle linéaire sur la variable 0/1) : « if any of the underlying probabilities are close to 0 or 1, this model would not be expected to fit well » — [Goldstein et al. 2002](https://bristol.ac.uk/media-library/sites/cmm/migrated/documents/pvmm.pdf).
- Méthode D (latente) : variance de niveau 1 = π²/3 = 3,29. Elle « may be reasonable where the (0, 1) response is, say, derived from a truncation of an underlying continuum […] but would seem to have less justification when the response is truly discrete, such as mortality or voting » — [Goldstein et al. 2002](https://bristol.ac.uk/media-library/sites/cmm/migrated/documents/pvmm.pdf).
- Exemple chiffré, avec β0 = −0,256 et σ²_u = 0,142 : VPC de 0,034 (A), 0,034 (B), 0,036 (C) et 0,041 (D). Au prédicteur linéaire −2,5 (p = 0,076) : 0,0096 (A), 0,0111 (B), 0,0257 (C) — [Goldstein et al. 2002](https://bristol.ac.uk/media-library/sites/cmm/migrated/documents/pvmm.pdf).
- Conclusion de l'article : « if a VPC is required for non-linear models, it should be computed for a range of values of the predictor variables » — [Goldstein et al. 2002](https://bristol.ac.uk/media-library/sites/cmm/migrated/documents/pvmm.pdf). Les quatre méthodes sont aussi résumées par le CMM de Bristol — [FAQ MLwiN « Partitioning variation across levels »](https://www.bristol.ac.uk/cmm/software/support/support-faqs/pval.html).
- Variances propres à la loi : π²/3 (logit), 1 (probit), π²/6 (cloglog). « These theoretical variances only exist for binomial distributions » — [Nakagawa, Johnson & Schielzeth 2017, *J R Soc Interface* 14:20170213](https://pmc.ncbi.nlm.nih.gov/articles/PMC5636267).
- Variance d'observation par la méthode delta : 1/(np(1 − p)), soit 1/(p(1 − p)) en binaire. « We can replace β0 with any value obtained from the fixed part of the model ». La distinction latente/observée est « strictly appropriate only for binomial distributions ». Utiliser π²/3 « implicitly assumes all datasets have the same observation-level variance regardless of mean proportion ». Comme min 1/(p(1 − p)) = 4 > π²/3, l'ICC « delta » est toujours plus petite que l'ICC latente — [Nakagawa et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5636267).
- Même article : Browne et al. (2005) ont trouvé des ICC calculées avec π²/3 « higher » que les ICC sur l'échelle observée — [Nakagawa et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5636267). Référence : Browne, Subramanian, Jones & Goldstein 2005, *JRSS A* 168(3):599–613 — [RePEc](https://econpapers.repec.org/RePEc:bla:jorssa:v:168:y:2005:i:3:p:599-613).
- rptR (Nakagawa & Schielzeth 2010, *Biol Rev* 85:935–956, cité en référence) : `rptBinary` renvoie R_link et R_org. Le code calcule R_org = var_a·Ep²/(1 + exp(qlogis(Ep)))² / [Σvar·Ep²/(1 + exp β0)² + Ep(1 − Ep)], avec Ep = moyenne observée par défaut (`expect = "meanobs"`). Pas de variance de surdispersion pour le binaire (« "Overdispersion" is not available for rptBinary »). R_org vaut `NA` en probit. Commentaire dans le code : « new computation, still to be discussed with Holger but probably ok » — [code source rptBinary.R](https://raw.githubusercontent.com/mastoffel/rptR/master/R/rptBinary.R). La théorie est renvoyée à Nakagawa & Schielzeth 2010 — [vignette rptR](https://cran.r-project.org/web/packages/rptR/vignettes/rptR.html).
- ICC du modèle logistique à intercept aléatoire : ρ̂ = σ̂²_v/(σ̂²_v + π²/3). Elle est « a different entity than the other ICCs, which are on a proportion scale ». « There is no simple formula for converting a random effect logistic ICC to the common correlation model ICC. » Sur trois essais réels, ces ICC étaient « strikingly higher than the ICCs from the other methods » — [Wu, Crespi & Wong 2012, *Contemp Clin Trials* 33(5):869–880](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610).
- Rodríguez & Elo comparent l'ICC latente des modèles probit, logit et cloglog avec des mesures « manifestes » (r de Pearson, Q de Yule) calculées à partir du modèle par la commande `xtrho`. Sur les mêmes données, les ICC latentes valent 0,6367 (probit), 0,6175 (logit corrigé) et 0,6595 (cloglog) — [Rodríguez & Elo 2003, *Stata Journal* 3(1):32–46](https://ideas.repec.org/a/tsj/stataj/v3y2003i1p32-46.html) (résumé et métadonnées ; texte intégral refusé, erreur 403).
- Un GLMM binomial probit « is exactly equivalent » au modèle à seuil. La formule de Dempster & Lerner (1950) et Robertson, h²_obs = t²/(p(1 − p))·h²_liab, où t est la densité normale au quantile p, y est donnée comme exacte en probit. Mais « variance components on the observed scale in a GLMM depend on the fixed effects », et « heritabilities on the data scales within a GLMM framework cannot be considered as intraclass correlation coefficients ». En général, les intégrales se résolvent numériquement — [de Villemereuil, Schielzeth, Nakagawa & Morrissey 2016, *Genetics* 204:1281–1294](https://pmc.ncbi.nlm.nih.gov/articles/PMC5105857).
- `QGglmm::QGicc` estime l'ICC sur l'échelle observée à partir des estimations latentes, par intégration numérique. Il utilise des formes fermées quand elles existent, notamment pour binomial/probit. Les effets fixes passent par `predict` — [manuel QGglmm](https://ftp.fau.de/cran/web/packages/QGglmm/refman/QGglmm.html).
- La VPC latente « has become the most widely used ». La VPC par simulation « is dependent on specific covariate patterns », d'où « a different value of the VPC for each distinct covariate pattern ». Formule du MOR : exp(√(2τ²)·Φ⁻¹(0,75)) — [Austin & Merlo 2017, *Stat Med* 36:3257–3277](https://pmc.ncbi.nlm.nih.gov/articles/PMC5575471).
- Empiriquement, log ICC croît linéairement avec log prévalence dans deux jeux de données (GPRD, et 136 ICC d'une revue HTA). ICC prédite à 1 % de prévalence : 0,008 (GPRD) ou 0,002 (HTA) ; à 40 % : 0,075 ou 0,046 — [Gulliford et al. 2005, *J Clin Epidemiol* 58:246–251 (résumé)](https://researchportal.ukhsa.gov.uk/en/publications/intraclass-correlation-coefficient-and-outcome-prevalence-are-ass/).
- « For binary outcomes, the ICC is a function of outcome prevalence » ; ρ = (R − 1)π/(1 − π), où R est un paramètre de dépendance, estimé par R̂ = 1 + ρ̂(1 − π̂)/π̂ — [Crespi, Wong & Wu 2011, *Clin Trials* 8(6):687–698](https://pmc.ncbi.nlm.nih.gov/articles/PMC3237741).

### Inferences
- **Formules exactes** (dérivées ici ; la formule générale est la méthode B, sans bruit de Monte-Carlo) :
  - Cas général : ρ_obs(p) = Var(P_j)/(p(1 − p)), avec P_j = g⁻¹(β0 + u_j) et β0 tel que E[P_j] = p. Raison : sachant u_j, deux écritures d'une même tâche sont indépendantes, donc leur covariance vaut Var(P_j).
  - Probit, forme fermée : ρ_obs = [Φ₂(z, z; ρ_L) − p²]/(p(1 − p)), avec z = Φ⁻¹(p). Entre deux types a et b de la même tâche : ρ_ab = [Φ₂(z_a, z_b; ρ_L) − p_a p_b]/√(p_a q_a p_b q_b). Contrôle : la quadrature et Φ₂ concordent à 5 décimales.
  - Linéarisation : comme π[1 + exp(Xβ)]⁻¹ = π(1 − π), la méthode A se réécrit τ_A = σ²π₀(1 − π₀)/(1 + σ²π₀(1 − π₀)), avec π₀ = expit(β0), la probabilité de la tâche « médiane ». Algébriquement, c'est σ²/(σ² + 1/(p(1 − p))), l'ICC « observation-level » par la méthode delta de Nakagawa et al. 2017, au choix de p près.
  - Petit p, logit : P_j ≈ exp(β0 + u_j) suit une loi log-normale, donc ρ_obs ≈ p(e^{σ²} − 1)/(1 − p). Valable seulement si p·e^{σ²} ≪ 1.
- **Tableau 1 : ICC observée pour une ICC latente fixée** (p = prévalence marginale du type) :

| ρ_L | lien | p = 10 % | 1 % | 0,1 % | 0,01 % |
|---|---|---|---|---|---|
| 0,05 | logit | 0,0159 | 0,00186 | 0,00019 | 0,00002 |
| 0,05 | probit | 0,0178 | 0,00410 | 0,00072 | 0,00011 |
| 0,1 | logit | 0,0340 | 0,00428 | 0,00044 | 0,00004 |
| 0,1 | probit | 0,0371 | 0,00936 | 0,00184 | 0,00032 |
| 0,2 | logit | 0,0763 | 0,0118 | 0,00126 | 0,00013 |
| 0,2 | probit | 0,0800 | 0,0241 | 0,00590 | 0,00132 |
| 0,3 | logit | 0,127 | 0,0251 | 0,00300 | 0,00031 |
| 0,3 | probit | 0,129 | 0,0461 | 0,0139 | 0,00397 |
| 0,5 | logit | 0,251 | 0,0861 | 0,0177 | 0,00237 |
| 0,5 | probit | 0,249 | 0,121 | 0,0533 | 0,0232 |
| 0,7 | logit | 0,415 | 0,230 | 0,102 | 0,0342 |
| 0,7 | probit | 0,409 | 0,259 | 0,159 | 0,0977 |
| 0,9 | logit | 0,660 | 0,534 | 0,421 | 0,326 |
| 0,9 | probit | 0,654 | 0,537 | 0,440 | 0,364 |

- **Ampleur.** En logit, pour ρ_L ≤ 0,3, ρ_obs perd environ un facteur 8 à 10 par décade de prévalence (régime log-normal). En probit, la queue plus mince donne une chute plus lente : facteur 3 à 6 par décade (ρ_L = 0,3 : 0,046, puis 0,014, puis 0,004). Pour ρ_L ≥ 0,7, la chute est plus lente dans les deux liens : en logit à 0,7, on passe de 0,23 à 0,10 puis à 0,034 ; en probit à 0,9, de 0,54 à 0,44 puis à 0,36. Sur toute la grille calculée, ρ_obs croît avec p pour p ≤ 10 %.
- **Tableau 2 : Deff = 1 + 9·ρ_obs pour m = 10** (illustratif) :

| ρ_L | lien | 10 % | 1 % | 0,1 % | 0,01 % |
|---|---|---|---|---|---|
| 0,1 | logit | 1,31 | 1,04 | 1,004 | 1,000 |
| 0,1 | probit | 1,33 | 1,08 | 1,02 | 1,003 |
| 0,3 | logit | 2,14 | 1,23 | 1,03 | 1,003 |
| 0,3 | probit | 2,16 | 1,41 | 1,13 | 1,04 |
| 0,5 | logit | 3,26 | 1,78 | 1,16 | 1,02 |
| 0,5 | probit | 3,24 | 2,09 | 1,48 | 1,21 |
| 0,7 | logit | 4,73 | 3,07 | 1,91 | 1,31 |
| 0,7 | probit | 4,68 | 3,34 | 2,43 | 1,88 |

- **Une ICC latente élevée veut dire des erreurs concentrées sur peu de tâches.** À ρ_L = 0,7 (logit) et p = 1 %, la tâche médiane n'a que 0,042 % de probabilité d'erreur (β0 résolu). Les 1 % de prévalence viennent de la queue de la distribution des tâches.
- **Tableau 3 : les approximations de premier ordre comparées au calcul exact** :

| ρ_L | p | logit exact | méthode A en π₀ (π₀) | méthode A en p marginal | probit exact | Dempster–Lerner |
|---|---|---|---|---|---|---|
| 0,1 | 1 % | 0,00428 | 0,00303 (0,84 %) | 0,00361 | 0,00936 | 0,00718 |
| 0,1 | 0,01 % | 0,00004 | 0,00003 | 0,00004 | 0,00032 | 0,00016 |
| 0,3 | 1 % | 0,0251 | 0,00711 (0,51 %) | 0,0138 | 0,0461 | 0,0215 |
| 0,3 | 0,01 % | 0,00031 | 0,00007 | 0,00014 | 0,00397 | 0,00047 |
| 0,7 | 1 % | 0,230 | 0,00322 (0,042 %) | 0,0706 | 0,259 | 0,0502 |
| 0,7 | 0,1 % | 0,102 | 0,00020 (0,0027 %) | 0,00761 | 0,159 | 0,00794 |
| 0,7 | 0,01 % | 0,0342 | 0,00002 (0,0002 %) | 0,00077 | 0,0977 | 0,00110 |

  Le facteur de Dempster–Lerner φ(z_p)²/(p(1 − p)) vaut 0,0717 à 1 %, 0,0113 à 0,1 % et 0,00157 à 0,01 %. Cette formule ne capte que la part linéaire de la covariance. Elle est proche du calcul exact pour ρ_L petit (0,05 à 1 % : 0,0036 contre 0,0041) et le sous-estime d'un facteur 5 à 90 à ρ_L = 0,7. La méthode A, évaluée comme dans l'article de Goldstein en u = 0, est 3,5 à 4,4 fois trop basse à ρ_L = 0,3, et 70 à 1 700 fois trop basse à ρ_L = 0,7. Évaluée au p marginal, elle reste 1,8 à 44 fois trop basse à partir de ρ_L = 0,3. Toutes ces approximations sont **anti-conservatrices** pour Deff.
- rptR : son R_org est une linéarisation (méthode A, avec Ep égal à la moyenne observée). D'après sa formule, à ρ_L = 0,7 et p = 1 %, il donne environ 0,07 contre 0,23 en calcul exact (mon calcul). Même biais anti-conservateur.
- Cohérence avec Gulliford et al. : une ICC latente logit constante de 0,05 à 0,1 donne 0,0019 à 0,0043 à 1 % et 0,039 à 0,076 à 40 % (calculé). C'est l'ordre de grandeur des valeurs empiriques prédites (0,002–0,008 et 0,046–0,075). Cela va dans le sens d'une dépendance entre ICC et prévalence en bonne partie mécanique. Ce n'est pas une preuve.
- **Les mesures « invariantes à la prévalence » ne sont pas équivalentes entre elles.** À ρ_L constante, R = E[P²]/p² (Crespi et al.) varie avec p dès que p·e^{σ²} n'est pas petit : pour σ² = 7,68, R vaut 24, 103 et 343 à 1 %, 0,1 % et 0,01 %, alors que e^{σ²} = 2157. Pour σ² = 1,41, R vaut 3,5, 4,0 et 4,1, presque constant. Inversement, à ρ_obs constante, ρ_L varie (§2). Chaque mesure « comparable » encode une hypothèse différente sur la façon dont la dépendance se transporte d'une prévalence à l'autre.
- MOR (formule d'Austin & Merlo, logit) : 3,1 à ρ_L = 0,3 et 14 à ρ_L = 0,7. Il ne dépend que de σ², donc il est comparable entre types sous l'hypothèse d'une variance latente commune, et sous elle seule.
- Code minimal, vérifié (il reproduit 0,23023, 0,09768, 0,00300 et la valeur croisée 0,0721 du §3) :

```python
import math
from scipy import integrate, optimize, special, stats

def rho_obs(rho_L, p, link="probit", p_b=None):
    """ICC observée (Pearson 0/1) entre deux écritures d'une même tâche ; p_b = prévalence d'un 2e type."""
    v_e = 1.0 if link == "probit" else math.pi ** 2 / 3
    s = math.sqrt(rho_L / (1 - rho_L) * v_e)
    F = stats.norm.cdf if link == "probit" else special.expit
    def E(b1, b2=None):  # E[F(b1+su)] ou E[F(b1+su)F(b2+su)], u ~ N(0,1)
        g = (lambda u: F(b1 + s*u)) if b2 is None else (lambda u: F(b1 + s*u) * F(b2 + s*u))
        return integrate.quad(lambda u: g(u) * stats.norm.pdf(u), -40, 40, points=[-b1 / s],
                              limit=1000, epsabs=0, epsrel=1e-11)[0]
    L = 10 * math.sqrt(v_e + s * s)
    b0 = lambda q: optimize.brentq(lambda b: E(b) - q, -L, L, xtol=1e-12)
    pa, pb = p, (p if p_b is None else p_b)
    ba, bb = b0(pa), b0(pb)
    return (E(ba, bb) - pa * pb) / math.sqrt(pa * (1 - pa) * pb * (1 - pb))
```

### Gaps
- Nakagawa & Schielzeth 2010 n'a pas été relu ici. Ses formules binaires ne sont connues dans cette note que par leur implémentation dans rptR.
- Rodríguez & Elo 2003 est resté inaccessible (403). Je n'ai pas pu vérifier qu'ils donnent la formule par la normale bivariée : elle est dérivée ici et vérifiée numériquement, sans source à comité de lecture lue.
- Aucune source trouvée ne tabule ρ_obs à 0,1 % et 0,01 % : tous les chiffres de ces colonnes sont les miens.
- Le « no simple formula » de Wu et al. 2012 vaut pour une forme fermée en logit. Sous le modèle, une conversion numérique exacte existe (méthode B, QGicc). Les deux affirmations ne se contredisent pas.

## 2. Estimer une seule ICC latente (tâche aléatoire, type et configuration en effets fixes) puis la convertir par type et configuration : est-ce fondé ? Pièges propres aux événements très rares

### Takeaway
C'est cohérent sous le modèle, et c'est même la pratique recommandée : Goldstein, Austin & Merlo et de Villemereuil disent tous que la quantité sur l'échelle observée doit être calculée par profil de covariables. Mais le transport de la corrélation des types fréquents vers les types rares repose entièrement sur des hypothèses que les données des types rares ne peuvent pas vérifier : variance latente commune, lien, intercept normal. Si le vrai mécanisme partage plutôt la corrélation observée (erreurs « en rafale »), la conversion sous-estime Deff pour les types rares : n_eff est surestimé d'un facteur 1,2 à 2,2 dans mes scénarios. Elle est aussi fragile à l'estimation : variance au bord (σ̂² = 0), séparation dans les cellules type × configuration sans erreur, biais des approximations.

### Cited Findings
- La VPC d'un modèle non linéaire dépend des prédicteurs et « should be computed for a range of values of the predictor variables » ; l'approche latente a « less justification when the response is truly discrete » — [Goldstein et al. 2002](https://bristol.ac.uk/media-library/sites/cmm/migrated/documents/pvmm.pdf).
- La VPC par simulation « is dependent on specific covariate patterns » : on peut avoir une VPC différente pour chaque profil de covariables — [Austin & Merlo 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5575471).
- « Variance components on the observed scale in a GLMM depend on the fixed effects » ; « all parameters on the expected and observed value scales are dependent on the intercept » — [de Villemereuil et al. 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5105857).
- Utiliser π²/3 suppose implicitement la même variance d'observation quelle que soit la proportion moyenne — [Nakagawa et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5636267).
- Dans deux études sur trois, l'ICC variait nettement selon la condition. Les auteurs jugent l'hypothèse d'une ICC commune « questionable » et recommandent des méthodes qui laissent l'ICC varier : GEE, régression logistique alternée (ALR), modèles mixtes à deux composantes de variance. L'ICC du modèle à intercept aléatoire « cannot be negative » et a été tronquée à 0 dans un bras. Avec beaucoup de grappes de taille 1, ils s'inquiètent de la normalité de l'effet aléatoire et proposent de tester « the sensitivity of ICC estimates to violations of the normality assumption » — [Wu, Crespi & Wong 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610).
- Supposer k constant ou ρ constant entre bras correspond à des hypothèses différentes sur l'effet de l'intervention, avec des conséquences sur la taille d'échantillon — [Thomson, Hayes & Cousens 2009, *Stat Med* 28(12):1739–1751 (résumé)](https://researchonline.lshtm.ac.uk/id/eprint/5458).
- Simulations de régression logistique multiniveau : les effets fixes sont sans biais avec 100 groupes de 50 ou plus. Les composantes de variance restent légèrement biaisées même dans ce cas, et leurs erreurs-types sont sous-estimées. Le biais est sévère pour des groupes de taille 5. Les événements peu fréquents demandent au moins 100 groupes de 50, avec une taille de groupe telle que le nombre attendu d'événements par groupe dépasse un — [Moineddin, Matheson & Glazier 2007, *BMC Med Res Methodol* 7:34](https://pmc.ncbi.nlm.nih.gov/articles/PMC1955447) (résumé).
- Un ajustement singulier a une matrice de variance-covariance estimée de rang incomplet, par exemple une variance exactement nulle. Ces modèles sont « statistically well defined » et peuvent être le vrai maximum de vraisemblance. Mais ils peuvent être surajustés, les problèmes de convergence deviennent plus probables, et les tests de Wald ou du rapport de vraisemblance peuvent être inappropriés. Remèdes : estimation pénalisée (MAP) par des a priori régularisants (Chung et al. 2013, paquet blme), ou méthodes bayésiennes complètes (MCMCglmm, rstanarm, brms) — [documentation lme4, `isSingular`](https://rdrr.io/cran/lme4/man/isSingular.html).
- Ajustements singuliers : « when there is insufficient data to estimate a variance parameter so that single variances collapse to zero ». Séparation complète : « some linear combination of parameters that divides zero from non-zero responses in a count or binomial model », « typically when one treatment combination has all-zero responses ». Remède : a priori sur les effets fixes et sur l'écart-type des effets aléatoires (estimation MAP) ; exemple binomial de quasi-séparation (Culcita) — [vignette glmmTMB « priors »](https://cran.r-project.org/web/packages/glmmTMB/vignettes/priors.html). Référence citée : Chung, Rabe-Hesketh, Dorie, Gelman & Liu 2013, « A nondegenerate penalized likelihood estimator for variance parameters in multilevel models », *Psychometrika* 78(4):685–709.
- Austin & Merlo ajustent leurs modèles par quadrature adaptative (`glmer(..., nAGQ = 10)`, SAS `proc glimmix method=quad`). Ils citent McCulloch & Neuhaus : « estimation of the random effects variance appears relatively robust to misspecification » de la loi des effets aléatoires — [Austin & Merlo 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5575471).
- Sur les mêmes données, l'ICC latente change selon le lien : 0,6367 (probit), 0,6175 (logit), 0,6595 (cloglog) — [Rodríguez & Elo 2003](https://ideas.repec.org/a/tsj/stataj/v3y2003i1p32-46.html).
- Les ICC négatives ne doivent pas servir aux calculs de taille ou de puissance : la pratique est d'utiliser 0 ou une petite valeur positive — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610). Comme la spécification de R est incertaine, « it would be prudent to conduct a sensitivity analysis » sur des valeurs plausibles — [Crespi et al. 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3237741).

### Inferences
- **Ce que la conversion suppose.** Un seul intercept de tâche, avec la même variance pour tous les types : un même « mauvais jour » de la tâche pousse toutes les écritures sur l'échelle latente. Une loi normale pour cet intercept. Un lien. Les erreurs de type rare ne contiennent presque aucune information pour tester ces hypothèses (voir le comptage de paires ci-dessous) : la conversion **extrapole** dans la queue du lien.
- **Sensibilité au lien** (mon calcul). On fixe ρ_obs sur le type fréquent (1 %), puis on extrapole :

| ρ_obs à 1 % | lien | ρ_L calibrée | ρ_obs extrapolée à 0,1 % | à 0,01 % |
|---|---|---|---|---|
| 0,02 | logit | 0,268 | 0,00229 | 0,00023 |
| 0,02 | probit | 0,176 | 0,00464 | 0,00098 |
| 0,05 | logit | 0,406 | 0,00754 | 0,00083 |
| 0,05 | probit | 0,315 | 0,0156 | 0,00459 |
| 0,3 | logit | 0,761 | 0,163 | 0,0745 |
| 0,3 | probit | 0,741 | 0,195 | 0,128 |

  À 0,01 %, l'écart entre probit et logit va d'un facteur 1,7 à 5,5. Le probit donne toujours la valeur la plus grande, donc la plus conservatrice des deux, sur les cas calculés. Le cloglog et les intercepts à queue lourde n'ont pas été calculés.
- **Deux hypothèses de transport incompatibles.** Si l'ICC observée est commune à tous les types, l'ICC latente requise varie selon le type :

| ρ_obs commune | lien | ρ_L requise à 1 % | à 0,1 % | à 0,01 % |
|---|---|---|---|---|
| 0,05 | logit | 0,406 | 0,615 | 0,729 |
| 0,05 | probit | 0,315 | 0,489 | 0,603 |
| 0,3 | logit | 0,761 | 0,848 | 0,891 |
| 0,3 | probit | 0,741 | 0,826 | 0,871 |
| 0,7 | logit | 0,959 | 0,974 | 0,981 |
| 0,7 | probit | 0,960 | 0,974 | 0,981 |

  Un modèle à ICC latente commune, estimé sur des données où ρ_obs est en réalité commune, est donc mal spécifié. Calibré sur le type fréquent, il donne pour le type à 0,01 % (m = 10) :

| ρ_obs vraie (tous types) | Deff vrai | Deff converti, logit | Deff converti, probit | n_eff surestimé |
|---|---|---|---|---|
| 0,05 | 1,45 | 1,007 | 1,04 | ×1,44 / ×1,39 |
| 0,3 | 3,70 | 1,67 | 2,15 | ×2,2 / ×1,7 |
| 0,7 (scénario du brief) | 7,30 | 6,04 | 6,14 | ×1,21 / ×1,19 |

  L'erreur est maximale aux corrélations moyennes. Dans l'autre sens, si la vérité est une ICC latente commune, appliquer à tous les types le ρ_obs du type fréquent est conservateur pour les types rares.
- **Information disponible par type.** ρ ne s'identifie que par les tâches qui ont au moins deux erreurs du même type. Nombre attendu de paires d'erreurs de même type par tâche : C(m, 2)·[p² + ρ_obs·p(1 − p)]. Avec m = 10 et ρ_obs = 0,1 : environ 0,049 paire par tâche à 1 %, soit environ 49 pour 1 000 tâches, mais environ 0,00045 à 0,01 %, soit environ 0,45 pour 1 000 tâches. Une ρ propre aux types les plus rares n'est donc pas estimable en pratique. Toute valeur utilisée vient d'une hypothèse de structure ou des types fréquents. Cela rejoint le seuil de Moineddin et al. : plus d'un événement attendu par groupe.
- **Artefacts qui font tomber Deff à 1, tous anti-conservateurs :**
  1. σ̂² = 0 (ajustement singulier) donne ρ_obs = 0 pour tous les types.
  2. Une cellule type × configuration sans erreur rend l'effet fixe infini (séparation), d'où p̂ = 0, puis ρ_obs(p̂) = 0.
  3. Une approximation de premier ordre, ou rptR R_org, à la place du calcul exact (§1).
  
  Parades (inférences) : a priori de Chung sur σ et a priori faibles sur les effets fixes (blme, glmmTMB, brms) ; quadrature adaptative plutôt que Laplace ou PQL ; borne haute (profil ou a posteriori) de σ² plutôt que l'estimation ponctuelle ; conversion **évaluée au seuil de prévalence p\*_t de la strate, pas à p̂_t**. Comme ρ_obs croît avec p sur la plage calculée, l'évaluer au seuil, qui est au-dessus du vrai taux si l'agent est bon, est conservateur pour une conclusion du type « taux sous le seuil ».
- **Borne sans hypothèse.** Avec ρ = 1, on obtient n_eff,t = (Σ_j m_jt)²/Σ_j m_jt², qui vaut au plus le nombre de tâches contenant ce type (voir §4). Quand la plupart des tâches n'ont qu'une ou deux écritures du type, le pire cas coûte peu. La question de ρ ne pèse vraiment que pour les types écrits souvent dans une même tâche.
- **Contrôle possible, seulement pour les types fréquents :** comparer, par type, le nombre observé de tâches avec au moins deux erreurs du type au nombre prédit par le modèle ajusté (bootstrap paramétrique). C'est le seul endroit où les données peuvent contredire le transport.
- Sur les PQL et MQL : sous-estimation forte des composantes de variance en binaire quand les effets aléatoires sont grands (Rodríguez & Goldman 1995, *JRSS A* 158(1):73–89 ; référence connue, non relue dans cette session).

### Gaps
- Aucune source trouvée n'évalue précisément « une ICC latente commune + effets fixes de type, convertie par type » pour des items hétérogènes dans une même grappe, avec des prévalences de 10⁻⁴ à 10⁻².
- Aucune source sur des agents IA, ni sur le mécanisme réel de corrélation des erreurs entre écritures réversibles, durables, messages et argent (seuil latent commun ou rafales) : c'est empirique.
- Pas de comparaison publiée trouvée des liens (logit, probit, cloglog, intercept à queue lourde) pour extrapoler une ICC sous 0,1 %.
- La restriction de `nAGQ > 1` aux modèles à un seul effet aléatoire scalaire dans lme4 n'a pas été vérifiée ici. Elle correspond au cas « intercept de tâche seul ».

## 3. Alternatives pour des données binaires groupées multi-items (prévalence propre à chaque type), et diagnostic de la dilution mesurée

### Takeaway
L'ICC ANOVA poolée n'est pas une estimation biaisée de la ρ par type : elle estime une autre quantité. C'est une moyenne, pondérée par p·q, des corrélations des paires de même type **et** des paires croisées. Or les paires croisées sont plafonnées par la borne de Fréchet : φ_max = 0,0995 entre 1 % et 0,01 %, même si les erreurs sont parfaitement liées sur l'échelle latente. Les alternatives saines travaillent paire de même type par paire de même type, avec des moyennes propres à chaque type. Elles doivent dire explicitement ce qui est partagé entre types :
- ρ observée : bêta-binomiale à φ commun ;
- k² ou R (Hayes, Crespi) ;
- σ² latente (GLMM) ;
- rapport de cotes par paires (ALR).

Chacune est une hypothèse différente.

### Cited Findings
- Les corrélations entre issues binaires sont contraintes par les moyennes marginales (contraintes de Prentice 1988, *Biometrics* 44:1033–1048). C'est la raison de l'ALR de Carey, Zeger & Diggle (1993) : modéliser l'association « by using log odds ratios instead of using correlations, as ordinary GEEs do », la corrélation étant « constrained to be within limits that depend in a complicated way on the means of the data » ; l'algorithme alterne une étape GEE pour la moyenne et une régression logistique pour le log du rapport de cotes — [documentation SAS PROC GEE, ALR](https://support.sas.com/documentation/cdl/en/statug/68162/HTML/default/statug_gee_details06.htm).
- Carey, Zeger & Diggle 1993, « Modelling multivariate binary data with alternating logistic regressions », *Biometrika* 80(3):517–526 : régression de la réponse sur les covariables avec modélisation simultanée de l'association par rapports de cotes par paires ; matrices d'ordre n² au lieu de n⁴ pour les GEE du second ordre — [Lancaster eprints](https://eprints.lancs.ac.uk/id/eprint/19623/).
- Les contraintes de Prentice et la définie-positivité sont nécessaires mais pas suffisantes pour qu'une loi binaire multivariée existe — [prépublication arXiv 2007.14080](https://arxiv.org/pdf/2007.14080), citant Chaganty & Joe 2006, « Range of correlation matrices for dependent Bernoulli random variables », *Biometrika* 93(1):197–206 — [IDEAS](https://ideas.repec.org/a/oup/biomet/v93y2006i1p197-206.html).
- Estimateurs comparés : ANOVA (carrés moyens inter et intra), Fleiss–Cuzick (type kappa), Pearson (corrélation entre paires, poids égal par paire), GEE (corrélation de Pearson des résidus sous structure échangeable), logistique à intercept aléatoire. Quand les probabilités diffèrent fortement entre bras, le GEE « may be preferred over the ANOVA, Fleiss-Cuzick or Pearson estimators » pour l'ICC globale. En simulation, le GEE avait le biais négatif le plus fort (sous-estimation de 20 à 25 % pour une ICC de 0,02) et l'ANOVA le plus faible. Le GEE a été le seul à fournir une erreur-type valide pour une ICC négative. Données corrélées simulées par la méthode d'Emrich & Piedmonte — [Wu, Crespi & Wong 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610).
- Ridout, Demétrio & Firth 1999, « Estimating intraclass correlation for binary data », *Biometrics* 55(1):137–148 : revue de nombreux estimateurs et vaste étude de simulation — [IDEAS](https://ideas.repec.org/a/bla/biomet/v55y1999i1p137-148.html) (recommandation finale non vérifiée, voir Gaps).
- Paramètre de dépendance R : ρ = (R − 1)π/(1 − π). Il est conçu pour être moins lié à la prévalence, ce qui ne peut se vérifier qu'empiriquement. Recommandation : analyse de sensibilité sur R et R propre à chaque bras si la dépendance peut changer — [Crespi, Wong & Wu 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3237741).
- k = coefficient de variation (écart-type/moyenne) des proportions vraies des grappes, base de formules simples de taille d'échantillon — [Hayes & Bennett 1999, *Int J Epidemiol* 28:319–326](https://doi.org/10.1093/ije/28.2.319).
- glmmTMB : famille `betabinomial` paramétrée selon Morris (1997), « V = μ(1 − μ)(n(φ + n)/(φ + 1)) » ; modèle de dispersion φ = exp(η) avec lien log s'il est spécifié — [référence des familles glmmTMB](https://glmmtmb.github.io/glmmTMB/reference/nbinom2.html).
- `performance::icc` : variance aléatoire sur variance totale, validée contre Nakagawa et al. (2017). Pour les modèles binomiaux, la variance par défaut est la variance théorique propre à la loi (échelle latente), avec option `"observation_level"`. Pour les modèles brms, `variance_decomposition()` calcule une décomposition à partir de la distribution prédictive a posteriori, « the recommended way to analyse random-effect-variances for non-Gaussian models » — [documentation performance::icc](https://easystats.github.io/performance/reference/icc.html).
- MuMIn `r.squaredGLMM` : variance d'observation par méthode delta (toutes lois et tous liens), log-normale ou trigamma (liens log seulement) ; variances « theoretical » spécifiques au lien pour le binomial ; révisé depuis la version 1.41.0 selon Nakagawa et al. (2017) — [documentation MuMIn](https://rdrr.io/cran/MuMIn/man/r.squaredGLMM.html).
- `QGglmm::QGicc` : ICC sur l'échelle observée à partir d'un GLMM ajusté — [manuel QGglmm](https://ftp.fau.de/cran/web/packages/QGglmm/refman/QGglmm.html).

### Inferences
- **Diagnostic de la dilution : limite en probabilité de l'ICC ANOVA poolée** (dérivée ici ; composition des tâches fixe, taille m égale, items i de prévalences p_i) :
  plim ρ̂_ANOVA = (C − D) / ((m − 1)(S + D)), avec S = Σ_i p_i q_i, C = Σ_{i≠j} Cov(Y_i, Y_j) et D = Σ_i (p_i − p̄)².
  - Contrôle Monte-Carlo sur 400 000 tâches (types à 2 % et 0,5 %, 3 écritures chacun, ρ_L probit = 0,8 commune) : 0,312 simulé contre 0,311 par la formule. Par type, ICC exactes 0,411 et 0,334 contre 0,410 et 0,336 simulées.
  - Pour des événements rares, D ≪ S et q ≈ 1 : plim ≈ [Σ_t m_t(m_t − 1)ρ_t p_t + Σ_{a≠b} m_a m_b ρ_ab √(p_a p_b)] / [(m − 1)Σ_t m_t p_t]. Si les ρ_ab croisées sont proches de 0 et que ρ_t = ρ pour tous les types : plim ≈ ρ·Σ_t m_t(m_t − 1)p_t/((m − 1)Σ_t m_t p_t). Si un type t\* porte presque toutes les erreurs : **plim ≈ ρ·(m_t\* − 1)/(m − 1)**. Si ce type fait la moitié des écritures, le rapport vaut environ 0,4 à 0,5, du même ordre que le défaut mesuré (0,34–0,41 pour 0,7, soit un rapport de 0,49 à 0,59). Le mécanisme suffit à expliquer l'essentiel. Si la composition des tâches varie, un terme inter-tâches supplémentaire (tâches riches en types fréquents) pousse en sens inverse.
  - Illustration : 4 types (1 %, 0,3 %, 0,1 %, 0,01 %), avec 4, 3, 2 et 1 écritures par tâche, ρ_L probit commune. À 0,7 : poolée 0,164, par type 0,259, 0,201, 0,159 et 0,098. À 0,95 : poolée 0,406, par type 0,667, 0,625, 0,590 et 0,526.
- **Borne de Fréchet sur les paires croisées** : φ_max = √(p_lo q_hi/(p_hi q_lo)), puisque P(A ∩ B) ≤ min(p_a, p_b). Corrélation croisée observée sous une ICC latente commune (mon calcul) :

| ρ_L | lien | (1 %, 0,1 %) | (1 %, 0,01 %) | (0,1 %, 0,01 %) |
|---|---|---|---|---|
| 0,3 | logit | 0,0086 | 0,0028 | 0,0010 |
| 0,3 | probit | 0,0237 | 0,0107 | 0,0071 |
| 0,7 | logit | 0,121 | 0,0454 | 0,0503 |
| 0,7 | probit | 0,161 | 0,0721 | 0,104 |
| 0,9 | logit | 0,280 | 0,0965 | 0,242 |
| 0,9 | probit | 0,292 | 0,0991 | 0,265 |
| 0,99 | les deux | 0,315 | 0,0995 | 0,316 |
| φ_max | — | 0,315 | 0,0995 | 0,316 |

  Aucune paire croisée ne peut donc porter une corrélation de 0,7. Tout estimateur de type Pearson qui moyenne sur toutes les paires de la tâche (ANOVA, Fleiss–Cuzick, GEE échangeable global, même avec des moyennes propres à chaque type) dilue mécaniquement. Des moyennes par type, comme dans la recommandation de Wu et al., retirent le terme D mais pas ce plafond.
- **Estimateur par paires, même type seulement, moyenne propre au type** (forme de l'estimateur de Pearson à poids égal par paire, restreint aux paires de même type) : ρ̂_t = [Σ_j Y_jt(Y_jt − 1)/Σ_j m_jt(m_jt − 1) − p̂_t²]/(p̂_t q̂_t), où Y_jt est le nombre d'erreurs de type t dans la tâche j. Deux façons de mettre en commun une ρ observée partagée :
  1. Rapport de sommes : Σ_t Σ_j [Y_jt(Y_jt − 1) − m_jt(m_jt − 1)p̂_t²] / Σ_t Σ_j m_jt(m_jt − 1)p̂_t q̂_t. Les types sont implicitement pondérés par p_t, donc le type fréquent domine.
  2. Moyenne des produits de résidus standardisés par paire (GEE à blocs échangeables par type). Les types sont pondérés par leur nombre de paires, mais les résidus des types rares (environ 1/√p) rendent l'estimation très instable.
  
  Aucune des deux n'est « la bonne » : c'est un arbitrage entre efficacité et représentativité, à figer au préenregistrement.
- **Bêta-binomiale par type, φ commun.** D'après la variance de glmmTMB, Var(Y_t) = n_t μ_t(1 − μ_t)[1 + (n_t − 1)/(φ + 1)], donc ρ_obs = 1/(φ + 1) et Deff_t = 1 + (m_t − 1)/(φ + 1) : exactement la forme de Kish. Un φ commun (dispersion constante) revient à une **ρ observée commune**, l'hypothèse opposée à une ICC latente commune (§2). Comparer `dispformula = ~type` et `~1` teste la différence, avec une puissance faible pour les types rares. Que `~1` soit la valeur par défaut de glmmTMB n'a pas été revérifié ici.
- **k² ou R communs.** R = E[P²]/p² = 1 + k². Dans le régime rare (p·e^{σ²} ≪ 1), le logit-normal donne k² ≈ e^{σ²} − 1, indépendant de p : partager k² revient alors approximativement à partager la variance latente logit. Les deux divergent quand p·e^{σ²} n'est pas petit (§1 : R = 24, 103, 343 pour σ² = 7,68). Forme de l'effet de plan : Deff = 1 + (m − 1)k²p/(1 − p) ≈ 1 + k²·λ_t, où λ_t = m_t p_t est le nombre attendu d'erreurs du type par tâche (identité tirée de ρ = k²π/(1 − π) ; voir §4).
- **ALR ou rapport de cotes par paires.** Le log OR n'est pas plafonné par les marges (SAS) et se modélise par type de paire (même type, croisée). Avec des événements très rares, il est porté par les mêmes rares tâches à deux erreurs ou plus (inférence ; comportement non documenté dans les sources trouvées).
- **GLMM multivarié** (intercepts de tâche propres à chaque type, corrélés entre eux) : il généralise et laisse σ²_t varier par type, avec des corrélations latentes croisées. Une mise en commun partielle bayésienne de log σ_t est le compromis naturel entre « commun » et « séparé ». Aucune source fetchée ne le traite pour ce cas : suggestion.

### Gaps
- Aucune source à comité de lecture trouvée sur l'estimation d'une ICC quand des items de types différents, dont les prévalences diffèrent d'un facteur 10 à 100, cohabitent dans la même grappe.
- La recommandation finale de Ridout, Demétrio & Firth 1999 n'a pas été vérifiée : texte non lu.
- La sous-estimation résiduelle par type (0,57–0,61 pour 0,7) n'est pas expliquée par les sources trouvées. Hypothèses non testées : biais de petit échantillon de l'ANOVA quand il y a peu de tâches à deux erreurs ou plus, pondération par m₀ quand les m_jt sont inégaux, mécanisme de génération dont le « ρ » n'est pas la corrélation de Pearson par paire. À vérifier par simulation dans le projet.
- Le comportement de l'ALR et du GEE à blocs avec des prévalences de 10⁻⁴ (estimabilité, couverture) n'est pas documenté dans ce que j'ai trouvé.

## 4. Ce que disent l'échantillonnage d'enquête et les essais en grappes sur l'effet de plan d'une proportion rare

### Takeaway
L'effet de plan d'une proportion est Deff = 1 + (b* − 1)ρ_obs (Kish ; justification par modèle chez Gabler et al. 1999). Avec des grappes de tailles inégales, b* = Σm²/Σm = m̄(1 + CV²), et non la moyenne arithmétique : la formule n_eff = n/(1 + (m̄ − 1)ρ) du projet est donc anti-conservatrice dès que le nombre d'écritures varie d'une tâche à l'autre. Pour les issues binaires, ρ_obs dépend de la prévalence (Gulliford ; Crespi). Pour une issue rare, l'effet de plan est gouverné par k² multiplié par le nombre attendu d'événements par grappe. Clopper–Pearson avec n_eff = n/Deff est exactement l'intervalle de Korn & Graubard (1998), conçu pour les proportions à petit nombre attendu de cas positifs.

### Cited Findings
- Kish : Deff = 1 + (n* − 1)ρ, n* = taille moyenne de grappe, sous les hypothèses que toute paire d'une même grappe a la corrélation ρ, que les paires de grappes différentes sont non corrélées et que les éléments ont la même variance — [Wikipédia, « Design effect »](https://en.wikipedia.org/wiki/Design_effect) (citant Kish 1965, p. 162, et Cochran 1977, p. 241).
- Gabler, Haeder & Lahiri 1999 posent le modèle Var(y_cj) = σ², Cov = ρσ² dans une même grappe et 0 sinon. Ils montrent deff = [m Σ_i w_i² m_i / (Σ_i w_i m_i)²]·[1 + (b* − 1)ρ] (éq. 4), avec b* = Σ_c (Σ_i w_i m_ic)² / Σ_i w_i² m_i. Par Cauchy–Schwarz, b* ≤ b_w (éq. 5–6). « If b_w is equal to b̄, e.g., if all b_c are equal, the upper bound of deff is simply Kish's formula. Thus Kish's formula serves as a conservative value for the actual design effect. » — [Gabler, Haeder & Lahiri 1999, *Survey Methodology* 25(1):105–106](https://www150.statcan.gc.ca/n1/pub/12-001-x/1999001/article/4718-eng.pdf).
- Wikipédia résume ce résultat ainsi : la formule de Kish avec la taille moyenne « serves as a conservative (upper bound) of the exact design effect » — [Wikipédia](https://en.wikipedia.org/wiki/Design_effect). Ce résumé est contredit, pour des poids égaux et des grappes inégales, par le texte même de Gabler et al. (voir Inferences).
- Grappes de tailles variables : DE = 1 + ((CV² + 1)m̄ − 1)ρ, où CV est le coefficient de variation des tailles ; l'ajustement est négligeable si CV < 0,23 — Eldridge, Ashby & Kerry 2006, *Int J Epidemiol* 35:1292–1300, [doi:10.1093/ije/dyl129](https://doi.org/10.1093/ije/dyl129). Forme de la formule confirmée seulement par des sources secondaires. Un protocole d'essai la cite sous une autre forme, 1 + (cv² + 1)(m − 1)ICC — [SAP NCT06640075](https://cdn.clinicaltrials.gov/large-docs/75/NCT06640075/SAP_000.pdf). Divergence non tranchée.
- Korn & Graubard 1998, « Confidence intervals for proportions with small expected number of positive counts estimated from survey data », *Survey Methodology* 24(2) : intervalle exact binomial adapté aux enquêtes complexes, meilleure couverture en simulation que les intervalles normal, logit et de Poisson — [Statistique Canada](https://www150.statcan.gc.ca/n1/en/catalogue/12-001-X19980024356). La taille effective vaut n/deff (citant Kish 1965) — [Ward 2019, article sur une commande Stata, PDF AgEcon](https://ageconsearch.umn.edu/record/340319/files/Ward.pdf). Implémentation R : `survey::svyciprop(method = "beta")` — [documentation svyciprop](https://rdrr.io/pkg/survey/man/svyciprop.html).
- ICC prédite de 0,002–0,008 à 1 % de prévalence contre 0,046–0,075 à 40 % — [Gulliford et al. 2005](https://researchportal.ukhsa.gov.uk/en/publications/intraclass-correlation-coefficient-and-outcome-prevalence-are-ass/). ρ = (R − 1)π/(1 − π) — [Crespi et al. 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3237741).
- Pour des issues binaires, k et ρ sont deux mesures de la variabilité inter-grappes ; les supposer constants entre bras n'a pas les mêmes implications — [Thomson, Hayes & Cousens 2009](https://researchonline.lshtm.ac.uk/id/eprint/5458). k = écart-type/moyenne des proportions de grappe — [Hayes & Bennett 1999](https://doi.org/10.1093/ije/28.2.319).
- Les ICC du modèle à intercept aléatoire et celles sur l'échelle des proportions ne sont pas interchangeables dans un calcul de taille : ce sont des entités différentes — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610).

### Inferences
- **Taille de grappe à utiliser.** À poids égaux (w = 1), l'éq. 4 de Gabler et al. donne b* = Σ_c b_c²/Σ_c b_c, et l'éq. 5 donne b_w = b*. Or Σb²/Σb = b̄(1 + CV²) (CV calculé avec la variance de population), ce qui retrouve exactement la formule d'Eldridge et al. 2006. La formule de Kish avec la **moyenne arithmétique** b̄ n'est donc conservatrice que si les tailles sont égales. Pour une strate t, il faut m\*_t = Σ_j m_jt² / Σ_j m_jt, la somme portant sur les tâches qui contiennent le type, puis n_eff,t = n_t / (1 + (m\*_t − 1)ρ_obs,t).
- **Pour une issue rare, Deff ≈ 1 + k²·λ.** À partir de ρ = k²π/(1 − π) (identité qui découle de la définition de k et de ρ = Var(P)/(π(1 − π)) ; équivalente à la formule de Crespi avec R = 1 + k²), Deff = 1 + (m − 1)k²π/(1 − π) ≈ 1 + k²·λ, où λ est le nombre attendu d'événements par grappe. C'est la surdispersion d'une loi binomiale négative (Var = λ + k²λ²). Avec moins d'une erreur attendue par tâche, Deff reste proche de 1, sauf concentration extrême (k² très grand). Contrôle : logit ρ_L = 0,5, donc k² ≈ e^{3,29} − 1 = 25,8 ; avec m = 10 et p = 0,01 %, Deff ≈ 1,026 en approximation contre 1,021 exact (Tableau 2).
- **Lien avec la procédure du projet.** Clopper–Pearson avec n_eff = n/Deff, c'est la construction de Korn & Graubard. Chez eux, Deff est estimé à partir de la variance de plan de p̂. Avec 0 ou 1 erreur dans une strate, cette estimation dégénère. D'où le besoin d'un Deff issu d'un modèle et évalué au seuil (§2), ou de la borne au pire cas ρ = 1 : n_eff,t = (Σ_j m_jt)²/Σ_j m_jt².
- Les tableaux 1 et 2 répondent pour le cas modélisé (Deff en fonction de p et de m). La littérature d'enquête trouvée ne donne pas de tels tableaux sous 1 % de prévalence.

### Gaps
- Kish 1965, 1987 et 1995 n'ont pas été consultés directement (seulement via Wikipédia et Gabler et al.).
- Korn & Graubard 1998 non lu en texte intégral : la façon de calculer les degrés de liberté et le traitement d'un deff inférieur à 1 (troncature) n'ont pas été vérifiés.
- Aucune source d'échantillonnage ou d'essais en grappes trouvée sur des effets de plan à des prévalences de 0,1 % ou 0,01 %. La gamme de prévalences couverte par les données de Gulliford et al. sous 1 % n'est pas connue (résumé seulement).
- La forme exacte de la formule d'Eldridge et al. 2006 n'a été confirmée que par des sources secondaires, dont l'une diverge.
