# Estimateurs d'un ρ commun pour des données binaires groupées : événements rares, beaucoup de grappes à zéro, prévalences très différentes entre strates

Conventions. ρ désigne l'ICC sur l'échelle des proportions, celui qui entre dans `n_eff = n / (1 + (m − 1) ρ)`. Une « vérification locale » est une simulation que j'ai lancée le 2026-11-06. Elle n'est pas publiée et ne remplace pas une source. Script : `/private/tmp/claude-502/-HOME-workspace/4ab88460-d607-4349-9bfe-89893f1ef75d/scratchpad/icc_strates_check.py`. Sortie : `icc_strates_resultats.txt`, dans le même dossier. Ce dossier est éphémère. Les configurations simulées approchent celles décrites dans la commande, mais ce ne sont pas les données réelles.

## 1. Comment les estimateurs classiques (ANOVA, Fleiss–Cuzick/kappa, moments/Pearson, maximum de vraisemblance bêta-binomial) se comportent-ils avec des événements rares, de petites grappes et des grappes à zéro ? Qu'ont trouvé Ridout, Demétrio & Firth (1999) ?

### Takeaway
Aucun estimateur classique n'est sûr dans ce régime. Tous reposent soit sur p̂(1−p̂), soit sur un rapport MSB/MSW, et deviennent 0/0 quand la population analysée n'a aucun événement. Dans les simulations publiées accessibles (prévalence ≥ 10 %) :
- presque tous les estimateurs ont un léger biais négatif ;
- l'ANOVA est le moins biaisé et le GEE le plus biaisé ;
- les intervalles par maximum de vraisemblance sont anti-conservateurs, ceux de l'ANOVA, de Fleiss–Cuzick et de Pearson sont conservateurs.

Le résumé accessible de Ridout et al. (1999) dit seulement deux choses. Plusieurs estimateurs sont « utiles », dont un jamais envisagé auparavant pour le binaire. Ceux fondés sur la quasi-vraisemblance étendue (EQL) peuvent être fortement biaisés. La liste exacte des estimateurs recommandés n'a pas pu être vérifiée.

### Cited Findings
- **Ridout et al. (1999)** passent en revue « de nombreux » estimateurs de ρ pour le binaire et les comparent dans une large simulation. Plusieurs estimateurs utiles en ressortent, dont un qui ne semblait pas avoir été envisagé pour le binaire. Les estimateurs fondés sur la quasi-vraisemblance étendue présentent un biais substantiel dans certaines circonstances. — [Europe PMC, PMID 11318148](https://europepmc.org/article/MED/11318148) ; [DOI 10.1111/j.0006-341X.1999.00137.x](https://doi.org/10.1111/j.0006-341X.1999.00137.x)
- Mots-clés zbMATH de Ridout et al. : beta-binomial, extended quasi-likelihood, kappa coefficient, pseudo-likelihood. — [MaRDI / zbMATH 1059.62601](https://portal.mardi4nfdi.de/wiki/Estimating_Intraclass_Correlation_for_Binary_Data)
- Un résumé de base de données (source secondaire, non vérifiée sur le texte) indique que l'efficacité relative des estimateurs y dépend de plusieurs facteurs de façon complexe. — [Bohrium](https://www.bohrium.com/paper-details/estimating-intraclass-correlation-for-binary-data/812349946677166081-922), vu seulement dans un extrait de résultat de recherche
- **Le paquet R ICCbin** (v1.2.0, 2026-05-11) implémente 16 estimateurs issus de cette littérature :
  - ANOVA `aov` (Elston et al. 1977) et ANOVA modifiée `aovs` ;
  - moments de Kleinman (1973) à poids égaux ou proportionnels à la taille, bruts ou modifiés : `keq`, `kpr`, `keqs`, `kprs` ;
  - estimateur stabilisé de Tamura & Young (1987) `stab` ;
  - équation d'estimation sans biais de Yamamoto & Yanagimoto (1992) `ub` ;
  - Fleiss–Cuzick (1979) `fc` et Mak (1988) `mak` ;
  - corrélations pondérées de Karlin, Cameron & Williams (1981), avec un poids égal par paire `peq`, par grappe `pgp` ou par individu `ppr` ;
  - rééchantillonnage `rm` ;
  - linéarisation `lin` et simulation `sim` de Goldstein, Browne & Rasbash (2002).

  Il propose aussi 5 intervalles de confiance : Smith, Wald modifié de Zou & Donner, Fleiss–Cuzick, Pearson et rééchantillonnage. — [ICCbin, manuel CRAN](https://cran.r-project.org/web/packages/ICCbin/refman/ICCbin.html) (lu sur le miroir [ftp.fau.de](https://ftp.fau.de/cran/web/packages/ICCbin/refman/ICCbin.html))
- ICCbin ne rend aucune estimation hors de [0, 1] : l'estimation et son intervalle sont supprimés, avec un avertissement. La documentation ne décrit aucun traitement des grappes de taille 1 ni des grappes à zéro événement. — [ICCbin, manuel CRAN](https://ftp.fau.de/cran/web/packages/ICCbin/refman/ICCbin.html). Le paquet est décrit dans [Chakraborty & Hossain 2018, PMID 29512507](https://europepmc.org/article/MED/29512507).
- **Zou & Donner (2004)** donnent des variances asymptotiques explicites pour trois estimateurs avec des grappes de tailles variables. Les intervalles fondés sur l'estimateur de Fleiss–Cuzick atteignent une couverture proche du nominal sur un large éventail de paramètres. — [Europe PMC, PMID 15339305](https://europepmc.org/article/MED/15339305)
- Ces trois estimateurs sont l'ANOVA, le Pearson par paires à poids constants et le kappa (Fleiss–Cuzick). Paul et al. (2003) et Lee (2004) en recommandent quatre, que la source ne nomme pas. Saha & Sen (2015) relèvent deux coquilles dans la formule de variance de l'ANOVA de Zou & Donner, corrigées après échange avec G. Zou. — [Saha & Sen, JSM 2015 Proceedings, p. 2964 et 2969](https://ww2.amstat.org/meetings/proceedings/2015/data/assets/pdf/234136.pdf)
- **Paul, Saha & Balasooriya** (J Stat Comput Simul, vol. 73, n° 7 ; année 2003 ou 2004 selon les index) comparent des estimateurs sous trois modèles de génération : bêta-binomial, probit-normal binomial et mélange de deux binomiales. Les mots-clés indiquent qu'ils mesurent biais, erreur quadratique moyenne et efficacité. — [MaRDI Q4444971, DOI 10.1080/0094965021000050883](https://portal.mardi4nfdi.de/wiki/Item:Q4444971)
- **Les formules** retenues par Wu, Crespi & Wong (2012) :
  - ANOVA : `ρ̂ = (MSB − MSW) / (MSB + (n_A − 1) MSW)`, avec `n_A = (N − Σn_i²/N)/(k − 1)` ;
  - Pearson, chaque paire à poids égal : `ρ̂ = [ΣZ_i(Z_i−1)/Σn_i(n_i−1) − μ̂²] / [μ̂(1−μ̂)]`, avec `μ̂ = ΣZ_i(n_i−1)/Σn_i(n_i−1)` ;
  - GEE échangeable (moments) : `α̂ = Σ_i Σ_{j<l} e_ij e_il / [Σ n_i(n_i−1)/2 − p]` ;
  - intercept aléatoire logistique : `ρ = σ²_v / (σ²_v + π²/3)`.

  — [Wu et al. 2012, PMC3426610](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- **Fleiss–Cuzick** : `ρ̂_FC = 1 − Σ_j Y_j(n_j − Y_j)/n_j / [(N − M) π̂(1 − π̂)]`, où M est le nombre de grappes. — [Saha & Sen 2015, p. 2970](https://ww2.amstat.org/meetings/proceedings/2015/data/assets/pdf/234136.pdf)
- **Wu et al. (2012), étude 1.**
  - Plan : 30 grappes (10 de taille 5, 10 de taille 10, 10 de taille 15), 2000 réplications, ρ ∈ {0,02 ; 0,05 ; 0,10 ; 0,25}, π de 0,1 à 0,5.
  - Presque toutes les méthodes sous-estiment légèrement ρ. L'ANOVA a le plus petit biais.
  - Le GEE a le plus grand : il sous-estime ρ de 20 à 25 % quand ρ = 0,02.
  - Le biais diminue quand π se rapproche de 0,5.
  - Aucune méthode n'atteint la couverture nominale de façon générale.

  — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- **Wu et al. (2012), cas indéfinis et estimations négatives.**
  - L'ANOVA, Fleiss–Cuzick, Pearson et le GEE peuvent donner des estimations négatives.
  - L'ICC à intercept aléatoire ne peut pas être négatif (tronqué à 0 dans un bras).
  - Dans un bras témoin à prévalence 0,108, aucune variance valide n'a pu être obtenue pour l'ANOVA, Fleiss–Cuzick et Pearson.
  - Beaucoup de grappes de taille 1 produisent une distribution à pics en 0 et 1, qui viole la normalité de l'effet aléatoire.

  — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- L'ICC du modèle logistique à intercept aléatoire est sur l'échelle latente. Il est « nettement plus élevé » que les ICC sur l'échelle des proportions. — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- **Saha & Paul (2005)** proposent un estimateur du maximum de vraisemblance corrigé du biais pour le paramètre de dispersion ρ du modèle bêta-binomial étendu. En simulation, il fait généralement mieux que le maximum de vraisemblance standard et que deux autres estimateurs, en biais comme en efficacité. — [Europe PMC, PMID 16007569](https://europepmc.org/article/MED/16007569)
- **Saha & Sen (2015)** testent les intervalles d'un ρ commun à deux groupes. Plan : π ∈ {(0,1 ; 0,3), (0,2 ; 0,4), (0,3 ; 0,6)}, ρ de 0,1 à 0,5, (19, 27) ou (73, 87) grappes. Couvertures pour un niveau nominal de 95 % :

  | Méthode | Couverture |
  |---|---|
  | Wald par maximum de vraisemblance | 0,755 à 0,928 |
  | ANOVA | 0,969 à 0,997 |
  | Fleiss–Cuzick | 0,950 à 0,996 |
  | Pearson | 0,949 à 0,996 |
  | Pivot généralisé | 0,867 à 0,949 |

  — [Saha & Sen 2015, tableau 1](https://ww2.amstat.org/meetings/proceedings/2015/data/assets/pdf/234136.pdf)
- **Mbekwe Yepnang et al. (2021).** Toutes les mesures de corrélation intra-grappe étudiées dépendent de la prévalence. La tétrachorique (approche de Kirk) en dépend le moins quand l'ICC vaut environ 0,05. Pour des ICC plus faibles (environ 0,01), les auteurs privilégient l'estimateur ANOVA. — [Europe PMC, PMID 34218744](https://europepmc.org/article/MED/34218744)
- **Gulliford et al. (2005).** Dans deux jeux de données, le log de l'ICC est lié linéairement au log de la prévalence. — [Europe PMC, PMID 15718113](https://europepmc.org/article/MED/15718113)
- **Crespi, Wong & Wu (2011).** « For binary outcomes, the ICC is a function of outcome prevalence. » Les bornes de ρ dépendent de la prévalence et de la taille des grappes. « The ICC is expected to increase as the prevalences increase. » Les auteurs proposent R = 1 + ρ(1−π)/π. — [Crespi et al. 2011, PMC3237741](https://pmc.ncbi.nlm.nih.gov/articles/PMC3237741)

### Inferences
- **Cas indéfinis**, d'après les formules :
  - Fleiss–Cuzick, Pearson et GEE divisent par p̂(1−p̂). Ils sont donc indéfinis dès que la population analysée (le tout, ou une strate) n'a aucun événement.
  - L'ANOVA donne 0/0 quand tous les y valent 0, car MSB = MSW = 0.
- **Grappes d'une seule écriture.** Elles ont un poids nul dans Fleiss–Cuzick (poids n_i − 1) et dans Pearson ou le GEE (aucune paire). Elles comptent en revanche dans les degrés de liberté du MSB de l'ANOVA. Les exclure ne change donc vraiment quelque chose que pour l'ANOVA.
- **Estimations négatives.** Avec des événements rares et ρ ≈ 0, elles sont fréquentes. En vérification locale (scénario D1), les médianes des estimateurs standardisés par strate sont légèrement négatives : −0,015 pour l'ANOVA sans les strates à zéro, −0,025 pour Fleiss–Cuzick à p_s, −0,025 pour le GEE à p_s. Écarter les valeurs hors [0, 1], comme le fait ICCbin, puis faire la moyenne de ce qui reste crée un biais de troncature vers le haut.
- **Maximum de vraisemblance bêta-binomial.** Il est borné à 0 : médiane 0 et moyenne 0,027 dans le scénario D1 en vérification locale. Son estimation ponctuelle tient la route, mais ses intervalles de Wald sont anti-conservateurs (Saha & Sen).
- **Effet du plancher à 0,3.** Il neutralise tout biais vers le bas. L'estimateur ne change le résultat que lorsque ρ̂ dépasse 0,3.

### Gaps
- La liste exacte des estimateurs jugés utiles par Ridout et al. est restée inaccessible, tout comme les conditions de leur simulation (prévalences, tailles de grappes) et le nom de l'estimateur « nouveau pour le binaire ». Le texte est payant (Wiley/OUP) et zbMATH répond 403. Je me souviens, sans l'avoir vérifié, que l'ANOVA et Fleiss–Cuzick y figurent parmi les bons estimateurs. À contrôler sur le texte intégral.
- Paul, Saha & Balasooriya (2003) : les quatre estimateurs recommandés ne sont pas identifiés. Lee (2004) n'a pas été retrouvé.
- Chakraborty et al. (2009) proposent une technique par simulation pour estimer l'ICC binaire, appliquée à un essai sur la réanimation néonatale. Leurs résultats chiffrés n'ont pas été obtenus. — [PMID 18723124](https://europepmc.org/article/MED/18723124)

## 2. Comment estimer un ρ commun entre strates ou bras dont les prévalences diffèrent : moyenne pondérée de ρ par strate, ANOVA poolée à moyennes et variances propres, résidus standardisés par strate, GEE échangeable avec effets fixes de strate, ALR ? Avec quels poids ?

### Takeaway
**Le diagnostic est établi.** Les estimateurs poolés à moyenne unique (ANOVA, Fleiss–Cuzick, Pearson) surestiment un ρ commun quand les prévalences divergent. Le GEE avec moyennes propres à chaque bras reste proche de la vraie valeur (Wu et al. 2012).

**Deux familles d'estimateurs valides sont publiées :**
1. un modèle unique, avec une moyenne propre à chaque strate et un ρ commun : maximum de vraisemblance bêta-binomial joint, ou GEE à effets fixes de strate ;
2. une moyenne pondérée d'estimations par strate, avec des poids inverses de la variance (Saha & Sen 2015) ou, pour le kappa stratifié, des poids proportionnels à la taille (Barlow et al. 1991).

**L'ANOVA stratifiée** (moyennes propres, MSW commun) n'a été évaluée dans aucun texte trouvé. La vérification locale montre qu'elle échoue dès que la prévalence et la structure de taille des grappes varient ensemble d'une strate à l'autre.

**Deux estimateurs corrigent le défaut** sans biais notable dans les cas ordinaires :
- un Fleiss–Cuzick standardisé par strate, avec une correction de petit échantillon ;
- le maximum de vraisemblance bêta-binomial à p_s propres.

### Cited Findings
- **Wu et al. (2012)** : l'ANOVA, Fleiss–Cuzick et Pearson reposent sur un modèle de corrélation commune où tous les individus ont la même probabilité de succès. — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- **Wu et al. (2012), étude 2** : deux bras, 60 grappes en tout.
  - Même ρ, π différents : l'ANOVA, Fleiss–Cuzick et Pearson surestiment le ρ commun, d'autant plus que les π divergent. Le GEE reste proche de la vraie valeur.
  - π et ρ différents, avec (π1, π2) = (0,1 ; 0,5) ou (0,2 ; 0,5) : ces trois estimateurs donnent un ρ global supérieur aux ρ des deux bras. Le GEE donne environ la moyenne des deux.

  — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- **Wu et al. (2012), recommandations.**
  - Si les prévalences diffèrent beaucoup entre conditions, « the GEE estimator may be preferred ».
  - Envisager des méthodes qui laissent ρ varier selon la condition.
  - L'hypothèse d'un ρ commun à tout l'échantillon « may be questionable ».
  - Les ρ par bras sont plus fiables, puisque l'hypothèse d'une probabilité égale y est plus plausible.
  - Alternatives citées : régression logistique alternée (ALR), et modèles logistiques mixtes à deux composantes de variance inter-grappes.
  - Aucun schéma de pondération n'est proposé.

  — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- **Saha & Sen (2015)** estiment un ρ commun à k groupes de deux façons. Première façon : le maximum de vraisemblance bêta-binomial joint, avec un π_i propre à chaque groupe et un φ commun (leur éq. 1). Seconde façon : une moyenne pondérée des estimations ANOVA, Fleiss–Cuzick ou Pearson de chaque groupe, de poids `W_i = 1/Var(φ̂_i)`. Ces variances, celles de Zou & Donner, sont évaluées aux estimations du groupe, à la suite de Mian & Shoukri (1997). Elles contiennent des termes en `1/(π_i(1−π_i))`. Les auteurs ajoutent un intervalle par pivot généralisé. — [Saha & Sen 2015, p. 2965 et 2969-2970](https://ww2.amstat.org/meetings/proceedings/2015/data/assets/pdf/234136.pdf)
- Exemple de Saha & Sen : 29 classes par bras, de 1 à 6 enfants, prévalences 0,618 et 0,422. ρ par bras puis commun :

  | Méthode | ρ bras 1 | ρ bras 2 | ρ commun |
  |---|---|---|---|
  | ANOVA | 0,337 | 0,266 | 0,301 |
  | Fleiss–Cuzick | 0,321 | 0,248 | 0,287 |
  | Pearson | 0,382 | 0,265 | 0,331 |
  | Maximum de vraisemblance | 0,324 | 0,249 | 0,286 |

  — [Saha & Sen 2015, tableau 4](https://ww2.amstat.org/meetings/proceedings/2015/data/assets/pdf/234136.pdf)
- **Kappa stratifié (Barlow, Lai & Azen 1991).** Le kappa est une somme pondérée des kappas de chaque strate, sous l'hypothèse d'un accord constant entre strates dont les marges diffèrent. Trois pondérations sont comparées : égale, par taille, par inverse de la variance. « Weighting by sample size moderately efficient under most conditions. » — [Europe PMC, PMID 1925174](https://europepmc.org/article/MED/1925174)
- **Test d'homogénéité des kappas (Donner, Eliasziw & Klar 1996).** Pour de petits effectifs ou une prévalence inférieure à 0,3, les auteurs recommandent l'approche par adéquation du modèle (goodness-of-fit). — [Europe PMC, PMID 8934591](https://europepmc.org/article/MED/8934591)
- **Thomson, Hayes & Cousens (2009).** Supposer k (coefficient de variation inter-grappes) constant ou ρ constant entre bras correspond à des hypothèses différentes sur l'effet étudié. — [Europe PMC, PMID 19378266](https://europepmc.org/article/MED/19378266)
- **Yelland et al. (2011)** calculent des ICC ajustés sur des covariables (lien log), par développement de Taylor ou par les propriétés de la loi log-normale. Ils recommandent la seconde méthode. — [Europe PMC, PMID 21335589](https://europepmc.org/article/MED/21335589)

### Inferences
- **Pourquoi l'ANOVA stratifiée échoue** (dérivation). Sous ρ = 0, dans chaque strate s :
  - `E[SSB_s] = (K_s − 1) v_s` et `E[SSW_s] = (N_s − K_s) v_s`, avec `v_s = p_s(1 − p_s)` ;
  - d'où `E[MSB]/E[MSW] = [Σ(K_s−1)v_s/(K−S)] / [Σ(N_s−K_s)v_s/(N−K)]`.

  Ce rapport vaut 1 seulement si v_s est le même partout, ou si `(N_s−K_s)/(K_s−1) ≈ m̄_s − 1` est le même partout. Quand des strates sans erreur ont de grandes grappes, elles gonflent les degrés de liberté du MSW sans ajouter de somme de carrés. Elles gonflent aussi `m0`. MSW s'effondre et ρ̂ grimpe.

  Calcul de contrôle sur le scénario D1 : le rapport vaut environ 14,6 et m0 environ 41, d'où ρ̂ ≈ 0,25. La simulation donne 0,249. C'est le défaut mesuré (0,41 dans la commande).
- **Le Fleiss–Cuzick poolé** échoue pour la même raison. Son dénominateur p̄(1−p̄) contient l'écart de prévalence entre strates et ne pondère pas correctement les strates.
- **Construction valide : standardiser par strate.** Fleiss–Cuzick à p_s propre à chaque strate :

  `ρ̂ = 1 − Σ_s SSW_s / Σ_s (N_s − K_s) p̂_s(1 − p̂_s)`, avec `SSW_s = Σ_{i∈s} y_i(m_i − y_i)/m_i`.

  Il est sans biais si l'on connaît les p_s, parce que `E[y(m−y)/m] = (m−1) p (1−p)(1−ρ)` sous corrélation échangeable, quelle que soit la loi. Il s'écrit aussi comme une moyenne pondérée des Fleiss–Cuzick de chaque strate, avec des poids `(N_s − K_s) p̂_s(1−p̂_s)`. Pour des événements rares, ces poids valent à peu près le nombre d'erreurs. C'est donc une « moyenne pondérée par les erreurs », mais d'estimateurs Fleiss–Cuzick. Une strate à 0 événement y reçoit automatiquement un poids nul.
- **Correction de petit échantillon** (construction locale, non trouvée dans la littérature, à valider). On a `E[p̂_s(1−p̂_s)] = p_s(1−p_s)(1 − deff_s/N_s)`, avec `deff_s = 1 + (m*_s − 1)ρ` et `m*_s = Σm_i²/N_s`. On remplace donc le dénominateur par `p̂_s(1−p̂_s)/(1 − deff_s(ρ)/N_s)` et on résout par point fixe. Sans correction, le biais vaut environ (1 − ρ)/n_eff,s par strate : il est sensible quand n_eff est petit.
- **GEE à p_s.** Il est valide en espérance (Wu et al.), mais chaque paire pèse autant. Ce sont donc les grosses grappes qui dominent. En vérification locale, avec des tailles de 2 à 150 et 12 grappes par strate, il sous-estime ρ d'environ 50 %. C'est le même sens que dans Wu et al., en plus marqué.
- **Poids par inverse de la variance.** Le terme dominant de la variance de Zou & Donner est en 1/(π(1−π)). Pour des événements rares, ces poids sont donc à peu près proportionnels au nombre d'événements. C'est voisin de la pondération par les erreurs, et nul pour une strate à zéro.
- **Vérification locale.** Données bêta-binomiales avec un ρ commun par construction. Moyennes sur 400 réplications :

  | Scénario (vrai ρ) | ANOVA poolée | ANOVA stratifiée | ANOVA strat. sans strates à 0 | Moy. ANOVA/strate, poids erreurs | FC poolé | FC à p_s | FC à p_s corrigé | GEE à p_s | MV bêta-binom. à p_s |
  |---|---|---|---|---|---|---|---|---|---|
  | D1 (0) | 0,310 | 0,249 | −0,002 | −0,002 | 0,297 | −0,012 | −0,002 | −0,014 | 0,027 |
  | D2 (0) | 0,205 | 0,161 | 0,159 | 0,004 | 0,195 | −0,003 | 0,004 | −0,001 | 0,001 |
  | D1bis (0,3) | 0,488 | 0,452 | 0,258 | 0,258 | 0,474 | 0,245 | 0,258 | 0,237 | 0,261 |
  | O1 (0,3) | 0,289 | 0,283 | 0,283 | 0,282 | 0,279 | 0,246 | 0,282 | 0,144 | 0,273 |
  | O2 (0,1) | 0,111 | 0,098 | 0,098 | 0,097 | 0,106 | 0,080 | 0,097 | 0,054 | 0,088 |
  | O4 (0,05) | 0,065 | 0,050 | 0,050 | 0,049 | 0,061 | 0,039 | 0,049 | 0,028 | 0,042 |
  | O3 (0,3) | 0,313 | 0,301 | 0,289 | 0,247 | 0,301 | 0,221 | 0,241 | 0,133 | 0,276 |

  Les scénarios :
  - D1 : strate A de 25 grappes de 2 à 6 écritures, p = 0,10 ; strates B et C de 8 grappes de 60 à 150 écritures chacune, p = 0.
  - D2 : comme D1, mais p = 0,003 dans B et C.
  - D1bis : configuration D1 avec ρ = 0,3.
  - O1, O2, O4 : 4 strates à p = 0,02 / 0,05 / 0,08 / 0,10, 12 grappes chacune, tailles log-uniformes de 2 à 150, avec ρ = 0,3, 0,1 et 0,05.
  - O3 : comme D1, mais p = 0,02 dans B et C, avec ρ = 0,3.

  Ce qu'on en tire :
  - Le défaut est reproduit.
  - Exclure les strates à zéro répare D1 mais pas D2. Le problème vient de l'hétérogénéité des variances entre strates, pas seulement des zéros.
  - Tous les estimateurs standardisés par strate donnent ≈ 0 sous ρ = 0.
  - Dans les cas ordinaires, les moins biaisés sont le Fleiss–Cuzick corrigé, la moyenne des ANOVA par strate et le maximum de vraisemblance bêta-binomial.
- **Le chiffre de 0,12 n'est pas reproduit.** Dans la commande, la moyenne pondérée par les erreurs donnait 0,12 pour un vrai ρ de 0,3. Ici, elle donne 0,25 à 0,28. L'écart vient sans doute de la configuration réelle. Hypothèses non vérifiées :
  - peu de grappes porteuses d'erreurs par strate, d'où un fort biais de petit échantillon de l'ANOVA ;
  - des estimations par strate négatives ou tronquées ;
  - un autre m0.
- **Sens du risque**, si la borne de Clopper–Pearson est une borne haute d'erreur comparée au seuil. Un ρ̂ trop grand fait baisser n_eff, élargit la borne et rend le test conservateur : il coûte de la puissance, pas des faux succès. Le défaut de l'ANOVA poolée est de ce type. C'est le biais vers le bas qui est dangereux, et le plancher à 0,3 le neutralise.
- **Point adjacent, dérivation simple, hors périmètre strict.** Pour p̂_s = Σy/N_s, on a `Var(p̂_s) = p(1−p)/N_s · [1 + (Σm_i²/N_s − 1) ρ]`. La taille qui convient dans le design effect est donc `m* = Σm²/N = m̄(1 + CV²)`, et non m̄. Avec des tailles de 1 à 150, la formule en m̄ peut nettement sous-estimer le design effect.

### Gaps
- Le livre de Donner & Klar (2000) et Donner & Koval (1980) n'ont pas été consultés. Leurs recommandations exactes pour pooler ρ entre bras (ANOVA poolée à moyennes propres, poids des moyennes) ne sont pas vérifiées. Mian & Shoukri (1997) n'a pas été consulté non plus.
- Aucune évaluation publiée de l'ANOVA stratifiée (moyennes propres, MSW commun) avec des prévalences hétérogènes n'a été trouvée.
- Le GEE corrigé du biais pour peu de grappes (équations matricielles ajustées, Preisser, Lu & Qaqish 2008) est une piste, non consultée.
- L'ALR (Carey, Zeger & Diggle 1993, Biometrika 80(3):517-526) n'a pas été évaluée ici. Wu et al. la citent seulement comme alternative, et la conversion en ρ pour n_eff n'est pas traitée.
- La vérification locale suppose qu'un ρ commun est vrai. Elle ne teste pas le cas réaliste où ρ_s varie avec la prévalence : variance latente constante, ou k constant.

## 3. Que faire des strates sans aucun événement (ρ indéfini dans la strate) ? Faut-il les écarter, leur emprunter un ρ, ou appliquer un plancher ?

### Takeaway
**Pour estimer ρ**, une strate à 0 événement n'apporte aucune information (0/0). On l'écarte du calcul, ce qui est automatique avec le Fleiss–Cuzick stratifié, le GEE et le maximum de vraisemblance à p_s propres. Il ne faut jamais laisser ses degrés de liberté entrer dans un MSW commun.

**Pour son propre n_eff**, trois conventions existent :
- emprunter le ρ commun, ce qui est cohérent avec l'hypothèse d'un ρ commun ;
- appliquer un plancher ;
- poser n* = n quand p̂ = 0, comme le NCHS (Korn–Graubard). Cela revient à ρ = 0 : c'est la convention la moins prudente.

Aucun texte trouvé ne tranche pour des expériences de ce type. C'est un choix d'hypothèse à préenregistrer.

### Cited Findings
- **Ward (2019), commande kg_nchs** : `n* = p(1−p)/var(p)`, et « Limits are set such that when p=0, then n*=n ». La même règle vaut pour n*_df. Le NCHS demande une revue statistique quand la largeur absolue de l'intervalle est ≤ 0,05 et que p = 0 ou 1 − p = 0. — [Ward 2019, Stata J 19(3):510-522, manuscrit NIH](https://stacks.cdc.gov/view/cdc/83564)
- **Tutoriel NHANES** : `n_e = min(n, n/DEFF)`, plafonné à la taille réelle. Pour Korn–Graubard, `n*_e = min(n, n/DEFF × (t_{n−1}/t_df)²)`. Source citée : Parker et al. 2017, Vital Health Stat 2(175). — [NHANES, Reliability of estimates](https://wwwn.cdc.gov/nchs/nhanes/tutorials/reliabilityofestimates.aspx)
- **Health, United States** : l'approche Korn–Graubard « performs well for proportions near zero or 1 » et « is generally conservative ». — [NCHS, Statistical reliability](https://www.cdc.gov/nchs/hus/sources-definitions/statistical-reliability.htm)
- **Wu et al. (2012)** : « negative ICCs should not be used in sample size and power calculations ». L'usage standard est d'employer 0 ou une petite valeur positive. — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- **Crespi et al. (2011)** : ρ = (R − 1)π/(1 − π). Si R est constant, ρ tend vers 0 quand π tend vers 0. — [Crespi et al. 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3237741)
- **Thomson et al. (2009)** : supposer k constant ou ρ constant, ce n'est pas la même hypothèse. — [Europe PMC, PMID 19378266](https://europepmc.org/article/MED/19378266)

### Inferences
- **Aucune information sur ρ.** Sous un modèle bêta-binomial à ρ commun, la vraisemblance des grappes toutes à zéro tend vers 1 quel que soit ρ quand p_s tend vers 0. Écarter ces strates de l'estimation équivaut donc au maximum de vraisemblance.
- **Leur effet dans l'ANOVA stratifiée.** Elles ajoutent (N_s − K_s) aux degrés de liberté du MSW et (K_s − 1) à ceux du MSB, et gonflent m0. C'est le biais vers le haut démontré en D1 (0,25).
- **ρ commun ou k commun ?** Par algèbre, k² = R − 1 = ρ(1−π)/π.
  - Sous un k commun, ρ_s ≈ k²·p_s est presque nul pour une strate très rare. Cela rejoint la convention n* = n.
  - Sous un ρ commun, on emprunte ρ̂.

  Une strate sans événement ne permet pas de départager les deux hypothèses.
- **Ordre de grandeur** (calcul illustratif). Avec x = 0, la borne haute unilatérale de Clopper–Pearson vaut `1 − α^{1/n_eff}`. Prenons n = 300, m* = 50, ρ = 0,3 : deff = 15,7 et n_eff ≈ 19. La borne à 95 % vaut alors environ 14,5 %, contre environ 1,0 % avec n_eff = n. La convention choisie pour les strates à zéro pèse donc plus lourd que le choix de l'estimateur.
- **Option prudente et cohérente avec le protocole actuel** : écarter ces strates de l'estimation de ρ, puis leur appliquer max(ρ̂ commun, plancher).

### Gaps
- Aucune source spécifique à l'estimation de ρ avec des strates sans événement dans un cadre expérimental n'a été trouvée. Aucune comparaison par simulation entre emprunt, plancher et n* = n non plus.
- Le rapport NCHS lui-même (Parker et al. 2017) n'a pas été lu. La règle « p = 0 donne n* = n » vient de Ward (2019).

## 4. Existe-t-il des preuves sur l'estimateur le moins biaisé pour des issues binaires rares (prévalence < 5 %), quand peu de grappes portent les événements ?

### Takeaway
Rien de tel n'a été trouvé dans la littérature à comité de lecture accessible. Les simulations consultées s'arrêtent à π ≥ 0,1 (Wu et al. ; Saha & Sen). Il ne reste que des indices indirects :
- l'ANOVA est le moins biaisé (Wu et al., π ≥ 0,1) ;
- l'ANOVA est privilégié pour les ICC faibles (Mbekwe Yepnang et al.) ;
- le maximum de vraisemblance est biaisé mais corrigeable (Saha & Paul).

La vérification locale (p de 0,003 à 0,10), non publiée, place en tête le maximum de vraisemblance bêta-binomial à p_s propres, le Fleiss–Cuzick stratifié corrigé et la moyenne des ANOVA par strate. Suivent le Fleiss–Cuzick stratifié brut, puis, loin derrière, le GEE par paires. Quand toute l'information vient d'environ 25 petites grappes d'une seule strate, aucun estimateur ne retrouve ρ sans biais : de −13 à −21 % pour ρ = 0,3.

### Cited Findings
- **Wu et al. (2012), étude 1** : π descend au plus à 0,1. Le biais diminue quand π se rapproche de 0,5. L'ANOVA est le moins biaisé. Le GEE sous-estime ρ de 20 à 25 % quand ρ = 0,02. — [Wu et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- **Saha & Sen (2015)** : π ≥ 0,1 dans toutes leurs configurations. — [Saha & Sen 2015](https://ww2.amstat.org/meetings/proceedings/2015/data/assets/pdf/234136.pdf)
- **Mbekwe Yepnang et al. (2021)** : estimateur ANOVA privilégié pour des ICC d'environ 0,01. — [PMID 34218744](https://europepmc.org/article/MED/34218744)
- **Saha & Paul (2005)** : le maximum de vraisemblance corrigé du biais fait mieux que le maximum de vraisemblance standard. — [PMID 16007569](https://europepmc.org/article/MED/16007569)
- **Gulliford et al. (2005)** : relation log-log entre ICC et prévalence. Une issue rare va donc avec un ICC faible sur l'échelle des proportions. — [PMID 15718113](https://europepmc.org/article/MED/15718113)
- **Chakraborty et al. (2009)** : méthode par simulation pour estimer un ICC binaire et sa distribution selon le nombre et la taille des grappes, appliquée à un essai néonatal. — [PMID 18723124](https://europepmc.org/article/MED/18723124)

### Inferences
- **Classement en vérification locale** (tableau de la question 2).
  - Le maximum de vraisemblance bêta-binomial à p_s propres a un biais de −8 à −16 % selon les cas ordinaires, et reste ≈ 0 sous ρ = 0.
  - Le Fleiss–Cuzick corrigé et la moyenne des ANOVA par strate sont quasi sans biais en O1, O2 et O4. Ils perdent 18 à 20 % en O3 et 14 % en D1bis.
  - Le Fleiss–Cuzick brut perd environ 20 %.
  - Le GEE par paires perd environ 50 %.
- **Pourquoi ce biais vers le bas.** Avec des événements rares et un ρ élevé, l'information se concentre dans quelques grappes. Le dénominateur p̂_s(1−p̂_s) est biaisé vers le bas d'un facteur (1 − deff_s/N_s), d'où le biais.
- **Suite à donner.** Avant préenregistrement, rejouer cette comparaison sur le générateur et les configurations réelles du protocole. Candidats : maximum de vraisemblance bêta-binomial à p_s propres, Fleiss–Cuzick stratifié corrigé, ANOVA par strate pondérée.

### Gaps
- Aucune simulation à comité de lecture à π < 0,05 avec peu de grappes porteuses d'événements n'a été trouvée.
- La plage de prévalences de Mbekwe Yepnang et al. (2021) n'a pas été vérifiée : seul le résumé était accessible, le texte HAL étant bloqué.
- La vérification locale ne porte pas sur les configurations réelles. Elle suppose un ρ commun vrai et ne mesure pas la couverture des bornes de Clopper–Pearson qui en découlent.
