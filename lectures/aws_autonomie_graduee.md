> **Corrections après relecture indépendante (4 novembre, détail dans `_verification.md`)** : mineur : la rétrogradation ramène au plancher de la plage (91), pas à 90.

# Fiche de lecture : AWS, autonomie graduée

## Référence
- **Auteurs** : Dev Arora, Meera Kezhukoot, Sathish Kumar Prabakaran (AWS ; techniciens et architectes, pas chercheurs).
- **Titre** : « Closing the AI agent trust gap with graduated autonomy », AWS Architecture Blog, 26 août 2026.
- **Lien** : https://aws.amazon.com/blogs/architecture/closing-the-ai-agent-trust-gap-with-graduated-autonomy/
- **Accès** : texte intégral lu (page HTML récupérée par téléchargement direct, texte extrait, lu en entier). Les figures (schéma « closed loop ») n'ont pas été vues. L'article est court (environ 1 700 mots) : un patron d'architecture, sans mesure ni jeu de données.

## Ce que dit la source
Les sections sont celles de l'article (pas de pagination).

**Principe** (intro, « The agent trust gap »). L'écart entre ce qu'un agent peut faire et ce qu'on lui confie s'appelle le « trust gap ». Les droits d'accès classiques sont donnés une fois, alors qu'un même agent peut être juste le lundi et faux le mardi « après un changement de consigne ou de modèle ». Trois capacités manquent aux journaux d'API : visibilité, **provenance de décision** (quel signal, quelles alternatives, quelle confiance) et **réversibilité** (capturer l'état avant l'action pour pouvoir récupérer).

**Six couches**, chacune « remplaçable » (poids, seuils, signaux = configuration) : moteur de score, système de paliers, couche pré-exécution, couche d'application (enforcement), couche post-exécution, barrière de livraison.

**Score** (« The scoring engine »). Note de 0 à 100 par agent, sur une **fenêtre glissante de 50 actions**, cinq dimensions : exactitude 25 %, sécurité 20 %, constance 20 %, conformité 20 % (qualité du raisonnement avant d'agir, respect des garde-fous), efficacité 15 %. La sécurité est un **plancher indépendant** : une bonne note ailleurs ne la compense pas. La valeur du plancher n'est pas donnée.

**Paliers** (« The tier system »). Tout agent démarre à T1, « quelle que soit sa performance aux tests ».
- T1 Probation, score 0-40 : lecture et liste seulement, deux outils visibles.
- T2 Supervisé, 41-70 : écritures ; un humain approuve le risque élevé.
- T3 Fiable, 71-90 : exécuter et modifier ; anomalies signalées pour revue.
- T4 Autonome, 91-100 : accès complet ; audit après coup seulement.

**Trois règles de transition**. (1) Promotion : le score doit rester au-dessus du seuil **pendant toute la fenêtre**. (2) Rétrogradation **immédiate** si la sécurité passe sous son plancher ou si une injection est détectée. (3) **Hystérésis** : pour monter dans un palier il faut 5 points au-dessus du bas de sa plage ; on descend dès le bas de la plage. Ma lecture : monter à T4 demande donc 96 tenus sur 50 actions, descendre se fait à 90. L'article ne dit pas si la rétrogradation va d'un cran ou jusqu'à T1.

**État de confiance** : un enregistrement courant plus une série temporelle par agent, dans DynamoDB ; chaque appel relit le palier.

**Pré-exécution** (six signaux, tous en code dans le processus de l'agent) : détection d'injection (une correspondance = blocage et pénalité), cibles sensibles (clés, jetons), outils dangereux, cohérence de comportement face à l'historique d'usage d'outils, **calibrage de confiance** (la confiance annoncée est comparée à l'exactitude passée ; les échecs trop sûrs d'eux sont **pénalisés deux fois plus**), qualité du raisonnement. Ce sont des filtres rapides, « pas une défense complète ».

**Application** (« The enforcement layer »). Hors du processus de l'agent : une passerelle route chaque appel d'outil vers des politiques Cedar, **l'interdiction l'emporte toujours**, refus par défaut. Le palier se traduit en politique : en Probation une interdiction bloque écriture, exécution, suppression ; promotion = retrait de l'interdiction ; rétrogradation = remise en place. L'agent ne voit même pas les outils interdits.

**Post-exécution**. Après chaque appel, huit signaux (calibrage, dérive, **dérogations humaines**, nouvelles tentatives...). Chaque action produit un enregistrement Think, Plan, Act, Observe, Score. Les enregistrements Plan et Act gardent l'état d'avant l'action, ce qui rend la récupération possible. Une requête de provenance explique une décision en langage clair.

**Barrière de livraison** (« The delivery gate »). **Chaque changement de consigne, de configuration ou de définition d'outil** déclenche une exécution de pipeline : le candidat passe en préproduction contre des cas de référence, dont des cas adverses (injection, exfiltration). **Un seul appel d'outil non autorisé dans un cas adverse fait échouer la barrière.** La version qui passe devient la « dernière version stable connue ».

**Surveillance en production** (« Production monitoring and recovery »). Des cas-pièges synthétiques (« honeypots ») à résultat attendu connu sont injectés dans une petite part du trafic ; on valide la **trajectoire d'appels d'outils** (outils attendus, ordre, aucun interdit), pas le texte. Leurs résultats restent hors des métriques de production. Si la sécurité passe sous le plancher : rétrogradation **et** redéploiement de la dernière version stable.

**Jugement de l'opérateur**. Le taux glissant de rejets des actions proposées par les opérateurs **plafonne** la mesure de sécurité : 30 % de rejets plafonnent la sécurité à 70. **Arrêt d'urgence** : une politique « tout refuser » appliquée en quelques secondes sans redéploiement. **Chaîne de délégation** : le palier effectif d'une action déléguée est le **minimum** de la chaîne.

**Conclusion** : poids et bornes des deux tableaux sont un « modèle de départ » pour un agent. Aucun résultat de terrain.

## Ce que ça change pour notre règle
Propositions, rien de décidé.
- **Reprendre l'hystérésis** : seuil de montée plus haut que seuil de descente. Notre principe « se gagne lentement, se perd vite » y est déjà, mais on peut le fixer par une marge explicite.
- **Reprendre le plancher indépendant** : pour un type d'action à enjeu, une erreur grave ne se compense pas par des réussites. Chez nous : pas de moyenne pondérée entre types d'action.
- **Reprendre la barrière de livraison** comme équivalent de nos remises à zéro : tout changement de fiche, de modèle ou d'outil rend le candidat à re-tester avant de retrouver son niveau. Différence à garder : AWS bloque la mise en production mais **ne dit pas ce que devient le score ni le palier** après un changement. Notre règle (erreurs conservées, réussites escomptées ou annulées) comble ce silence.
- **Reprendre le minimum sur la chaîne de délégation** : [company] qui lance une session Claude Code ou un sous-agent ne doit pas dépasser son propre niveau pour ce type d'action.
- **Reprendre le refus par défaut hors du processus de l'agent** : c'est déjà le rôle des garde-fous (702 blocages). Cela confirme qu'un blocage est une barrière, pas une preuve de sûreté de l'agent.
- **Reprendre les cas-pièges validés sur la trajectoire d'outils** (pas sur le texte) : bonne forme des « épreuves de vigilance » évoquées dans le rapport, pour mesurer l'humain comme l'agent.
- **Reprendre le schéma d'enregistrement** Think / Plan / Act / Observe / Score et l'état avant l'action comme champs minimaux du registre. C'est ce qui manque aux journaux de [company] (61 validations sur 83 seulement retrouvent leur demande).
- **Éviter le score composite unique par agent** : il écrase les types d'action, ignore gravité et réversibilité (AWS ne les croise pas avec les paliers ; les paliers sont des classes d'outils : lire, écrire, exécuter, supprimer). Notre niveau par type d'action pondéré par gravité et réversibilité est un vrai dépassement.
- **Éviter les poids (25/20/20/20/15) et les bornes (40/70/90)** : aucune source ni mesure, présentés comme point de départ. Nos seuils sont aussi des hypothèses, mais il faut l'écrire.
- **Éviter les signaux évalués par modèle sans validation** (qualité du raisonnement, exactitude « contre résultat attendu ») : nous n'avons de vérité que les accords et refus humains.
- **Point de vigilance sur le taux de rejets** : AWS plafonne la sécurité par le taux de rejets. Avec 1 refus sur 83 (ou 0), ce plafond ne dit presque rien ; il ne vaut que si la relecture humaine est réelle (cf. délai médian de 8 secondes).
- **Distinguer ce qu'AWS ne distingue pas** : rien sur l'origine d'un échec (agent, outillage, environnement). Notre principe « seules les erreurs de l'agent comptent » est absent de leur modèle.
- **Un doute signalé** : AWS pénalise la fausse assurance, ne dit rien sur le coût d'un doute exprimé. Notre principe (doute gratuit) va dans le sens du calibrage, à garder tel quel.
- **Place du protocole ouvert** : le patron est lié à Bedrock AgentCore, Cedar, DynamoDB, CodePipeline. Il n'y a ni format de dossier portable, ni signature, ni vérification par un tiers.

## Ce que ça corrige dans le rapport
- **Faux** : le tableau du rapport donne « Réévaluation après changement de modèle ou d'outils : absente, sauf les certificats de Feng ». AWS a une barrière de livraison déclenchée par tout changement de consigne, configuration ou définition d'outil, avec cas adverses (section « The delivery gate »). Elle ne traite pas la réévaluation du niveau lui-même, mais l'affirmation « absente » est fausse pour AWS.
- **Imprécis** : « Exigence de réversibilité avant élargissement : absente ». AWS fait de la réversibilité l'une des trois capacités centrales et capture l'état avant l'action ; mais ce n'est pas une condition de promotion. Écrire : « présente comme capacité de journalisation, absente comme condition d'élargissement ».
- **Imprécis** : « la rétrogradation est immédiate en cas de violation de sécurité » : le texte dit « quand la sécurité passe sous son plancher (valeur non donnée) ou qu'une injection est détectée ».
- **Incomplet** : le rapport ne cite ni le plafonnement de la sécurité par le taux de rejets des opérateurs, ni les cas-pièges en production, ni le minimum sur la chaîne de délégation, ni le retour à la dernière version stable, ni la pénalité double de la fausse assurance. Ces cinq mécanismes sont directement utiles.
- **Imprécis** : « Niveaux par classe d'action : partiel » : chez AWS le palier est **par agent** (un score unique), les classes d'actions n'entrent que comme classes d'outils autorisées par palier.
- **Exact** : quatre paliers, 0-100, fenêtre de 50 actions, marge de 5 points, arrêt d'urgence par politique d'interdiction, registre, « point de départ », aucun résultat de terrain.
- **Précision utile** : « promotion sur preuves » est en fait une promotion sur un score composite dont la plupart des signaux sont des appréciations automatiques ; la preuve n'est pas portable.

## Questions ouvertes
- Valeur du plancher de sécurité ? Poids des violations dans le score ?
- Après un changement (version qui passe la barrière), le score et le palier sont-ils conservés, remis à T1 ou re-mesurés ? Le texte est muet.
- Rétrogradation d'un cran ou jusqu'à T1 ? Combien d'actions pour remonter ?
- Comment le score « exactitude » est obtenu sans vérité terrain en production ?
- Les mêmes 50 actions valent-elles pour tous les types d'action, quelle que soit leur gravité ?
- Aucune donnée : combien d'agents, de temps, de fausses promotions ? À surveiller (suites ou preuve de terrain publiées par AWS).
