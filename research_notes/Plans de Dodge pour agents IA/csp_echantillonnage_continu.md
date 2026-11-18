# Plans d'échantillonnage continu (famille Dodge CSP) et règles de commutation, comme fondation d'une règle d'autonomie méritée

Notes de recherche, 2026-11-04. Convention : « Cité » = vu dans une source consultée (lien). « Calcul » = dérivé ou vérifié par moi (algèbre + simulation Monte-Carlo locale), à ne pas confondre avec une citation. Limite : les articles primaires (Dodge 1943, Dodge-Torrey 1951, Lieberman-Solomon 1955, Dodge 1955) n'ont PAS été lus (paywall/403) ; les formules viennent de la revue Hryniewicz 2011, qui les attribue à ces articles, et de Rodriguez & Jeske 2018. Les pages Project Euclid et MDPI étaient inaccessibles (403 ou contenu vide).

Notation : p = taux d'erreur par action (iid sauf mention), q = 1-p, i = « clearing number » (chez nous N), f = fraction échantillonnée, d = taux de détection a posteriori (chez nous 0,95).

---

## 1. CSP-1 (Dodge 1943) : définition exacte, AFI, AOQ, AOQL, lien i / f / AOQL

### Takeaway
CSP-1 alterne contrôle à 100 % et échantillonnage à fraction f ; il repasse à 100 % à la première non-conformité vue pendant l'échantillonnage. Les formules AFI/AOQ sont fermées (iid Bernoulli) ; l'AOQL n'a pas de forme fermée en (i, f) mais une relation paramétrique exacte (Dodge) et une approximation en 1/(e·i) (Shor-Pakhomov). Attention : la page MetricGate donne une formule u erronée.

### Cited Findings
- Définition en deux étapes. Étape 1 : contrôler 100 % jusqu'à i unités conformes consécutives. Étape 2 : ne contrôler qu'une fraction f (échantillonnage par probabilité f, systématique 1 sur n, ou 1 au hasard par segment de n) jusqu'à trouver une unité non conforme, puis retour immédiat à l'étape 1. Les non-conformes trouvés sont retirés ou remplacés par des conformes. — [Hryniewicz 2011, Zeszyty Naukowe WIT](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf) (§2.1, PDF lu en local via pdftotext)
- Sous iid Bernoulli (Dodge 1943) : u = (1-q^i)/(p·q^i) (durée moyenne étape 1) ; v = 1/(f·p) (durée moyenne étape 2) ; AFI F(p) = (u+f·v)/(u+v) = f / (f + (1-f)·q^i) ; AOQ(p) = p·[1-F(p)] = p·(1-f)·q^i / (f + (1-f)·q^i) ; AOQL = max_p AOQ(p). — [Hryniewicz 2011, eqs. 1-7](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Si les non conformes sont seulement retirés (pas remplacés), remplacer i par i-1 dans l'AFI. — même source
- AOQL sans forme fermée en (i, f). Relation de Dodge entre f, i et pL = AOQL, p1 étant le p où AOQ atteint son max : f = (1-p1)^(i+1) / (i·pL + (1-p1)^(i+1)) et p1 = (1+i·pL)/(i+1). — [Hryniewicz 2011, eqs. 8-9](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Approximation de conception (Shor & Pakhomov 1973), plans à remplacement : i = (1/α - 1)(1-pL)/(e·pL) avec contrainte AFI(pL) ≤ α ; 1/f - 1 = (1/α - 1)(1-pL)^i ; version « retrait » : i = (1/α - 1)/(e·pL). — même source, eqs. 11-14. Note : le facteur 1/e apparaît déjà dans cette littérature.
- Critère de Dodge pour f : (1 - f·pr)^N ≤ α (probabilité de ne pas détecter une dérive vers pr pendant N unités). — même source, eq. 10
- Effet des paramètres : i ou f plus grand réduit l'AOQL mais augmente l'AFI. — [MetricGate](https://metricgate.com/docs/csp-1-continuous-sampling-plan-dodge/) (source secondaire)
- Erreur à signaler : MetricGate écrit u = (1-q^i)/(f·q^i) ; Hryniewicz (eq. 2) donne u = (1-q^i)/(p·q^i). La seconde est la bonne (c'est l'espérance du temps d'attente de i succès consécutifs), et ma dérivation de AFI = f/(f+(1-f)q^i) ne ferme que avec elle. — [MetricGate](https://metricgate.com/docs/csp-1-continuous-sampling-plan-dodge/) contredit [Hryniewicz](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Méthode Markov pour l'état stationnaire de CSP-1 : Roberts (1965) ; extension à qualité markovienne (corrélation sérielle positive augmente l'AOQL, négative le diminue) : Sampath Kumar & Rajarshi 1987 ; AOQL exact seulement pour CSP-1, itératif pour CSP-2/MLP-2. — [IDEAS/RePEc, Naval Res. Logist. 34(5):629-644](https://ideas.repec.org/a/wly/navres/v34y1987i5p629-644.html) ; [Roberts 1965 cité par](https://projecteuclid.org/euclid.aoms/1177706103) (non ouvert, via résumé de recherche)
- Tables de conception (i, f) pour un AOQL donné : Dodge 1943 (courbes d'AOQL constant), MIL-STD-1235C, et Gauri Shankar & Mohapatra (existence d'un couple unique optimisant l'inspection moyenne). — [Hryniewicz 2011](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf) ; [Thai J. Stat.](https://ph02.tci-thaijo.org/index.php/thaistat/article/download/34321/28761) (non ouvert)

### Inferences
- Chez nous, i = N (série de succès avant autonomie), et « échantillonnage » = autonomie. Mais voir §2 : notre cas n'est pas CSP-1 avec f petit.

### Gaps
- Valeurs numériques des tables (i, f, AOQL) non extraites ; Dodge 1943 lui-même non lu.
- Pas pu vérifier l'exactitude des formules (8)-(9) contre l'original ; je les ai seulement recoupées avec la structure de AOQ ci-dessus.

---

## 2. Détection après coup complète (f = 0 pendant « l'échantillonnage ») : la littérature la traite-t-elle ? AOQL = ?

### Takeaway
Je n'ai trouvé aucune source traitant exactement notre schéma (unités non contrôlées avant livraison mais toutes vérifiées après exécution, erreur détectée non corrigée, perte d'autonomie au premier échec détecté). Les calculs de l'utilisateur sont corrects (vérifiés). Mais le « f = 0 » est trompeur : dans les termes de Dodge, la détection est à fraction f_det = 1 (toute unité est vue) sans rectification de l'unité fautive. Le bon cousin dans la littérature est l'UAOQL de Lieberman/Derman, dont notre borne 1/(i+1) est le pendant « sans correction ».

### Cited Findings
- Dodge suppose que l'inspection corrige (retrait/remplacement) les défauts trouvés ; l'AOQ de CSP-1 compte donc les unités non échantillonnées uniquement. — [Hryniewicz 2011](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Avec f → 0 dans la formule de Dodge, AOQ → p (aucune détection ; la phase d'échantillonnage ne se termine jamais) : ce n'est donc PAS notre cas. Calcul à partir de AOQ(p) = p(1-f)q^i/(f+(1-f)q^i).
- UAOQL (limite sans hypothèse de contrôle statistique, qualité arbitraire, adversaire omniscient) pour CSP-1 à échantillonnage probabiliste, défauts remplacés : UAOQL = (1-f)/(1+i·f) (Lieberman 1953 ; Derman, Johns & Lieberman 1959 pour l'échantillonnage aléatoire par segment). Version « défauts simplement retirés » : même formule avec i-1 (Endres 1969). — [Hryniewicz 2011, eq. 15](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf) ; [Derman, Johns, Lieberman 1959, Ann. Math. Stat. 30:1175-1191](https://projecteuclid.org/euclid.aoms/1177706103)
- White (1965) : l'UAOQL est la qualité sortante d'un processus piloté par un « démon omniscient » ; calcul par programmation linéaire / jeu stochastique. — [Hryniewicz 2011](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Wald & Wolfowitz 1945 (Ann. Math. Stat. 16:30-49) avaient déjà noté que CSP-1 ne garantit pas l'AOQL quand la qualité varie ; leur plan WSP garantit une limite sans hypothèse de contrôle : par groupe de N unités, on échantillonne 1 par segment de 1/f, et on bascule le reste du groupe en 100 % dès la (c+1)-ième non conformité, c étant le plus petit entier avec (c+1)(1-f)/n > AOQL (n = nombre de segments). — [Hryniewicz 2011, §4](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Concept voisin : « deferred sentencing » (Anscombe, Godwin, Plackett 1947, JRSS Suppl. 9) : jugement différé de la production continue. Non vérifié, cité de mémoire d'après la bibliographie standard, non consulté.

### Calculs (mes vérifications, non issus de la littérature)
- Modèle : qualification = attendre N succès consécutifs (action validée par l'humain) ; phase autonome = jusqu'à la première erreur détectée (détection prob. d, immédiate) ; l'erreur détectée a déjà eu lieu (non corrigée).
- Cycle : durée qualification E[Q] = (1-q^N)/(p·q^N) ; phase autonome E[A] = 1/(d·p). Fraction du temps en autonomie = q^N / (d(1-q^N) + q^N). Pour d = 1 : exactement q^N. Excès attendu = 0,95·p·fraction = 0,95·p·q^N quand d = 1 ; pour d = 0,95 le facteur correctif est 1/(0,95 + 0,05·q^N), soit au plus +5,3 %. La formule de l'utilisateur est donc exacte pour d = 1 et sous-estime d'au plus ~5 % pour d = 0,95. Ce « 5 % » est du même ordre que la marge d'arrondi 0,37 vs 0,35.
- Maximum de p·(1-p)^N : atteint exactement en p = 1/(N+1) ; valeur (N/(N+1))^N/(N+1). Numériquement (grille) × (N+1) : N=9 → 0,387 ; N=99 → 0,3697 ; N=949 → 0,36807 ; N=2599 → 0,36795 ; limite 1/e = 0,36788. Donc max ≈ 1/(e(N+1)) est confirmé, légèrement optimiste pour N petit (+5 % à N=9, +0,5 % à N=99).
- Simulation Monte-Carlo (N=99, d=0,95, 3·10^6 actions) : fraction autonome et erreurs en phase autonome cohérentes avec p·q^N (ex. p=0,01 : 0,0038 simulé vs 0,0037 théorique ; p=0,02 : 0,0028 vs 0,0027), bien sous la borne 0,95/(N+1)=0,0095.
- Borne sur trajectoire quelconque : chaque phase autonome se termine par (au plus) une erreur détectée et est précédée de N succès (phase de qualification). Donc nb d'erreurs détectées en phase autonome ≤ nb de cycles ≤ T/(N+1) ; l'excès par action ≤ 1/(N+1) (×0,95 pour le différentiel face à « tout valider »). Forme équivalente à l'UAOQL de Derman pour un contrôle à f = 1 sans correction : 1/(1+i·f)|_{f=1} = 1/(i+1). Le pendant de (1-f)/(1+i·f) est donc 1/(1+i·f) quand l'unité détectée n'est pas corrigée (ajoute l'unité détectée : (1-f)/f + 1 = 1/f erreurs par cycle de longueur i + 1/f). C'est ma dérivation, cohérente avec la formule publiée mais absente de la littérature consultée.

### Inferences
- Verdict sur la dérivation : mathématiquement correcte dans le cadre posé (iid, détection immédiate et fiable). La borne par trajectoire est un argument de comptage, du type UAOQL, donc « connu dans l'esprit » (Wald-Wolfowitz 1945, Lieberman 1953, Derman-Johns-Lieberman 1959, White 1965) mais, faute de preuve contraire dans mes recherches, la variante « détection après coup non corrective, f_det = 1 » ne semble pas publiée telle quelle. À présenter comme adaptation d'un résultat connu, pas comme nouveauté absolue (je n'ai pas pu fouiller Technometrics/JQT en texte intégral).
- N+1 ≥ 0,37/p* (stationnaire) et N+1 ≥ 1/p* (tout comportement) : le rapport e ≈ 2,7 entre les deux est le coût de la robustesse. Cohérent avec N≈950 vs 2600 pour p* = 1/2600.
- Le « f = 0 » devrait s'écrire f_avant = 0, f_après = 1 pour éviter qu'un lecteur du CSP reprenne la formule de Dodge avec f → 0 (qui donne AOQ → p).
- Failles à noter dans le protocole (voir §5) : (a) les ~5 % d'actions non vérifiables ne déclenchent jamais de perte d'autonomie, donc un agent fautif seulement sur ces actions échappe à la borne 1/(N+1) ; la borne ne vaut que pour les erreurs détectables. (b) Latence de détection : si l'erreur n'est connue qu'après k actions, la borne passe à ~ (1+k)/(N+1) par cycle.

### Gaps
- Aucune source primaire lue pour confirmer l'absence du cas. Recherches de « inspection after the fact / audit / non-corrective CSP » : rien de pertinent.
- Les chiffres SPRT (7 600 / 15 200) n'ont pas été vérifiés ; non couverts ici.

---

## 3. Variantes : CSP-2, CSP-3, multi-niveaux, CSP-F, CSP-T, CSP-V, MIL-STD-1235, skip-lot, règles de commutation ISO 2859-1 ; lesquelles correspondent à des niveaux d'autonomie gradués

### Takeaway
CSP-2/3 et les plans tightened tolèrent des erreurs isolées sans révocation totale (utile si 1 erreur ne doit pas tout casser) ; les multi-niveaux (MLP, CSP-T) sont l'analogue direct de « demander d'abord / agir puis notifier / agir seul ». ISO 2859-1 et skip-lot s'appliquent à des lots, pas à des flux, mais fournissent le vocabulaire de commutation.

### Cited Findings
- CSP-2 (Dodge & Torrey 1951, Industrial Quality Control 7:7-12) : après une non-conformité vue en échantillonnage, on continue à la fraction f ; retour à 100 % seulement si une 2e non-conformité survient dans les k unités suivantes (k = i en général). AOQ(p) = p(1-f)q^i[2-q^k] / (f[1-q^i][1-q^k] + q^i[2-q^k]). — [Hryniewicz 2011, eq. 25](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf) ; référence : [Rodriguez & Jeske 2018, réf. 8](https://escholarship.org/uc/item/2pt504p3)
- CSP-3 (id.) : CSP-2 + contrôle des 4 unités suivant une non-conformité ; si une est non conforme, retour immédiat à 100 %. AOQ en eq. 26 (non recopiée). Tolère les défauts accidentels mais protège contre une dégradation brusque. — [Hryniewicz 2011](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Multi-niveaux MLP (Lieberman & Solomon 1955, Ann. Math. Stat. 26:?) : k niveaux d'échantillonnage f1 > f2 > ... > fk ; i_j succès consécutifs montent d'un niveau ; une non-conformité redescend d'UN niveau (au niveau 1, retour à 100 %). k = 1 donne CSP-1. AOQ cas i0=i1=...=i, f_j = f^j : AOQ = p·z·[(1-z^k)/(1-z^(k+1)) - (f(1-z)/(1-fz))·(1-(fz)^k)/(1-z^(k+1))] avec z = (1/f)(q^i/(1-q^i)). Approximation des contours d'AOQL : f_k ≈ f_∞[1-(1/k)^(1/3) + ... ] (eq. 43-45, non recopiée). UAOQL existe (conjecture de L&S, algorithme de White 1965). — [Hryniewicz 2011, §3](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Plans tightened (Derman, Littauer & Solomon 1957, Ann. Math. Stat. 28:395-404) : MLP-r×1 (redescente de r niveaux), MLP-T (retour direct à 100 % à toute non-conformité). Sackrowitz 1972 (Technometrics 14) : variantes à vitesses de montée alternatives. — [Hryniewicz 2011](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Dérivés de CSP-1 sans hypothèse de contrôle : CSP-4, CSP-5 de Derman, Johns, Lieberman 1959 (formules d'AOQL et d'UAOQL dans l'article). — [Hryniewicz 2011](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- MIL-STD-1235C (1988) : cinq types : CSP-1, CSP-F (séries finies, tableaux indexés par AQL/AOQL, 32 intervalles de longueur de série), CSP-T (trois niveaux, fréquences f, f/2, f/4), CSP-2, CSP-V (comme CSP-2 avec 100 % sur k unités après la 2e non-conformité, comme CSP-3). Fréquences préférées de 1/2 (lettre A) à 1/200 (lettre K) ; la phase de criblage est plafonnée par une constante S, au-delà de laquelle l'inspection est suspendue et une action corrective est requise ; l'« AQL » y est un simple indice. Précurseurs : H-106, H-107, QSTAG 340 ; MIL-STD-1235A (1974). — [Hryniewicz 2011, §6](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Skip-lot : ISO 2859-3:2005 spécifie des procédures de contrôle par lots « sautés » : décision aléatoire, avec une probabilité donnée, d'accepter un lot sans le contrôler ; elles exigent que ISO 2859-1 soit en usage (inspection normale ou réduite, niveaux généraux I-III) ; la norme précise que ses procédures sont à distinguer des plans skip-lot de Dodge (SkSP). — [ISO 2859-3:2005, notice EVS](https://www.evs.ee/en/iso-2859-3-2005) (via résumé de recherche, page non ouverte)
- ISO 2859-1 règles de commutation (source secondaire, schéma fragmenté, à vérifier dans la norme) : normal → renforcé : 2 lots non acceptés sur 5 consécutifs ; normal → réduit : score de commutation ≥ 30 ET production stable ET autorisation ; réduit → normal : un lot non accepté ; interruption de l'inspection si 5 lots non acceptés pendant l'inspection renforcée. — [SQC Online](https://www.sqconline.com/switching-rules-iso-2859-1) ; édition 2026 publiée, seuils à confirmer dans le texte officiel ([aperçu ANSI](https://webstore.ansi.org/preview-pages/ISO/preview_ISO+2859-1-2026.pdf))
- Dodge 1955 SkSP-1 (non sourcé en ligne) : de mémoire, qualification par i lots consécutifs acceptés en inspection normale, puis inspection d'une fraction f des lots, retour à la normale au premier rejet ; AOQL tabulés dans Dodge 1955 / Schilling-Neubauer. À vérifier avant usage.

### Inferences
- Correspondance avec les niveaux d'autonomie (hypothèse de conception, pas de source) :
  - « Demander avant » = 100 % de contrôle (étape 1 de CSP-1 / inspection normale ou renforcée).
  - « Agir puis notifier » = niveau intermédiaire d'un MLP (f1 élevé, vérification a posteriori systématique par l'humain) ou CSP-T (f, f/2, f/4).
  - « Agir seul » = niveau terminal (fk faible) ; chez nous la vérification automatique reste à 100 % mais sans humain.
  - Montée de niveau = i_j succès consécutifs ; descente d'un niveau (MLP) ou retour total (MLP-T, CSP-1) selon le niveau d'enjeu : enjeu élevé → MLP-T / CSP-1 (révocation totale), enjeu faible → MLP ou CSP-2 (tolérance à l'erreur isolée).
  - CSP-3/CSP-V : « un incident n'éteint pas immédiatement l'autonomie, mais une 2e erreur sous k actions oui ».
- Skip-lot / ISO 2859 : utile pour des lots (batchs de tâches), moins pour l'autonomie par type d'action ; la règle « score de commutation » (points accumulés) est une alternative à « N succès consécutifs » plus tolérante, à regarder si N est trop grand.
- CSP-F (séries finies) est pertinent si un type d'action n'a que quelques centaines d'occurrences : les formules infinies surestiment le niveau de confiance (voir §5, Blackwell 1977).

### Gaps
- Dodge 1955 (skip-lot), Lieberman-Solomon 1955 (pages exactes), Dodge-Torrey 1951 : originaux non lus.
- Seuils exacts ISO 2859-1 (notamment score 30, règle des 5/10 lots) : non confirmés dans le texte de la norme.
- Montgomery et Schilling-Neubauer non consultés.

---

## 4. Résultats sous inspection imparfaite, dérive de processus, garanties sur trajectoire

### Takeaway
Sous inspection imparfaite, l'AOQL de Dodge disparaît : AOQ croît jusqu'à 1-θ sans mode (pas de « bosse »). Sous dérive, l'AOQL stationnaire n'est plus une garantie ; l'UAOQL (adversaire) et l'AEDL de Hillier la remplacent.

### Cited Findings
- Case, Bennett & Schmidt (1973), « The Dodge CSP-1 Continuous Sampling Plan under Inspection Error », AIIE Transactions 5:193-202 : adaptation de CSP-1 aux erreurs d'inspection ; l'effet est appréciable. — [Rodriguez & Jeske 2018, réf. 2](https://escholarship.org/uc/item/2pt504p3) ; [liste des références MDPI](https://mdpi.com/1999-4893/11/4/46)
- Rodriguez & Jeske (2018, Algorithms 11(4):46) : simulation de CSP-1 avec test imparfait (détection correcte des défauts avec probabilité θ) et séries courtes. Exemple θ = 0,8 : AOQ passe à 1,07 % (plan 1) et 1,52 % (plan 2), la proportion échantillonnée baisse (APS 58,15 % et 29,69 %) car les défauts non vus raccourcissent la phase de criblage. Avec test imparfait « l'AOQ part de 0 et croît jusqu'à 1-θ » sans garantie de forme en bosse ; la bosse revient pour θ ≥ 0,82 (dans leur exemple). — [Rodriguez & Jeske 2018 (PDF eScholarship lu en local)](https://escholarship.org/uc/item/2pt504p3)
- Même article : les formules de Dodge supposent lots infinis et test parfait ; l'analyse en forme fermée du cas imparfait + série courte est laissée en travail futur. — idem
- Séries courtes : Blackwell 1977 (Technometrics 19:259-262), Chen 2005 (Tamkang J. Sci. Eng. 8:81-85), Wang & Chen 1998 (J. Appl. Stat. 25:733-738) ; approximations AOQN = AOQ∞ + correction en 1/N par renouvellement (Yang 1983, Technometrics 25:59-67), McShane & Turnbull 1991 pour résultats dépendants. — [Rodriguez & Jeske 2018, réfs. 3-6](https://escholarship.org/uc/item/2pt504p3) ; [Hryniewicz 2011, eq. 19-24](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- Dépendance entre unités : corrélation sérielle positive augmente l'AOQL, négative le diminue (chaîne de Markov à deux états). — [Sampath Kumar & Rajarshi 1987](https://ideas.repec.org/a/wly/navres/v34y1987i5p629-644.html)
- Dérive soudaine de p0 (acceptable) à p1 (inacceptable) : Hillier 1964 (Technometrics 6) introduit l'AEDL, plus petit nombre tel que E(D) ≤ AEDL + L·AOQL, D = défauts non inspectés parmi les L unités suivant l'unité M, pour tous L, M, p0, p1. Pour CSP-1 : AEDL = ((1-f)/f)[1-(1-f)^x - x·pL] pour x>0, 0 sinon, avec x = ln(-f·pL/((1-f)ln(1-f)))/ln(1-f). — [Hryniewicz 2011, eqs. 16-18](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf) ; [Hillier 1964 (Technometrics 6)](https://informahealthcare.com/doi/abs/10.1080/00401706.1964.10490161) (notice via résultats de recherche, non lu)
- Critique de l'UAOQL : conditions « peu réalistes » (démon omniscient) ; la mesure de Hillier est jugée plus réaliste. — [Hryniewicz 2011](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- L'AOQL est une moyenne de long terme sur une production infinie ; le risque sur série courte ou dérive est traité par l'AEDL, CSP-F et le plafond S de MIL-STD-1235C. — idem
- Les plans CSP ne définissent pas de LTPD au sens lot par lot ; la protection contre une dérive est le critère de détection de Dodge (1-f·pr)^N ≤ α. — [Hryniewicz 2011, eq. 10](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf) (l'absence de LTPD est mon constat de lecture, non une citation).

### Inferences
- Notre cas « 5 % non vérifiables » est le pendant de θ = 0,95 de Rodriguez-Jeske, mais pas au même endroit : dans leur modèle l'inspecteur manque 1-θ des défauts, ce qui rallonge la phase échantillonnée (APS baisse) et fait monter l'AOQ vers 1-θ ; chez nous la détection a posteriori manque 5 % des erreurs, donc la phase autonome dure en moyenne 1/(0,95p) et non 1/p, et un adversaire qui ne se trompe que sur les actions non vérifiables n'est jamais arrêté. Le seul plafond est alors le taux de fautes « non vérifiables » lui-même ; le protocole doit donc plafonner la part des actions non vérifiables par type, ou les exclure de la qualification et de l'autonomie.
- Gaming : un agent peut espacer ou concentrer ses erreurs ; la borne 1/(N+1) par trajectoire reste valable pour les erreurs détectées, c'est son avantage sur l'AOQL stationnaire. Les erreurs corrélées (une panne qui fait tout rater d'un coup) sont couvertes par l'argument de comptage (1 erreur détectée par cycle) tant que la détection n'est pas retardée.
- Après dérive vers p1, l'excès attendu avant révocation est ≈ 1/d erreurs, quel que soit p1 (le temps croît quand p1 est petit). C'est une version « AEDL » du protocole ; à comparer à la formule de Hillier si on veut un chiffre publiable (calcul à faire, non fait).

### Gaps
- Article Case-Bennett-Schmidt 1973 non lu (formules de l'AOQ sous erreurs de type I et II non extraites) ; Barbosa-Correa & Galindo-Pacheco (Dyna) signalé mais non ouvert ([lien](https://revistas.unal.edu.co/index.php/dyna/article/view/37710)).
- Aucun résultat trouvé sur CSP avec détection retardée (latence) ni sur CSP avec dérive progressive (au lieu de saut).
- Texte intégral de Derman-Johns-Lieberman 1959, White 1965, Hillier 1964 : non lu, énoncés repris de Hryniewicz 2011 et des notices.

---

## 5. Verdict (résumé pour le rédacteur)

- Formule stationnaire excès = (1-0,05)·p·(1-p)^N, max en p = 1/(N+1), max ≈ 0,95/(e(N+1)) : CORRECTE (exacte pour d = 1 ; pour d = 0,95 à +5 % près), vérifiée analytiquement et par simulation. Légère sous-estimation à N petit (e.g. +5 % à N = 9).
- Borne par trajectoire excès ≤ 0,95/(N+1) : CORRECTE sous : détection immédiate, fiable, à ≤ 1 erreur détectée par phase autonome, et seulement pour les erreurs détectables. Non couverte : actions non vérifiables et latence de détection.
- « f = 0 » : formulation à corriger (f_avant = 0, f_après = 1, sans rectification).
- Déjà connu ? Le principe (garantir une limite de qualité sortante sans hypothèse de stationnarité, par comptage de cycles) l'est : Wald-Wolfowitz 1945, Lieberman 1953, Derman-Johns-Lieberman 1959 (UAOQL = (1-f)/(1+if)), White 1965. Le cas précis « détection a posteriori de toutes les unités, sans correction » n'a pas été trouvé ; c'est une adaptation directe, à qualifier de « dérivée de l'UAOQL » plutôt que de nouveauté.
- À citer dans le protocole : Dodge 1943, Dodge & Torrey 1951, Lieberman & Solomon 1955 (multi-niveaux), Derman-Johns-Lieberman 1959 (UAOQL), Hillier 1964 (AEDL), Case-Bennett-Schmidt 1973 (erreurs d'inspection), MIL-STD-1235C.
- Non vérifié : tous les originaux ; chiffres SPRT 7 600 / 15 200 ; seuils ISO 2859-1 ; SkSP-1 de Dodge.
