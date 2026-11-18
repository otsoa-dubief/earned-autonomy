# Dépôt des résultats : fiche (17/11/2026)

**Publié sur Zenodo le 17/11/2026 à 17:49:13 UTC** (OSF n'accepte plus de résultats dans ses enregistrements ; voir `ZENODO_PLAN.md` et les audits `revues/2026-11-17_audit_plan_zenodo.md`, `revues/2026-11-17_audit_brouillon_zenodo.md`).

- **Fiche** : https://zenodo.org/records/24321214 ; **DOI de la version** : 10.5281/zenodo.24321214 ; DOI de l'ensemble des versions : 10.5281/zenodo.24321213. Déposé par Claude dans le navigateur d'Orca, sur le compte Zenodo d'Otsoa (connexion ORCID), avec son accord (« Publie »).
- **Fichier** : `earned_autonomy_results_2026-11-17.zip` (copie renommée de `depot_osf_resultats_2026-11-17.zip`), SHA-256 `7e8f8a7d9ac92d3a1f7a961c53c17d872f8cfdf5a98744c4a29400ed1f5be6b3`, MD5 `23551142e7c0fd2c4c0c52fe23493619`, 3 660 293 octets, 41 fichiers. Retéléchargé après publication : SHA-256 identique.
- **Accès** : fiche publique ; fichiers restreints, **embargo jusqu'au 04/11/2030**, motif « Files will be opened by the author when the paper is posted. » ; à ouvrir à la main le jour J. Vue anonyme vérifiée : aucun nom de fichier, API des fichiers « Permission denied », téléchargement renvoyé vers la connexion. Demandes d'accès (connectés et anonymes) décochées ; aucun lien de partage.
- **Règle** : ne jamais utiliser « Edit published files » sur cette fiche ; pas de « New version » avant le jour J.
- **Capture Internet Archive** : refusée le 17/11 (« Job failed », deux essais) ; à retenter, et seconde capture prévue après le 18/12/2026.
- **Le jour J** : fichiers en public, embargo décoché, retirer de la description les mentions de l'embargo, ajouter le lien vers l'article (Is supplement to) et vers l'archive du code ; vérifier le téléchargement anonyme et l'empreinte ; sur OSF, ajouter le DOI Zenodo comme ressource « Data » de vycge.

---

## Historique : préparation pour OSF (abandonnée)

# Dépôt OSF des résultats : fiche (PLAN_SUITE T40, 17/11/2026 ; corrigée après l'audit `revues/2026-11-17_audit_depot_resultats.md`)

**Rien n'est déposé.** La soumission est la tâche T41 et demande l'accord écrit d'Otsoa (question Q6). Rappel R12 : après l'approbation de l'embargo, on ne peut plus annuler.

- **Paquet** : `paquet/`, 41 fichiers (40 plus `SHA256SUMS.txt`), construit par `outils/construire_depot_resultats.py depots/2026-11-17_resultats` ; reconstruit deux fois, même zip. Le PDF de l'article n'y est plus (il peut encore changer ; il ira sur OSF Preprints).
- **Zip à joindre** : `depot_osf_resultats_2026-11-17.zip`, SHA-256 `2c1cda3a8d920b336edcd2d067d3feeca48d63f587ddb229ef4687c920320343` ; décompressé, tous les fichiers passent `SHA256SUMS.txt` ; aucune clé ni mot de passe ; aucun fichier de `donnees/`, `pilote/`, `data/` ni des dossiers de vague (le manifeste les cite par empreinte seulement, comme dans cusv6).
- **Journal du tirage** : `JOURNAL_TIRAGE.md`. `impulsion.json` commence par fa61235b et `partage.json` par 76e04fca. `tirage_public.py verifier --en-ligne` le 17/11 : « tirage vérifié ».
- **Résumé OSF** : `resume_osf_texte.txt`, texte brut sans chevrons ni esperluettes.

## Traduction française du résumé OSF

Dépôt des résultats de l'étude préenregistrée « Earned Autonomy for AI Agents: A Pre-registered Error-Budget Test of Per-Action-Type Delegation » (antériorité 7ju3c, préenregistrement vycge, gel des verdicts cusv6). Étiquette préenregistrée : R4. Aucune des douze configurations (trois modèles Claude 5.5 sur quatre bancs publics : τ-bench aviation, commerce et banque, et WorkBench) n'a atteint le niveau de preuve fixé à l'avance pour qu'on lui délègue des actions. Une seule avait assez de volume pour être jugée : son taux d'erreurs, 8,6 % (borne basse 4,1 %), est établi au-dessus de son seuil de 0,76 %. Les onze autres n'avaient pas assez de volume pour conclure. La règle n'est pas réfutée, mais elle a peu été mise à l'épreuve, et son utilité n'a pas pu être jugée. Le paquet contient les sorties du rejeu final, les analyses exploratoires faites après le verdict (datées du 17/11/2026, sans effet sur l'étiquette), les fichiers et le journal du tirage public (impulsion NIST 2031457), les journaux des deux passages du rejeu avec la note sur le correctif en mémoire, et les entrées figées pour refaire le tirage. L'article n'y est pas : il sera déposé sur OSF Preprints, avec un lien vers cet enregistrement. Contrôle : shasum -a 256 -c SHA256SUMS.txt. Textes et données sous CC BY 4.0.

## Traduction française du README (résumé)

Comment lire : `replay/` = sorties du rejeu final (écrites en français par le moteur ; « témoin battu » y est le libellé d'un critère, pas un résultat : sous R4 le point 2 n'est pas jugé) ; `exploratory/` = analyses après le verdict ; `draw/` et le journal = tirage public et ses entrées figées ; deux journaux du rejeu (premier passage en échec, second réussi avec le correctif en mémoire, étiquette indépendante du correctif, six tables identiques) ; deux commits dans le journal (le second n'ajoute que la déclaration de l'échec et du correctif) ; `SHA256SUMS.txt` fait foi, l'ancienne liste de 13 h 28 ne correspond plus à `RESUME.md`. Commande exacte du rejeu final recopiée. Sorties surtout en français ; chemins locaux de l'auteur dans quelques fichiers.

## Gestes prévus pour T41 (en français)

0. Le jour même, relire en ligne l'aide d'OSF sur les enregistrements et les embargos (l'audit signale que les projets existants passeront en lecture seule le 19/02/2027 et qu'on ne pourra plus y créer d'enregistrement : à confirmer).
1. Sur le projet OSF (bd4g5), créer un enregistrement « Open-Ended Registration » intitulé « Earned autonomy for AI agents: results of the pre-registered replay ».
2. Coller le résumé de `resume_osf_texte.txt` ; licence CC BY 4.0 ; mots-clés du projet.
3. Joindre le zip ; vérifier son empreinte après téléversement.
4. Option retenue en Q6. Si embargo : date de fin le **04/11/2030** (comme les autres), levé à la main le jour J (T43) ; un embargo se lève de lui-même à sa date.
5. Soumettre. OSF envoie un courriel d'approbation (48 h pour annuler, ensuite plus jamais) : **ne pas approuver** avant d'avoir retéléchargé le zip archivé, comparé l'empreinte et relu le résumé sur le serveur.
6. Lire l'état par l'API d'OSF ; noter l'identifiant et `date_registered` ici et dans `SUIVI.md`.
