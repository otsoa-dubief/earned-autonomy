# Audit du brouillon Zenodo des résultats (17/11/2026, 18 h 40, heure de Paris)

Objet : brouillon non publié n° 24321214 sur le compte Zenodo d'Otsoa. Auditeur indépendant. Aucun fichier existant modifié. Aucune action sur un site. Aucun dossier interdit ouvert.

Pièces lues : l'export du brouillon (`zenodo_brouillon_24321214.json`, révision 11, modifié à 17:35:47 UTC), `zenodo_brouillon_fichiers.json`, la capture `zenodo_apercu.png`, le « Plan corrigé » de `revues/2026-11-17_audit_plan_zenodo.md`, le zip local et `paquet/`.

Pages web lues le 17/11/2026 : aide de Zenodo (create-new-upload), référence des métadonnées InvenioRDM (le logiciel de Zenodo), et, pour constater ce que voit un inconnu, une fiche publique sous embargo d'un autre déposant (zenodo.org/records/24319741 et la réponse publique de l'API).

## En bref

- **Feu vert.** Aucun constat bloquant. Le brouillon est conforme au « Plan corrigé » et aux décisions D1 à D4, champ par champ.
- Le zip téléversé est bien le nouveau zip (README reconstruit) : MD5, taille et SHA-256 concordent.
- Rien de public ne révèle le résultat. Pendant l'embargo, un visiteur ne voit ni le nom du fichier ni la liste interne du zip.
- Une condition : **publier aujourd'hui, avant minuit (heure de Paris)**. Sinon, deux retouches (constat 1).
- Trois écritures locales sont en retard sur le dépôt (constats 2 à 4). Elles ne changent rien à ce qui sera publié.

## Tableau champ par champ

| Champ | Attendu | Constaté | Verdict |
|---|---|---|---|
| Type | Dataset | `dataset` | Conforme |
| Titre | `Earned Autonomy for AI Agents: outputs of the pre-registered final replay, exploratory analyses and public draw log` | Identique, caractère pour caractère | Conforme |
| Date de publication | Jour réel du clic (2026-11-17 si publié ce jour) | `2026-11-17` | Conforme si publié aujourd'hui (constat 1) |
| Auteur, nom | Personne ; Dubief ; Otsoa | `Dubief, Otsoa`, type `personal` | Conforme |
| Auteur, ORCID | `0009-0002-7322-7575` | Identique ; chiffre de contrôle recalculé : juste ; pastille ORCID visible sur l'aperçu | Conforme |
| Auteur, affiliation | Texte libre `Independent researcher` | Identique, sans identifiant d'organisation ; aucun rôle | Conforme |
| Contributeurs | Aucun | Champ absent | Conforme |
| Description (texte A) | Texte A, avec l'empreinte et la taille du nouveau zip | Quatre paragraphes identiques au texte A (comparaison automatique). Taille `3,660,293 bytes`. SHA-256 `7e8f8a7d…5be6b3`. Aucune adresse électronique. | Conforme |
| Note IA (texte B) | Texte B, type « Notes » | Identique ; type `notes` ; une seule note ; pas de phrase sur l'ancien README (normal : D2 = reconstruire) | Conforme |
| Licences | CC BY 4.0 et MIT | `cc-by-4.0` et `mit` | Conforme |
| Mots-clés | Les sept du plan | Les sept, mêmes mots, même ordre | Conforme |
| Langues | English (et French si possible) | `eng`, `fra` | Conforme |
| Version | `1.0` | `1.0` | Conforme |
| Éditeur | `Zenodo` | `Zenodo` | Conforme |
| Lien 1 | `Is documented by` ; `https://osf.io/vycge/` ; URL | Identique | Conforme |
| Lien 2 | `Is derived from` ; `https://osf.io/cusv6/` ; URL | Identique | Conforme |
| Lien 3 | `References` ; `https://osf.io/7ju3c/` ; URL | Identique | Conforme |
| Liens, « Resource type » | Non prévu par le plan | Vide pour les trois | Sans gravité (constat 5) |
| Financement, identifiants alternatifs | Vides | Absents | Conforme |
| Accès, fiche | Public | `record: public` | Conforme |
| Accès, fichiers | Restricted | `files: restricted` | Conforme |
| Embargo | Coché, `2030-11-04` (D1) | `active: true`, `until: 2030-11-04` ; l'aperçu affiche « November 4, 2030 » | Conforme |
| Motif d'embargo | `Files will be opened by the author when the paper is posted.` | Identique | Conforme |
| Demandes d'accès, liens secrets | Aucun | `allow_user_requests: false`, `allow_guest_requests: false`, `links: []`, `grants: []` | Conforme |
| DOI | Rien de réservé ; « No, I need one » | `pids: {}` : aucun DOI réservé, aucun DOI extérieur saisi | Conforme |
| Communauté | Aucune | `communities: {}` ; l'aperçu dit « not included in any communities » | Conforme |
| Fichier, nombre | Un seul | `count: 1` | Conforme |
| Fichier, nom | `earned_autonomy_results_2026-11-17.zip` | Identique | Conforme |
| Fichier, MD5 | `23551142e7c0fd2c4c0c52fe23493619` | Identique côté Zenodo ; recalculé par moi sur le zip local : identique | Conforme |
| Fichier, taille | 3 660 293 octets | `3660293` | Conforme |
| Fichier, téléversement | Terminé | `status: completed` | Conforme |

## Contrôles du zip (refaits par moi)

| Contrôle | Résultat |
|---|---|
| SHA-256 du zip local | `7e8f8a7d9ac92d3a1f7a961c53c17d872f8cfdf5a98744c4a29400ed1f5be6b3` : égal à l'attendu et à la description. |
| MD5 et taille | `23551142e7c0fd2c4c0c52fe23493619`, 3 660 293 octets : égaux à ce que Zenodo a reçu. Le fichier en ligne a donc le même contenu que le zip local. |
| Contenu | 41 fichiers. Zip décompressé dans un dossier à part : identique à `paquet/`. Aucun `.DS_Store`, aucun `__MACOSX`. Dates neutralisées. Aucun fichier binaire. |
| Empreintes internes | Les 40 lignes de `SHA256SUMS.txt` passent toutes. |
| README (D2) | Dit bien « Zenodo record » et « this record ». Plus aucune mention d'un enregistrement OSF pour ce dépôt. |
| Secrets | Recherche par motif (clés Anthropic, OpenAI, GitHub, AWS, Google, Slack, jetons, clés privées, « password », « secret », « token », « api key ») : **0 résultat**, y compris dans le manifeste de 68 990 lignes. |
| Données personnelles | Une seule adresse : celle d'Otsoa (README). 22 fois le chemin local `HOME/…` (déclaré dans le README). Aucun autre nom, aucun autre courriel, aucun téléphone, aucune adresse IP. **Aucun tiers.** |
| Manifeste | Ne contient que des empreintes et des noms de fichiers (tâches des bancs publics, journaux, fiches de relecture). Aucun contenu de `donnees/` ni des vagues. |

## Le résultat est-il révélé pendant l'embargo ?

**Non.**

- Titre, description, note, mots-clés, liens, motif d'embargo : aucun ne contient R4, un taux (8,6 ; 0,76 ; 4,1), « douze », « aucune configuration », ni une formule de `article/FORMULATION_VERDICT.md`. Contrôle automatique puis lecture.
- La liste interne du zip, visible sur la capture, n'est montrée qu'à l'auteur connecté. Constat sur une fiche sous embargo d'un autre déposant, lue sans connexion : la partie « Files » n'affiche que « Embargoed », la date et le motif. Ni nom de fichier, ni taille, ni empreinte, ni aperçu. L'API publique rend une liste de fichiers vide.
- Même si ces noms étaient vus un jour : ils ne donnent pas le résultat. Ils disent seulement qu'un premier passage a échoué (`replay_run1_failed.log`) et quels sujets ont été explorés. Le nom du zip est neutre.
- Le résultat (« R4 ») est dans le zip (README, `RESULTATS.md`, journal). C'est voulu : le zip est fermé.
- La description donne la taille et l'empreinte du zip. On ne peut rien en déduire.
- À confirmer quand même sur la vraie fiche, en fenêtre privée, juste après la publication (geste 2).

## Constats

### Bloquants

Aucun.

### Importants

**1. La date ne vaut que pour aujourd'hui.**
- La date de publication (`2026-11-17`) et la phrase « deposited on 17 November 2026 » sont justes seulement si le clic a lieu le 17/11.
- Zenodo horodate en temps universel : le 18 commence à 1 h du matin à Paris.
- Correction : publier avant minuit, heure de Paris. Sinon, avant de publier, changer la date de publication **et** la phrase du texte A (et sa traduction) pour le jour réel.

**2. `FICHE_DEPOT.md` est périmée.**
- Elle dit « Rien n'est déposé », décrit des gestes OSF, et donne l'ancienne empreinte du zip (`2c1cda3a…`). Le zip a changé (D2).
- Risque : quelqu'un compare un jour le zip à la mauvaise empreinte et croit à une altération.
- Correction, juste après la publication : y écrire le dépôt Zenodo, la nouvelle empreinte SHA-256 `7e8f8a7d…5be6b3`, le MD5, la taille, le DOI, l'adresse, l'heure UTC, la date d'embargo, et la règle « ne jamais modifier les fichiers de cette fiche ». Marquer les gestes OSF comme abandonnés.

**3. Le script qui a construit le zip n'est pas enregistré dans git.**
- `outils/construire_depot_resultats.py` (nouveau README) et `SHA256SUMS.txt` sont modifiés mais non validés.
- Risque : sans ces deux modifications, on ne peut plus reconstruire le même zip.
- Correction : les valider (commit) avec l'accord d'Otsoa, avec `ZENODO_PLAN.md`, les exports du brouillon et les deux audits.

**4. Le zip local n'est sauvegardé nulle part.**
- `.gitignore` exclut `*.zip` et `paquet/`. Les seules copies sont sur ce disque et, fermée, sur Zenodo.
- Correction : en garder une copie ailleurs. L'auteur connecté peut aussi le retélécharger depuis Zenodo.

### Mineurs

**5. « Resource type » vide dans les liens : pas un problème.**
- Référence des métadonnées du logiciel de Zenodo : dans un lien, `identifier`, `scheme` et `relation_type` sont obligatoires ; `resource_type` est facultatif (cardinalité 0-1).
- Le brouillon a été enregistré ainsi, et l'aperçu s'affiche sans message d'erreur.
- Ce champ décrirait la nature de la page liée. Aucun choix ne s'impose pour un enregistrement OSF. Le laisser vide est le plus juste.
- Si le bouton « Publish » refusait quand même : rien n'est publié dans ce cas. Choisir alors « Other » pour les trois liens, enregistrer, revérifier l'aperçu, puis publier.

**6. L'export date de 17:35 UTC.**
- Je n'ai contrôlé que cet export et la capture, pas le site.
- Correction : juste avant le clic, rouvrir l'aperçu et vérifier qu'il est identique à la capture (titre, embargo au 4 novembre 2030, un fichier, même MD5).

**7. Ordre des liens.** L'aperçu affiche cusv6 avant vycge. Sans conséquence.

**8. DOI affiché dans l'aperçu.** « 10.5281/zenodo.24321213 » est le DOI de l'ensemble des versions. Il n'existe qu'après publication. Le DOI de la version sera très probablement `10.5281/zenodo.24321214` : à lire sur la fiche publiée, pas à deviner. C'est celui-là que l'article citera.

**9. Compte.** Je n'ai pas pu vérifier le profil du compte (adresse confirmée, ORCID relié). Sans effet sur la publication ; peut jouer sur l'indexation.

**10. Rappel.** Titre, description et nom d'auteur deviennent publics pour de bon, et partent chez DataCite. Les relire une dernière fois sur l'aperçu. `resume_osf_texte.txt` contient le résultat : ne jamais le coller dans Zenodo.

## Feu vert ou non pour publier

**Feu vert**, à deux conditions simples :

1. Publier le 17/11/2026 avant minuit, heure de Paris (sinon constat 1).
2. Rouvrir l'aperçu juste avant le clic et constater qu'il n'a pas changé (constat 6).

Aucune correction du brouillon n'est nécessaire. Ne rien modifier d'autre : ni communauté, ni DOI réservé, ni type de ressource des liens.

## Gestes après la publication

### Tout de suite

1. Noter : DOI de la version, DOI de l'ensemble des versions, adresse de la fiche, heure UTC de publication.
2. Fenêtre privée, sans connexion : la fiche s'ouvre ; titre, description, note, licences, liens visibles ; « Embargoed » et « November 4, 2030 » affichés ; **aucun nom de fichier, aucune liste du zip, aucun bouton de téléchargement**. Noter ce qui est vu. Si un nom interne apparaissait : le signaler à Otsoa avant toute autre action.
3. Connecté, onglet « Share » : « Access requests » décoché des deux côtés ; aucun lien secret.
4. Connecté : retélécharger le zip ; SHA-256 = `7e8f8a7d9ac92d3a1f7a961c53c17d872f8cfdf5a98744c4a29400ed1f5be6b3`.
5. D3 : faire capturer la page publique par Internet Archive (« Save Page Now ») ; noter l'adresse de la capture.
6. Écrire dans `FICHE_DEPOT.md` et `SUIVI.md` : tout le point 1, les empreintes, la date d'embargo, l'adresse de la capture, la règle « ne jamais utiliser Edit published files ni New version avant le jour J » (constat 2).
7. Mettre à jour `PLAN_SUITE.md` : T41 (le dépôt est sur Zenodo, plus sur OSF), T42 (ajouter la fiche Zenodo à l'inventaire), T43 (gestes du jour J ci-dessous), Q6, Q7, ordre du jour J (ligne 67).
8. Article : citer le DOI de la version dans « Availability and licences », l'annexe F et les références.
9. Sauvegarder le zip (constat 4). Valider les fichiers dans git avec l'accord d'Otsoa (constat 3).

### Le 18/12/2026 (31e jour)

10. Seconde capture par Internet Archive. À partir de là, l'auteur ne peut plus changer les fichiers seul.

### Le jour J (à inscrire dans T43)

11. Fiche Zenodo, « Edit » : fichiers en « Public » ; embargo décoché ; retirer du texte A les deux mentions de l'embargo (parenthèse du premier paragraphe à adapter, première phrase du troisième) ; ajouter le lien vers l'article (`Is supplement to`, DOI de la prépublication) et vers l'archive du code ; « Publish ». Le DOI ne change pas.
12. Fenêtre privée : le zip se télécharge sans connexion ; SHA-256 identique.
13. OSF, après la levée des embargos : ajouter le DOI Zenodo comme ressource « Data » de vycge ; dans Zenodo, remplacer les trois adresses OSF par leurs DOI.
14. Si le geste 11 échoue : « New version » avec le même zip en accès public (nouveau DOI ; la version 1 reste la preuve de date), ou écrire au support de Zenodo.

## Limites de cet audit

- Je n'ai vu ni le formulaire ni le site : seulement l'export, la liste des fichiers et la capture.
- La visibilité pendant l'embargo est constatée sur la fiche d'un autre déposant, pas sur celle-ci (elle n'existe pas encore en public). D'où le geste 2.
- L'aide de Zenodo ne dit pas, en toutes lettres, ce qu'un visiteur voit des fichiers sous embargo.
