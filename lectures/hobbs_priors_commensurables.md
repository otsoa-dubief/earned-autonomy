# Hobbs et al., priors commensurables : fiche de lecture

## Référence et accès
- **Le document PMC4007051 n'est pas Hobbs et al. 2011.** C'est : Brian P. Hobbs, Daniel J. Sargent, Bradley P. Carlin, « Commensurate Priors for Incorporating Historical Information in Clinical Trials Using General and Generalized Linear Models », *Bayesian Analysis* 7(3), 2012, p. 639-674 (manuscrit NIH). DOI 10.1214/12-BA722. https://pmc.ncbi.nlm.nih.gov/articles/PMC4007051/
- Hobbs 2011 est : Hobbs, Carlin, Mandrekar, Sargent, « Hierarchical commensurate and power prior models for adaptive incorporation of historical information in clinical trials », *Biometrics* 67(3):1047-1056, DOI 10.1111/j.1541-0420.2011.01564.x, PMC3134568. **Non lu.**
- **Accès : texte intégral lu** (PMC4007051, récupéré en XML via l'API NCBI eutils, la page HTML de PMC est bloquée par un défi anti-robot). Formules lues en texte brut ; les tableaux et les figures (images) ne sont pas vus.

## Ce que dit la source
Contexte : un nouvel essai clinique, un bras témoin déjà étudié dans un essai passé. Question : combien d'information emprunter à l'historique, sachant qu'il peut être biaisé ?
- §1 : tout emprunter (homogénéité complète) peut avoir des conséquences « drastiques » pour la puissance et le risque de type I si l'historique est biaisé (résumé). La méta-analyse classique est trop sensible au choix de la loi a priori de la variance entre études quand il y a 1 ou 2 études historiques (§1.2, figure 1).
- §2.1, éq. (1) : le prior commensurable pour le paramètre courant μ est N(μ | μ0, 1/τ). μ0 = paramètre historique, **τ = « paramètre de commensurabilité »**. Grand τ : on emprunte presque tout (poids de l'historique élevé). Petit τ : on n'emprunte presque rien. Pour une seule étude : τ = 1/(2η²), η² = variance entre études. Le biais Δ = μ − μ0 est de **direction inconnue** (suit Pocock 1976).
- §2.3.1, éq. (4)-(5), Bayes empirique : τ estimé par maximum de la loi marginale des données ; **borné** dans [lν, uν], par ex. η ∈ [0,05 ; 10] ; sans borne, quand l'écart observé Δ̂ est petit, τ → ∞ (homogénéité totale). Les auteurs disent que les bornes doivent être choisies par évaluation formelle des propriétés fréquentistes.
- §2.3.2, éq. (6)-(8), complètement bayésien : loi a priori gamma sur τ (centre τ̃, confiance c) ou « spike and slab » (masse sur une grande valeur K = commensurable). Ils notent que le prior diffus de Hobbs 2011 sur log τ n'est pas neutre : ~83 % de la masse en homogénéité ou hétérogénéité extrême.
- §2.3.3, éq. (9)-(15) : estimation sous perte quadratique ; les modèles commensurables sont « admissibles a posteriori » (risque pré-postérieur) et donnent un compromis biais-variance entre « aucun emprunt » et « homogénéité totale », avec plus d'emprunt quand Δ est proche de 0.
- §4.1.1 : réponse binaire = régression logistique, historique remplacé par une approximation normale (théorème central limite bayésien), échantillonnage Metropolis. **Pas de forme fermée Bêta-binomiale.**
- §1.1 : les auteurs **n'étudient pas** le « commensurate power prior » de Hobbs 2011 (a0 sur la vraisemblance historique), jugé trop coûteux en calcul pour les données non gaussiennes.
- Hypothèses : observations indépendantes d'un modèle de régression, historique et courant de même forme, biais non systématique, normalité du prior ; peu d'études historiques (H ≤ 3 dans les simulations, n0 = 60, n = 180). Ils notent que ces méthodes sont subjectives et peuvent donner de mauvais résultats si le modèle est mal spécifié (§2.3.2).

## Ce que ça change pour notre règle
Idée à garder : le poids de l'ancien régime ne doit pas être fixé à l'avance mais **dépendre de l'accord entre ancien et nouveau**. Si, après un changement, le taux d'échec observé ressemble à l'ancien, on rend du poids aux anciens succès ; sinon, on les oublie. Idée à ne pas copier : le papier est gaussien/logistique, un bras témoin, des centaines de patients ; pas de formule prête pour 20 actions.
Analogue simple, **de moi, non de l'article** : prior d'emprunt a0 (type « power prior ») sur les compteurs Bêta, r ← a0·r, s ← a0·s, puis on ajoute les nouvelles actions. Calculs (taux d'échec q, P(q < 10 %) ; prior uniforme de départ) :
Historique 30 succès / 0 échec, après changement 9 succès / 1 échec :
- aucun emprunt : 30,3 % ; emprunt total : 92,6 % ; a0 = 0,5 : 74,9 % ; a0 = 0,25 : 56,5 %.
Historique 29 succès / 1 échec, après changement 10 succès / 0 échec :
- aucun emprunt : 68,6 % ; total : 92,6 % ; a0 = 0,5 symétrique : 85,7 % ; **succès ×0,5 mais échec entier : 75,8 %** (cadre du projet).
Nouveau seul 20 succès / 0 échec, historique 30/0 : aucun 89,1 % ; a0 = 0,5 : 97,7 % ; total : 99,5 %.
→ Lecture : à effectifs de quelques dizaines, a0 pèse plus que les données nouvelles ; la valeur 0,5 du cadre est un choix de poids majeur, pas un détail. Un a0 adaptatif à la Hobbs (selon l'écart Δ̂) serait très bruité avec 10 actions : l'estimation de τ est justement le point faible du papier à petit effectif (borné à la main).
Asymétrie : Hobbs suppose un biais **de direction inconnue** ; nous savons qu'une dérive vers plus d'échecs est la seule qui compte. D'où l'emprunt asymétrique du rapport : échecs entiers, succès escomptés. Hobbs n'en dit rien ; c'est donc une règle de l'équipe, à tester.
Hypothèses qui tombent : indépendance des actions (corrélation intra-mission) ; « même population » : un changement de modèle peut faire un agent très différent, a0 vrai proche de 0 ; peu de versions historiques : seule la dernière version est pertinente.

## Ce que ça corrige dans le rapport
- Le rapport cite « PMC4007051 » comme « priors commensurables » : c'est Hobbs, Sargent, Carlin 2012, pas Hobbs et al. 2011. Corriger la référence ou citer les deux (2011 non lu).
- « Emprunter intégralement l'historique peut fausser la décision si l'historique est biaisé » : **confirmé** (résumé et §1), au sens de la puissance et du risque de type I d'un essai clinique, pas pour une règle d'autonomie.
- « Les échecs passés se transfèrent entièrement, les succès escomptés » : **ne vient pas de Hobbs** (biais non orienté). Le rapport dit « l'équipe en déduit » : correct, mais à ne pas laisser croire appuyé par l'article.
- Les 0,5 de a0 : ni Hobbs ni Jøsang ne les fournissent ; hypothèse du cadre, à garder balisée « hypothèse ».
- Le rapport écrit « aucun article trouvé ne traite le transfert d'évidence entre versions d'agents LLM » : non contredit par cette lecture.

## Questions ouvertes
- Lire Hobbs 2011 (Biometrics, PMC3134568) : le « commensurate power prior » donne précisément a0 adaptatif ; plus proche de notre besoin.
- Un a0 constant par type d'action, ou lié au type de changement (consigne, outil, modèle) ?
- Combien d'actions après un changement avant d'estimer l'accord ancien/nouveau (petit effectif : bruit) ?
- Sensibilité du verdict du rejeu à a0 ∈ {0, 0,25, 0,5, 1} : à montrer systématiquement.
