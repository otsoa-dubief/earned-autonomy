# Audit du plan de dépôt Zenodo des résultats (17/11/2026)

Objet : `depots/2026-11-17_resultats/ZENODO_PLAN.md`. Auditeur indépendant. Aucun fichier existant modifié. Aucune action sur un site. Aucun dossier interdit ouvert. Dans `paquet/`, seul le README a été lu ; le zip n'a été ouvert que pour la liste de ses noms de fichiers.

Toutes les pages web citées ont été lues le **17/11/2026**, texte intégral (pas un résumé).

## En bref

- Le plan est **bon dans son principe** : Zenodo est la voie qu'OSF recommande lui-même, les métadonnées ne révèlent pas le résultat, l'ORCID est juste, l'empreinte du zip est juste.
- Il n'est **pas prêt** : 3 points bloquants, dont 2 sont des décisions d'Otsoa.
- Point central : **la levée anticipée d'un embargo est possible** (la documentation le dit). Donc la bonne stratégie est une date lointaine et une levée à la main, pas une date à six mois qui s'ouvre toute seule.
- Deuxième point : sur Zenodo, **les fichiers restent modifiables par l'auteur pendant 30 jours, sans changer le DOI**. La preuve de date est donc moins forte que sur OSF. Il faut la renforcer (constat 4).

## Ce qui a été vérifié et qui est bon

| Contrôle | Résultat |
|---|---|
| Empreinte SHA-256 du zip | `2c1cda3a8d920b336edcd2d067d3feeca48d63f587ddb229ef4687c920320343`, recalculée, égale à la fiche. |
| Empreinte MD5 du zip (celle que Zenodo affichera) | `a29d1cfe6e83e37b2f2b39805ac00b2d`, calculée par moi. Taille : 3 660 253 octets. |
| Contenu du zip | 41 fichiers, 40 lignes dans `SHA256SUMS.txt`. Aucun `.DS_Store` ni `__MACOSX`. Dates des fichiers neutralisées. |
| ORCID | `0009-0002-7322-7575` : chiffre de contrôle juste ; identique à `SUIVI.md` (ligne 325) et à l'article. |
| Nom, affiliation | « Dubief, Otsoa », « Independent researcher » : conformes à l'article et au compte arXiv. |
| Neutralité du titre, de la description, des mots-clés | Aucun ne contient R4, un taux, un seuil, « aucune configuration », ni une formule de `FORMULATION_VERDICT.md`. |
| OSF refuse les résultats | Confirmé : « Unacceptable submissions to the registries on OSF include: […] Any other research outputs (e.g., data) that are not a part of the research plan » (https://help.osf.io/article/330-welcome-to-registrations). OSF conseille de déposer ailleurs, « like Zenodo », puis de relier le DOI à l'enregistrement (https://help.osf.io/article/768-osf-projects-transition-registration-questions-and-use-cases). |
| Licence et embargo | Compatibles. « Users must specify a license for all publicly available files » ; l'embargo est une option prévue (https://about.zenodo.org/policies/). |
| Type de ressource | « Dataset » convient : le paquet est surtout fait de tables CSV. Règle Zenodo : choisir le type « which best describes and/or is most significant » (https://help.zenodo.org/docs/deposit/describe-records/resource-type/). |
| Renommer le zip | Sans effet sur l'empreinte : elle porte sur le contenu, pas sur le nom. À recontrôler quand même sur la copie renommée. |

## Règles Zenodo relevées (point 1 de la mission)

| Sujet | Règle, mot pour mot | Source |
|---|---|---|
| Ce qui est public | « the metadata is always publicly accessible » | https://help.zenodo.org/docs/deposit/create-new-upload/ |
| Embargo | « Set the files visibility to restricted and check the Apply an embargo. Provide an Embargo until date. The files will automatically be made publicly available on the chosen date at midnight UTC. Optionally, provide a reason for the embargo. Users viewing the record landing page will be made aware of the embargo period. » | même page |
| Durée maximale | **Non indiquée** dans les pages lues. À constater dans le formulaire. | — |
| Levée anticipée | « The visibility can also be edited after the record is published by editing the record. » Et : « You can now edit the record's metadata and/or file visibility. […] click the green publish button […]. This does not affect your DOI. » | https://help.zenodo.org/docs/deposit/manage-files/ et https://help.zenodo.org/docs/deposit/manage-records/ |
| Refermer des fichiers | Possible à tout moment : « You can hide the files of your record at any time ». | https://support.zenodo.org/help/en-gb/1-upload-deposit/217-can-i-restrict-the-visibility-of-my-record |
| DOI | « The DOI will only be registered once the record is published. » Deux DOI sont créés : un pour la version, un pour l'ensemble des versions. | create-new-upload ; https://support.zenodo.org/help/en-gb/1-upload-deposit/97-what-is-doi-versioning |
| Métadonnées après publication | Modifiables à tout moment. | manage-records |
| Fichiers après publication | « if you would like to make minor corrections, and you are within 30 days after publication, you can edit the uploaded files of the record. […] The draft must be published within 45 days of the original publishing of the record. Publishing the draft will not change the DOI. » Ensuite : support seulement, « duly justified cases ». | manage-files |
| Suppression | « Records on Zenodo can be deleted by their owner within 30 days after publication. » Il reste une page « tombstone » avec la citation. Ensuite : support seulement. | manage-records |
| Empreinte | « All data files are stored along with a MD5 checksum of the file content. » | https://about.zenodo.org/policies/ |
| IA | Usage substantiel d'IA à déclarer dans la description ; une IA ne peut pas être auteur ni contributeur. | https://support.zenodo.org/help/en-gb/13-policies/227-what-is-your-usage-policy-for-generative-ai-for-depositors (27/04/2026) |

Note : la documentation se contredit sur le délai (30 jours sur une page, 45 sur une autre). Retenir **30 jours**.

## Constats

### Bloquants

**1. La date d'embargo du 17/05/2027 ouvre les fichiers toute seule. [Décision d'Otsoa]**
- Preuve : ouverture automatique « on the chosen date at midnight UTC » (soit 2 h du matin à Paris en mai). Le jour J n'est pas fixé (`PLAN_SUITE.md`, Q16).
- Risque si l'article sort plus tard : les résultats sortent seuls, sans article. On peut refermer les fichiers ensuite, mais ils auront été publics.
- Risque si l'article sort plus tôt : aucun. La levée à la main est documentée (tableau ci-dessus). Le plan dit que la documentation « ne confirme pas clairement » : elle le confirme, en termes généraux.
- Le plan contredit la précaution déjà adoptée pour OSF (`revues/2026-11-17_audit_depot_resultats.md`, constat 10 ; `FICHE_DEPOT.md`, geste 4) : embargo long, levée à la main.
- Correction : **embargo jusqu'au 04/11/2030**, comme les trois enregistrements OSF. Une seule règle à retenir : tout s'ouvre à la main le jour J. Si le formulaire refuse cette date, prendre la plus lointaine acceptée et le noter.
- Filet de sécurité si la levée à la main échouait le jour J : publier une « nouvelle version » avec les mêmes fichiers en accès public (nouveau DOI, la version 1 reste la preuve de date), ou écrire au support.
- Si Otsoa garde le 17/05/2027 : poser deux rappels (17/03 et 17/04/2027) pour repousser la date si l'article n'est pas sorti.

**2. La description n'est pas finie et repose sur une règle mal lue.**
- Preuve : elle contient le texte à remplacer « [empreinte du zip] ».
- Preuve : le plan écrit « fichiers et DOI non modifiables après publication ». C'est inexact pendant 30 jours (voir constat 4). La phrase « the deposit date and the fingerprints attest that the outputs did not change » promet donc plus que Zenodo ne garantit.
- Il manque la déclaration d'usage de l'IA, attendue par Zenodo dans la description (constat 6).
- Il manque la traduction française du texte publié (règle R10 de `PLAN_SUITE.md`).
- Correction : texte complet dans le « Plan corrigé », avec sa traduction.

**3. Le README dans le zip parle d'un enregistrement OSF. [Décision d'Otsoa]**
- Preuve : `paquet/README.md`, lignes 4-5 : « it will be posted on OSF Preprints with a link to this registration ». Le dépôt ne sera pas un enregistrement OSF mais une fiche Zenodo.
- Risque : après 30 jours, le zip ne se corrige plus. Le lecteur cherchera un enregistrement OSF qui n'existe pas.
- Correction préférée (propre) : remplacer « this registration » par « this record » dans le README, reconstruire le paquet aujourd'hui avec le script, refaire les contrôles (empreintes, zip décompressé, secrets), mettre à jour l'empreinte dans la fiche et dans la description.
- Correction acceptable (sans reconstruire) : garder le zip actuel et l'expliquer dans la note publique de la fiche Zenodo (texte dans le « Plan corrigé »).
- Dans les deux cas, décider avant de publier.

### Importants

**4. La preuve de date est moins forte que sur OSF.**
- Preuve : l'auteur peut changer les fichiers pendant 30 jours sans changer le DOI ; les métadonnées (donc l'empreinte écrite dans la description) restent modifiables pour toujours.
- Risque : un lecteur méfiant peut dire que le zip a été remplacé après coup.
- Corrections :
  - ne jamais utiliser « Edit published files » sur cette fiche ; l'écrire dans `FICHE_DEPOT.md` ;
  - garder l'empreinte SHA-256 du zip dans la description (déjà prévu) ;
  - le jour de la publication, faire enregistrer la page publique de la fiche par un tiers daté (Internet Archive, « Save Page Now »), avec l'accord d'Otsoa ; recommencer après le 31e jour ;
  - après publication, retélécharger le zip depuis Zenodo et comparer le SHA-256 (plus fort que le MD5 affiché).

**5. Le titre porte une mention qui deviendra fausse.**
- Preuve : « (files under embargo until publication) ». Le titre entre dans la citation et dans le DOI. Zenodo affiche déjà l'embargo sur la page.
- Correction : titre sans parenthèse (voir « Plan corrigé »). Zenodo demande aussi d'éviter les titres génériques (https://support.zenodo.org/help/en-gb/2-content/146-what-can-i-do-to-avoid-spam-detection).

**6. Usage de l'IA non déclaré.**
- Preuve : « Depositors are expected to disclose substantive use of AI tools in the description of their record ». Le code qui a produit les sorties a été écrit avec Claude ; les relectures d'alertes aussi (article, « Use of AI tools »).
- Risque : pas de retrait pour ce seul motif, mais Zenodo retire les contenus d'IA « without verifiable research basis », et son filtre anti-spam est automatique.
- Correction : une note de trois phrases, reprise de l'article. Ne jamais inscrire Claude comme auteur ou contributeur.

**7. Identifiants liés : types de relation mal choisis, un identifiant oublié.**
- « Is supplement to » désigne un supplément d'article. À réserver à l'article, le jour J.
- La description cite 7ju3c, mais la liste des liens ne le contient pas.
- Format : mettre des adresses (`https://osf.io/vycge/`), type « URL ». Pas de DOI OSF aujourd'hui : « All registrations on OSF receive DOIs when they are made public » (article 768). Les enregistrements sont sous embargo ; leur DOI n'existe pas encore.
- Correction : vycge = « Is documented by » ; cusv6 = « Is derived from » ; 7ju3c = « References ». Si l'un de ces choix manque dans la liste du formulaire : « References » pour les trois. Les adresses mènent à des pages fermées jusqu'au jour J : normal.

**8. Licence incomplète.**
- Preuve : le README dit « Text and data under CC BY 4.0; code under MIT ». Le zip contient deux scripts (`tirage_public.py`, `rejeu_final_correctif.py`). Zenodo prévoit plusieurs licences sur une fiche (https://help.zenodo.org/docs/deposit/describe-records/licenses/).
- Correction : ajouter « MIT License » à côté de CC BY 4.0.

**9. Pièges dans les gestes, absents du plan.**
- Deux réglages distincts dans « Visibility » : la fiche entière et les fichiers. La fiche entière doit rester **Public** ; seuls les fichiers passent en **Restricted**. L'inverse cacherait tout.
- Compte : si Otsoa n'a pas de compte Zenodo, la connexion par ORCID en crée un et demande une adresse à confirmer par courriel. À faire par Otsoa avant tout.
- Profil : nom complet, affiliation, ORCID relié. Zenodo classe plus bas et peut ne pas indexer les fiches de comptes non vérifiés (adresse gmail) (https://support.zenodo.org/help/en-gb/2-content/235-how-does-account-verification-affect-the-indexing-of-my-uploads). Sans gravité pendant l'embargo ; à savoir.
- DOI : répondre « No » à « Do you already have a DOI ». « Get a DOI now! » est facultatif ; utile pour noter le DOI avant de publier. Supprimer le brouillon perd ce DOI.
- Communauté : aucune. Avec une communauté, le bouton devient « Submit for review ».
- Après publication : dans « Share », onglet « Access requests », les deux cases doivent être décochées. Aucun lien secret créé.
- « New version » : ne pas y toucher avant le jour J (nouveau DOI).
- Vérifier que le téléversement est fini (pas d'état « Pending »).
- Fenêtre privée après publication : relever ce que voit un inconnu, en particulier si le nom du fichier s'affiche. Non documenté. Le nom neutre prévu couvre ce cas.

**10. Répétition conseillée sur le bac à sable.**
- Preuve : Zenodo le propose : « Want to test Zenodo? Use our sandbox environment on https://sandbox.zenodo.org ».
- Intérêt : constater, avec un fichier sans valeur, que la levée anticipée marche, quelle date maximale est acceptée, et ce qui est visible pendant l'embargo. Dix à quinze minutes. Compte séparé à créer par Otsoa.
- Ne jamais y déposer le vrai zip.

**11. Le reste du projet parle encore d'OSF pour les résultats.**
- `PLAN_SUITE.md` : T41, T42, T43, Q6, Q7 et la ligne 67 (ordre du jour J) ne connaissent pas ce dépôt. À ajouter au jour J : lever l'embargo Zenodo, retirer de la description les phrases sur l'embargo, ajouter les liens vers l'article et vers l'archive du code.
- `FICHE_DEPOT.md` décrit des gestes OSF périmés. `resume_osf_texte.txt` contient le résultat : **ne jamais le coller dans Zenodo**.
- Article : oui, il faudra citer le DOI Zenodo. Aujourd'hui, « Availability and licences » et l'annexe F ne citent qu'OSF, et le README du zip promet un lien depuis l'article. Citer le **DOI de la version** (pas celui de l'ensemble des versions), dans « Availability », l'annexe F et les références. Le DOI existe dès la publication de la fiche : l'article peut le citer tout de suite.
- OSF, le jour J : ajouter le DOI Zenodo comme ressource « Data » de vycge (« A resource must have a DOI before it can be added », article 768).
- Second dépôt Zenodo prévu (code et données, T51-T52) : fiche séparée, reliée par identifiants. Ne pas en faire une « nouvelle version » de celle-ci.

**12. Recherche de secrets à refaire sur le paquet actuel.**
- Preuve : l'audit précédent a contrôlé 35 fichiers. Le zip en a 41 : sept fichiers ajoutés depuis (deux journaux, un script, quatre entrées figées), le PDF retiré. La fiche affirme « aucune clé ni mot de passe » ; je ne l'ai pas contrôlé (accès limité au README).
- Correction : avant le téléversement, relancer la recherche par motif sur le zip décompressé et noter le résultat dans la fiche.
- Données personnelles : rien d'autre, d'après le README, que l'adresse d'Otsoa et son chemin local `HOME/…`. Aucun tiers.

### Mineurs

**13.** Date de publication : mettre le jour réel du clic « Publish ». Si Otsoa dit « publie » un autre jour que le 17/11, changer la date.

**14.** Langue : « English » pour la fiche ; ajouter « French » si le champ accepte deux valeurs (les sorties sont surtout en français).

**15.** Mot-clé « replication package » : le paquet ne permet pas à lui seul de refaire l'étude. Préférer « replay outputs ».

**16.** Le plan dit « 30 à 45 jours ». Écrire : suppression et correction de fichiers par l'auteur pendant 30 jours ; ensuite support seulement.

**17.** L'adresse électronique n'a pas à figurer dans la description. Elle est déjà dans le README.

**18.** Après publication, les métadonnées partent chez DataCite et dans les moteurs. Titre, description et nom sont publics pour de bon, même si la fiche est supprimée dans les 30 jours (page « tombstone »).

## Plan corrigé

### Décisions à demander à Otsoa avant d'agir

- D1. Date d'embargo : **04/11/2030** (recommandé) ou 17/05/2027 avec rappels.
- D2. README du zip : reconstruire avec « this record » (recommandé) ou garder le zip et l'expliquer en note.
- D3. Accord pour la capture de la page publique par Internet Archive.
- D4. Répétition sur sandbox.zenodo.org : oui (recommandé) ou non.

### Valeurs à saisir

| Champ | Valeur exacte |
|---|---|
| Do you already have a DOI? | No |
| Resource type | Dataset |
| Title | `Earned Autonomy for AI Agents: outputs of the pre-registered final replay, exploratory analyses and public draw log` |
| Publication date | date du jour de la publication (2026-11-17 si publié ce jour) |
| Creators | Person ; Family name `Dubief` ; Given names `Otsoa` ; ORCID `0009-0002-7322-7575` ; affiliation en texte libre `Independent researcher` (ne pas choisir une organisation proposée) ; aucun rôle |
| Description | texte A ci-dessous |
| Additional description, type « Notes » | texte B ci-dessous |
| Licenses | `Creative Commons Attribution 4.0 International` et `MIT License` |
| Contributors | aucun |
| Keywords | `AI agents` ; `delegation` ; `earned autonomy` ; `error budget` ; `continuous sampling` ; `pre-registration` ; `replay outputs` |
| Languages | English (et French si possible) |
| Version | `1.0` |
| Publisher | laisser `Zenodo` |
| Funding, Communities, Alternate identifiers | vides |
| Related works 1 | relation `Is documented by` ; identifiant `https://osf.io/vycge/` ; schéma `URL` |
| Related works 2 | relation `Is derived from` ; identifiant `https://osf.io/cusv6/` ; schéma `URL` |
| Related works 3 | relation `References` ; identifiant `https://osf.io/7ju3c/` ; schéma `URL` |
| Visibility, Full record | **Public** |
| Visibility, Files only | **Restricted** |
| Apply an embargo | coché ; Embargo until `2030-11-04` (selon D1) |
| Embargo reason | `Files will be opened by the author when the paper is posted.` |
| Fichier | `earned_autonomy_results_2026-11-17.zip` : copie renommée de `depot_osf_resultats_2026-11-17.zip` |

Empreintes attendues du zip actuel (à recalculer si D2 = reconstruire) : SHA-256 `2c1cda3a8d920b336edcd2d067d3feeca48d63f587ddb229ef4687c920320343` ; MD5 `a29d1cfe6e83e37b2f2b39805ac00b2d` ; 3 660 253 octets.

**Texte A (description, anglais).**

> Output files of the final confirmatory replay of the pre-registered study "Earned Autonomy for AI Agents: A Pre-registered Error-Budget Test of Per-Action-Type Delegation" (OSF registrations, under embargo until the paper is posted: priority record 7ju3c, preregistration vycge, verdict freeze cusv6).
>
> The archive holds the outputs of the final replay, the exploratory analyses run after the verdict, the files and log of the public draw of the calibration/confirmation split with the frozen inputs needed to redo the draw, the logs of the replay runs, and SHA-256 fingerprints of every file. The paper is not included.
>
> The files are under embargo and will be opened when the paper is posted; no result is stated here until then. SHA-256 of the archive (earned_autonomy_results_2026-11-17.zip, 3,660,253 bytes): 2c1cda3a8d920b336edcd2d067d3feeca48d63f587ddb229ef4687c920320343. Once the files are open, anyone can check that they are the files deposited on 17 November 2026.
>
> Text and data under CC BY 4.0; code under the MIT licence.

Traduction : Fichiers de sortie du rejeu final de confirmation de l'étude préenregistrée « … » (enregistrements OSF, sous embargo jusqu'à la mise en ligne de l'article : antériorité 7ju3c, préenregistrement vycge, gel des verdicts cusv6). L'archive contient les sorties du rejeu final, les analyses exploratoires faites après le verdict, les fichiers et le journal du tirage public du partage calibration/confirmation avec les entrées figées pour le refaire, les journaux des passages du rejeu, et les empreintes SHA-256 de chaque fichier. L'article n'y est pas. Les fichiers sont sous embargo et seront ouverts à la mise en ligne de l'article ; aucun résultat n'est donné ici d'ici là. Empreinte SHA-256 de l'archive (nom, taille) : … Une fois les fichiers ouverts, chacun peut vérifier que ce sont ceux déposés le 17 novembre 2026. Textes et données sous CC BY 4.0 ; code sous licence MIT.

**Texte B (note, anglais).**

> Use of AI tools: Claude models (Anthropic), through Claude Code, were used under the author's direction to write the code that produced these outputs, to draft the documentation in the archive, and to review automated alerts; the agents evaluated in the study are also Claude models. The author takes full responsibility for all contents.

À ajouter seulement si D2 = garder le zip :

> The README in the archive was written for an OSF registration. OSF no longer accepts research outputs in registrations, so the package is deposited here unchanged: where the README says "this registration", read "this Zenodo record".

Traduction : Usage d'outils d'IA : des modèles Claude (Anthropic), par Claude Code, ont servi, sous la direction de l'auteur, à écrire le code qui a produit ces sorties, à rédiger la documentation de l'archive et à relire les alertes automatiques ; les agents évalués sont aussi des modèles Claude. L'auteur assume l'entière responsabilité du contenu. (Si D2 = garder) Le README de l'archive a été écrit pour un enregistrement OSF. OSF n'accepte plus les résultats dans ses enregistrements ; le paquet est donc déposé ici tel quel : là où le README dit « this registration », lire « cette fiche Zenodo ».

### Gestes, dans l'ordre

0. Otsoa répond à D1-D4. Si D2 = reconstruire : corriger le README, reconstruire, refaire les contrôles, mettre à jour les empreintes dans la fiche et dans le texte A.
1. Relancer la recherche de secrets par motif sur le zip décompressé. Noter le résultat.
2. Copier le zip sous le nom `earned_autonomy_results_2026-11-17.zip` dans un dossier à part. Recalculer SHA-256 et MD5 de la copie : égaux à l'original.
3. (Si D4 = oui) Répétition sur sandbox.zenodo.org avec un fichier sans valeur : embargo, publication, levée anticipée, vue en fenêtre privée, date maximale acceptée.
4. Otsoa se connecte à zenodo.org par ORCID, confirme son adresse si demandé, accepte les conditions, complète son profil. Claude ne touche à aucun mot de passe.
5. Claude ouvre « New upload », téléverse le zip renommé, attend la fin du téléversement, saisit les valeurs du tableau. Aucune communauté.
6. « Save draft ». Corriger toute erreur affichée. Ne pas publier.
7. « Preview ». Contrôler : titre, auteur et ORCID, textes A et B sans faute, deux licences, trois liens, fiche publique, fichiers restreints, date d'embargo, MD5 affiché = `a29d1cfe6e83e37b2f2b39805ac00b2d`, un seul fichier, taille juste. Relever le DOI s'il a été réservé.
8. Otsoa relit l'aperçu et la traduction. Il écrit « publie ».
9. Claude clique « Publish » et confirme. Ajuster avant la date de publication si le jour a changé.
10. Tout de suite après :
    - noter le DOI de la version, le DOI de l'ensemble des versions et l'adresse ;
    - ouvrir la fiche en fenêtre privée : métadonnées visibles, fichiers fermés, embargo affiché ; noter si le nom du fichier se voit ;
    - « Share » : onglet « Access requests » décoché, aucun lien ;
    - connecté, retélécharger le zip et comparer le SHA-256 ;
    - (si D3 = oui) faire capturer la page publique par Internet Archive ; noter l'adresse de la capture.
11. Écrire dans `FICHE_DEPOT.md` et `SUIVI.md` : DOI, adresse, heure UTC, empreintes, date d'embargo, et la règle « ne jamais modifier les fichiers de cette fiche ». Mettre à jour `PLAN_SUITE.md` (T41 à T43, Q6, Q7, ordre du jour J) et l'article (DOI dans « Availability », annexe F, références). Aucun commit sans accord.
12. Après le 31e jour (18/12/2026) : seconde capture par Internet Archive.

### Le jour J (à inscrire dans T43)

1. Fiche Zenodo : « Edit » ; fichiers en « Public » ; embargo décoché ; retirer du texte A les deux mentions de l'embargo ; ajouter le lien vers l'article (`Is supplement to`, DOI de la prépublication) et vers l'archive du code ; « Publish ». Le DOI ne change pas.
2. Fenêtre privée : le zip se télécharge sans connexion ; SHA-256 identique.
3. OSF : après la levée des embargos, ajouter le DOI Zenodo comme ressource « Data » de vycge ; remplacer dans Zenodo les adresses OSF par leurs DOI.
4. Si l'étape 1 échoue : « New version » avec le même zip en accès public, ou support Zenodo.
