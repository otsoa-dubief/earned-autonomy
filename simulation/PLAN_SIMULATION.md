# Simulation de niveau 1 · plan (4 novembre 2026)

Le but : faire tourner la règle de `REGLE.md` sur des **agents fictifs dont on connaît la fiabilité**, avec ses règles témoins, sans aucun modèle d'IA ni appel payant. Cette simulation sert à trois choses :
1. **Un contrôle mécanique** : la règle a-t-elle les propriétés annoncées ? C'est le troisième contrôle avant le gel.
2. **Des courbes de choix** : Otsoa fixe les seuils (agent « bon » ou « mauvais » pour chaque niveau d'enjeu, risque de laisser de côté un bon agent, marge de dégâts, réactivité K) en voyant ce que coûte chaque réglage.
3. **Une première réfutation possible** : si la règle ne bat pas les règles simples, même dans ce monde idéal, il faut le savoir avant de dépenser un dollar.

Ce n'est **pas l'expérience de confirmation**. Ajuster des réglages au vu de ces courbes est légitime ; c'est l'étape de conception.

Toutes les valeurs ci-dessous sont des **hypothèses déclarées**. Les changer, c'est changer le plan, et cela se note dans ce fichier.

## 1. Les types d'action (pièce 2)

| code | type | enjeu | réversible | paliers possibles |
|--|--|--|--|--|
| LEC | Lecture | faible | oui (sans effet) | 1, 2, 3 |
| ECR | Écriture réversible | faible | oui | 1, 2, 3 |
| DUR | Écriture durable | moyen | non (par prudence) | 1, 3 |
| EXE | Exécution et délégation | moyen | oui | 1, 2, 3 |
| MSG | Message interne | faible | non | 1, 3 |
| SOR | Sortie vers l'extérieur | fort | non | 1, 3 |
| ARG | Argent sous le montant | fort | non | 1, 3 |
| PLA | Plafonné | — | — | toujours 1 |

Ce qui est rangé dans PLA : les plafonds absolus (garde-fous, accord de l'humain, secrets), 20 % des actions d'argent (celles au-delà du montant) et 20 % des sorties (le premier message à une personne inconnue).

## 2. Les flux d'actions (deux mélanges, hypothèses)

| mélange | LEC | ECR | DUR | EXE | MSG | SOR | ARG | PLA (absolus) |
|--|--|--|--|--|--|--|--|--|
| « bureau » | 45 % | 15 % | 8 % | 8 % | 6 % | 12 % | 5 % | 1 % |
| « service client » | 40 % | 5 % | 20 % | 2 % | 3 % | 15 % | 14 % | 1 % |

Les parts de SOR et ARG ci-dessus incluent leur fraction plafonnée.

- **Actions invérifiables** : 5 % des actions, tirées au hasard. Elles sont exécutées selon le palier et peuvent faire des dégâts, mais elles n'apportent aucune preuve.
- **Horizon** : 3 000 actions par agent.
- **Répétitions** : 1 000 par cas, et 5 000 pour les cas clés.
- **Graines** fixées et notées.

## 3. Les agents fictifs

Chaque type d'action a son taux d'erreur vrai q. Une part h = 10 % des actions est « difficile », avec un taux d'erreur min(0,9 ; 6·q) ; le taux des actions faciles est réglé pour que la moyenne fasse q. Les erreurs se concentrent donc sur les cas difficiles. C'est ce qui donne un sens aux épreuves, qui sont tirées parmi les cas difficiles du type.

| agent | taux d'erreur vrai |
|--|--|
| A1 excellent | 0,5 % sur tous les types |
| A2 bon | 2 % partout |
| A3 moyen | 5 % partout |
| A4 mauvais | 15 % partout |
| A5 mauvais sur la sortie | 2 % partout, sauf SOR à 15 % |
| A6a dégradation annoncée | 2 %, puis 10 % à t = 1 500, avec un changement de modèle déclaré (remise à zéro appliquée) |
| A6b dérive silencieuse | 2 %, puis 10 % à t = 1 500, sans changement déclaré : seules les erreurs peuvent la révéler |
| A7 amélioration annoncée | 10 %, puis 2 % à t = 1 500, avec un changement déclaré |
| A8 consigne modifiée | A2 avec une consigne modifiée sur SOR à t = 1 500 (réussites de SOR divisées par deux), taux inchangé |

**Comportements de doute**, testés sur A2 et A4 :
- jamais (comportement par défaut) ;
- calibré : sur une action difficile, l'agent doute une fois sur deux ;
- abusif : il doute sur 30 % de toutes ses actions.

Un doute entraîne une validation, qui compte dans la charge, et n'apporte aucune preuve.

## 4. Le validateur humain simulé

- **Palier 1, demander avant** : une action fausse est arrêtée avec une probabilité de 1 − e. L'erreur ratée part, et compte dans les dégâts.
- **Palier 2, agir puis prévenir** (types réversibles) : une action fausse est exécutée, puis corrigée avec une probabilité de 1 − e. La correction compte dans la charge ; une erreur non corrigée compte dans les dégâts.
- **Palier 3, agir seul** : une action fausse compte dans les dégâts.

Valeurs de e : 0, 2, 5 et 10 %. La valeur principale est **5 %**. Le contrôle automatique voit toutes les actions vérifiables, quel que soit le palier : la preuve est complète, mais les dégâts dépendent du palier et du validateur.

## 5. La règle (pièces 4 à 8)

- **Compteurs par type** : r, les réussites vérifiées, et s, les erreurs vérifiées. Le doute et l'invérifiable sont neutres.
- **Score de Wald**, pour chaque palier visé : LLR = s·ln(pm/pb) + r·ln((1 − pm)/(1 − pb)). Le seuil d'acceptation est ln B = ln(β/(1 − α)), avec β = 5 % (le risque de promouvoir un agent mauvais) et α le risque de laisser de côté un agent bon. L'agent est au **plus haut palier dont le score est sous ln B**, avec les exceptions ci-dessous.
- **Plancher** : r est plafonné à r_max = (a − ln B)/b, calculé sur le test du palier le plus strict, où a = ln(pm/pb) et b = −ln((1 − pm)/(1 − pb)). Le score ne descend donc pas sous ln B − a.
- **Erreur à enjeu faible** : quand le score repasse au-dessus de ln B, l'agent descend, mais d'un seul palier par événement.
- **Erreur à enjeu moyen ou fort** :
  - retour immédiat au palier 1, r = 0, et s augmente de 1 ;
  - une épreuve de 3 variantes, tirées parmi les cas difficiles du type, doit être réussie en entier avant que r recommence à compter ;
  - si l'épreuve est ratée, nouvel essai après 50 actions de ce type.
- **Changement de modèle annoncé** : r = 0 sur tous les types. Les erreurs passées à enjeu moyen ou fort deviennent des épreuves ; une épreuve réussie efface son erreur (s diminue de 1).
- **Droits élargis** : même traitement, mais sur le seul type concerné.
- **Consigne modifiée** : r est divisé par deux sur le type concerné.
- **Réglages de départ (pb ; pm)**, pour chaque niveau d'enjeu :

  | niveau d'enjeu | vers le palier 3 | vers le palier 2 (réversibles) |
  |--|--|--|
  | faible | (5 % ; 20 %) | (10 % ; 30 %) |
  | moyen | (2 % ; 10 %) | (5 % ; 20 %) |
  | fort | (1 % ; 5 %) | sans objet |

  Deux variantes : « stricte » (taux divisés par deux) et « souple » (taux multipliés par 1,5). α vaut 5 % ou 20 %.

## 6. Les règles témoins (pièce 1)

1. **Tout approuver.**
2. **Tout faire valider.**
3. **Liste fixe** : LEC et ECR agissent seuls, tout le reste demande une validation.
4. **Tri par le risque, sans historique** : toute action à enjeu faible agit seule ; les enjeux moyen et fort demandent une validation.
5. **Trois réussites** : l'autonomie est accordée après 3 réussites d'affilée sur le type, quel que soit l'enjeu, et retirée à la première erreur.
6. **La règle sans remise à zéro.**
7. **La règle sans pondération par l'enjeu** : les réglages de l'enjeu moyen partout.
8. **La règle sans doute gratuit** : le doute compte comme une erreur.
9. **La règle sans palier du milieu** : deux paliers seulement.
10. **La règle sans épreuve** : compteur seul.
11. **L'oracle** : un type agit seul si et seulement si son vrai q est au plus pb pour le palier 3. C'est la borne haute.
12. **Le hasard** : chaque type est promu à des moments tirés au hasard, pendant la même part du temps que sous la règle.

## 7. Les mesures

- **Charge** pour 100 actions : validations, corrections et doutes. Elle est donnée sur toutes les actions, et aussi **hors lectures**, parce que dans un flux où les lectures dominent, « diviser par deux par rapport à tout faire valider » devient trop facile.
- **Dégâts** pour 100 actions, séparément pour chaque niveau d'enjeu, avec un intervalle.
- **Garantie** : la part des couples (agent mauvais sur un type, ce type) promus au palier 3 avant l'horizon. Cible : au plus 5 %.
- **Agents bons laissés de côté** : la part des types d'A1 et A2 jamais promus avant l'horizon, et le délai moyen de promotion.
- **Réactivité** (A6a, A6b) : le nombre d'actions entre la dégradation et le retour au palier 1, et les dégâts pendant cet intervalle.
- **Épreuves** : le taux de réussite des épreuves comparé à celui des tâches ordinaires.
- **Verdict de la pièce 1**, pour chaque réglage. La charge est-elle au plus la moitié de celle de « tout faire valider » (en tout, et hors lectures) ? Les dégâts, pour chaque niveau d'enjeu, sont-ils au plus ceux de « tout faire valider » plus une marge (0, 0,1 et 0,5 point pour 100 actions) ? La règle bat-elle la liste fixe et le tri par le risque, en charge à dégâts égaux ou en dégâts à charge égale ?

## 8. Contrôles du code (tests obligatoires)

Les tests doivent retrouver les nombres connus des fiches de lecture :
- avec pb = 2 %, pm = 10 % et α = β = 5 %, il faut **35 réussites** depuis zéro pour monter ;
- avec une erreur dans le compteur, il en faut **54 de plus** ;
- depuis le plancher, **2 erreurs** rapprochées font descendre ;
- les risques réels, calculés par Monte-Carlo, sont proches de 2,97 % et 4,89 % pour le test sans borne ;
- la probabilité d'enchaîner N réussites vaut p^N (0,95^20 = 0,358).

Les tests portent aussi sur les points suivants :
- une erreur à enjeu moyen ramène au palier 1 et ouvre une épreuve ;
- les actions plafonnées ne sont jamais autonomes ;
- le doute ne change ni r ni s ;
- les remises à zéro ne touchent jamais s, sauf quand une épreuve réussie efface une erreur après un changement de configuration.

## 9. Livrables

Dans `simulation/` :
- le code ;
- les tests ;
- `resultats/` : les tableaux CSV, les figures (courbes charge contre dégâts, garantie, délai de promotion, réactivité) et `RESULTATS.md`, un résumé avec les chiffres et leurs intervalles.

Aucun appel réseau, aucune donnée réelle.

## Amendement A1 (4 novembre 2026, après la première passe ; décision d'Otsoa)

Les résultats de la première passe sont archivés dans `resultats_v1/` et ne sont pas modifiés. Seules deux choses changent ; tout le reste du plan est identique.

1. **Plancher.** Il ne porte plus sur le nombre de réussites : il porte sur le score lui-même (score réfléchi, Page 1954). Les opérations sont détaillées dans `../REGLE.md`, section « Amendements », A1 :
   - réussite : L = max(L − b, ln B − a) ;
   - erreur à enjeu faible : L + a, puis descente d'un seul palier si L > ln B ;
   - erreur à enjeu moyen ou fort : L = max(L, 0) + a, retour au palier 1, épreuve ;
   - changement de modèle, ou droits élargis : L = 0 ;
   - consigne modifiée : L divisé par deux si L < 0.

   Un score par type et par palier visé.
2. **Changement de modèle.** Les erreurs à enjeu faible disparaissent. Celles à enjeu moyen ou fort deviennent des épreuves, et une épreuve réussie efface son erreur.

**Marges.** Le verdict de dégâts est calculé pour chaque niveau d'enjeu sur une grille fine de marges (0 ; 0,01 ; 0,02 ; 0,05 ; 0,1 ; 0,2 ; 0,5 ; 1 pour 100 actions), pour pouvoir lire le résultat aux marges qu'Otsoa fixera à l'aveugle.

**Pas d'autre correction.** Si la règle corrigée échoue encore, l'échec est rapporté.
