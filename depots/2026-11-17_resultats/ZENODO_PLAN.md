# Plan du dépôt Zenodo des résultats (17/11/2026) — à auditer avant toute action

Contexte : OSF n'accepte plus de résultats dans ses enregistrements (page « Add New Registration », lue le 17/11 : « Unacceptable submissions […] Any other research outputs (e.g., data) that are not part of the research plan »). Le paquet des résultats (`depot_osf_resultats_2026-11-17.zip`, voir `FICHE_DEPOT.md`) va donc sur Zenodo, déposé par Claude dans le navigateur d'Orca, sur le compte d'Otsoa, avec son accord. Rien n'est publié sans un « publie » explicite d'Otsoa.

Règles Zenodo lues le 17/11 (help.zenodo.org) : métadonnées toujours publiques ; accès « restricted » + « Apply an embargo » : fichiers cachés, ouverts automatiquement à la date choisie à minuit UTC ; DOI attribué à la publication ; fichiers et DOI non modifiables après publication (modification de fichiers ou suppression seulement dans les 30 à 45 jours, puis via le support) ; nouvelle version = nouveau DOI.

## Métadonnées proposées

- **Resource type** : Dataset.
- **Title** : « Earned autonomy for AI agents: outputs of the pre-registered replay (files under embargo until publication) ».
- **Creators** : Dubief, Otsoa — ORCID 0009-0002-7322-7575 — affiliation : Independent researcher.
- **Description (publique, neutre, sans le résultat)** : « Output files of the final confirmatory replay of a pre-registered study of an earned-autonomy rule for AI agents (OSF: priority record 7ju3c, preregistration vycge, verdict freeze cusv6). The package holds the replay outputs, the exploratory analyses run after the verdict, the files and log of the public draw of the calibration/confirmation split, the logs of the replay runs, the frozen inputs needed to redo the draw, and SHA-256 fingerprints of every file. The files are under embargo until the paper is posted; the deposit date and the fingerprints attest that the outputs did not change while the paper was written. SHA-256 of the archive: [empreinte du zip]. »
- **Publication date** : 2026-11-17.
- **Licence** : Creative Commons Attribution 4.0 International.
- **Keywords** : AI agents ; delegation ; earned autonomy ; error budget ; continuous sampling ; pre-registration ; replication package.
- **Related works** : « is supplement to » / « references » : https://osf.io/vycge/ et https://osf.io/cusv6/ (identifiants OSF) ; pas encore de lien vers l'article (il viendra en nouvelle métadonnée le jour J, les métadonnées restant modifiables).
- **Language** : English.
- **Version** : 1.0.
- **Communities** : aucune.
- **Access** : record public (métadonnées), files restricted, **embargo** jusqu'au **17/05/2027** (six mois ; date à valider par Otsoa ; si l'article sort avant, on tente de rendre les fichiers publics en éditant la visibilité, ce que la documentation ne confirme pas clairement).
- **Fichier** : le zip seul (`depot_osf_resultats_2026-11-17.zip`, 41 fichiers), sous un nom neutre : `earned_autonomy_results_2026-11-17.zip` (même contenu, même empreinte).

## Gestes

1. Otsoa se connecte (ORCID) et accepte les conditions ; Claude ne touche à aucun mot de passe.
2. Claude crée le dépôt, remplit les métadonnées, téléverse le zip, règle l'accès et l'embargo, enregistre le brouillon (« Save draft »), sans publier.
3. Claude vérifie l'aperçu : métadonnées, empreinte affichée (MD5 côté Zenodo) comparée à celle du fichier local, embargo et date.
4. Otsoa relit l'aperçu et dit « publie ». Claude publie, puis note le DOI et l'adresse dans `FICHE_DEPOT.md` et `SUIVI.md`, et vérifie la page publique (métadonnées visibles, fichiers cachés).
