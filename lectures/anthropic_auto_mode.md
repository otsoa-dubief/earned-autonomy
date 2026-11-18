# Anthropic, « How we built Claude Code auto mode » (fiche de lecture)

## Référence
- John Hughes (équipe Engineering). « How we built Claude Code auto mode: a safer way to skip permissions », publié le 25 mars 2026. https://www.anthropic.com/engineering/claude-code-auto-mode
- **Accès : texte intégral lu** (page entière récupérée en HTML brut : toutes les sections, légendes de figures et tableau de résultats). Les images des figures ne sont pas lues, seulement leurs légendes. Pas d'annexe technique liée dans la page.
- Note : le tableau des résultats a été lu tel quel dans le texte ; les valeurs sont celles de la page (une lecture par un outil de résumé avait donné les mêmes).

## Ce que dit la source

### Contexte et chiffre de départ (section « How it works », introduction)
- Par défaut, Claude Code demande l'approbation avant d'exécuter des commandes ou de modifier des fichiers. Cela produit la « fatigue d'approbation », où l'on cesse de lire ce qu'on approuve.
- Citation : « in practice users accept 93% of them anyway ». Le **93 %** désigne la part des demandes d'approbation manuelle que les utilisateurs acceptent. La page ne dit ni la période, ni la population, ni le nombre de demandes, ni la méthode de calcul.
- Alternatives présentées : bac à sable (sûr, mais lourd à maintenir) ou `--dangerously-skip-permissions` (aucune protection). Le mode automatique est le compromis.
- Journal interne d'incidents : suppression de branches git distantes, envoi d'un jeton GitHub sur une grappe interne, tentative de migration sur une base de production. Toutes ces causes sont du « trop d'initiative », renvoyées au System Card d'Opus 4.6 (§6.2.1 et §6.2.3.3).

### Architecture
- **Couche d'entrée** : une sonde serveur d'injection de prompt analyse les sorties d'outils avant qu'elles entrent dans le contexte et ajoute un avertissement si le contenu ressemble à un détournement.
- **Couche de sortie** : un classifieur de transcription (Sonnet 4.6) évalue chaque action avant exécution. Deux étages : filtre rapide à un jeton (oui = bloquer), tuné pour bloquer en cas de doute ; puis raisonnement en chaîne seulement si le premier étage signale. Le classifieur ne voit que les messages de l'utilisateur et les appels d'outils (texte de l'assistant et résultats d'outils retirés) : il est « aveugle au raisonnement ».
- **Trois niveaux de décision** : (1) liste blanche d'outils en lecture seule et règles de l'utilisateur ; à l'entrée en mode auto, les règles à exécution de code arbitraire sont retirées (shell large, interpréteurs, gestionnaires de paquets) ; (2) écritures dans le projet sans classifieur (révisables par contrôle de version) ; (3) tout le reste passe par le classifieur (shell, web, intégrations externes, sous-agents, système de fichiers hors projet).
- **Modèle de menace** : excès d'initiative, erreurs honnêtes (mauvaise idée de l'étendue), injection de prompt, modèle désaligné (« pas observé en pratique »). Le classifieur est réglé sur les deux premiers.
- **Règles** : plus de vingt règles de blocage en quatre groupes (détruire ou exfiltrer ; dégrader la sécurité ; franchir une frontière de confiance ; contourner la relecture ou affecter les autres), des exceptions étroites, un « environnement » de confiance (par défaut, seul le dépôt git courant). Principe : on juge l'effet réel de l'action, pas le texte de la commande. Tout ce que l'agent choisit seul est non autorisé tant que l'utilisateur ne l'a pas dit ; « nettoie mes branches » n'autorise pas une suppression en lot.
- Sous-agents : classifieur à la délégation (peut refuser) et au retour (avertit seulement).

### Chiffres exacts avec leur définition (section « Results »)
Trois jeux de données :
- **Trafic interne réel** n = 10 000 : appels d'outil réels d'employés d'Anthropic.
- **Actions « trop zélées » réelles** n = 52 : issues de sessions où un employé a refusé l'action ou où elle a été signalée après coup.
- **Exfiltration synthétique** n = 1 000 : POST de données sensibles, push vers dépôts non fiables, identifiants dans les URL, souvent obfusqués.

Définitions : **taux de faux négatifs (FNR)** = part des actions dangereuses que le classifieur laisse passer ; **taux de faux positifs (FPR)** = part des actions bénignes qu'il bloque.

| | Trafic réel (FPR) | Zélées réelles (FNR) | Exfiltration synthétique (FNR) |
|---|---|---|---|
| Étage 1 seul | 8,5 % | 6,6 % | 1,8 % |
| Pipeline complet (déployé) | **0,4 %** | **17 %** | **5,7 %** |

- Le passage à l'étage 2 fait baisser le FPR de 8,5 % à 0,4 % « au prix d'une partie du rappel ».
- Le **17 %** (n = 52) est « le chiffre honnête » selon les auteurs. Il est calculé sur un petit échantillon ; aucun intervalle de confiance n'est donné. À titre indicatif (calcul de l'équipe, intervalle exact de Clopper-Pearson, 17 % de 52 ≈ 9 cas) : environ 8 % à 30 %. À vérifier si on veut le citer.
- Dans la majorité des ratés examinés, le classifieur voit bien le danger (force-push, suppression) mais se trompe sur le point de savoir si un signal de consentement dans la session couvre l'étendue de l'action. Exemples du texte : « nettoie la PR » ne nomme pas le force-push ; une approbation antérieure d'une action semblable n'est pas un usage établi. Les auteurs disent avoir essayé d'ajuster le prompt « sans trouver de correctif dont le coût soit inférieur au gain ».
- Comparaison faite par les auteurs : par rapport à `--dangerously-skip-permissions`, c'est une nette amélioration ; par rapport à une approbation manuelle attentive de chaque action, c'est « arguably a regression ». Le mode auto « n'est pas un remplaçant direct d'une relecture humaine attentive pour l'infrastructure à enjeu élevé ».

### Règle de retour à l'humain (section « Deny-and-continue »)
- Un refus du classifieur revient à l'agent comme résultat d'outil avec la consigne de chercher un chemin plus sûr sans contourner la limite.
- Citation : « If a session accumulates 3 consecutive denials or 20 total, we stop the model and escalate to the human. »
- En mode sans interface (`claude -p`), le processus est terminé faute d'humain.
- « Refus » = refus du **classifieur**, pas de l'humain. Les seuils 3 et 20 sont donnés sans justification chiffrée.
- Justification : une borne contre un agent compromis ou trop zélé qui insiste. Un faux positif coûte un essai de plus (l'agent trouve en général une autre voie).

### Choix de conception avec leur coût (section « Design decisions »)
- Retirer le texte de l'assistant : l'agent ne peut pas persuader le classifieur. Inclure texte et résultats d'outils a **dégradé** la performance sur le jeu « excès d'initiative ». Une variante « appels d'outils seuls » avait le FNR le plus bas mais perdait l'ancrage sur l'intention de l'utilisateur et bloquait des actions demandées.
- Retirer les résultats d'outils : défense principale contre l'injection. Coût : perte de provenance (le classifieur ne sait pas si l'identifiant « job abc123 » vient d'une requête ou a été inventé).
- Les deux couches se renforcent : une injection doit passer la sonde puis faire émettre un appel que le classifieur juge sûr et conforme.
- Blocage d'actions et surveillance de la chaîne de raisonnement sont complémentaires.

### Limites reconnues
- 17 % de FNR sur les actions trop zélées réelles (section Results).
- Jeu « zélé » petit parce qu'il faut qu'un agent tente quelque chose de dangereux dans une vraie session, capturé et étiqueté.
- Perte de provenance par choix de conception (section Design decisions).
- Risque résiduel : « stay aware of residual risk » (section What's next).
- Données : trafic interne d'employés Anthropic, un seul produit, un seul fournisseur. Les auteurs prévoient d'élargir le jeu zélé.

## Ce que ça change pour notre règle (propositions, rien de décidé)
1. **Journaliser chaque blocage avec son motif de règle**, et compter séparément les blocages consécutifs et le total par session. La règle d'Anthropic (3 de suite, 20 au total) est un modèle prêt à tester sur nos 702 blocages : combien de sessions auraient été arrêtées ?
2. **Refus automatique et refus humain sont deux compteurs différents** : l'article n'utilise que le premier comme déclencheur. Nous avons 1 refus humain sur 83, donc pas de signal ; les blocages automatiques sont le seul signal.
3. **Traiter un blocage comme une erreur pour son type d'action** (déjà dans notre règle) est cohérent avec leur motif « attaque bloquée = tentative », mais l'article distingue FP (action bénigne bloquée) et FN. Prévoir de journaliser aussi la **nature du blocage** (vrai danger / faux positif), au moins sur un échantillon relu à la main ; sans cela un blocage de bonne foi compte comme erreur de l'agent.
4. **Journaliser le « signal de consentement »** : la cause principale des ratés d'Anthropic est un accord antérieur qui ne couvre pas la portée de l'action. Pour nos accords humains, enregistrer ce que l'accord nommait (action, cible, portée) et si l'action exécutée correspondait.
5. **Qualité de la relecture** : l'article donne l'argument inverse de notre biais : 93 % d'acceptation est présenté comme un symptôme de fatigue. Notre médiane de 8 secondes plaide pour traiter une validation rapide comme un signal faible, et pour garder un échantillon de vérification.
6. **Retour à l'humain** : tester des seuils de type « N blocages consécutifs, M au total par session », et un retour immédiat pour les règles du groupe « détruire ou exfiltrer » (irréversible).
7. **Garde-fou sur la configuration** : le groupe « dégrader la sécurité » inclut la modification de la propre configuration de permissions de l'agent. À reprendre comme type d'action à niveau fixe.
8. **Retirer les règles larges** à l'entrée dans un palier plus autonome : l'article le fait pour les interpréteurs et le shell, car sinon le classifieur ne voit jamais les commandes les plus dangereuses.

## Ce que ça corrige dans le rapport
- **93 %** : exact, mais la source ne donne ni période, ni population, ni effectif. Le rapport compare 93 % à notre 98,8 % ; cette comparaison est indicative seulement (dénominateurs et populations inconnus). Le rapport écrit que cette approbation « mène à la fatigue d'approbation » : conforme au texte, mais c'est une affirmation du billet, pas un résultat mesuré.
- **Rapport et faux positifs 0,4 % / faux négatifs 17 % / 0,8 % / 3 refus ou 20** : **aucun de ces chiffres n'apparaît dans le corps du rapport relu** (le rapport ne cite que 93 % et 20 % à 40 % ; je n'ai trouvé aucun des autres). Vérifiés dans la source : FPR 0,4 % (n = 10 000, trafic interne réel), FNR 17 % (n = 52 actions réelles trop zélées), règle 3 consécutifs ou 20 au total, avec les définitions ci-dessus. Le chiffre 0,8 % vient de l'autre source (voir `anthropic_mesurer_autonomie.md`). Si la demande les place dans le rapport, ils sont à ajouter, pas à corriger.
- **À ajouter** : les 17 % sont sur 52 cas seulement ; le rappel dépend du jeu (5,7 % sur exfiltration synthétique, 6,6 % pour l'étage 1) ; la règle des 3 / 20 compte des **refus du classifieur**, pas des refus humains.
- Le rapport dit que le mode auto est une mesure d'usage ; en réalité c'est un billet d'ingénierie sur un produit, évalué sur du trafic interne, sans données d'usage externes.

## Questions ouvertes
- D'où vient le 93 % (période, nombre de demandes, population) ?
- Quel intervalle de confiance sur 17 % de 52 ? Quels types d'actions dans ces 52 cas, et lesquels sont ratés ?
- Pourquoi 3 consécutifs et 20 au total ? Aucune donnée sur la fréquence d'atteinte de ces seuils en pratique.
- Le classifieur est-il stable d'une version de modèle à l'autre ? Le billet ne dit pas ce qui est retesté à chaque changement de modèle (point central pour notre règle de remise à zéro).
- Quelle part des blocages d'un agent sont de vrais dangers plutôt que des faux positifs, dans notre propre jeu de 702 blocages ?
