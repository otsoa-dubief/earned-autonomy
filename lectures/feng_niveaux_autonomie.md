> **Corrections après relecture indépendante (4 novembre, détail dans `_verification.md`)** : le PDF fait 16 pages et le Tableau 1 est lisible (page 16), contrairement à ce que dit la fiche.

# Fiche de lecture : Feng, McDonald, Zhang, niveaux d'autonomie

## Référence
- **Auteurs** : K. J. Kevin Feng, David W. McDonald, Amy X. Zhang (University of Washington). Publié aussi par le Knight First Amendment Institute.
- **Titre** : « Levels of Autonomy for AI Agents », arXiv 2506.12469 [cs.HC].
- **Dates** : v1 le 14 juin 2025 ; **v2 le 28 juillet 2025** (dernière version, celle lue). Aucune v3 à la date du 4 novembre 2026 (page de résumé arXiv vérifiée).
- **Lien** : https://arxiv.org/abs/2506.12469 (PDF https://arxiv.org/pdf/2506.12469)
- **Accès** : texte intégral lu (PDF v2, 14 pages, texte extrait ; sections 1 à 6, hors bibliographie). Le Tableau 1 (cadre complet, colonne « Characteristics ») n'apparaît pas dans le texte extrait : il n'a pas été lu en tant que tel ; j'ai lu les descriptions de chaque niveau dans la section 3, qui le détaillent. La version HTML a été récupérée mais le PDF a servi de lecture.

C'est un **essai de position** (« essay »), pas une étude : pas de données, pas d'expérience, pas de code.

## Ce que dit la source
**Thèse** (résumé, §1, p.1-2). L'autonomie est une **décision de conception**, séparée de la capacité et de l'environnement. Définition : « l'étendue dans laquelle un agent est conçu pour agir sans implication de l'utilisateur ». Elle est aussi séparée de l'**agency** (la capacité d'agir via des outils ; §2.2 p.3). Un agent très capable peut être conçu à faible autonomie.

**Cinq niveaux, définis par le rôle de l'utilisateur** (§3, p.4-9 ; Fig. 1 p.1). L'ordre est sans ambiguïté dans le texte :
- **L1 opérateur** : l'utilisateur dirige, l'agent aide sur demande ; il n'agit pas sans être invoqué (p.4-5).
- **L2 collaborateur** : plan et exécution partagés, délégation dans les deux sens, l'utilisateur peut reprendre la main à tout moment (p.5-6).
- **L3 consultant** : l'agent prend l'initiative et consulte pour avis et préférences ; l'utilisateur ne peut plus éditer directement ni reprendre la main, seulement mettre en pause et demander des changements (p.6-7).
- **L4 approbateur** : l'utilisateur n'intervient que sur blocage (échec, identifiants, **validation d'actions conséquentes**) ; il peut préciser à l'avance quelles actions exigent son accord (p.7-8).
- **L5 observateur** : autonomie complète ; journaux d'activité lisibles, **seul contrôle : un interrupteur d'arrêt d'urgence** (p.8).
Chaque niveau se termine par des questions ouvertes de conception, sans réponse. Pour L4 : comment éviter l'approbation-tampon (« rubber stamping »), comment éviter qu'un agent mal aligné profite du désengagement de l'utilisateur pour obtenir des approbations risquées, comment l'agent sait quand demander (p.8). Pour L5 : quels outils de surveillance, comment concevoir l'interrupteur (p.8). Les auteurs disent qu'ils sont **descriptifs, pas prescriptifs** (p.4) et que L5 ne se justifie guère hors environnement fermé ou tâche trop complexe pour l'humain (p.8).

**Certificats d'autonomie** (§4, p.9-10). Un certificat est un document numérique qui fixe le **niveau maximal** auquel un agent peut opérer, pour un ensemble donné de spécifications techniques (modèle, consignes, outils) **et** un environnement. Délivré par un **tiers** (agence publique, ONG comme METR, ou entreprise). Pour l'obtenir, le développeur fournit (1) un agent déployé en privé pour test et (2) un **« dossier d'autonomie » (autonomy case)**, argument fondé sur des preuves, analogue à un « dossier de sûreté » (safety case) : objectifs, arguments, preuves, périmètre. Le tiers fait des évaluations privées, délivre ou renvoie (p.10, Fig. 2).
**Renouvellement** (p.10) : un changement des spécifications **ou** de l'environnement « peut altérer » le comportement et donc **invalider** le certificat (exemples : un nouvel outil touchant une base de données ; passage d'un éditeur de documents à un tableau blanc). Le développeur doit refaire la procédure avec un agent et un dossier mis à jour ; elle peut être **accélérée si le changement est mineur** et le dossier facile à réviser vu l'approbation de la version précédente. Le certificat est lié à l'agent « stocké avec ses métadonnées » pour être lu par d'autres agents (usages : évaluation du risque, cadres de sûreté, systèmes multi-agents ; §4.1 p.9).

**Évaluer l'autonomie : évaluation assistée** (§5, p.11-12). Idée : mesurer **combien d'aide humaine** l'agent requiert pour dépasser un seuil de réussite T, plutôt que mesurer sa seule capacité. Procédure : (1) lancer sans aide ; si T est atteint sur toutes les tâches, L5 ; (2) sinon, augmenter l'implication (approbations et refus = L4, puis L3...) jusqu'à T ; (3) classer le niveau à partir du journal d'implication de l'utilisateur. Coût : jusqu'à cinq tours pour classer un agent L1 ; on peut commencer au niveau supposé. T n'est pas fixé.

**Ce que l'article ne contient pas** : aucune règle de promotion ou de retrait en cours d'usage, aucun seuil, aucune fenêtre, aucun registre, aucune durée de validité, aucune procédure de révocation (hors invalidation lors d'un changement), aucun niveau par type d'action (le niveau est par agent, avec la nuance de L4 « l'utilisateur précise les actions qui exigent son accord »).

## Ce que ça change pour notre règle
- **Reprendre la séparation autonomie / capacité / périmètre d'outils.** Elle clarifie notre objet : nous mesurons le niveau d'autonomie **accordé** à un type d'action, pas la compétence en général ni l'étendue des droits.
- **Reprendre l'idée de « dossier » (autonomy case)** : niveau, périmètre exact (spécifications + environnement), preuves, argument. C'est la forme la plus proche de notre « dossier de preuves ouvert et portable », mais chez eux la preuve est une **évaluation préalable en laboratoire par un tiers**, pas un historique de terrain. Notre apport : le dossier est **alimenté par l'historique d'usage**.
- **Reprendre le lien niveau-certificat-configuration** : le niveau est valable pour un triplet (modèle, consignes, outils) et un environnement. Une remise à zéro à chaque changement est cohérente, mais notre règle est plus fine (erreurs conservées, réussites escomptées) et eux plus binaire (certificat valide ou non, renouvellement éventuellement accéléré).
- **Reprendre la notion de niveau maximal** : le certificat fixe un plafond, pas un état. Notre règle peut distinguer plafond (permis) et niveau courant (gagné).
- **Reprendre la grille des rôles humains comme vocabulaire des niveaux**, par exemple pour nommer ce que fait l'humain à chaque palier (approuve, est consulté, est informé après coup). Les cinq rôles sont utiles pour décrire l'état actuel de [company] (surtout L4 : approbateur sur blocage, avec une liste d'actions à approuver).
- **Reprendre les deux risques de L4** comme exigences : mesurer l'approbation-tampon, et se protéger d'un agent qui profite du désengagement. Les auteurs les laissent en questions ouvertes ; c'est exactement là que le rejeu a quelque chose à apporter (délai médian de 8 s).
- **Reprendre l'interrupteur d'arrêt** comme seul contrôle garanti au niveau le plus haut.
- **Reprendre l'évaluation assistée avec prudence** : l'idée de déduire le niveau du **journal d'implication humaine** est exactement notre rejeu (les validations deviennent la mesure de l'implication). Mais leur seuil T est un taux de réussite de tâche, pas une gravité d'erreur ; il faut garder notre pondération.
- **Dépasser** : promotion et retrait **en continu** sur preuves de terrain, **par type d'action**, avec pondération gravité et réversibilité ; durée de validité et réévaluation sur événement ; révocation. Rien de tout cela n'est dans l'article, donc on ne réinvente rien en l'ajoutant.
- **Éviter** : un tiers certificateur obligatoire. Il est coûteux et absent pour une petite organisation ; nous visons une vérification possible par un tiers, pas dépendante de lui.
- **Éviter** de nommer nos paliers L1 à L5 sans les redéfinir : les niveaux de Feng sont par agent et par rôle de l'utilisateur, les nôtres seraient par type d'action. Dire la correspondance si on la garde.

## Ce que ça corrige dans le rapport
- **Résolu** : « L'ordre exact des cinq niveaux de Feng et al. diffère entre les sources ». Dans le texte original l'ordre est : L1 opérateur, L2 collaborateur, L3 consultant, L4 approbateur, L5 observateur (Fig. 1, p.1 ; §3). Cette réserve peut être retirée.
- **Exact mais incomplet** : « certificats d'autonomie délivrés par un tiers, invalidés si les spécifications ou l'environnement changent ». Précisions : le certificat fixe un niveau **maximal** ; il est fondé sur un **dossier d'autonomie** évalué en privé **avant** déploiement ; l'invalidation est « possible » (un changement « peut » altérer le comportement) ; le **renouvellement peut être accéléré** pour un changement mineur (p.10). Le rapport ne dit pas que ce sont des preuves de laboratoire, pas de terrain.
- **Exact** : « proposition sans spécification ni code ». Je confirme : essai de position, aucune donnée, ni format, ni algorithme.
- **À nuancer** : le tableau du rapport crédite Feng pour « réévaluation après changement ». Oui, mais seulement comme principe (p.10), sans critère ni seuil ; et c'est une **recertification totale**, pas une pondération des preuves passées.
- **Incomplet** : le rapport n'indique pas que l'article place l'**approbation-tampon** et l'**exploitation du désengagement par l'agent** parmi ses questions ouvertes à L4 (p.8), ni l'évaluation assistée (§5). Les deux touchent directement à nos limites connues.
- **Imprécis** : « cinq niveaux définis par le rôle de l'humain » : exact, mais le niveau est **par agent** et **choisi par conception**, il n'est pas gagné par historique.

## Questions ouvertes
- Existe-t-il une suite (autre version, implémentation, bureau de certification, METR ou autre) depuis juillet 2025 ? À chercher à part ; non vérifié ici.
- Le Tableau 1 complet (colonnes de contrôle et de caractéristiques) devrait être relu dans le PDF pour citer exactement les mécanismes de contrôle par niveau.
- Comment passer d'un niveau par agent à un niveau par type d'action sans perdre la signification des rôles ?
- Quel seuil T, quelle gravité d'erreur dans l'évaluation assistée ?
- Un certificat « accéléré » après un changement mineur : qui juge qu'un changement est mineur ? C'est la question centrale de notre règle de remise à zéro.
