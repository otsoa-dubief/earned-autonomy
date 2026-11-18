> **Corrections après relecture indépendante (4 novembre, détail dans `_verification.md`)** : « environ 50 succès après 1 échec » se lit 44 ; l'exemple r = 15, s = 1 donne 48 % et ne franchit pas le seuil de 50 %.

# Jøsang & Ismail (2002), système de réputation bêta : fiche de lecture

## Référence et accès
- Audun Jøsang et Roslan Ismail, « The Beta Reputation System », 15th Bled Electronic Commerce Conference, Bled (Slovénie), 17-19 juin 2002, 14 p. https://mn.uio.no/ifi/english/people/aca/josang/publications/ji2002-bled.pdf
- **Accès : texte intégral lu** (PDF 14 pages ; formules lues sur les images des pages 3, 4, 5, 7 car l'extraction texte les abîme ; exemples numériques des §3 et conclusion lus en texte ; la définition 4 sur l'escompte par opinions, §2.5, parcourue seulement).

## Ce que dit la source
- §2.1, éq. (1)-(3) : la loi bêta f(p | α, β) représente la probabilité d'un événement binaire. Avec r occurrences de l'issue x et s de l'issue contraire : α = r + 1, β = s + 1 (prior uniforme). Espérance E(p) = α/(α+β) (éq. 2). Exemple : 7 x et 1 contraire → Beta(8, 2), E = 0,8.
- §2.2, définition 1, éq. (4)-(5) : fonction de réputation φ(p | r, s) et **E = (r+1)/(r+s+2)**. En mots : la probabilité attendue du bon résultat, avec « un succès et un échec imaginaires » au départ. Ici p est la probabilité du **succès** ; le taux d'échec attendu est (s+1)/(r+s+2).
- §2.3, définition 2, éq. (6) : note Rep = (r − s)/(r + s + 2), dans [−1, +1], 0 = neutre.
- §2.4, éq. (7) : combiner des retours = additionner les r et les s. Hypothèse explicite (p. 5) : **indépendance** des sources, on ne compte pas deux fois le même retour.
- §2.5 : escompte de l'avis d'un tiers selon sa propre réputation (non utile à notre règle).
- §2.6, éq. (12)-(14) : **oubli**. r = Σ rᵢ λ^(n−i), s = Σ sᵢ λ^(n−i), 0 ≤ λ ≤ 1 ; récursif : r(i) = r(i−1)·λ + rᵢ, pareil pour s. λ = 1 : rien oublié ; λ = 0 : seul le dernier retour compte. **λ s'applique de la même façon aux succès r et aux échecs s**, et par retour reçu (pas par temps). L'article dit de régler λ « selon la rapidité de changement attendue » de l'entité : aucune méthode de choix.
- §2.7, éq. (15) : un retour peut être fractionnaire, (r, s) avec r+s = poids du retour ; (0,5 ; 0,5) vaut 1 ; (0 ; 0) = pas de retour.
- §3 : exemples chiffrés (poids, escompte, oubli) ; plus λ est bas, plus la note se stabilise vite et moins elle est extrême. §4 : l'immunité contre les changements d'identité n'est pas traitée, système supposé centralisé.
- **Absent de l'article** : seuils de décision, test, promotion ou rétrogradation, intervalle de crédibilité, asymétrie des coûts, changement de configuration de l'entité noté.

## Ce que ça change pour notre règle
Un compteur (r, s) par type d'action, mis à jour à chaque action jugée. Décision : on ne regarde pas l'espérance seule mais la probabilité que le taux d'échec q soit sous un seuil (q ~ Beta(s+1, r+1)). Calculs (prior uniforme) :
| r | s | échec attendu | P(q < 10 %) | borne haute 95 % de q |
|---|---|---|---|---|
| 35 | 0 | 2,7 % | 97,8 % | 8,0 % |
| 30 | 0 | 3,1 % | 96,2 % | 9,2 % |
| 28 | 0 | 3,3 % | 95,3 % | non calculée |
| 35 | 1 | 5,3 % | 89,6 % | 12,2 % |
| 15 | 0 | 5,9 % | 81,5 % | 17,1 % |
| 15 | 1 | 11,1 % | 51,8 % | 25,0 % |
→ Promotion : « P(q < 10 %) ≥ 95 % » ≈ 28 succès sans échec ; 1 échec repousse à environ 50 succès. Rétrogradation : « P(q > 10 %) ≥ 50 % » (ici r=15, s=1 : 48 %) donne un déclencheur rapide en petit effectif.
**Forgetting, attention au plafond.** Avec λ par action, r est borné par 1/(1−λ). λ = 0,95 : r ≤ 20, échec attendu ≥ 4,5 % pour toujours : on ne peut jamais atteindre un seuil à 2 %. λ = 0,98 : r ≤ 50, plancher 1,9 %. λ = 0,99 : r ≤ 100, plancher 0,98 %. Il faut λ ≥ 0,98 pour des seuils bas. Contre-exemple chiffré : 30 succès puis 1 échec, λ = 0,98 : r = 22,3, s = 1,0, échec attendu 7,9 %, P(q<10 %) = 71 %. Les 30 succès valaient 96 % sans oubli.
**Oubli asymétrique (notre variante, pas celle de l'article).** Jøsang oublie aussi les échecs (λ sur s). Pour « les échecs passés comptent toujours, les réussites perdent leur poids » : λ sur r seulement, s non touché. Conséquence : à r borné, un échec ancien pèse de plus en plus ; c'est voulu mais il faut une règle d'expiration (sinon rétrogradation à vie). 
Remise à zéro partielle après un changement de consigne : r ← a0·r (a0 = 0,5 dans le cadre), s inchangé. Exemple : r = 30, s = 0 → r = 15 : P(q<10 %) tombe de 96,2 % à 81,5 % ; il faut ~13 succès de plus pour revenir à 95 % de seuil (28 − 15). Changement de modèle ou élargissement de droits : r = s = 0 à tout (mais les échecs passés comptent toujours selon le cadre ; le cadre ne dit pas si, après un changement de modèle, ils sont gardés. À trancher.)
Un doute signalé par l'agent : retour fractionnaire (0 ; 0) selon §2.7 = comme si rien n'avait eu lieu ; c'est exactement « ne lui coûte rien ».
Hypothèses qui tombent pour un agent IA : indépendance des actions (même mission = corrélées) ; stationnarité (un changement de version casse l'histoire, l'oubli lisse seulement) ; non-identité (Jøsang suppose l'authentification, l'agent change sous le même nom) ; retours binaires fiables (la relecture de 8 s est bruitée).

## Ce que ça corrige dans le rapport
- « (r+1)/(r+s+2) » : **exact**, éq. (5), mais c'est la probabilité du **succès** ; la formule d'échec attendu est (s+1)/(r+s+2). À écrire explicitement.
- « facteur d'oubli » : existe (éq. 12-14, §2.6), par retour, 0 ≤ λ ≤ 1. Mais **il oublie aussi les échecs**. La règle du rapport (« les échecs passés se transfèrent entièrement, les succès passés s'escomptent ») **n'est pas dans Jøsang** ; c'est une variante de l'équipe. À dire.
- À ajouter : λ borne le nombre de succès pris en compte (plafond 1/(1−λ)) ; un λ trop bas interdit la promotion. Le rapport ne le dit pas.
- À ajouter : l'article ne propose aucun seuil de promotion ni de test ; la décision (probabilité que q < seuil) vient de l'équipe.
- Le rapport écrit que le modèle « compte succès et échecs et applique un facteur d'oubli » : correct.

## Questions ouvertes
- Prior uniforme (1,1) : trop optimiste pour un type à enjeu ? Un prior Beta(1, k) plus méfiant ?
- Valeur de λ par type d'action ; en nombre d'actions, pas en jours (volume ~43 tâches/semaine tous types confondus d'après le rapport).
- Expiration des échecs non oubliés : jamais, ou après N actions ?
- Détail §2.5 (escompte) non relu en détail : utile si plusieurs relecteurs ?
