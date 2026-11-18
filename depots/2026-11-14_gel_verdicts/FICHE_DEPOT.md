# Dépôt OSF du gel des verdicts : fiche pour Otsoa

Préparée le 14/11/2026. À soumettre par Otsoa. **L'heure de soumission affichée par OSF lance le délai de 72 heures avant le tirage.**

## Ce qu'on dépose

- `depot_osf_gel_verdicts_2026-11-14.zip` (3,2 Mo), SHA-256 `10c40d40ef4d0a2f8f65db7791c7c099484a72f7eef59173abd1365eb2a1ff1a`. Il contient :
  - `manifeste_verdicts.txt` : les empreintes des 68 990 fichiers de l'expérience. Son empreinte, `f2347d87…3c97`, entre dans la graine du tirage ;
  - `gel_plan.json` : le lien avec le plan gelé du 09/11 ;
  - `README.md` : l'explication en anglais (traduction ci-dessous) ;
  - `SHA256SUMS.txt` : les empreintes des trois fichiers.
- Aucune donnée : seulement des empreintes.

## Les gestes, dans l'ordre

1. Ouvrir le projet OSF *Earned autonomy for AI agents* (https://osf.io/bd4g5/).
2. Déposer le zip dans l'onglet **Files** du projet (OSF Storage), dans un dossier `gel_verdicts_2026-11-14`.
3. Cliquer sur **Registrations**, puis **New registration**, et choisir le modèle **Open-Ended Registration**.
4. Remplir :
   - **Title** : `Earned autonomy for AI agents: freeze of the confirmed verdicts before the public draw`
   - **Description** : `Freeze, by SHA-256 fingerprints, of every input of the final confirmatory computation of the study preregistered at https://osf.io/vycge/, before the public random draw of the calibration and confirmation sets.`
   - **Summary** (le seul champ du formulaire) : le texte de `resume_osf_texte.txt`. C'est le `README.md` en texte brut, sans les symboles Markdown (dièses, astérisques, accents graves), parce qu'OSF affiche ce champ tel quel. Changé le 14/11, à la remarque d'Otsoa.
   - **Category** : Project. **License** : CC-By Attribution 4.0 International. **Subjects** : Artificial Intelligence and Robotics. **Tags** : `preregistration`, `AI agents`, `earned autonomy`, `verdict freeze`.
   - Joindre le zip déposé à l'étape 2 (il doit apparaître dans les fichiers de la registration).
5. **Embargo** : oui, jusqu'au **4 novembre 2030**, comme les deux dépôts précédents.
6. Soumettre. OSF demande parfois d'approuver l'embargo par e-mail : approuver.
7. **Me donner** l'identifiant de la registration (osf.io/xxxxx) et l'heure de soumission affichée (avec le fuseau). Je recalcule l'heure du tirage et je vérifie sur le serveur que le zip déposé a bien l'empreinte ci-dessus.

## Traduction du texte déposé (pour savoir ce que tu signes)

**Titre.** Autonomie méritée pour les agents IA : gel des verdicts confirmés.

Cet enregistrement fige, par leurs empreintes SHA-256, toutes les entrées du calcul confirmatoire final de l'étude préenregistrée sur https://osf.io/vycge/ (préenregistrement OSF du 10 novembre 2026). Il est fait après la dernière vague de collecte et avant le tirage public qui partage les tâches réservées entre calibration et confirmation (plan, section 3.4). Les données elles-mêmes n'en font pas partie. Elles seront publiées avec les résultats, et chacun pourra les comparer aux empreintes déposées ici.

**Fichiers.**
- `manifeste_verdicts.txt` contient une ligne « empreinte  chemin » par fichier, soit 68 990 fichiers :
  - toute la production des deux vagues : traces des parties, actions typées, verdicts par action, coûts, journaux des tentatives, plans de jeu, réussite des tâches ;
  - la relecture de chaque alerte : 2 529 en vague 2 et 232 en vague 1, avec les décisions, les correspondances, les journaux, les tirages à l'aveugle et les accords, gardés à 13 sur 15 dans les deux vagues ;
  - les retraits de tâches défectueuses avec l'opposition de l'auteur : 13 retirées, 1 gardée ;
  - l'audit des tâches sans alerte : 20 tâches, aucun retrait.
  
  Son empreinte est donnée.
- `gel_plan.json` donne le commit du dépôt au moment du manifeste et l'empreinte du manifeste du plan gelé, identique à celle déposée avec le préenregistrement (étiquette `gel-2026-11-09`).

**Le tirage que cet enregistrement fixe.**
- **Le nombre désigné :** la première impulsion de la balise du NIST (version 2.0) datée d'au moins 72 heures après l'horodatage de soumission de cet enregistrement, tel qu'OSF l'affiche.
- **Le secours :** si le NIST ne publie aucune impulsion dans l'heure qui suit, on prend le premier tour de drand (réseau quicknet) publié à partir de l'heure désignée. Le tirage se lance au plus tôt une heure après l'heure désignée.
- **La graine :** l'empreinte de l'étiquette fixe, de l'empreinte du manifeste et du nombre publié. Dans chaque strate, les paires de tâches figées se partagent par rang.
- **Les scripts figés :** leurs empreintes sont données.

Le journal du tirage sera déposé avec les résultats, et chacun pourra refaire le tirage.

**Écarts depuis le préenregistrement**, datés dans `JOURNAL_CHANGEMENTS.md`, à déclarer dans l'article :
- la page simplifiée pour ta relecture à l'aveugle ;
- le message vide de l'agent, compté comme une panne puis exclu, ce qui biaise vers la délégation ;
- l'incident de reprise de la vague 2, sans effet sur les verdicts ;
- la relecture de la vague 2 faite par Opus 5.5, modèle noté, alors que celui de la vague 1 ne l'avait pas été.

Auteur : Otsoa Dubief (chercheur indépendant), ORCID 0009-0002-7322-7575. Préparé avec l'aide de Claude (Anthropic).

## Fait (14/11/2026)

- Soumis par Claude dans le navigateur d'Orca, sur la session d'Otsoa (Otsoa s'est connecté lui-même), après son accord explicite (QCM).
- **Registration : https://osf.io/u26kr/** (Open-Ended Registration), **soumise le 2026-11-14 à 06:44:26.304408 UTC**. Embargo jusqu'au 2030-11-04 ; approbation de l'embargo en attente (e-mail d'OSF, ou automatique sous 48 heures).
- Vérifié sur le serveur : titre, description, licence CC-BY 4.0, 4 mots-clés, résumé identique à `resume_osf_texte.txt`, fichier joint `depot_osf_gel_verdicts_2026-11-14.zip` archivé avec le SHA-256 `10c40d40…1a`. Le zip archivé a été retéléchargé : son SHA-256 est recalculé à l'identique, ses trois fichiers passent `SHA256SUMS.txt`, et `manifeste_verdicts.txt` est identique octet pour octet à `experience/manifeste_verdicts.txt`.
- **Heure désignée du tirage** (calculée par `tirage_public.py heure`) : **2026-11-17T06:44:26.304Z** (07 h 44 à Paris). NIST : première impulsion datée d'au moins cette heure, https://beacon.nist.gov/beacon/2.0/pulse/time/1794897900000 ; secours drand : tour 34031501. Le tirage se lance au plus tôt une heure après, soit le 17/11 à partir de 07:44 UTC (08 h 44 à Paris).
