# Audit indépendant du travail du 10 au 14 novembre 2026

Relecteur : Claude (Fable 5.2), instance séparée, 14/11/2026. Dépôt lu à HEAD `1d24f6a`.

## Périmètre et méthode

- Lu : `JOURNAL_CHANGEMENTS.md` (l. 53 à 59), `SUIVI.md` (l. 350 à 386), `LANCEMENT_VAGUES.md`, les quatre scripts de `outils/`, le code figé de `banc/relecture/`, `banc/tirage/tirage_public.py`, `gel/manifeste_verdicts.py`, `simulation/rejeu/bout_en_bout.py` (options et contrôles d'entrée seulement), le plan (2.5, 3.2 à 3.4, 4.3 à 4.7, 5.2, 5.14 point 0, 1.4), `article/brouillon.md` en entier, le paquet `depots/2026-11-14_gel_verdicts/`.
- Du manifeste des verdicts : seulement les chemins et les comptes de lignes, jamais les empreintes pour en tirer un contenu.
- **Non ouvert** : `donnees/`, `pilote/`, `data/`, `experience/`, `externe/`, `simulation/rejeu/sorties_pilote/`, aucune partie, action, décision, fiche, preuve de retrait ni réponse. Conséquence : tout ce qui dépend du contenu de ces fichiers est marqué « non vérifié par moi » et renvoyé à l'équipe comme contrôle à faire.
- Rien modifié, rien lancé d'autre que `git log`, `git diff --stat`, `shasum`, `unzip -l` et un calcul de dates.

Vérifié par moi (recalculé, pas repris du texte) :
- `git diff --stat gel-2026-11-09 HEAD -- banc simulation gel REGLE.md PLAN_EXPERIENCE.md` est vide : le périmètre figé suivi par git n'a pas bougé.
- SHA-256 de `tirage_public.py` (`6970dfd9…e027`), de `paires.py` (`d218d705…1081`), de `gel/MANIFESTE_SHA256.txt` (`88715a0d…9600`) : identiques au texte déposé ; la dernière figure bien dans le dépôt du 09/11.
- SHA-256 du zip (`10c40d40…ff1a`), des trois fichiers du paquet contre `SHA256SUMS.txt`, du manifeste (`f2347d87…3c97`), 68 990 lignes.
- Heure désignée : 14/11 06:44:26,304 UTC + 72 h = 17/11 06:44:26,304 UTC ; l'adresse NIST `…/pulse/time/1794897900000` est bien 17/11 06:45:00 UTC ; le tour drand 34031501 tombe à 06:44:27 UTC. Conformes au code.
- Arithmétique de la garantie (brouillon 3.4) : juste (détail au constat 20).

Gravité : **bloquant** = à régler avant le tirage, faute de quoi le défaut devient irréparable ou l'étude attaquable sur son point central ; **important** = affaiblit une conclusion ou la crédibilité, à corriger ou à déclarer ; **mineur** = à corriger au passage.

---

## Constats

### A. Gel des verdicts, tirage, rejeu final

**1. La commande du rejeu final n'est fixée nulle part, et le code laisse des variantes. Bloquant.**
- Preuve : `simulation/rejeu/bout_en_bout.py` l. 317 (« alertes et bilan facultatifs : chaîne vide »), l. 469 à 472 (`--retirees` et `--oppositions` facultatifs), l. 494 à 504 (seuls `--dossier`, `--partage`, `--vague`, `--manifeste-verdicts` sont exigés). `controles_experience` (l. 281 à 303) vérifie que ce qui est lu est au manifeste, pas que tout ce qui doit être lu l'est.
- Conséquence : après le tirage, quatre calculs « confirmatoires » au moins passent tous les contrôles : avec ou sans `accord.json` (donc avec ou sans les quatre décisions d'Otsoa qui l'emportent), avec ou sans `--oppositions` (donc WorkBench 179 gardée ou retirée). Le garde-fou « une seule fois » ne tient qu'à un dossier de sortie vide (l. 300) : un autre `--sortie` ouvre un autre journal. Le plan dit lequel est le bon (4.4, 4.5), mais rien de daté ne l'écrit. `SUIVI.md` l. 385 donne la commande du tirage, pas celle du rejeu.
- Correction : écrire avant le 17/11 06:45 UTC la commande complète du rejeu final (tous les arguments, chemins relatifs à `experience/`, tels qu'au manifeste), la commiter, et l'ancrer hors de la machine (fichier ajouté au projet OSF `bd4g5`, ou empreinte du commit envoyée à un tiers). Y écrire aussi : un seul lancement ; tout lancement de plus est déclaré avec son journal.

**2. « Horodatage tel qu'OSF l'affiche » : deux lectures, deux impulsions. Bloquant (se règle en dix minutes).**
- Preuve : texte déposé, `resume_osf_texte.txt` l. 13 (« submission timestamp of this registration, as shown by OSF ») ; `FICHE_DEPOT.md` l. 64 (06:44:26.304408 UTC, valeur de l'API) ; `tirage_public.py` l. 186 à 188 et 217 (`_plafond_minute`).
- Si l'on lit l'heure à la minute, comme l'interface d'OSF la montre (06:44), l'heure désignée est 06:44:00 pile et l'impulsion est celle de 06:44:00. Avec la valeur de l'API, c'est celle de 06:45:00. Le texte déposé ne tranche pas. `--depot` est saisi à la main (l. 411).
- La fiche (commit `c802347`) nomme déjà l'impulsion de 06:45:00, mais un commit local sans dépôt distant ne prouve pas sa date à un tiers.
- Correction : avant le tirage, écrire dans le journal et ancrer hors de la machine (même moyen qu'au constat 1) : champ retenu = `date_registered` de l'API, valeur complète, impulsion NIST de 2026-11-17T06:45:00Z, secours drand 34031501. Relire ce champ par l'API après l'approbation de l'embargo et juste avant le tirage ; s'il a changé, le déclarer et garder l'heure de soumission.

**3. `gel_plan.json` ne porte pas l'étiquette du gel et renvoie à un commit qu'aucun tiers ne peut voir. Mineur.**
- Preuve : `paquet/gel_plan.json` (`"etiquette": null`, commit `700fddb`) ; `gel/manifeste_verdicts.py` l. 65 à 71 (`git describe --exact-match` sur HEAD). Le plan 5.2 annonce « commit et étiquette du gel du plan ».
- Ce qui tient : l'empreinte `manifeste_gel` est la bonne, et c'est elle qui lie au préenregistrement. Le README du paquet décrit honnêtement le commit comme « celui où le manifeste a été écrit ».
- Intérêt réel du commit `700fddb` : il fige l'état du journal, du suivi et de `outils/` au moment du gel. Cela ne vaudra que si le dépôt est publié avec son historique intact. À dire dans l'article.

**4. Le texte déposé ne suffit pas, seul, à refaire le tirage dans un autre langage. Mineur.**
- Preuve : `resume_osf_texte.txt` l. 15, contre `tirage_public.py` l. 69 à 84. Manquent : octets gros-boutistes, champs en octets bruts (empreinte et valeur de balise décodées de l'hexadécimal), strate et identifiant en UTF-8, formule du rang, définition des strates WorkBench par fichier.
- Sans gravité : l'empreinte du script est déposée, et le script fait foi. À compléter dans l'article ou son annexe.

**5. Le manifeste couvre ce que demande le plan 5.2. Rien d'important ne manque.**
- Vu dans les chemins : les deux dossiers de vague en entier, `reussite.csv`, `actions_typees.csv`, `actions.csv`, `cout.json`, `tentatives.jsonl`, `plan_de_jeu.json` ; pour chaque vague `decisions.csv`, `alertes.json`, `accord.json`, `tirage_aveugle.json`, `journal_relecture.jsonl`, `reponses.csv`, les invites et sorties de lots ; l'audit (`audit_tirage.json`, `audit_conclusion.json`, `taches_retirees_audit.json`) ; `retraits_motif_a.json` et `oppositions_motif_a.json` ; `gel_plan.json`. Aucun `.DS_Store`.
- En plus du plan, et c'est bien : `relecture_simple.html`, `relecture_otsoa.html`, `lots/execution.jsonl`, `lots/lancement.log`, les réponses de l'audit.
- Asymétrie visible : `execution.jsonl` existe en vague 2, pas en vague 1 (voir constat 8).
- Risque pratique : `ecarts()` (`manifeste_verdicts.py` l. 114 à 116) refuse tout fichier nouveau dans un dossier lu. Un `.DS_Store` créé par le Finder d'ici le 17/11 bloquera le rejeu. Ne pas ouvrir `experience/` dans le Finder ; lancer `manifeste_verdicts.py verifier` juste avant le tirage.

**6. Dépôt soumis par Claude dans le navigateur, embargo jusqu'en 2030. Mineur, à déclarer.**
- Preuve : `FICHE_DEPOT.md` l. 3 (« À soumettre par Otsoa ») contre l. 63 (« Soumis par Claude dans le navigateur d'Orca, sur la session d'Otsoa »).
- À écrire tel quel dans l'article. Et dire que, sous embargo, l'horodatage n'est vérifiable par un tiers qu'à la levée : « anyone can redo the draw » (brouillon l. 177) n'est vrai qu'à ce moment.

### B. Relecture des alertes par Claude

**7. Le journal figé perd la raison d'une relance ; le script annonce le contraire. Important (sans effet si « 0 relance » est vrai).**
- Preuve : `banc/relecture/journal_lots.py` l. 49 à 55 : `raison` n'est écrite que si le lot était **déjà fermé**. `outils/relecture_lots.py` l. 128 à 161 relance **avant** toute fermeture, puis appelle `fermer --relance` : la ligne écrite est une « fermeture » ordinaire, sans raison. Le journal des changements (l. 59) et l'en-tête du script (l. 5 à 7) affirment que « la raison est notée à la fermeture du lot ». C'est faux pour le journal inscrit au plan (4.5, P11) ; la trace n'existe que dans `execution.jsonl`.
- Conséquence : « 0 tentative ratée, 0 relance » (`SUIVI.md` l. 376) ne se prouve pas par `journal_relecture.jsonl`. Non vérifié par moi.
- Correction : l'équipe vérifie dans `execution.jsonl` qu'aucun lot n'a de ligne `essai` supérieur à 1 ni `ok` faux, et l'écrit. Corriger la phrase du journal des changements.

**8. La relecture de la vague 2 n'est pas comparable, de façon démontrable, à celle de la vague 1. Important.**
- Trois différences, dont une seule est déclarée :
  - modèle : Opus 5.5 en vague 2, inconnu en vague 1 (déclaré, journal l. 59) ;
  - lots : 232 alertes en 52 lots en vague 1 (4,5 fiches par lot), 2 529 en 1 428 lots en vague 2 (1,8 par lot, au plus 120 Ko et 15 fiches, `relecture_lots.py` l. 32 et 33). La règle de découpage de la vague 1 n'est écrite nulle part ;
  - harnais : en vague 2, `claude -p --setting-sources project`, donc sans les instructions personnelles d'Otsoa (l. 136 à 140). Rien ne dit comment les instances de la vague 1 ont été lancées. Si elles héritaient des instructions globales (« lis seulement les fichiers strictement nécessaires », « minimum de tokens »), leur lecture a pu être moins complète que ce que demande la consigne.
- Ce qui limite le dégât : la vague 1 pèse 8 % des alertes ; elle prend les premiers 10 % de chaque configuration, donc elle n'est confondue ni avec un modèle ni avec un environnement ; l'accord d'Otsoa est le même (13/15).
- « La même invite mot pour mot » (journal l. 59) : vérifiable, puisque les 52 invites de la vague 1 sont au manifeste. Non vérifié par moi.
- Le plan ne fixe pas le modèle du relecteur (4.3). C'est un degré de liberté resté ouvert, tranché après la vague 1 : à dire comme tel.
- Corrections : (a) comparer une invite de chaque vague, chemins mis à part, et écrire le résultat ; (b) retrouver et noter le modèle et le mode de lancement de la vague 1 (historique des sessions), ou écrire qu'ils sont perdus ; (c) annoncer avant le tirage une analyse exploratoire : les 232 alertes de la vague 1 relues avec le harnais de la vague 2, pour publier un taux d'accord entre les deux, sans rien changer aux décisions gelées.

**9. Opus 5.5 relit ses propres erreurs. Important, à écrire comme limite.**
- Preuve : journal l. 59 ; brouillon l. 146 (Opus 5.5 est l'un des trois agents jugés) et l. 307 (limite 9, qui ne parle que du « même fournisseur »).
- Les fiches cachent le modèle, pas le style. Un relecteur peut être plus indulgent avec une conversation qui ressemble à la sienne. Le sens du biais possible favorise la délégation pour Opus.
- Correction : renforcer la limite 9. Analyse exploratoire annoncée d'avance : part d'alertes levées par modèle de l'agent, à motif égal (calculée après le verdict, puisque le plan l'interdit avant), et relecture d'un échantillon par un modèle d'un autre fournisseur.

**10. L'aveugle des relecteurs repose sur leur obéissance, et aucune trace ne permet de la contrôler. Important.**
- Preuve : `relecture_lots.py` l. 136 à 140 : outils `Read`, `Write`, `Edit` sans restriction de chemin, `cwd` = le dossier `relecture/` qui contient `alertes.json` (la correspondance alerte, modèle, tâche), les sorties des autres lots et, à la fin, `decisions.csv` ; `--no-session-persistence` : aucune transcription gardée. Même chose pour l'audit (`audit_relecture.py` l. 49 à 52, `cwd` = le dossier qui contient `audit_tirage.json`).
- Le plan (4.3) dit que les relecteurs « ne voient pas » `alertes.json`. Ici ils pouvaient l'ouvrir ; on ne peut pas montrer qu'ils ne l'ont pas fait. `Write` et `Edit` leur permettaient aussi de toucher d'autres fichiers avant le manifeste.
- De même, rien ne prouve que chaque fiche a été lue en entier (environ 37 000 jetons par fiche, lecture par morceaux demandée, l. 40).
- Correction : le déclarer. Contrôle indirect possible sans regarder une décision : dans `execution.jsonl`, rapporter le coût équivalent et la durée de chaque lot à la taille de ses fiches ; un lot bien moins cher que ses fiches n'a pas tout lu. Pour toute relecture future : dossier de travail ne contenant que la consigne et les fiches du lot, transcriptions gardées.

**11. Durée de la relecture : 1 428 lots en 2 h 05, à expliquer. Important tant que ce n'est pas levé.**
- Preuve : `SUIVI.md` l. 376 (19 h 11 à 21 h 16, « environ 93 millions de jetons de fiches » au journal l. 59) ; `relecture_lots.py` l. 203 (6 lots en parallèle par défaut).
- À 6 en parallèle, cela fait 31 secondes par lot pour lire la consigne, environ 65 000 jetons de fiches en plusieurs appels, écrire et vérifier. Ce n'est pas plausible. Soit le parallélisme était bien plus haut (non noté), soit des fiches n'ont pas été lues en entier. Le coût équivalent (883,50 $, soit 0,62 $ par lot) plaide pour la première explication, sans la prouver.
- Correction : lire dans `lancement.log` le parallélisme réel, donner la distribution de `duree_s`, et l'écrire au journal. Non vérifié par moi.

**12. Haiku 5.5 apparaît dans `execution.jsonl`, « non vérifié ». Mineur.**
- Preuve : `SUIVI.md` l. 376. À lever : part des jetons par modèle dans `modelUsage` (le script ne garde que les noms, l. 145). Si la part de Haiku n'est pas négligeable, une partie de la lecture a pu être faite par un autre modèle que celui déclaré.

**13. Extension de la règle de relance, déclarée. Mineur.**
- Le plan (4.5) ne permet une relance que pour une sortie mal formée ; le script relance aussi sur limite d'usage (l. 152 à 158). Déclaré au journal (l. 59). Sans objet si aucune relance n'a eu lieu (constat 7).

### C. Relecture à l'aveugle d'Otsoa

**14. La page simplifiée change la tâche du relecteur, pas seulement la présentation. Important.**
- Preuve, `outils/relecture_simple.py` contre `banc/relecture/tirage_aveugle.py` l. 230 à 244 et 275 à 282 :
  - l. 116 : « Commence par le cadre "L'écart" : souvent, c'est suffisant. […] Tu n'as pas à tout lire. » La page figée disait de lire dans l'ordre jusqu'à la conversation, toutes sections ouvertes ; la consigne figée demande aux instances de lire chaque fiche en entier. Les motifs c et a4 ne se jugent pas sans la conversation et la consigne du client ;
  - l. 130 à 133 et 139 : le verdict n'est plus donné par Otsoa, il est **calculé** à partir de quatre oui/non, dans l'ordre b, c, a, d, avec arrêt au premier oui (l. 160 à 164). L'ordre de la consigne figée est a, b, c, d. Le motif enregistré est donc le premier dans l'ordre de la page ;
  - l. 132 : la question (a) omet trois règles de la consigne : « ce qu'a fait l'agent peut signaler le défaut, jamais le prouver », « un client simulé qui se contredit n'est pas un défaut », et « un défaut non prouvable avec les pièces ne se lève pas » (banque, WorkBench) ;
  - l. 133 : la question (d) dit « refus causé par notre banc et pas par l'agent ».
- Effet observé, et non supposé : en vague 1, les deux désaccords sont deux fiches qu'Otsoa a levées en (d) pour un client simulé qui dérive (`SUIVI.md` l. 353 et 354). La consigne figée classe ce cas explicitement comme non-défaut (`CONSIGNE_RELECTURE.md` l. 58), et le motif (d) y vise notre code de comparaison, pas le client simulé. La formulation de la question (d) a très probablement produit ces deux réponses.
- Sens du biais sur le 13/15 : indéterminé. La lecture partielle et « dans le doute, vraie erreur » poussent vers « vraie erreur », donc contre l'accord sur les 10 levées ; les questions fermées calquées sur la consigne alignent le raisonnement d'Otsoa sur celui de Claude, donc pour l'accord. Ce qui est sûr : le contrôle mesure « un humain guidé par la même grille, sur lecture partielle, arrive-t-il au même oui/non », pas « les décisions de Claude sont-elles justes ». Le seuil est atteint sans marge dans les deux vagues : une seule réponse déplacée par la présentation changeait la suite (second tour).
- « Le contenu est le même » (journal l. 56) est inexact : la page simplifiée ajoute le résultat de l'outil, l'état initial et le règlement entier, que la page figée ne montrait pas.
- La page n'a pas le garde-fou de la page figée contre les noms de modèle et les identifiants (`tirage_aveugle.py` l. 376 à 380) ; « vérifié par recherche », à la main.
- L'écart est déclaré pour la vague 1 seulement (journal l. 56, brouillon l. 327) ; rien pour la vague 2, où la page a resservi (`SUIVI.md` l. 377).
- Corrections : déclarer la vague 2 ; décrire dans l'article les quatre différences ci-dessus et pas seulement « présentation » ; écrire que l'instrument humain figé n'a jamais servi en vrai ; publier les deux pages.

**15. Deux levées d'Otsoa hors de tout motif figé entrent dans les verdicts, sans déclaration. Important.**
- Preuve : `SUIVI.md` l. 354 (« ce cas n'entre dans aucun motif figé ») ; `accord.py` l. 176 et 193 à 200 (sa décision remplace celle de Claude, sans contrôle du motif). Absent du journal des changements et du texte déposé sur OSF.
- Le plan (4.3) : « une alerte n'est levée que pour un motif écrit d'avance ». Ces deux alertes confirmées par Claude deviennent levées pour une raison que la consigne exclut. Le même type de cas reste confirmé partout où Otsoa n'a pas regardé. Cela contredit aussi la limite 7 du brouillon (« les erreurs induites par le client simulé ne sont pas séparées »).
- Poids : deux alertes sur 2 761. Sens : en faveur des agents.
- Correction : le déclarer avant le tirage. Annoncer une analyse de sensibilité avec ces deux alertes confirmées.

**16. Ce que 13 sur 15 établit, et ce qu'il n'établit pas. Important pour l'article.**
- L'échantillon est stratifié (10 levées, 5 confirmées) et Otsoa connaît cette composition, puisqu'il a écrit le plan. L'accord n'est pas corrigé du hasard : kappa d'environ 0,70 pour 13/15. Intervalle exact à 95 % sur 13/15 : environ 60 % à 98 %.
- En vague 2, un des désaccords est une levée de Claude jugée vraie erreur par Otsoa (`SUIVI.md` l. 378). Un cas sur dix levées relues : la part de levées à tort parmi toutes les levées de la vague peut aller, à 95 %, jusqu'à environ 40 %. La décision d'Otsoa ne corrige que la fiche qu'il a vue. Ce biais éventuel va vers la délégation.
- Correction : donner dans l'article les deux tableaux 2 × 2, le kappa, les intervalles, et cette phrase. L'analyse en verdicts bruts, déjà prévue (plan 4.6), est la borne prudente : le dire à cet endroit.

### D. Tâches défectueuses et audit

**17. Trois retraits de la banque motivés par « les règles de la base de connaissances » : contraires à la lettre de la consigne, sauf preuve du contraire. Bloquant tant que ce n'est pas vérifié.**
- Preuve : `SUIVI.md` l. 379 (« banque task_026, task_056, task_083 (a1, règles de la base de connaissances) ») ; `CONSIGNE_RELECTURE.md` l. 28 à 31 et plan 4.5 (P10) : « un défaut qui ne se prouve pas avec les pièces de la fiche ne se lève pas : c'est le cas de la base de connaissances de la banque, que la fiche ne montre pas ». Le cas a1 exige « un paragraphe explicite du règlement que reçoit l'agent ».
- Deux lectures possibles, que je ne peux pas départager sans lire les preuves : (i) la preuve cite le règlement présent dans la fiche, et c'est la formule du suivi qui est fautive ; (ii) la preuve cite un document de la base vu dans la conversation, et le retrait sort du critère figé.
- Correction : relire les trois preuves contre la consigne, par quelqu'un qui n'a pas recommandé ces retraits. Si (ii) : soit s'y opposer, ce qui change `oppositions_motif_a.json`, donc le manifeste, et oblige à un nouvel enregistrement OSF avec 72 heures de plus (prévu par le plan 3.4, point 3 : « tout autre enregistrement est déclaré ») ; soit garder le gel et déclarer l'écart avec une analyse de sensibilité annoncée. Dans les deux cas, décider et écrire avant le tirage.

**18. Commerce 98 retirée « pour ne pas compter des fautes » : hors critère, et incohérent avec l'opposition sur WorkBench 179. Important.**
- Preuve : `SUIVI.md` l. 357 (« a3 douteux : "l'autre carte" dépend de ce que propose l'agent, mais la garder ferait des fautes d'actions faites à la demande du client ») et l. 379 ; plan 4.5 : défectueuse « si, et seulement si, ses propres fichiers se contredisent », preuve « sans s'appuyer sur ce qu'ont fait les agents » ; consigne l. 14 : « dans le doute, tu confirmes ».
- Trois défauts de raisonnement :
  - un a3 qualifié de « douteux » ne remplit pas un critère en « si et seulement si » ;
  - le défaut « dépend de ce que propose l'agent » : c'est exactement ce que le critère interdit de retenir comme preuve ;
  - le motif donné est une conséquence sur le décompte des fautes, pas une propriété de la tâche. C'est le type de raisonnement que le gel du critère devait empêcher.
- Incohérence : WorkBench 179, « a3 non prouvé », reçoit une opposition au nom de « dans le doute, vraie erreur » ; commerce 98, « a3 douteux », est retirée. Le même doute est tranché dans deux sens.
- Le raisonnement est-il défendable ? En partie. Le mécanisme figé n'offre que deux issues, retrait ou erreurs confirmées, et aucune voie pour reclasser ces alertes en motif (c). Retirer est l'issue neutre : la tâche sort avec ses réussites comme avec ses erreurs, pour tous les modèles et toutes les règles. Mais c'est un jugement d'opportunité, pris par Otsoa sur la recommandation du Claude qui pilote l'étude, et il va dans le sens favorable aux agents. Il ne peut passer que comme écart déclaré.
- Poids : 1 tâche sur 91 en commerce. « banque task_082 (a3, un peu moins net) » appelle la même vérification.
- Correction : déclarer avant le tirage, avec l'analyse de sensibilité annoncée (commerce 98 gardée, alertes du motif a confirmées). Si le constat 17 conduit à refaire le gel, corriger aussi ce point.

**19. Portée des retraits et de l'audit. Mineur, à écrire.**
- Les retraits ne viennent que de tâches où un agent a déclenché une alerte ; une seule levée (a) par une seule instance suffit à retirer la tâche pour tous (`retraits_motif_a.py` l. 34 à 40 ; plan 4.5). L'article doit donner, par tâche retirée, combien d'alertes portaient le motif (a) sur combien d'alertes de la tâche.
- 13 tâches retirées, toutes dans τ-bench (commerce 7 sur 91, banque 5 sur 77, aviation 1 sur 40), aucune dans WorkBench, qui n'a pas de règlement : l'asymétrie déclarée au plan joue en plein.
- Audit : 0 erreur invisible sur 21 écritures laisse une borne haute à 13 % (`SUIVI.md` l. 381, calcul juste). Il ne peut donc pas appuyer d = 0,95, qui suppose au plus 5 % d'erreurs ratées. La limite 4 du brouillon doit le dire en chiffres.
- `outils/audit_relecture.py` n'est pas au journal des changements, alors que son jumeau `relecture_lots.py` y est.

### E. Journal des écarts

**20. Le journal des changements s'arrête au 13/11 ; plusieurs écarts des 13 et 14/11 n'y sont pas, ni dans le texte déposé. Important.**
- Preuve : `JOURNAL_CHANGEMENTS.md`, dernière ligne l. 59 (13/11) ; `resume_osf_texte.txt` l. 24 (quatre écarts cités).
- Manquent :
  - les noms d'outils absents de la table : en banque, 19 vrais outils présents dans les définitions figées et absents de `table_outils.json`, plus 8 noms inventés ; en commerce, 2 noms inventés (`SUIVI.md` l. 370, qui se termine par « À déclarer »). C'est un défaut d'instrument découvert après le gel : ces écritures restent sans verdict. La couverture de la banque est à 0,925, sous 0,95 ; le seuil global tient (0,985) parce que le plan le place sur l'ensemble. « Ils expliquent sans doute l'essentiel des 298 écritures inconnues (à vérifier) » : non vérifié ;
  - la page simplifiée en vague 2 (constat 14) ;
  - les deux levées hors motif (constat 15) ;
  - commerce 98 et, le cas échéant, les trois retraits de la banque (constats 17 et 18) ;
  - `audit_relecture.py` et le modèle de l'audit ;
  - la soumission OSF faite par Claude (constat 6) ;
  - l'écart de une partie entre l'aperçu (13 081, `SUIVI.md` l. 359) et le plan joué (13 080, l. 367), à expliquer en une ligne.
- Correction : compléter le journal avant le tirage, dans un commit daté et ancré hors de la machine.

**21. Exclusions pour message vide : 69 parties sur 706 pour Haiku en banque, soit 9,8 %. Important.**
- Preuve : `SUIVI.md` l. 369 ; journal l. 57 ; brouillon, limite 10 et D2.
- L'écart est déclaré, et son sens aussi. Mais « probablement » est faible pour une exclusion de près d'un dixième d'une configuration, due à un comportement de l'agent. L'analyse exploratoire promise (« ces parties comptent comme des échecs de l'agent ») n'a pas de définition : une partie exclue n'a pas d'écriture, donc on ne sait pas ce qu'elle ajoute à un rejeu par écriture.
- Correction : écrire la définition de cette analyse avant le tirage. Donner dans l'article le taux par configuration, et pas seulement le compte.

### F. Brouillon d'article

**22. Le brouillon ne dit pas que H1 ne peut presque pas échouer par les données. Important.**
- Preuve : brouillon l. 197 (H1 présenté comme critère « éliminatoire ») et l. 38 (« a preregistered protocol that can fail », « rule refuted ») ; plan 1.4 : « R1 peut signifier un écart de mélange », « R1 ne peut pas signifier, à lui seul, que les agents sont peu fiables ».
- Dans le rejeu, toute erreur confirmée au palier 3 est constatée aussitôt. La borne est alors déterministe : au plus une erreur exécutée pour N + 1 écritures du type. Le budget ne peut être dépassé que si la part réelle s dépasse la part attendue q d'environ 5 %. Le plan le dit sans détour ; le brouillon ne le dit que pour le critère de retrait (l. 197) et, de biais, dans la limite 12.
- Un lecteur comprendra « la règle a tenu le budget sur des erreurs réelles » là où le résultat est acquis par construction, à l'écart de mélange près. C'est l'exagération la plus coûteuse du brouillon.
- Correction : reprendre en 5.2 et en limites le paragraphe « ce que R1 et "confirmée" peuvent et ne peuvent pas signifier » du plan 1.4. Dire que la partie qui peut vraiment échouer est H2, avec la mesure de l'écart de délégation.

**23. Section 3.4 : le calcul est juste ; trois formulations à resserrer. Mineur.**
- Vérifié : cycle de N réussites puis 1/d erreurs en moyenne, d'où au plus 1/(1 + N d) ; 1/(1 + N d) ≤ 1/(d (N + 1)) ≤ barre puisque d ≤ 1 ; avec constat complet, budget × s/q exécuté et 0,95 × budget × s/q en plus ; avec d = 0,95, budget × s/(0,95 q) et budget × s/q ; banque à enjeu faible, 0,95 × 2,2 ≈ 2,1. Tout concorde avec le plan 1.4.
- À resserrer :
  - « in expectation » : pour d < 1, c'est un rapport d'espérances par cycle, donc une borne de long terme ; sur une suite finie, le dernier cycle incomplet n'est pas couvert par l'énoncé tel qu'il est écrit ;
  - résumé (l. 22) : « the extra errors […] are bounded » sans dire par quoi. Ajouter « by the budget times s/q », comme dans la contribution 1 ;
  - titre : « with an error-budget guarantee » promet plus que la garantie conditionnelle (constat immédiat, erreurs ratées non ciblées, s ≤ q). Préférer « conditional guarantee » ou sortir le mot du titre.

**24. Résumé : « every write action is judged ». Faux tel quel. Mineur.**
- Preuve : brouillon l. 22, contre l. 161 (« every write action with a known tool ») et `SUIVI.md` l. 370 (écritures sans verdict, 7,5 % en banque).
- Correction : « every write made with a tool of the frozen table », et donner la couverture par environnement.

**25. Sections 4.3, limites et écarts : à mettre à jour avec la période. Important, attendu.**
- Le brouillon date du 10/11 et le dit (l. 2). À ajouter : modèle et harnais des relecteurs, découpage des lots, modèle inconnu en vague 1 ; limite 9 renforcée (constat 9) ; écarts D4 et suivants (constats 14, 15, 17, 18, 20, 21) ; coût réel hors de l'intervalle annoncé (837 $ contre 517 à 674 $, l. 157) ; l. 163 : « only an opaque alert ID » est vrai des fiches, pas de l'environnement de lecture (constat 10).
- L. 38 : « the code, the seeds […] frozen and registered before any confirmatory episode existed » : le commit du dépôt OSF est de 06 h 03 et la vague 1 commence à 06 h 19 le 10/11. L'ordre est bon, l'écart est de seize minutes, et un enregistrement OSF reste annulable 48 heures. Donner les deux horodatages serveur.

**26. `outils/tables_article.py` : trois défauts de mise en forme. Mineur.**
- l. 99 : le résumé de la table 5 ne garde que les configurations ; les 48 scénarios de changement de modèle, qui sont des cellules du point 1, disparaissent. Les ajouter, ou le dire en titre.
- l. 195 : la ligne « budget » de `fig_budget.png` prend le budget de la première cellule jugée ; faux si des cellules de niveaux différents sont jugées.
- l. 96 et 105 à 108 : `worst` part de 0 et `max(0, NaN)` rend 0 ; une cellule sans rapport calculable s'affiche « 0,00 » au lieu de « – ». Le docstring dit « computes no new statistic » alors qu'il agrège des comptes et un maximum.
- Point positif : script écrit et commité avant le verdict.

---

## Réponses aux sept questions

1. **Respect du plan.** Le code figé n'a pas bougé et les étapes ont suivi l'ordre du plan. Écarts non déclarés ou mal déclarés : constats 7, 14 (vague 2 et « même contenu »), 15, 17, 18, 20.
2. **Relecture de la vague 2.** Comparabilité avec la vague 1 non démontrable (modèle, lots, harnais) ; poids limité (8 % des alertes). Les vrais problèmes de validité sont ailleurs : aveugle non garanti et non traçable (10), durée inexpliquée (11), Opus juge d'Opus (9).
3. **Page simplifiée.** Oui, elle a influencé des réponses : les deux désaccords de la vague 1 viennent de la formulation de la question (d). Sens net sur le 13/15 indéterminé ; indépendance du contrôle affaiblie (14, 16).
4. **Dépôt OSF.** Le tirage lui-même est bien fixé : manifeste, script, paires et réserve sont liés par des empreintes vérifiées. Deux marges restent : la lecture de l'horodatage (2) et, surtout, la commande du rejeu final (1). Rien d'important ne manque au manifeste (5).
5. **Retraits et opposition.** L'opposition sur WorkBench 179 suit le critère. Commerce 98 ne le suit pas (18). Trois retraits de la banque sont à vérifier contre la clause sur la base de connaissances (17).
6. **Brouillon.** Règle, méthode et calcul de la garantie corrects. Exagération par omission sur H1 (22) ; résumé inexact sur « every write » (24) ; titre et résumé à resserrer (23) ; mises à jour attendues (25).
7. **Avant le 17/11.** Voir ci-dessous.

---

## À faire avant le tirage du 17/11 (06:45 UTC)

Dans l'ordre. Aucun de ces gestes ne demande d'ouvrir un résultat.

1. **Vérifier les trois preuves a1 de la banque** (task_026, 056, 083) et relire commerce 98 et banque task_082 contre le critère figé (constats 17 et 18). Décider : nouveau gel et nouvel enregistrement OSF (72 heures de plus, enregistrement actuel déclaré), ou gel gardé avec écart déclaré et analyses de sensibilité annoncées. C'est la seule décision qui peut encore déplacer la date.
2. **Écrire la commande exacte du rejeu final**, avec `accord.json` des deux vagues, `--oppositions`, `--retirees`, `--manifeste-verdicts`, le dossier de sortie, et la règle « un seul lancement » (constat 1).
3. **Écrire l'impulsion désignée** : champ `date_registered` de l'API, valeur complète, NIST 2026-11-17T06:45:00Z, secours drand 34031501. Relire le champ par l'API après l'approbation de l'embargo (constat 2).
4. **Compléter `JOURNAL_CHANGEMENTS.md`** avec les lignes des 13 et 14/11 qui manquent (constat 20), et corriger la phrase sur la raison des relances (constat 7).
5. **Annoncer par écrit les analyses exploratoires**, avec leur définition : alertes d'Otsoa hors motif reconfirmées (15) ; commerce 98 gardée (18) ; parties exclues pour message vide (21) ; relecture de la vague 1 avec le harnais de la vague 2 et relecture d'un échantillon par un autre modèle (8, 9) ; part de levées par modèle de l'agent (9).
6. **Ancrer hors de la machine** les points 2 à 5 : un fichier daté ajouté au projet OSF `bd4g5`, ou l'empreinte du commit envoyée à un tiers. Sans cela, ces écrits ne prouvent pas qu'ils précèdent le tirage.
7. **Contrôles sans lecture de décisions**, à noter au suivi : essais et `ok` dans `execution.jsonl` (7) ; parallélisme et durées (11) ; coût par lot rapporté à la taille des fiches (10) ; part de Haiku (12) ; identité des invites des deux vagues (8).
8. **Garde du gel** : copie sur T9 des fichiers produits depuis le 13/11 (annoncée à `SUIVI.md` l. 382, non notée comme faite) ; ne pas ouvrir `experience/` dans le Finder ; `gel/manifeste_verdicts.py verifier` et `gel/manifeste.py --verifier` juste avant le tirage.

---

## Ce qui est solide

- **Le périmètre figé est intact.** Diff vide sur `banc/`, `simulation/`, `gel/`, `REGLE.md`, `PLAN_EXPERIENCE.md` depuis `gel-2026-11-09`. Tous les outils nouveaux sont dans `outils/`, hors périmètre, et commités avant le manifeste (sauf `tables_article.py`, sans effet sur les entrées).
- **La chaîne d'empreintes tient.** Zip, paquet, manifeste, scripts de tirage, manifeste du gel du plan : tout se recalcule à l'identique, et l'empreinte du gel est bien celle du dépôt du 09/11.
- **Le tirage est bien conçu.** Graine liée au manifeste et à une impulsion future, délai de 72 heures justifié par les 48 heures d'annulation d'OSF, secours écrit d'avance et déclenché par la seule archive publique, paires et réserve comparées au gel, refus d'écraser. Le texte déposé décrit correctement le code, aux précisions du constat 4 près.
- **Le manifeste est plus large que ce que le plan exige** : pages de relecture, réponses d'Otsoa, journaux d'exécution, invites des deux vagues. C'est ce qui rend vérifiables plusieurs des contrôles demandés ici.
- **Les écarts qui desservent l'étude sont dits.** Message vide compté comme panne et biais vers la délégation, erreur de Claude sur ses points d'étape, modèle de la vague 1 non noté, couverture de la banque sous 0,95, deux levées « hors de tout motif figé » : tout cela est écrit par l'équipe elle-même dans `SUIVI.md`. Le défaut est de ne pas l'avoir porté au journal, pas de l'avoir caché.
- **L'opposition sur WorkBench 179** applique le critère contre l'intérêt de l'étude.
- **L'indépendance d'Otsoa a été protégée sur un point clé** : il a demandé si Claude pouvait vérifier à sa place, et la réponse a été non (`SUIVI.md` l. 352).
- **L'arithmétique de la garantie** du brouillon est juste et cohérente avec le plan ; le brouillon ne revendique pas la borne comme nouvelle et signale les sources non lues.
- **Dépense** : 852 $ au décompte interne, recoupée par la console (environ 6 % en dessous), sous le budget de 1 100 $.
