# Audit du paquet de dépôt OSF des résultats (17/11/2026)

Objet : `depots/2026-11-17_resultats/` (paquet, zip, empreintes, journal du tirage, résumé, fiche), construit par `outils/construire_depot_resultats.py`. Question à éclairer : Q6 de `PLAN_SUITE.md`.

Auditeur indépendant. Rien n'a été modifié, rien n'a été déposé. Aucun dossier interdit n'a été ouvert. Les fichiers hors de ma liste d'accès n'ont été touchés que par leur empreinte ou leur nom.

## En bref

- Le paquet est **sain** : aucun secret, aucune donnée brute, empreintes justes, tirage cohérent, résumé exact.
- Il n'est **pas encore prêt** : 3 points bloquants, tous simples à corriger (une heure de travail environ).
- Recommandation pour Q6 : **option b**, après corrections, avec deux précautions (voir la fin).

## Ce qui a été vérifié et qui est bon

| Contrôle | Résultat |
|---|---|
| Empreinte du zip | `d300a694…84b4`, identique à la fiche. |
| Zip décompressé dans un dossier vide | 35 fichiers ; les 34 lignes de `SHA256SUMS.txt` passent, 0 échec. |
| `paquet/` contre `SHA256SUMS.txt` | 34 sur 34. Les deux copies de `SHA256SUMS.txt` et de `JOURNAL_TIRAGE.md` sont identiques. |
| Paquet contre ses sources | `replay/` = `experience/rejeu_final/` (15 fichiers), `exploratory/` = `experience/exploratoire/` (9), `draw/` = `experience/tirage/` (2), les 6 autres fichiers : identiques octet pour octet. |
| Journal du tirage contre `experience/tirage/` | Heure désignée, numéro et heure de l'impulsion, valeur, graine, empreintes de la réserve et des paires : tout concorde. |
| Graine | Recalculée par moi (étiquette, empreinte du manifeste, valeur de la balise, chacune précédée de sa longueur sur 4 octets, en octets bruts) : égale à `3cf2e0ca…7f36`. |
| Heure désignée | 14/11 08:17:47.424176 UTC + 72 h = 17/11 08:17:47 UTC. L'impulsion de 08:18:00 est bien la première après. |
| Impulsion brute | `outputValue` = valeur utilisée ; `pulseIndex` 2031457 ; `statusCode` 0. |
| Partage | 379 tâches en calibration, 381 en confirmation, aucune en double ; effectifs égaux à ceux annoncés ; total 760 = réserve. |
| Empreintes citées | Script du tirage `6970dfd9…e027` et manifeste des verdicts `904aa8d3…f88d` : recalculées, justes. `impulsion.json` commence par `fa61235b`, `partage.json` par `76e04fca`. |
| Six tables du premier passage | Les 6 empreintes de `rejeu_final_echec_1_SHA256.txt` passent sur le dossier mis de côté, et égalent celles du second passage. |
| Résumé OSF | 1 313 caractères, ASCII pur, aucun chevron, aucune esperluette. Chiffres vérifiés dans `ecart.csv` : 79 erreurs sur 914 = 8,64 % ; borne basse 4,14 % ; barre 0,757 %. Phrases conformes à `article/FORMULATION_VERDICT.md`. Aucune formulation interdite (R8). Titre identique à celui de l'article. |
| Secrets | Aucune clé, aucun jeton, aucun mot de passe dans les 35 fichiers. |
| Données | Que des agrégats. Aucune conversation, aucune trace de partie, aucune ligne de relecture. Aucun fichier de `donnees/`, `pilote/`, `data/`, ni des dossiers de vague. |
| Données personnelles | Une seule adresse : celle d'Otsoa, choisie par lui (`SUIVI.md`, T34). Aucun tiers. |

Non vérifié : la relecture en ligne de l'impulsion sur le site du NIST (accès web non autorisé pour cet audit). La fiche dit « tirage vérifié » le 17/11 ; je ne l'ai pas refait.

## Constats

### Bloquants (à corriger avant tout dépôt)

**1. La liste d'empreintes `SHA256_sorties_finales.txt` est périmée et se contredit dans le paquet.**
- Preuve : `shasum -a 256 -c SHA256_sorties_finales.txt` donne « exploratoire/RESUME.md: FAILED ». La liste date de 13 h 28. `RESUME.md` a été réécrit à 13 h 56 (ajout des analyses E, F, G). La liste donne `1444c867…`, le fichier du paquet vaut `62ec247e…`.
- Les trois fichiers E, F et G n'y figurent pas.
- Ses chemins (`rejeu_final/`, `exploratoire/`, `tirage/`) ne sont pas ceux du paquet (`replay/`, `exploratory/`, `draw/`). La commande de contrôle ne peut donc pas tourner dans le paquet.
- Elle cite trois fichiers absents du paquet : `manifeste_verdicts.txt`, `rejeu_final.log`, `../outils/rejeu_final_correctif.py`.
- Le journal du tirage l'appelle « Final replay outputs (27 files) ». Seules 15 lignes sont des sorties du rejeu.
- Risque : un lecteur qui contrôle trouve un échec dans un document de preuve. Une fois déposé, cela ne se corrige plus.
- Correction : ne pas réécrire l'ancienne liste. Ajouter dans le README trois phrases : la liste est un instantané de 13 h 28 ; `RESUME.md` a été complété ensuite par E, F, G (exploratoire, sans effet sur l'étiquette) ; les empreintes qui font foi pour le paquet sont celles de `SHA256SUMS.txt`, et les 15 sorties du rejeu y ont les mêmes empreintes que dans la liste. Corriger aussi la ligne du journal : « 15 sorties du rejeu, dans une liste de 27 fichiers ».

**2. Le PDF de l'article est un brouillon, et il serait figé pour toujours.**
- Preuve : la première page de `main.pdf` porte « Draft, 17 November 2026 ». Le PDF a été compilé à 17 h 55, deux minutes avant le paquet. Il fait 55 pages. Aucune relecture extérieure (T38 sautée).
- Il contient des phrases qui seront fausses le jour J : « At the time of writing the three OSF registrations are under embargo ». Il ne peut pas citer l'enregistrement des résultats, qui n'existe pas encore. Il cite la liste périmée du constat 1.
- Le README dit « The paper (`main.pdf`) states the result and its limits » : il présente donc ce brouillon comme la référence.
- Voir le constat 12 pour l'analyse. Correction recommandée : **retirer `main.pdf` du paquet**. Mettre la phrase de référence du verdict dans le README. Corriger le résumé OSF (enlever « and the paper (main.pdf) »).

**3. Il manque la traduction française du texte qui sera publié.**
- Preuve : la fiche de T40 promet « `FICHE_DEPOT.md` (gestes à faire, traduction française) ». La règle R10 l'exige avant tout accord. `FICHE_DEPOT.md` donne les gestes, mais ni le résumé ni le README n'y sont traduits.
- Risque : Otsoa signerait un texte anglais définitif sans l'avoir lu en français. C'est ainsi que l'erreur de u26kr est passée.
- Correction : ajouter à la fiche la traduction du résumé et du README, dans leur version finale.

### Importants

**4. Le journal renvoie à un mauvais document pour la règle du tirage.**
- Preuve : `JOURNAL_TIRAGE.md` dit « specification in `banc/tirage/TIRAGE.md` ». Ce fichier décrit un autre tirage : celui des tâches de développement du 05/11 (autre méthode, autre graine). Il annonce même un jeu de confirmation « chiffré », idée abandonnée depuis.
- La vraie règle est dans `PLAN_EXPERIENCE.md`, section 3.4, point 2, et dans le README du gel des verdicts (cusv6).
- L'annexe F de l'article fait le même renvoi : à corriger aussi.
- Correction : remplacer le renvoi par « plan, section 3.4 (préenregistrement vycge) et README de cusv6 ».

**5. La commande exacte du rejeu final n'est pas dans le paquet.**
- Preuve : la note du correctif dit « exactement les arguments de la commande déposée sur cusv6 », sans les donner. La commande n'existe que dans le README de cusv6, sous embargo jusqu'en 2030.
- Le script réellement lancé, `outils/rejeu_final_correctif.py` (46 lignes), n'est pas joint. Seule son empreinte est citée.
- Risque : si l'embargo de cusv6 n'est pas levé (option b de Q7), le paquet des résultats renvoie à un document que personne ne peut lire.
- Correction : recopier la commande dans le README. Joindre `rejeu_final_correctif.py` après avoir vérifié qu'il ne contient ni chemin sensible ni secret.

**6. La commande pour refaire le tirage ne marche pas avec le paquet seul.**
- Preuve : elle demande `experience/manifeste_verdicts.txt` (dans cusv6), le script `tirage_public.py`, les paires et la réserve figées (dans le dépôt du gel, vycge, et dans le dépôt git, pas encore public). Elle écrit `experience/tirage`, alors que le paquet range ces fichiers dans `draw/`.
- Le plan promet : « N'importe qui peut refaire le tirage à partir des empreintes déposées et de l'impulsion publique. » Ce sera vrai seulement quand vycge, cusv6 et le code seront publics.
- Correction : dire dans le journal où se trouve chaque ingrédient (manifeste : cusv6 ; script, paires, réserve : vycge et dépôt de code) et que `draw/` correspond à `experience/tirage`. Ajouter la recette de la graine en une phrase, pour qu'on puisse la recalculer sans le script (je l'ai fait : elle tombe juste).

**7. Les traces du premier passage raté sont incomplètes.**
- Preuve : `experience/rejeu_final_echec_1/` contient 7 fichiers. La liste d'empreintes n'en couvre que 6. Le septième, le journal de l'échec (`rejeu_final.log`, empreinte `336b6cf2…`), n'est ni joint ni empreint. C'est pourtant la seule pièce qui montre la cause de la panne.
- `journal_rejeu_final.jsonl` montre deux lignes « début » avec deux commits différents (`ee0df60` puis `1a5b4c3`). Le paquet ne l'explique pas. L'explication existe : le second commit est celui qui déclare l'incident, fait 30 secondes avant la relance. Le manifeste du gel est le même aux deux passages.
- Correction : joindre les deux journaux d'exécution (après lecture, pour vérifier qu'ils sont publiables), ou au moins leurs empreintes. Ajouter une phrase au README sur les deux commits.

**8. `RESULTATS.md` contient des tournures que l'audit des résultats a jugées trop fortes, et le README ne prévient pas.**
- Preuve : la table de décision figée dit « témoin liste_fixe : battu », « témoin tri_risque : battu », « les trois témoins battus ». La règle R8 interdit ces tournures dans l'article et les messages. Le fichier est figé (R5) : on ne le corrige pas, on l'annote à côté.
- Si le PDF sort du paquet (constat 2), plus rien ne cadre la lecture.
- Correction : un paragraphe « How to read » dans le README : la phrase de référence du verdict ; R4 repose sur un seul type d'action, jugeable de justesse ; « battu » veut dire ici « dépassement de budget établi chez le témoin », pas un gain démontré de la règle ; aucune comparaison des modèles.

**9. Le calendrier d'OSF change : à relire en ligne avant d'agir.**
- Lu le 17/11/2026 sur l'aide d'OSF (https://help.osf.io/article/759-details-of-osf-projects-transition et https://help.osf.io/article/770-registrations) : plus de nouveau projet depuis le 16/11/2026 ; **les projets existants passent en lecture seule le 19/02/2027** ; les projets privés seront retirés plus tard, avec préavis ; il ne sera plus possible de créer un enregistrement depuis un projet. Les enregistrements existants, sous embargo ou non, et OSF Preprints ne sont pas touchés.
- Ces pages ont été lues par un outil de résumé. L'exécutant doit les relire lui-même (R6).
- Conséquences : le geste 1 de la fiche (« sur le projet bd4g5, créer un enregistrement ») a une date limite. Si le jour J glisse après février 2027, l'option c devient plus compliquée. L'article cite le projet privé bd4g5 comme source (référence 42) : à remplacer par les enregistrements.

**10. La fiche ne dit pas quoi faire du courriel d'approbation ni quelle date de fin d'embargo choisir.**
- Lu sur l'aide d'OSF (https://help.osf.io/article/158-create-a-preregistration) : après la soumission, 48 heures pour approuver ou annuler ; passé ce délai, approbation automatique ; ensuite, ni modification ni suppression, seulement un retrait, qui laisse en public le titre, l'auteur et le motif. Un embargo dure 4 ans au plus et **se lève tout seul à sa date de fin**. La levée anticipée se demande, puis s'approuve par courriel, ou passe seule après 48 heures.
- Risque 1 : approuver trop vite, comme pour u26kr.
- Risque 2 : un embargo « court » qui arrive à sa fin avant que l'article soit prêt publie les résultats tout seul. La date du jour J n'est pas décidée (Q16).
- Correction : écrire dans la fiche : (i) ne pas approuver le courriel avant d'avoir retéléchargé le zip, comparé l'empreinte et relu le résumé sur le serveur ; (ii) date de fin d'embargo au 04/11/2030, comme les trois autres, et levée à la main le jour J ; (iii) le jour J, approuver tout de suite le courriel de levée, sinon la page ne s'ouvre que 48 heures plus tard.

### Mineurs

**11. Petits écarts de forme.**
- La fiche dit « 34 fichiers ». Le zip en contient 35 (les 34, plus `SHA256SUMS.txt`).
- `meta.json` (9 fois) et `journal_rejeu_final.jsonl` (3 fois) contiennent des chemins locaux `HOME/…`, dont des noms de dossiers de vague. Ce sont des noms, pas des contenus. Publiable. À signaler d'une phrase dans le README.
- Le README est en anglais, presque tout le reste est en français (`RESULTATS.md`, colonnes des CSV, `RESUME.md`, les deux notes). Le dire dans le README, avec un petit lexique (rejeu = replay, tirage = draw, écart = gap, barre = bar).
- Le journal ne donne pas l'heure d'exécution du tirage (09:18 UTC, soit plus d'une heure après l'heure désignée, comme la règle l'exige) ni le fait que le secours drand n'a pas servi. Une ligne suffit.
- L'adresse `otsoa.dubief@gmail.com` sera publique et définitive. C'est le choix d'Otsoa ; à confirmer une dernière fois.
- Le script ne contrôle que les chemins des sources. La recherche de secrets a été faite à la main. Si le paquet est reconstruit (il le sera), refaire les contrôles : empreintes, zip décompressé, secrets. Le script reprend le PDF du moment : une recompilation de l'article change l'empreinte du zip sans prévenir.
- Les métadonnées du PDF (titre, auteur) sont vides. Sans effet ici ; à remplir pour OSF Preprints (T43 bis).
- Le résumé OSF ne dit pas que la jugeabilité du seul type jugé est fragile (environ un tirage sur dix la ferait tomber, analyse G). Ce n'est pas une erreur. Une phrase de plus le rendrait plus honnête.

### Analyse demandée : joindre le PDF de l'article ?

**12. Risque supérieur à l'avantage. Recommandation : ne pas le joindre.**

Avantages de le joindre :
- le lecteur a l'explication à côté des chiffres ;
- la version du 17/11 est datée par un tiers.

Risques :
- un brouillon devient une pièce permanente, publique à la levée, impossible à corriger ; toute erreur trouvée ensuite y reste ;
- deux versions de l'article circuleront : celle du dépôt et celle d'OSF Preprints, puis d'arXiv. Un lecteur peut citer la mauvaise ;
- un écart entre les deux versions peut être lu comme une retouche du récit après coup, alors que c'est le contraire qu'on veut montrer ;
- il n'apporte rien à la preuve. Ce que le dépôt doit prouver, c'est que les sorties n'ont pas bougé. Les sorties suffisent.

Si Otsoa tient à garder une trace datée du texte : mettre dans le README la seule empreinte SHA-256 du PDF du 17/11, sans le fichier. On peut alors prouver plus tard ce qu'était le brouillon, sans le publier.

## Réponse recommandée à Q6

**Choisir b : déposer maintenant, sous embargo, et lever le jour J. Mais pas ce soir : après les corrections.**

Pourquoi, en mots simples.

- **Ce que le dépôt prouve.** OSF met une date que personne ne peut changer. Cette date dit : « à ce moment, les résultats étaient déjà ceux-là ». Le tirage date du 17/11 au matin, le rejeu de 12 h 53. Plus le dépôt est proche, plus la preuve est forte. Si on attend le jour J, il s'écoule des semaines pendant lesquelles on écrit l'article. C'est exactement la période où un lecteur méfiant se demande si les chiffres ont été retouchés.
- **a (public tout de suite) n'apporte rien de plus que b.** La date est la même. En revanche le verdict sortirait seul, sans article, avec des renvois vers trois enregistrements encore fermés et un code pas encore public. Personne ne pourrait vérifier. Et rien ne pourrait être repris.
- **c (le jour J seulement) perd la preuve de date.** Son seul avantage est de ne rien figer aujourd'hui. Il y a aussi un risque de calendrier : les projets OSF passent en lecture seule le 19/02/2027 (constat 9).
- **b garde la date et n'annonce rien.** Son risque est connu : après l'approbation, on ne revient plus en arrière. Il se traite par la préparation, pas par l'attente.

Deux précautions, qui font partie de la recommandation :

1. **Embargo long, levée à la main.** Mettre la fin d'embargo au 04/11/2030, comme les autres, et lever le jour J. Un embargo court se lève tout seul à sa date : si l'article a du retard, les résultats sortiraient sans lui.
2. **Ne pas approuver le courriel d'OSF avant la vérification.** Pendant 48 heures, on peut encore annuler. On retélécharge le zip, on compare l'empreinte, on relit le résumé sur le serveur. Ensuite seulement on approuve.

Une conséquence pour Q7 : si on dépose les résultats, il faut lever aussi vycge et cusv6 le jour J (option a de Q7). Le paquet des résultats s'appuie sur eux.

### À corriger avant de déposer (dans l'ordre)

1. Retirer `main.pdf` du paquet ; adapter le README et le résumé OSF (constats 2 et 12).
2. Expliquer dans le README la liste d'empreintes de 13 h 28 et corriger la ligne « 27 files » du journal (constat 1).
3. Corriger le renvoi à `TIRAGE.md` dans le journal (constat 4).
4. Ajouter au README : la commande exacte du rejeu final, le paragraphe « How to read », la note sur les deux commits, la note sur la langue et les chemins locaux (constats 5, 7, 8, 11).
5. Joindre `outils/rejeu_final_correctif.py` et les deux journaux d'exécution, après lecture (constats 5 et 7).
6. Dire dans le journal où trouver le manifeste, le script, les paires et la réserve ; ajouter l'heure d'exécution du tirage (constats 6 et 11).
7. Reconstruire le paquet. Refaire tous les contrôles : empreintes, zip décompressé, secrets, chevrons et esperluettes du résumé.
8. Compléter `FICHE_DEPOT.md` : traduction française du résumé et du README, consigne sur le courriel d'approbation, date de fin d'embargo, nombre de fichiers (constats 3, 10, 11).
9. Relire en ligne, le jour du dépôt, les pages d'OSF sur la transition des projets et sur l'embargo (constat 9).
10. Montrer la fiche à Otsoa. Déposer seulement après son accord écrit.
