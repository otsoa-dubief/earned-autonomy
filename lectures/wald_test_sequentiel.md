> **Corrections après relecture indépendante (4 novembre, détail dans `_verification.md`)** : GRAVE : le nombre d'échecs pour rétrograder dépend du point de départ du score : 2 depuis zéro, 4 depuis un plancher à ln B, 5 depuis ln B moins un échec, 3 après une remise à zéro partielle (−1,47). « Deux échecs rapprochés rétrogradent toujours » est faux. « 7 échecs » doit se lire 8. Recalcul vérifié par Claude.

# Wald (1945), test séquentiel : fiche de lecture

## Référence et accès
- Abraham Wald, « Sequential Tests of Statistical Hypotheses », *Annals of Mathematical Statistics* 16(2), 1945, p. 117-186 (pages données de mémoire, non vérifiées). DOI 10.1214/aoms/1177731118. https://projecteuclid.org/euclid.aoms/1177731118
- **Accès : inaccessible.** Project Euclid renvoie une page anti-robot (Incapsula) pour la page, le PDF et le téléchargement ; WebFetch ne rend rien. Je n'ai pas cherché de copie ailleurs : un essai sur des copies tierces a été refusé par le garde-fou de l'outil (contenu sous droits), et je ne contourne pas.
- Conséquence : **rien de ce qui suit n'est lu dans Wald.** Aucune section ni page citée. Les formules du paragraphe suivant sont celles du test du rapport de vraisemblance séquentiel tel qu'on l'enseigne (connaissance générale, non vérifiée sur le texte). Les calculs, eux, sont faits par moi (script Python, résultats vérifiables).

## Ce que dit la source
Non lu. À vérifier sur le texte avant publication : (1) les seuils A ≈ (1−β)/α et B ≈ β/(1−α) sont des approximations, pas des égalités ; (2) l'hypothèse d'observations indépendantes et de même loi ; (3) la proposition d'optimalité (nombre moyen d'observations minimal pour des risques α, β donnés) ; (4) le traitement du dépassement du seuil.

Rappel général (non sourcé) pour un taux d'échec p, hypothèse acceptable p0 contre inacceptable p1 : à chaque action, on ajoute au score LLR le log du rapport de vraisemblance. Succès : ln((1−p1)/(1−p0)) (négatif). Échec : ln(p1/p0) (positif). On accepte p0 quand LLR ≤ ln B, on rejette quand LLR ≥ ln A, sinon on continue. En mots : chaque échec pèse lourd vers « inacceptable », chaque succès pèse peu vers « acceptable ».

## Ce que ça change pour notre règle
Calcul recalculé (p0 = 2 %, p1 = 10 %, α = β = 5 %, seuils ± ln 19 = ± 2,944) :
- Succès : −0,0852. Échec : +1,6094. Un échec = 18,9 succès.
- Depuis zéro : 34,58 → **35 succès d'affilée** pour accepter (promotion).
- Après 1 échec : il faut (1,609 + 2,944)/0,0852 = 53,5 → **54 succès** de plus.
- Rejet (rétrogradation) depuis zéro : 2 échecs (2 × 1,609 = 3,22 > 2,944) ; 1 seul échec ne suffit pas (1,83 échecs nécessaires).
- Risques réels, calculés exactement par programmation dynamique (pas par l'approximation de Wald) : si p = 2 %, rejet à tort 2,97 % ; si p = 10 %, acceptation à tort 4,89 %. Les 5 % sont donc tenus.
- Taille moyenne d'échantillon : 54,6 actions si p = 2 % ; 38,3 si p = 10 % ; 76,7 si p = 5 % (zone grise : décision quasi pile ou face, 54 % accepté).
Pour la règle : un SPRT par type d'action, avec p0, p1 fixés par la gravité et la réversibilité (type grave : p1 plus bas, donc plus de succès requis). Promotion = franchir ln B ; rétrogradation = franchir ln A ou une alerte plus rapide (voir CUSUM). Oubli et remise à zéro : le LLR n'a pas d'oubli propre ; on le remet à une valeur de départ (voir ci-dessous).
**Défaut majeur pour nous : le SPRT n'a pas de plancher.** Après 100 succès, LLR = −8,5 : il faudrait 7 échecs (+11,3) pour atteindre ln A, et chaque échec ne défait que 18,9 succès. Un long passé propre achète une grosse réserve, donc on perd lentement, pas vite. Remède (inférence, non sourcée) : borner le LLR par le bas (par ex. à ln B − 1 échec, sorte de CUSUM réfléchi) ; ainsi 35 succès restent nécessaires, et 2 échecs rapprochés rétrogradent toujours.
Remise à zéro partielle : multiplier le LLR négatif (la preuve de succès) par un facteur a0 < 1 après un changement ; laisser le LLR positif (les échecs) intact. Exemple : LLR = −2,9 (promu) ; consigne modifiée, a0 = 0,5 → −1,47 ; il faut 17 succès de plus (1,47/0,0852) pour être de nouveau à ln B, et 1 échec (+1,609 → +0,14) ne rétrograde pas encore mais 2 échecs oui.
Quand les hypothèses tombent pour un agent IA : (1) indépendance : des actions d'une même mission, d'un même contexte ou d'un même prompt sont corrélées, 35 succès valent moins que 35 essais indépendants ; (2) stationnarité : un changement de modèle ou de consigne change p, c'est le but des remises à zéro ; (3) p0, p1 sont des choix, pas des mesures ; (4) la « réussite » doit être observée : une action non relue sans erreur détectée compte-t-elle comme succès ? Les validations de 8 secondes rendent le label bruité.

## Ce que ça corrige dans le rapport
- « 35 succès d'affilée » : **exact** (34,58 arrondi à 35), mais c'est un **minimum depuis zéro**, pas un nombre typique ; moyenne 54,6 si l'agent est à 2 %.
- « Un échec annule environ 19 succès » : **exact** (18,9), mais vrai seulement sans plancher ; après un échec, le retour demande 54 succès, pas 35.
- « Risques d'erreur de 5 % » : tenus (2,97 % et 4,89 % exacts), mais pour le test continu non borné ; toute borne ou troncature (limite de taille) change ces risques et il faut les recalculer.
- À ajouter : le rapport dit « révoquer » ; 1 échec ne révoque pas, 2 échecs rapprochés oui.
- Le lien vers Wald est correct ; mais la phrase ne peut pas être attribuée à une lecture du texte de Wald.

## Questions ouvertes
- Lire Wald (ou Wald & Wolfowitz 1948 sur l'optimalité) : accès par la bibliothèque d'Otsoa ou un exemplaire papier ?
- Choix de p0 et p1 par type d'action : qui les fixe, sur quelle base ?
- Plancher du LLR : quelle valeur ? Quel effet sur les risques ? À calculer avant le rejeu.
- Corrélation entre actions d'une même mission : compter par mission plutôt que par action ?
