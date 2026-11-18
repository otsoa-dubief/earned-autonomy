# Règles à trois issues (nettement au-dessus / en dessous / indéterminé) pour un taux d'erreur rare sous erreurs groupées

Légende. **[lu]** : texte intégral consulté. **[résumé]** : résumé, extrait de moteur de recherche ou source secondaire, à revérifier avant de le citer formellement. **[calcul]** : calcul illustratif fait pour ces notes (script Python, Clopper-Pearson exact sur effectif efficace). Ce n'est pas une source. Exemple de référence utilisé pour tous les [calcul] : un seul type, n = 1 600 actions, k = 160 tâches, m̄ = 10, barre = 1/132 ≈ 0,00758, DE = 1 + (m̄ − 1)ρ fixé (non estimé).

## 1. Décisions à trois issues (indifférence, équivalence, NI/supériorité, TOST) : que recommandent-elles pour le côté « nettement pire » ?

### Takeaway
Les traditions trouvées font toutes de « nettement au-dessus » une affirmation qui demande sa propre preuve : une borne unilatérale qui exclut le seuil, ou un multiple du seuil (zone d'indifférence), avec un risque d'erreur nommé. On les trouve dans les règles à trois décisions, le test « three-sided », TOST/IUT, les designs de phase II à trois issues, les cadres Go/Consider/Stop et l'échantillonnage d'acceptation. Aucune ne convertit un échec à établir « en dessous » en « au-dessus » : ce cas tombe dans une zone explicite (« pas d'affirmation », « non concluant », « consider »).

### Cited Findings
**Règles à trois décisions**
- Jones & Tukey (2000, *Psychological Methods* 5:411–414) présentent le test comme un choix entre trois issues : affirmer θ > θ0, affirmer θ < θ0, ou ne rien affirmer. L'égalité ponctuelle étant tenue pour impossible, les deux tests unilatéraux tournent chacun au niveau nominal plein (pas α/2), d'où plus de puissance que la version de Kaiser (1960). [résumé] — [arXiv 1710.06676](https://arxiv.org/pdf/1710.06676) ; [Rice & Krakauer, Annual Review of Statistics](https://annualreviews.org/doi/pdf/10.1146/annurev-statistics-033021-111159) (page refusée en 403, contenu vu par extrait)
- Une procédure à cinq décisions (*The American Statistician* 2019) généralise Jones-Tukey et s'y réduit si la nulle ponctuelle est jugée impossible. [résumé] — [IDEAS](https://ideas.repec.org/a/taf/amstat/v73y2019i4p321-326.html)
- Goeman, Solari & Stijnen (2010, *Stat Med* 29:2117–2125) testent simultanément infériorité, équivalence et supériorité, avec une multiplicité contrôlée par le principe de partition. Les tests unilatéraux donnent plus de puissance qu'un test bilatéral pour conclure non-infériorité ou non-supériorité. L'article examine aussi le lien avec les intervalles de confiance. [résumé] — [BOA Unimib](https://boa.unimib.it/handle/10281/20176)
- Les tutoriels divergent sur la correction de multiplicité de Goeman et al. : Bonferroni sur les tests d'infériorité et de supériorité selon l'un, besoin de tests bilatéraux selon un autre. Le « three-sided testing » combine TOST et tests d'effet minimal, et l'équivalence seule ne permet pas de conclure qu'un effet est important. [résumé] — [Isager & Fitzgerald, tutoriel TST](https://jack-fitzgerald.github.io/files/TST_Tutorial.pdf)

**Équivalence, TOST, IUT**
- Lakens, Scheel & Isager (2018, *AMPPS* 1(2):259–269) :
  - les bornes d'équivalence découlent de la plus petite taille d'effet d'intérêt (SESOI), fixée avant de voir les données pour éviter le p-hacking ;
  - TOST revient à vérifier que l'IC est entièrement dans les bornes.

  [résumé] — [vignette TOSTER](https://cran.nics.utk.edu/cran/web/packages/TOSTER/vignettes/IntroductionToTOSTER.Rmd) ; [typeset](https://typeset.io/papers/equivalence-testing-for-psychological-research-a-tutorial-26mcb08huo)
- Berger & Hsu (1996, *Statistical Science* 11(4):283–319) :
  - le cadre intersection-union (IUT) « clarifie, simplifie et unifie » les tests de bioéquivalence, TOST en étant un cas ;
  - ils dérivent un test plus puissant que celui des guidelines FDA/CE ;
  - ils critiquent les IC à 100(1−2α) % au profit d'ensembles à 100(1−α) % correspondant à des tests de taille α.

  [résumé] — [Project Euclid](https://projecteuclid.org/euclid.ss/1032280304). Senn conteste cette position. [résumé] — [Error Statistics](https://errorstatistics.com/2014/07/31/roger-berger-on-senns-blood-simple-with-a-response-by-s-senn-guest-posts/)

**Designs binomiaux à trois issues (phase II)**
- Sargent, Chan & Goldberg (2001, *Controlled Clinical Trials* 22:117–125) proposent un design de phase II à trois issues. [résumé] — [Mayo Clinic](https://mayoclinic.elsevierpure.com/en/publications/a-three-outcome-design-for-phase-ii-clinical-trials/)
- La région « non concluante » y est définie par deux seuils sur le nombre de réponses et ne rejette ni H0 ni H1. Elle dépend des taux d'erreur choisis et de n, pas de la biologie. Le précurseur est Storer (1992), l'extension randomisée Hong & Wang (2007). [résumé] — [NEJSDS 2025](https://nejsds.nestat.org/journal/NEJSDS/article/94)
- Exemple de type Sargent : H0 ORR ≤ 7,5 % contre H1 ≥ 27,5 %, α = 0,05, β = 0,10, n = 27. On obtient 0–3 réponses = NO-GO, ≥ 5 = GO, 4 = non concluant. [résumé] — [arXiv 1908.07751](https://arxiv.org/pdf/1908.07751)

**Go / Consider / Stop**
- Frewer et al. (2016, *Pharm Stat* 15:255–263) calculent les critères go et stop à partir d'une valeur cible (TV) et d'une valeur de référence basse (LRV) pré-spécifiées. Une zone « consider » autorise des études plus petites. [résumé] — [PubMed](https://www.pubmed.gov/26991401/)
- Présentation de Cytel [lu] — [Cytel](https://cytel.com/perspectives/decision-making-in-early-clinical-development/) :
  - « 3 outcome decision framework which includes Go, Stop and Consider », fondé sur Lalonde et al. ;
  - deux risques nommés : « False Stop Risk – Risk of a stop if the truth is better than TV » et « False Go Risk – Risk of a go if the truth is worse than the LRV » ;
  - LRV et TV doivent être scientifiquement justifiées ;
  - en zone Consider, il faut définir des critères pour en sortir.

**Échantillonnage d'acceptation (zone d'indifférence)**
- Risque producteur α = 1 − Pa(AQL), risque consommateur β = Pa(LTPD) : ce sont deux points de la courbe d'efficacité (OC). Conventions courantes : α ≈ 0,05, β ≈ 0,10. [résumé, secondaire] — [MetricGate](https://metricgate.com/calculator/producer-and-consumer-risk). Courbes OC binomiales à échantillon unique : [NIST Dataplot](https://itl.nist.gov/div898/software/dataplot/refman1/auxillar/singsamp.htm) [résumé]
- Berger (1982) pose l'acceptation à plusieurs caractéristiques comme un test : H0 = « un ou plusieurs paramètres ne respectent pas leur standard ». [résumé] — [Scilit](https://scilit.com/publications/d4301c6161f128a1c2f1609c25490645)

**Non-infériorité**
- L'extension CONSORT NI/équivalence (Piaggio et al., *JAMA* 2012;308:2594–2604) recommande une figure qui montre les IC face à la marge de non-infériorité. [résumé] — [EQUATOR](https://www.equator-network.org/?p=7626)

### Inferences
- Correspondance avec le protocole : barre = seuil, « délégable » = côté « en dessous », R4 = côté « nettement au-dessus ». Go/Consider/Stop est le cadre le plus proche : deux critères distincts, deux risques nommés (faux go ≈ délégation à tort, faux stop ≈ R4 à tort) et une zone intermédiaire qui porte un nom et une conduite à tenir.
- Deux variantes pour le côté pire :
  - « au-dessus » : borne inférieure > barre ;
  - « nettement au-dessus » : borne inférieure > c × barre avec c > 1. C'est l'équivalent d'une RQL/LTPD et cela rend R4 encore plus sûr.
- Aucun de ces cadres n'impose le même niveau de confiance des deux côtés. Garder 50 % pour la délégation et passer à 80–95 % pour R4 est cohérent avec eux.

### Gaps
- Textes primaires non lus : Schuirmann (1987), le livre de Wellek, Jones & Tukey (2000), Goeman et al. (2010), Sargent et al. (2001), Frewer et al. (2016), Lalonde et al. (2007). Les niveaux de confiance précis de Go/Stop chez Frewer/Lalonde n'ont pas été vérifiés : l'extrait AstraZeneca trouvé était illisible.
- Libellés exacts des catégories de la figure CONSORT NI (inférieur / non concluant / non inférieur…) : non trouvés.

## 2. Proportions binaires groupées : quelles bornes, et quel ρ pour établir un dépassement ? ρ = 1 est-il un choix conservateur connu ?

### Takeaway
La pratique établie (Korn-Graubard, NCHS, paquet R survey) applique Clopper-Pearson sur n/DE, avec correction de degrés de liberté et DE tronqué à 1. Mais avec un DE estimé, tous les intervalles sous-couvrent, et l'incertitude sur n_eff en est la cause principale (Franco et al.). Pour une borne destinée à établir un dépassement, sous-estimer ρ est anticonservateur. ρ = 1 (chaque tâche compte pour une observation, Miller) donne le DE maximal à tailles de tâche égales, donc un choix conservateur, au prix d'une forte perte de puissance quand le groupement réel est faible. Je n'ai trouvé aucune source qui recommande explicitement ρ = 1 pour cet usage.

### Cited Findings
**Korn-Graubard et effectif efficace**
- Korn & Graubard (1998, *Survey Methodology*) modifient l'intervalle binomial exact pour les proportions d'enquête avec peu de positifs. Couverture meilleure que les intervalles normal, logit et Poisson ; simulations avec des grappes de taille 10 ou 100. [résumé] — [Statistique Canada](https://www150.statcan.gc.ca/n1/en/catalogue/12-001-X19980024356)
- Ajustement KG : n_eff^df = n_eff × [t_{n−1}(1−α/2) / t_d(1−α/2)]², avec d = nombre de grappes − nombre de strates. Fort groupement → rapport < 1 → n_eff réduit → IC plus larges. Le texte extrait écrit « n − 1 < d », vraisemblablement une coquille pour d < n − 1. Dean & Pagano (2015) mettent z au numérateur, ce qui donne un n_eff plus petit et une couverture plus haute. [lu] — [Franco et al.](https://math.umd.edu/~slud/s770/SurveyConfidenceIntervals/JSSAM-2017-065-FINAL.pdf)
- Franco, Little, Louis & Slud (version de travail du 2 août 2018, publiée dans JSSAM) [lu] — [PDF](https://math.umd.edu/~slud/s770/SurveyConfidenceIntervals/JSSAM-2017-065-FINAL.pdf) :
  - « all intervals undercover when there is clustering and design effects are computed from a simple design-based estimator of sampling variance » ;
  - « the principal cause of undercoverage in complex surveys is uncertainty in estimating the effective sample size » ;
  - avec le vrai DE, les 6 intervalles hors Wald tendent à être conservateurs ;
  - Clopper-Pearson avec un n_eff estimé « tends to over-cover, at the expense of very large width » ;
  - ICC repérés dans le texte : 0,001, 0,1 et 0,25 (aucune valeur élevée repérée) ;
  - « For large cluster-size c and ICC ρ, undercoverage for either the DP or Kish method is common », le cas le plus problématique étant c = 7 ;
  - ils recommandent Wilson ou Bayes à prior uniforme (Jeffreys proche), et jugent leur approche superpopulation plus efficace que les ajustements KG et DP.
- Les mêmes auteurs signalent des travaux sur la couverture **unilatérale** (Kott & Liu 2009, *Int Stat Rev* 77:251–265 ; Liu & Kott 2009, *JOS* 25:569–588) et précisent ne traiter eux-mêmes que le bilatéral. [lu, référence] — [Franco et al.](https://math.umd.edu/~slud/s770/SurveyConfidenceIntervals/JSSAM-2017-065-FINAL.pdf)
- Dean & Pagano (2015, *JSSAM* 3(4):484–503) comparent 7 méthodes sur un design 30 × 7 calqué sur les enquêtes vaccinales. L'ajustement des ddl compte. Si l'ICC est élevé et la prévalence < 0,10, Agresti-Coull et Clopper-Pearson sont les meilleurs. [résumé] — [TechNet-21](https://www.technet-21.org/en/resources/journal-article/survey-publication-dean-j-survey-stats-methods-2015)
- Normes de présentation du NCHS (Parker et al. 2017, *Vital Health Stat* 2(175)) [lu] — [NCHS](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf) :
  - IC Clopper-Pearson, ou Korn-Graubard pour les enquêtes complexes ;
  - n ou n_eff < 30 → estimation supprimée ;
  - « When the effective sample size is greater than the sample size, the sample size should be used » : DE tronqué à 1 ;
  - zéro événement → utiliser n et signaler l'estimation pour revue.
- La méthode « beta » de `svyciprop` (paquet R survey) implémente Korn-Graubard, avec un n_eff fondé sur la variance estimée. [résumé] — [svyciprop](https://r-survey.r-forge.r-project.org/survey/html/svyciprop.html)

**Évaluations d'IA**
- Miller (2024, Anthropic, arXiv:2411.00640) [lu] — [arXiv](https://arxiv.org/html/2411.00640v1) :
  - erreurs-types groupées recommandées quand les questions viennent en groupes (Éq. 4) ;
  - rapport groupé/naïf : 3,05 sur DROP (1,34 contre 0,44), 1,88 sur MGSM, 1,10 sur RACE-H ;
  - quand les scores d'une grappe sont parfaitement corrélés, « each cluster acts as a single independent observation » ;
  - rapporter le nombre de grappes à côté du nombre de questions, et sous-échantillonner au niveau grappe (annexe C) ;
  - rien sur les erreurs rares.

**ρ et son estimation**
- Ridout, Demétrio & Firth (1999, *Biometrics* 55:137–148) passent en revue de nombreux estimateurs de l'ICC binaire en simulation. Leur efficacité relative dépend de plusieurs facteurs, de façon complexe. [résumé] — [IDEAS](https://ideas.repec.org/a/bla/biomet/v55y1999i1p137-148.html). Fleiss-Cuzick y apparaît comme un estimateur de type kappa (Wu, Crespi & Wong). [résumé] — [PMC3426610](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- Gulliford et al. (2005, *J Clin Epidemiol* 58:246–251) : l'ICC binaire croît avec la prévalence (relation linéaire en log-log). ICC prédit de 0,008 (GPRD) ou 0,002 (HTA) à 1 % de prévalence, contre 0,075 ou 0,046 à 40 %. [résumé] — [UKHSA](https://researchportal.ukhsa.gov.uk/en/publications/intraclass-correlation-coefficient-and-outcome-prevalence-are-ass/)
- Turner, Prevost & Thompson (2004, *Stat Med*) modélisent l'incertitude de l'ICC par simulation bayésienne. En tenir compte réduit la puissance attendue. [résumé] — [QxMD](https://read.qxmd.com/read/15083478/allowing-for-imprecision-of-the-intracluster-correlation-coefficient-in-the-design-of-cluster-randomized-trials)
- Une étude de 2021 (*SMMR*, attribuée à Lewis & Julious par l'extrait) juge l'usage de la borne supérieure de l'IC de l'ICC « largement inefficace » (surpuissance) et préfère une approche par distribution. [résumé] — [White Rose](https://eprints.whiterose.ac.uk/178220)
- Eldridge, Ashby & Kerry (2006, *IJE* 35:1292–1300) : le DE dépend de la taille moyenne et du coefficient de variation (CV) des tailles de grappe. Exemple appliqué : DE de 18,35 avec CV = 0, de 20,36 avec CV = 0,34. [résumé] — [Trials 2015](https://trialsjournal.biomedcentral.com/articles/10.1186/1745-6215-16-S2-P124)
- Carter, Schnepel & Steigerwald (2017, *REStat* 99(4):698–709) définissent un nombre effectif de grappes G*, réduit selon l'hétérogénéité, qui peut être nettement inférieur au nombre réel. Formule G* = G/(1+Γ) (Lee & Steigerwald 2018). Un grand G ne garantit pas un grand G*. [résumé] — [IDEAS](https://ideas.repec.org/a/tpr/restat/v99y2017i4p698-709.html) ; [Stata Journal](https://econpapers.repec.org/RePEc:tsj:stataj:v:18:y:2018:i:2:p:447-460). Les extraits se contredisent sur le sens de la distorsion (sous-rejet ou sur-rejet).

**Autres intervalles pour une proportion groupée**
- Short et al. (2020, *SMMR*) : Wilson score avec correction de continuité, plus proche du nominal à petit n (au moins 5 mesures par grappe). Saha, Miller & Wang (2016, *IJB*) : profile-likelihood et Wilson comparés à likelihood, GEE et Rao-Scott. Shan (2020) : intervalles exacts de type Buehler, coûteux, en difficulté près de 0 ou 1. [résumé] — [SAGE](https://journals.sagepub.com/doi/abs/10.1177/0962280218823231) ; [EconPapers](https://econpapers.repec.org/RePEc:bpj:ijbist:v:12:y:2016:i:2:p:18:n:2) ; [UNLV](https://digitalscholarship.unlv.edu/env_occ_health_fac_articles/468)

### Inferences
- **Mécanisme du faux R4 [calcul].**
  - La « médiane » (borne supérieure CP à 50 % sur n_eff) vaut environ (x + 0,67·DE)/n, d'après l'approximation de la médiane d'une loi bêta. Le DE ajoute donc environ 0,67·DE « erreurs fantômes ».
  - Exemple de référence : « médiane > barre » dès x ≥ 12 (ρ = 0), 10 (ρ = 0,3), 8 (ρ = 0,7), 6 (ρ = 1). Une seule tâche entièrement ratée (10 erreurs) suffit dès ρ ≥ 0,3.
  - Sous groupement total, le nombre de tâches ratées F suit Bin(k, p). P(F ≥ 1) = 1 − (1−p)^k = **21,5 %** pour p = 0,2 × barre et k = 160, ce qui retrouve les ~20 % simulés par le protocole.
  - Avec un modèle bêta-binomial ρ = 0,7 (DE fixé à ρ = 0,7) on obtient 15 %, et 0,4 % sous indépendance.
  - Critère générique : sous groupement fort, la médiane bascule dès F > k·barre − 0,67ρ (environ). La règle est donc fragile quand **k·barre (nombre attendu de tâches ratées au niveau de la barre) est ≲ 1–2**.
  - Avec k·barre = 5 (k ≈ 660 tâches par type), P(faux « non délégable ») ≈ 0,4 % même sous groupement total.
- **Zéro erreur.** Sans aucune erreur, la médiane CP vaut environ 0,693/n_eff. Elle dépasse 1/132 dès n_eff < 92. Avec le plancher ρ = 0,3 et m̄ = 10 (DE = 3,7), un type de moins de ~340 actions est donc non délégable avec zéro erreur. Sous la définition actuelle, R4 peut ainsi naître du seul manque de données.
- **Sens du conservatisme.** Un DE plus grand élargit les deux bornes : c'est conservateur pour toute affirmation « établie » (délégation sûre comme R4). Mais il pousse aussi la médiane CP vers le haut. Le plancher ρ ≥ 0,3 est donc conservateur pour la délégation et anticonservateur pour R4 tant que R4 est défini comme le complément de la délégation.
- **Borne d'exceedance avec ρ̂.** Elle est anticonservatrice si ρ̂ sous-estime ρ (Franco : l'erreur sur n_eff est la cause principale de sous-couverture). Avec 4 à 12 erreurs dans une ou deux tâches, ρ̂ repose sur une ou deux grappes informatives (logique de G*), donc il est très instable. La correction de ddl de KG (d = nombre de tâches − nombre de strates) ne capte pas cette concentration.
- **ρ = 1.**
  - DE = m̄, n_eff = k, x_eff = x/m̄. Sous groupement total à tailles égales, x/m̄ = F suit exactement Bin(k, p) : Clopper-Pearson est alors exact, donc valide (couverture ≥ 1−α).
  - Si les tailles de tâche varient, le DE réel à ρ = 1 pour le taux poolé vaut n·Σm_i²/(Σm_i)² = m̄(1+CV²), qui est **> m̄**. « ρ = 1 avec m̄ » n'est donc pas le pire cas. Il faut utiliser m̄(1+CV²), ce qui semble coïncider avec la formule CV d'Eldridge à ρ = 1 (à vérifier dans l'article).
- **Coût en puissance de ρ = 1 [calcul]**, sur l'exemple de référence. Le seuil « borne inférieure > barre » est atteint à partir de :

  | ρ | borne à 95 % | borne à 90 % | borne à 80 % |
  |---|---|---|---|
  | 0 | x ≥ 19 | x ≥ 18 | x ≥ 16 |
  | 0,3 | x ≥ 26 | x ≥ 23 | x ≥ 20 |
  | 0,7 | x ≥ 33 | x ≥ 29 | x ≥ 24 |
  | 1 | x ≥ 38 | x ≥ 32 | x ≥ 26 |

  Avec ρ = 1 et 95 %, R4 demande un taux brut ≥ 2,4 % (≈ 3,1 × barre). Le tableau de la section 5 donne la puissance correspondante.
- **Voie médiane.** Prendre ρ à sa borne supérieure, ou intégrer l'incertitude sur ρ (Turner). La littérature de planification juge ce choix inefficace, mais ici l'inefficacité se traduit par davantage de « preuves insuffisantes », ce qui reste compatible avec l'intention : un R4 rare et sûr.

### Gaps
- Aucune source trouvée qui recommande ρ = 1 comme choix conservateur pour une borne d'exceedance. La justification reste mathématique (DE maximal à tailles égales), complétée par la remarque de Miller.
- Aucune étude de couverture trouvée pour un ICC ≥ 0,7 avec une prévalence rare : Franco s'arrête à 0,25, et le « ICC élevé » de Dean & Pagano n'est pas chiffré dans ce que j'ai vu.
- Bootstrap par grappes quand les événements rares tiennent dans une ou deux grappes : pas de source spécifique trouvée. Seule la recommandation de Miller de rééchantillonner par grappe existe.
- Zou & Donner (IC de la proportion ou de l'ICC binaire) : rien dans les résultats. Kott & Liu (intervalles unilatéraux) : repérés mais non lus.

## 3. Exiger « tous les types au-dessus » sur de nombreuses strates ou configurations : multiplicité, puissance, IUT

### Takeaway
Exiger que chaque type jugeable soit établi au-dessus de sa barre est exactement un test intersection-union (Berger 1982). Il n'y a pas de correction de multiplicité : le faux R4 reste ≤ α par cellule quel que soit le nombre de cellules. En revanche la puissance est au plus celle de la cellule la plus faible, et elle chute comme un produit (exemple FDA : 0,8 × 0,8 = 64 %). La FDA déconseille plus de deux co-critères et refuse que l'on relève α par critère pour compenser.

### Cited Findings
- Berger (1982, *Technometrics* 24(4):295–300) [résumé] — [Scilit](https://scilit.com/publications/d4301c6161f128a1c2f1609c25490645) ; [jocre::iutsize](https://search.r-project.org/CRAN/refmans/jocre/html/iutsize.html) :
  - H0 : un ou plusieurs paramètres ne respectent pas leur standard ; H1 : tous les respectent ;
  - la région de rejet est l'intersection des régions individuelles ;
  - l'article donne une condition sous laquelle l'IUT est de taille α si chaque test individuel l'est.
- Critique : la méthode de Berger ignore les corrélations entre statistiques de test. [résumé] — [thèse GUPEA](https://gupea.ub.gu.se/items/f4314307-6ba3-473b-8174-8cb216a37c0f)
- FDA, *Multiple Endpoints in Clinical Trials* (version finale d'octobre 2022) [lu] — [FDA](https://www.fda.gov/media/162416/download) :
  - §III.B : « Using two or more endpoints for which demonstration of an effect on each is recommended … will increase the Type II error rate and decrease study power … If the endpoints are independent, the power to show success on both will be approximately 64% (0.8 x 0.8) … the individual endpoints could be powered at approximately 90% to ensure the probability of success is at least 80%. The calculation would be different if the endpoints were highly positively correlated or the power was not equal for each endpoint. »
  - §III.C.1 : « there is no multiplicity problem when the study is designed to demonstrate efficacy on all of the separate endpoints. However, co-primary endpoint testing increases the Type II error rate. In general, unless clinically very important, the use of more than two co-primary endpoints should be carefully considered because of the loss of power. »
  - Tester chaque critère à α = 0,06–0,07 pour compenser : « not acceptable », car cela compromet l'interprétation de l'effet sur chaque composante.
- Berger & Hsu (1996) : TOST est un IUT, et il existe des IUT plus puissants que le test réglementaire. [résumé] — [Project Euclid](https://projecteuclid.org/euclid.ss/1032280304)

### Inferences
- **Taille de l'IUT.** C'est un sup sur la nulle composite. Il est atteint quand une cellule est exactement à la barre et toutes les autres très au-dessus. Pour un agent fiable (toutes les cellules bien en dessous), P(faux R4) est d'environ le produit de probabilités individuelles déjà minuscules [calcul : 0,0001 par type à 0,2 × barre avec la borne à 95 % et ρ = 1].
- **Contrôle à la frontière [calcul].** Au point p = barre, la règle « borne inférieure > barre à ρ = 1 » déclenche :

  | Modèle générateur | borne à 95 % (α nominal 0,05) | borne à 80 % (α nominal 0,20) |
  |---|---|---|
  | groupement total | 0,034 | 0,123 |
  | bêta-binomial ρ = 0,7 | 0,014 | 0,093 |

  Le taux reste sous α nominal même dans le pire modèle : la règle est bien conservatrice.
- **Choix de α_cellule.** Comme le niveau ne se dilue pas, on peut le prendre moins exigeant (0,10 à 0,20) pour regagner de la puissance, avec P(faux R4) ≤ α_cellule. La FDA refuse ce genre d'assouplissement pour un médicament, au nom de l'interprétabilité de chaque composante. L'argument vaut ici aussi si le rapport affiche un verdict par type.
- **Puissance [calcul].** Avec K types indépendants de puissance π chacun, la puissance globale vaut π^K. À 3 × barre, borne à 80 % et ρ = 1 : 0,71³ = 0,36 et 0,71⁵ = 0,18. Les types d'un même agent sont probablement corrélés positivement, ce qui rend la perte moins forte que le produit (cf. la FDA).
- **Leviers.**
  - Réduire le nombre de cellules : définir « jugeable » a priori, par exemple un nombre minimal de tâches ou un k·barre minimal.
  - Regrouper les configurations quand l'agent est le même.
  - Un modèle hiérarchique bêta-binomial (P a posteriori que tous les types dépassent) est une alternative non couverte par les sources lues.
- **Types trop petits.** Un type trop petit ne peut jamais être établi au-dessus avec ρ = 1. L'IUT donne alors « preuves insuffisantes », ce qui est le comportement voulu.

### Gaps
- Aucune source trouvée qui quantifie la puissance d'un IUT sur de nombreuses strates rares et groupées. La littérature sur les co-critères (Sozu, Hamasaki, Offen ; Hung & Wang 2009) n'a pas été consultée. Texte intégral de Berger (1982) non lu.

## 4. Asymétrie entre une décision de « meilleure estimation » (médiane ≤ seuil) et l'étiquette donnée quand rien ne passe

### Takeaway
Je n'ai trouvé aucun texte sur ce cas précis : un seuil à 50 % d'un côté, et son complément étiqueté négativement. Le principe, lui, fait consensus : l'absence de preuve d'un côté n'est pas une preuve de l'autre. Les cadres opérationnels (NCHS, Go/Consider/Stop, phase II à trois issues, NI) réservent une étiquette distincte, motivée, au cas non concluant.

### Cited Findings
- Altman & Bland (1995, *BMJ* 311:485) : les essais dits « négatifs » montrent le plus souvent une simple absence de preuve d'une différence, avec des effectifs souvent trop faibles pour détecter des différences réelles. [résumé] — [BMJ](https://www.bmj.com/content/311/7003/485)
- Une p-valeur > 0,05 ne permet pas de conclure à l'absence d'effet. [résumé] — [Stanley, ch. 11](https://dstanley4.github.io/psyc4780bookdown/equivalence-tests-and-sample-size.html). L'équivalence seule ne permet pas non plus de conclure qu'un effet est important. [résumé] — [tutoriel TST](https://jack-fitzgerald.github.io/files/TST_Tutorial.pdf)
- NCHS : trois issues pour une estimation (présenter, signaler pour revue, supprimer). Une estimation peut être « unreliable but not be suppressed », et une note de bas de page doit donner la raison du signalement ou de la suppression. [lu] — [NCHS](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- Go/Consider/Stop : en zone Consider, les critères pour en sortir sont définis à l'avance (critère secondaire, données externes). [lu] — [Cytel](https://cytel.com/perspectives/decision-making-in-early-clinical-development/)
- Issue « non concluante » de Sargent [résumé] — [NEJSDS](https://nejsds.nestat.org/journal/NEJSDS/article/94). Issue « pas d'affirmation » de Jones-Tukey [résumé] — [arXiv 1710.06676](https://arxiv.org/pdf/1710.06676)

### Inferences
- « Délégable » est une décision de meilleure estimation (médiane ≤ barre, soit environ P(p ≤ barre) ≥ ½), pas une affirmation à confiance élevée. Son complément mêle deux états : « nettement au-dessus » et « on ne sait pas ». L'étiqueter entièrement R4, c'est traiter une décision à 50 % comme une preuve d'infériorité : c'est l'erreur décrite par Altman & Bland.
- Schéma cohérent avec les sources :
  - **Délégable** : médiane ≤ barre, inchangé ;
  - **Rien à déléguer** : IUT, chaque type jugeable a une borne inférieure > barre, avec ρ conservateur ;
  - **Preuves insuffisantes** : tous les autres cas.
- Les trois issues s'excluent [calcul] : pour α < 0,5, LB(ρ=1) < LB(ρ̂) < médiane(ρ̂). En effet, le quantile α de Beta(x_eff, n_eff−x_eff+1) est inférieur à la médiane de Beta(x_eff+1, n_eff−x_eff), et la borne inférieure baisse quand le DE monte (seuils 19 < 26 < 33 < 38).
- Comme au NCHS, motiver l'étiquette : « erreurs concentrées dans une ou deux tâches », « k·barre < 2 », « type non jugeable ».
- Préenregistrer α, la règle de choix de ρ, la définition de « jugeable » et la conduite à tenir en zone intermédiaire (par exemple : ajouter des tâches).

### Gaps
- Aucune source sur l'asymétrie précise « médiane contre étiquette du complément ». Les go/no-go bayésiens à deux seuils de probabilité a posteriori (Pulkstenis 2017, etc.) n'ont pas été consultés.

## 5. Calibrer la règle par simulation : faux « nettement mauvais » pour les agents fiables, puissance à k × barre

### Takeaway
Les sources vont dans le même sens. Il faut fixer a priori deux points de calibration : un niveau « bon » où le faux négatif doit être rare et un niveau « mauvais » où la détection doit être probable (AQL/LTPD, LRV/TV, H0/H1 de Sargent). On rapporte ensuite les probabilités des trois issues, y compris « non concluant », sur une grille factorielle de scénarios qui inclut des cas extrêmes. Enfin, on dimensionne n_sim pour obtenir une erreur Monte-Carlo acceptable, avec MCSE = √(p(1−p)/n_sim).

### Cited Findings
- Morris, White & Crowther (2019, *Stat Med* 38:2074–2102) [lu] — [PMC6492164](https://pmc.ncbi.nlm.nih.gov/articles/PMC6492164/) :
  - cadre ADEMP ;
  - MCSE de la couverture et du taux de rejet (puissance, erreur de type I) = √(p̂(1−p̂)/n_sim) (Table 6) ;
  - n_sim = E(cov)(1−E(cov))/MCSE² : par exemple 1 900 répétitions pour 95 % et une MCSE de 0,5 %, et 10 000 dans le pire cas (50 %) ;
  - des scénarios « unrealistically extreme » aident à comprendre quand et comment une méthode échoue ;
  - faire varier les facteurs de façon factorielle plutôt qu'un par un (ou en factorielle fractionnaire).
- Les risques de faux go et de faux stop sont les caractéristiques opératoires à produire. [lu] — [Cytel](https://cytel.com/perspectives/decision-making-in-early-clinical-development/)
- La courbe OC lit α à l'AQL et β à la LTPD. [résumé, secondaire] — [MetricGate](https://metricgate.com/calculator/producer-and-consumer-risk)
- Chez Sargent, la région non concluante dépend des taux d'erreur et de n. [résumé] — [NEJSDS](https://nejsds.nestat.org/journal/NEJSDS/article/94)
- La FDA fournit un calcul de puissance conjointe pour des co-critères. [lu] — [FDA](https://www.fda.gov/media/162416/download)
- Turner et al. intègrent l'incertitude de l'ICC dans les simulations de puissance. [résumé] — [QxMD](https://read.qxmd.com/read/15083478/allowing-for-imprecision-of-the-intracluster-correlation-coefficient-in-the-design-of-cluster-randomized-trials)

### Inferences
- **Plan de calibration** (transposition) :
  - **Contrainte de sûreté** : P(R4) ≤ α_R4 (par exemple 1 à 5 %) pour p ≤ c_bon × barre. On teste aussi p = barre, la frontière où se joue la taille de l'IUT. La contrainte doit tenir dans le **pire cas** des paramètres de nuisance : ρ ∈ {0 ; 0,3 ; 0,7 ; 1}, CV des tailles de tâche, nombre K de types, corrélation entre types et entre configurations.
  - **Puissance** : P(R4) à k × barre (k = 2, 3, 5), rapportée sous des ρ réalistes.
  - **Troisième issue** : rapporter P(preuves insuffisantes) dans chaque scénario, comme le λ de Sargent.
  - **Courbes OC complètes** : P(délégable), P(insuffisant), P(R4) en fonction de p/barre.
- **n_sim.** Pour un faux R4 visé à 1 %, une MCSE de 0,2 % demande environ 2 500 répétitions, et une MCSE de 0,1 % environ 9 900. Pour une puissance autour de 50 % avec une MCSE de 1 %, il en faut 2 500.
- **Exemple [calcul]** : un seul type, DE fixé. Valeurs = probabilité que chaque règle se déclenche.

  | Modèle générateur | p/barre | Médiane > barre (DE ρ=0,7) | Médiane > barre (DE ρ=0,3) | Borne 95 % > barre (ρ=1) | Borne 80 % > barre (ρ=1) |
  |---|---|---|---|---|---|
  | Groupement total (tâches tout ou rien) | 0,2 | 0,215 | 0,215 | 0,0001 | 0,002 |
  | | 1 | 0,704 | 0,704 | 0,034 | 0,123 |
  | | 2 | 0,913 | 0,913 | 0,225 | 0,438 |
  | | 3 | 0,975 | 0,975 | 0,494 | 0,707 |
  | | 5 | 0,998 | 0,998 | 0,859 | 0,944 |
  | Bêta-binomial ρ = 0,7 | 0,2 | 0,154 | 0,101 | 0,0000 | 0,0009 |
  | | 1 | 0,653 | 0,571 | 0,014 | 0,093 |
  | | 2 | 0,915 | 0,880 | 0,158 | 0,423 |
  | | 3 | 0,983 | 0,973 | 0,440 | 0,733 |
  | | 5 | 0,999 | 0,999 | 0,873 | 0,969 |
  | Indépendance | 0,2 | 0,004 | 0,000 | 0,0000 | 0,0000 |
  | | 1 | 0,916 | 0,769 | 0,0000 | 0,0003 |
  | | 2 | 1,000 | 1,000 | 0,006 | 0,387 |
  | | 3 | 1,000 | 1,000 | 0,414 | 0,971 |
  | | 5 | 1,000 | 1,000 | 0,999 | 1,000 |

  Lecture :
  - la règle « borne > barre à ρ = 1 » ramène le faux « nettement mauvais » de ~20 % à ≤ 0,2 % à 0,2 × barre ;
  - elle ne détecte de façon fiable que vers 5 × barre, ou 3 × barre avec la borne à 80 % ;
  - sous indépendance, ρ = 1 coûte très cher à 2 × barre (0,6 % de puissance à 95 %).

  Ces chiffres justifient de simuler aussi une variante où ρ est pris à sa borne supérieure, et de rapporter la puissance par scénario de ρ. Limite : ρ̂ réel est estimé (Fleiss-Cuzick, plancher 0,3), le comportement du protocole se situera donc entre les colonnes ; un seul type est modélisé, pas l'agrégation R4 sur tous les types et configurations.

### Gaps
- Aucun guide trouvé qui soit propre aux évaluations d'agents IA pour calibrer des étiquettes à trois issues. Pas de valeurs de référence trouvées pour α_R4 ou pour la puissance à viser hors des conventions cliniques et industrielles (α ≈ 0,05, β ≈ 0,10–0,20, de source secondaire).
