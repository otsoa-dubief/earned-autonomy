# Relecture indépendante · plan d'exploration E1 (4 novembre 2026)

> Relecteur : agent sans accès aux échanges qui ont produit le plan.
> Lu : `simulation/PLAN_EXPLORATION_E1.md`, `REGLE.md`, `simulation/PLAN_SIMULATION.md`, `simulation/resultats/RESULTATS.md` (résumé, verdicts, limites, choix), `reports/Plans de Dodge pour agents IA.md`, `config.py`, `regle.py`, `temoins.py`, `mesures.py`, `flux.py`, `executer.py`, `explorations/verif_barre_2026-11-04.py`, `SUIVI.md` (état).
> Pas ouvert : `donnees/` (ni la note scellée, ni rien d'autre).
> Méthode : formules refaites en Python, en fractions exactes. Moteur v2 lancé hors du dépôt pour mesurer les épreuves. Petite simulation de la règle des séries. Aucun fichier du dépôt modifié, sauf celui-ci. Aucun appel réseau.
> Balises : [calcul] dérivé ou vérifié ici ; [moteur] mesuré avec le code existant ; [lecture] tiré des documents.

## STATUT

- **Verdict : lançable après corrections.** La structure est saine : quatre règles, même flux, critère éliminatoire puis charge, règle de choix écrite avant. Les corrections sont ciblées, sans refonte.
- 2 bloquants, 11 importants, 12 mineurs.
- Tel quel, l'issue la plus probable est « aucune règle » ou « B-tout par élimination ». Ce serait pour des raisons de comptabilité et de formule, pas de politique d'autonomie (voir le pronostic).

## Formules recalculées

Barres : **toutes justes** [calcul]. Bureau 1/39,9 ; 1/304 ; 1/2 584. Service client 1/15,2 ; 1/418 ; 1/4 408.

| | bureau faible | bureau moyen | bureau fort | SC faible | SC moyen | SC fort |
|--|--|--|--|--|--|--|
| B-régulier, plan | 15 | 117 | 1 000 | 5 | 161 | 1 707 |
| B-régulier, « 0,37 » à la lettre | 15 | 118 | 1 006 | 5 | 162 | 1 716 |
| B-régulier, exact : plus petit N avec N^N/(N+1)^(N+1) ≤ d·barre | 15 | 118 | 1 001 | **6** | 162 | 1 707 |
| B-tout, plan | 42 | 320 | 2 719 | 15 | 440 | 4 640 |
| B-tout, exact (fractions) : N = 1/(d·barre) − 1 | 41 | 319 | 2 719 | 15 | 439 | 4 639 |
| B-tout, flottants puis `ceil` (parts sommées depuis `config.py` ; le bruit dépend de l'ordre des opérations) | 41 | 319 | **2 720** | **16** | 439 | **4 640** |
| A½ : réussites depuis L = 0 (α = 5 %) | 231 | 1 786 | 15 213 | 86 | 2 458 | 25 954 |
| A¼ : réussites depuis L = 0 | 155 | 1 192 | 10 143 | 58 | 1 639 | 17 303 |
| A½ : après une erreur moyenne ou forte (L = a) | — | 2 207 | 18 794 | — | 3 036 | 32 064 |
| A¼ : après une erreur moyenne ou forte | — | 1 752 | 14 918 | — | 2 411 | 25 450 |
| vérifiables par type, 3 000 actions | ECR 427, MSG 171 | DUR 228, EXE 228 | SOR 274, ARG 114 | ECR 142, MSG 85 | DUR 570, EXE 57 | SOR 342, ARG 319 |

- 1/(d·barre) vaut pile 100 × part ÷ budget (42 ; 320 ; 2 720 ; 16 ; 440 ; 4 640), puisque d = 0,95 = 1 − e. Ce sont des entiers exacts, d'où le piège des flottants.
- Lorden : 717 observations pour 0,5 % → 2 % avec une fausse alerte toutes les 10 000 actions. **Juste** [calcul].
- À 150 000 actions, il y a 50 fois plus de vérifiables. A½ n'atteint jamais le palier 3 à fort : il faut 15 213 réussites de SOR pour 13 680 vérifiables en bureau, et 25 954 pour 17 100 en service client.

## Pronostic du plan tel quel (calcul, pas résultat)

| hypothèse d'implémentation | issue attendue |
|--|--|
| épreuve à toute erreur moyenne ou forte, pour A et B (pièce 7, code v2) | les quatre règles échouent à fort, dès A2, par les seules variantes d'épreuve (B1) → « aucune règle » |
| épreuve seulement après une erreur au palier 3 pour B (plan, section 2, à la lettre) | A½ et A¼ éliminées par les épreuves ; B-régulier éliminée par A4 en service client, enjeu faible (B2) → B-tout |
| épreuves corrigées, N de B-régulier non corrigé | B-régulier éliminée (B2) → B-tout, charge la plus basse parmi les survivantes |
| les deux corrigés | les quatre passent probablement. B-régulier a la charge la plus basse. B-régulier ou B-tout selon le seuil d'un point |

## OBSERVATIONS

### Bloquant

**B1. Les seules variantes d'épreuve dépassent le budget fort, et moyen pour les agents mauvais.**
- Mécanisme [lecture du code] :
  - chaque erreur moyenne ou forte ouvre une épreuve, à tout palier (`regle.py`, `Ed[ih] += …`) ;
  - 3 cas difficiles par essai, au taux min(0,9 ; 6q), un nouvel essai 50 actions du type après un échec ;
  - les variantes s'ajoutent au flux, au palier 1, et 5 % de leurs erreurs passent ;
  - « tout faire valider » n'a pas de variantes : leur dégât est donc entièrement « en plus ».
- Ce dégât ne dépend ni du palier ni des réglages. Il est le même pour A½, A¼ et la v2.
- Dégât des variantes seules, pour 100 actions du flux, et rapport au budget E1 [moteur, réglage de départ, 1 000 répétitions, e = 5 %] :

| agent | bureau moyen | bureau fort | SC moyen | SC fort |
|--|--|--|--|--|
| A1 | 0,0003 | 0,0003 (0,1×) | 0,0005 | 0,0005 (0,1×) |
| A2 | 0,0062 (0,1×) | 0,0054 (**1,1×**) | 0,0096 (0,2×) | 0,0096 (**1,9×**) |
| A3 | 0,020 (0,4×) | 0,017 (**3,5×**) | 0,029 (0,6×) | 0,030 (**6,0×**) |
| A4 | 0,045 (0,9×) | 0,040 (**7,9×**) | 0,062 (**1,2×**) | 0,065 (**13×**) |
| A4-calibre | 0,091 (**1,8×**) | 0,078 (**16×**) | 0,122 (**2,4×**) | 0,128 (**26×**) |
| A6b | 0,019 (0,4×) | 0,016 (**3,3×**) | 0,027 (0,5×) | 0,027 (**5,4×**) |
| A7 | 0,028 (0,6×) | 0,023 (**4,6×**) | 0,035 (0,7×) | 0,038 (**7,6×**) |

- Conséquence :
  - à 3 000 actions, A n'agit jamais seule à moyen ni à fort. Son « dégât en plus » à fort vient donc entièrement des épreuves, et il dépasse le budget dès A2 ;
  - le plan ne dit pas si B ouvre une épreuve après une erreur au palier 1 ou 2. Selon la lecture, ce sont les quatre règles qui tombent, ou A seulement (voir le pronostic) ;
  - dans les deux cas, le choix vient de la comptabilité des épreuves, pas de l'autonomie.
- Même biais sur la charge : 0,4 à 6 validations pour 100 actions du flux (`charge_epreuve`, `resultats/mesures.csv`), soit jusqu'à environ 10 points hors lectures. C'est plus que le seuil d'égalité (1 point).

**B2. B-régulier : la formule de N est fausse pour les petits N (service client, enjeu faible).**
- 0,37 ≈ 1/e est la limite de (N/(N+1))^N. À N = 5, ce facteur vaut (5/6)^5 = 0,402.
- Pire agent régulier : max p(1−p)^5 = 5^5/6^6 = 0,0670, soit **1,018 × barre** (barre 0,0658) [calcul].
- A4 (15 %) : 0,15 × 0,85^5 = 0,0666, soit **1,012 × barre**. La simulation donne 1,012 [calcul, 4 millions d'actions, 5 % d'invérifiables].
- Pas d'épreuve à enjeu faible, et le transitoire est négligeable (N = 5). L'excès mesuré sera donc d'environ 101 % du budget : « indécis » ou « échoue ». B-régulier est éliminée par l'approximation, pas par sa famille de règles. Avec le N exact (6), on tombe à 0,86 × barre.
- Enjeu : si B-régulier survit, elle a la charge la plus basse. L'erreur peut donc faire basculer le choix entre B-régulier et B-tout.
- Au passage :
  - avec des invérifiables tirés au hasard, d se simplifie pour un agent régulier : l'excès vaut p(1−p)^N par action, N compté en réussites vérifiées (simulation conforme) ;
  - le d de B-régulier n'est donc qu'une marge d'environ 5 % ;
  - cette marge couvre les autres cellules (pire cas 0,95 × barre), pas N = 5.
- La formule vient de la décision 2 elle-même. Elle demande une note datée dans REGLE.md, que ce relecteur ne modifie pas.

### Important

**I1. B ne garde pas toute la pièce 7, et sa spécification a des trous qui changent les chiffres.**
- Pièce 7.3 : « même après l'épreuve réussie, l'erreur reste dans le compteur… plus de réussites qu'au départ ».
  - A½ en bureau, enjeu moyen : 1 786 réussites au départ, 2 207 après une erreur ;
  - B : N, comme au départ ;
  - « Toutes gardent les pièces … 7 » est donc faux pour B, qui gagne de la charge par construction. Il faut déclarer l'écart et le faire valider par Otsoa, ou le corriger (N plus une marge après une erreur moyenne ou forte).
- Points non spécifiés :
  - (a) une erreur au palier 1 ou 2 ouvre-t-elle une épreuve (B1) ?
  - (b) le compteur avance-t-il pendant une épreuve ouverte ? Avec v2, le score ne bouge pas ;
  - (c) le compteur est-il borné à N ? C'est décisif pour la consigne divisée par deux : borné, le palier 3 est perdu ; non borné, il est souvent gardé ;
  - (d) arrondi de N/2 ;
  - (e) que devient le palier après une erreur à enjeu faible au palier 2 ?
  - (f) quelles erreurs deviennent des épreuves au changement de modèle (le s de v2) ?
- « B avant A (un compteur plutôt qu'un score) » : B garde le score de Wald du palier 2 (« le palier 2 garde les réglages de départ »). B, c'est donc un compteur plus un score, et l'argument de simplicité ne tient pas tel quel.

**I2. L'étalonnage fixe déjà l'issue, et le plan doit le dire.**
- Réussites exigées, en ordre de grandeur : B-tout environ 1/barre ; A¼ environ 3,9/barre ; A½ environ 5,9/barre (tableau des formules).
  - A certifie un taux (pm = barre, risque 5 %) ;
  - B borne des dégâts ;
  - le critère « budget, puis charge » récompense la seconde propriété.
- À 3 000 actions, A ne peut atteindre le palier 3 ni à moyen ni à fort. Le critère 2 se joue donc sur la vitesse à enjeu faible (MSG surtout), et à enjeu moyen pour B-régulier. B gagne par construction.
- La note de coordination (point 3) et `verif_barre` donnaient déjà ces ordres de grandeur. Ce n'est pas une fuite de données d'E1, mais le critère a été écrit en connaissant le gagnant en charge.
- Ce qu'E1 peut vraiment apprendre : si B tient le budget, et ce que B coûte en garantie et en retrait. Écrire la prédiction datée avant de lancer.
- Pour une vraie compétition sur le même objectif, ajouter une variante A réglée sur les dégâts (pm tel que l'excès du pire agent régulier égale le budget), sous réserve de l'accord d'Otsoa.

**I3. La garantie « 5 sur 100 » n'est mesurée que pour A (mesure 5).**
- La décision 5 la demande « chez les agents constants », sans restriction.
- B accorde le palier 3 à des agents au-dessus de la barre. Exemple : A1 (0,5 %) en bureau, enjeu moyen, barre 0,33 % :
  - B-régulier : 0,995^118 ≈ 55 % par tentative ;
  - B-tout à l'horizon long : 0,995^319 ≈ 20 % par tentative, donc promu presque sûrement.
- L'omettre pour B cache le principal coût de B.
- À mesurer pour les quatre règles et aux deux horizons. À 3 000 actions, la garantie de A est vide à moyen et à fort : A ne promeut rien.

**I4. La mesure 8 est exclue du choix avec une justification fausse, contraire à la décision 2.**
- « Elle touche toutes les règles de la même façon » est faux :
  - à enjeu faible, A absorbe déjà une erreur isolée, tandis que B se retire à la première. Une erreur ratée change peu A, beaucoup B ;
  - la borne « tout comportement » de B est précisément ce qu'un contrôle imparfait casse ;
  - inversement : si les erreurs des cas difficiles sont ratées, le taux vu d'A1 à enjeu moyen (environ 0,2 %) passe sous la barre (0,33 %). La dérive du score de A½ devient négative, et A finit par promouvoir un agent dont le vrai taux vaut 1,5 × la barre.
- La décision 2 dit « tient le budget dans tous les cas simulés ». Exclure des cas simulés demande une décision d'Otsoa, avec la vraie raison : l'hypothèse du protocole (décision 5, erreur constatée aussitôt).
- Sémantique non fixée : une erreur ratée compte-t-elle comme une réussite (faux négatif) ou comme neutre ? Le résultat en dépend.
- Avec k = 100, la borne (1 + k)/(N + 1) dépasse 1 à enjeu faible (N = 15 ou 41) : elle est vide.

**I5. L'oracle redéfini n'a pas de palier 2 : « part du gain de l'oracle » peut dépasser 100 %.**
- A1, bureau :
  - l'oracle « barre » n'accorde que l'enjeu faible, d'où une charge hors lectures de 61,8 ;
  - toute règle met EXE au palier 2 (réglages de départ), d'où environ 50 pour B-tout et 59 pour A½ ;
  - part = (100 − 50)/(100 − 61,8) ≈ 1,3, et ≈ 1,07 pour A½.
- Dans ce modèle, le palier 2 ne coûte aucun dégât en plus : même tirage du validateur que le palier 1. Il domine donc le palier 1 pour tout type réversible.
- Oracle juste : palier 3 si q ≤ barre ; sinon palier 2 si le type est réversible ; sinon palier 1. Pour A1 en bureau, l'oracle tombe à 47,4, et la part à 0,95 (B-tout) et 0,78 (A½).

**I6. Ajouts au plan initial et couverture des cas : le critère éliminatoire est presque vide à enjeu fort.**
- Règle générale [calcul] : hors épreuves, un agent sous la barre sur tous les types d'un niveau ne peut pas dépasser le budget de ce niveau, quelle que soit la règle. Seuls des agents au-dessus de la barre, près du pire cas de chaque règle, mettent une règle à l'épreuve.
- **A0** : neutre pour le choix, puisqu'il est sous la barre partout et ne peut rien dépasser. Orienté pour le récit : il montre la vitesse de B, et que A n'agit jamais seule à fort en 150 000 actions.
- **A0d** : plutôt défavorable à B. B l'a promu à fort avant la dérive, A non. Les deux retirent à la première erreur.
- **Horizon long** : nécessaire, mais vide pour A à enjeu fort (jamais de palier 3). Pour B-tout, il ne teste que A0 et A0d.
- **Agrégat « charge moyenne »** : orienté (I8).
- Pire cas régulier de B-régulier, p* = 1/(N + 1), avec les N du plan :
  - bureau : 6,3 % ; 0,85 % ; 0,10 % ;
  - service client : 16,7 % ; 0,62 % ; 0,06 % ;
  - les agents l'approchent par hasard à enjeu faible (A3, A4) et moyen (A1), jamais à fort.
- Ajouter des agents « bord », aux deux horizons : sur un seul niveau, q = p* de B-régulier, puis 1,5 × barre et 3 × barre, et le taux d'A0 ailleurs.

**I7. Répétitions inégales, « cas clés » non définis.**
- « Passe » dépend de la largeur de l'intervalle. B-régulier est réglé à environ 93-95 % du budget sur ses pires cellules : A3 en bureau, enjeu faible, 0,927 ; A1 en service client, enjeu moyen, environ 0,93.
- Les quatre règles doivent avoir le même nombre de répétitions, sur les mêmes tirages.
- Écrire d'avance la règle pour « indécis » : par exemple une relance à 4 fois plus de répétitions, puis échec.
- 200 répétitions à l'horizon long, sans justification. Mesuré [moteur] : 79 µs par pas pour 800 lignes, soit environ 12 s pour 150 000 pas, par agent et par mélange. 1 000 répétitions, par blocs de 200, restent à quelques minutes.

**I8. Le critère 2 et le départage penchent vers B.**
- La charge est moyennée sur 26 couples de l'horizon court, et 8 agents sur 13 sont des variantes à 2 %.
- En bureau, enjeu faible (barre 2,5 %), 2 % tombe dans la zone d'indifférence de A½ (pb 1,25 %, pm 2,5 %) :
  - dérive du score de A½ : +0,0013 par action vérifiée, donc presque jamais promu ;
  - B-tout : 0,98^41 = 44 % du temps au palier 3 ;
  - l'agrégat amplifie l'écart, à cause du choix des agents.
- Les agents mauvais, à charge à peu près égale partout, diluent les écarts. Un écart sous 1 point devient plus probable, et le départage, écrit d'avance, favorise B.
- L'unité du seuil « 1 point pour 100 actions » n'est pas précisée (hors lectures ?), et le seuil n'est pas justifié.
- Proposition :
  - critère sur les couples où au moins un type est sous la barre ;
  - charges données couple par couple ;
  - départage d'abord par la prudence (la plus grande marge au budget dans la pire cellule).

**I9. La « dérive comprise » est diluée.**
- L'excès est moyenné sur tout l'horizon, et la dérive tombe au milieu : l'excès après dérive compte pour moitié.
- Ajouter le verdict sur la fenêtre allant du changement à la fin.
- Effet faible avec les agents actuels, fort avec les agents « bord ».

**I10. Utilité pour l'expérience réelle et « réussite » de la décision 3.**
- Volume minimal du flux avant le palier 3, pour un agent sans erreur [calcul] :

| type | A½ | A¼ | B-tout | B-régulier (N exact) |
|--|--|--|--|--|
| ECR (bureau / SC) | 1 621 / 1 811 | 1 088 / 1 221 | 288 / 316 | 105 / 126 |
| MSG | 4 053 / 3 018 | 2 719 / 2 035 | 719 / 526 | 263 / 211 |
| DUR | 23 500 / 12 937 | 15 684 / 8 626 | 4 197 / 2 311 | 1 553 / 853 |
| SOR | 166 809 / 227 667 | 111 217 / 151 781 | 29 814 / 40 693 | 10 976 / 14 974 |
| ARG | 400 342 / 243 929 | 266 921 / 162 622 | 71 553 / 43 600 | 26 342 / 16 043 |

- Volume de l'expérience réelle : SUIVI parle d'un pilote d'environ 10 $ et d'une expérience fin novembre, sans volume trouvé dans les documents lus. Si elle compte quelques milliers d'actions, seul l'enjeu faible compte (plus l'enjeu moyen pour B-régulier), et l'horizon long ne dit rien d'utile pour elle. Écrire le volume prévu dans le plan, et lire le choix à ce volume.
- « Réussite » (décision 3 : moins de validations que la liste fixe et le tri, à budget tenu) : ni opérationnalisée (par couple ? en agrégé ?), ni intégrée au choix.
- Estimation [calcul] : A2 en service client, B-tout ≈ 90 hors lectures, dont environ 5 d'épreuves, contre 86,7 pour le tri. B-tout perd ; sans la charge des épreuves, il gagne (≈ 85). À rapporter pour chaque règle, avec et sans charge d'épreuve.

**I11. La mesure 9 (Lorden) est trompeuse telle quelle.**
- B lance une fausse alerte à la première erreur : son ARL vaut 1/(p0·d), soit 210 actions du type à p0 = 0,5 %. Elle « battra » donc un plancher calculé pour une ARL de 10 000.
- ln(ARL)/KL est un équivalent asymptotique, pas un plancher à ARL finie.
- Placer le point (ARL mesurée, délai) de chaque règle sur la courbe du CUSUM optimal pour les mêmes p0 et p1, ou supprimer la mesure.

### Mineur

- **M1. Valeurs de N.** Plan décalé d'une unité : B-tout dans 4 cellules sur 6 (il donne N + 1), B-régulier en service client à fort (1 707 = N + 1 selon 1/e, égal par hasard à l'exact). Le texte dit 0,37, les chiffres suivent 1/e. En flottants, `ceil` donne 41 / 2 720 / 16 : incohérent. Calculer en fractions et épingler les valeurs dans le test. Note de coordination : « 7 600 » correspond à pb → 0, pas à A¼ (10 143).
- **M2. α de A non précisé** (5 % présumé, comme le réglage principal de v2).
- **M3. Reproductibilité de v2.**
  - Les changements LEC (autonome dès le départ, hors dégâts) « pour toutes les règles » cassent `resultats/` s'ils ne sont pas derrière un interrupteur.
  - Ajouter A0 et A0d à la fin de `AGENTS` (graines par `ID_AGENT`), sinon `graine_regle` retombe sur `hash()`, qui est salé.
  - Tirer le contrôle imparfait sur une graine à part.
- **M4. Code fixé à l'horizon court.**
  - `lignes_reactivite` prend `T = C.HORIZON` (3 000) : avec tc = 75 000, masque vide et délais faux.
  - `simuler_regle` prend 1 500 comme instant de l'instantané par défaut.
  - `lignes_consigne` utilise `T_CHANGEMENT`.
  - À paramétrer.
- **M5. Tests.**
  - Ajouter « moteur B = référence B, action par action », comme pour v2.
  - Épingler les N.
  - Ajouter un piège « rafale » (N réussites, puis des erreurs jusqu'au retrait) : excès environ 0,95/(d·N + 1). C'est lui qui teste la borne « tout comportement » ; le piège du plan donne 0,95/(N + 1), sans d.
- **M6. Mesure 6** par type (SOR et ARG diffèrent d'un facteur 2,4 en bureau). Y joindre la table analytique de I10, sinon A est censurée à 100 % à fort.
- **M7. Mesure 4.3** binaire par répétition : environ 100 % pour B à enjeu faible (N = 5 à 15), donc peu informative. Donner plutôt la part du temps au palier 3 après la dérive, sur les types devenus mauvais (q > barre).
- **M8. Témoins et A8.** Apparier le hasard aux quatre règles (coût nul). A8 est vide à l'horizon court (fort inatteignable) : ajouter un A8 long sur la base d'A0 si la pièce 8 doit être testée.
- **M9. Intervalles.** Approximation normale sur des moyennes d'événements rares avec 200 répétitions : la borne haute est sous-estimée. Bootstrap, ou plus de répétitions.
- **M10. Gel.** Le dossier n'est pas sous git (SUIVI, « En attente ») : « écrite avant la relance » n'est pas vérifiable. Noter dans le plan l'empreinte sha256 du plan et du code avant de lancer.
- **M11. Décision 1 (« la mesure »).** Certifier q < barre demande environ 3/barre réussites sans erreur (règle de trois) : environ 7 750 à fort en bureau, 13 200 en service client. Table utile pour l'expérience réelle.
- **M12.** « Pannes injectées » (décision 3) : non simulées. Le dire.

## Faisabilité (code)

- **Temps.** Moteur vectorisé : 79 µs par pas pour 800 lignes [moteur]. Horizon long : environ 12 à 25 s par appel. Grille E1 complète : quelques minutes. Pas de contrainte de calcul.
- **Mémoire**, à 200 répétitions et 150 000 actions :
  - flux : environ 0,5 Go ;
  - `PT`, `ep_var`, `ep_err` : 120 Mo chacun ;
  - comptable : environ 0,3 Go ;
  - pour 1 000 répétitions, travailler par blocs.
- **Difficile dans `regle.py`** :
  - (1) règle B dans le moteur : compteur par type, coexistence avec L2, épreuves, consigne, changement de modèle. Il faut une référence `RegleUnTypeB` et un test de cohérence ;
  - (2) constat différé de k actions du type : une file par ligne et par type, plus l'interaction avec les épreuves et les paliers. C'est le plus délicat ;
  - (3) contrôle imparfait : un nouveau tirage, plus une sémantique à fixer.
- **Facile** : barres, N, oracle avec palier 2, LEC hors dégâts (dans `mesures.py`, derrière un interrupteur).

## CORRECTIONS PROPOSÉES (par ordre)

1. **Épreuves** (B1) :
   - décision d'Otsoa sur leur dégât : compté, compté à part, ou variantes sans effet réel ;
   - même déclencheur pour A et B : toute erreur moyenne ou forte, quel que soit le palier (pièce 7, v2) ;
   - dégâts et charge des épreuves en colonnes séparées ;
   - verdict du budget donné avec et sans.
2. **N exact** (B2, M1) :
   - B-régulier : 15 ; 118 ; 1 001 ; 6 ; 162 ; 1 707 ;
   - B-tout : 41 ; 319 ; 2 719 ; 15 ; 439 ; 4 639 ;
   - calcul en fractions, valeurs épinglées dans les tests ;
   - note datée sur la formule de la décision 2.
3. **Spécifier B en entier** (liste I1). Écrire l'écart à la pièce 7.3, ou le corriger, et le faire valider par Otsoa.
4. **Garantie « 5 sur 100 »** pour les quatre règles, aux deux horizons (I3).
5. **Mesure 8** :
   - soit dans le choix, avec un verdict à part ;
   - soit hors du choix sur décision d'Otsoa, avec la vraie raison ;
   - fixer la sémantique d'une erreur ratée.
6. **Oracle** avec palier 2 pour les types réversibles (I5).
7. **Agents « bord »** par niveau (I6). Mêmes répétitions pour les quatre règles. 1 000 répétitions à l'horizon long. Règle écrite pour « indécis » (I7).
8. **Critère 2** :
   - couples où au moins un type est sous la barre ;
   - unité et justification du seuil ;
   - départage par la prudence avant la simplicité (I8).
9. **Mesures en plus** :
   - fenêtre après changement (I9) ;
   - « réussite » de la décision 3, opérationnalisée et rapportée (I10) ;
   - volume prévu de l'expérience réelle écrit dans le plan (I10) ;
   - mesure 9 refaite à ARL égale, ou supprimée (I11).
10. **Avant de lancer** :
    - écrire la prédiction datée (B gagne la charge par construction) ;
    - empreinte du plan et du code ;
    - corriger les mineurs.

## VERDICT

**Lançable après corrections.**

Bloquants :
- **B1** : les variantes d'épreuve dépassent à elles seules le budget fort (de 1,1 à 26 fois).
- **B2** : le N de B-régulier est faux à N = 5 (1,018 × barre ; A4 à 1,012).

Sans ces deux corrections, le résultat le plus probable est « aucune règle » ou « B-tout par élimination », pour des raisons comptables. Les points I1 à I4 (pièce 7.3, issue connue d'avance, garantie absente pour B, mesure 8 hors choix) sont à régler dans le même passage.
