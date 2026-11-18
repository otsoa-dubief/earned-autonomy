# Audit de contrôle des corrections · 18 novembre 2026

Objet : corrections du commit `ca8fbbc` (et `883e5a7`) à « Earned Autonomy for AI Agents », après les trois relectures du 18/11.
Auditeur : Claude (Fable 5.2), instance séparée.
Lu : les trois rapports de relecture ; le diff de `ca8fbbc` sur `atelier.md`, `brouillon.md`, `main.tex`, `FORMULATION_VERDICT.md`, `controle_fr.md`, `outils/`, `SUIVI.md` ; `article/resultats/tables.md` et `tables_exploratoires.md` ; le PDF (52 pages, texte extrait, corps lu en entier, annexes par recherche ciblée) ; `article/sources_chiffres.csv` ; `simulation/rejeu/classes.py:375-400` ; trois passages de `PLAN_EXPERIENCE.md` et `REGLE.md`.
Non ouvert : `experience/`, `donnees/`, `pilote/`, `data/`, `notes/`, `~/.config/`. Contrôle des chiffres non relancé. Aucun fichier modifié hors ce rapport.

## Verdict

**Corrections justes sur les chiffres, incomplètes sur l'alignement : tous les chiffres ajoutés sont exacts au regard des tableaux, mais une phrase nouvelle est fausse (contribution 3), la version longue garde la phrase bloquante B1, et quatre passages d'annexe contredisent maintenant le corps.**

## Bloquant

### B1. La version longue garde la phrase que la relecture avait classée bloquante
- Endroit : `article/brouillon.md:338` (section 7). Absent du PDF, mais `brouillon.md` est « the extended version » citée en section 2 et en annexe F, et part dans l'archive de code.
- Preuve : « On airline the margin is thinner (31 % to 55 %), within what the author's blind sample allows (3 of 10 confirmed alerts lifted; exact 95 % interval 7 % to 65 %; limitation 23). » Les trois seuils (31, 48, 55 %) sont sous 65 % (table X2). La limite 23 du même fichier dit maintenant l'inverse (« 9 of the 20 established excesses would be lost »).
- Portée : bloquant pour l'archive publique, pas pour le PDF.
- Correction : reprendre la phrase de `atelier.md:61` (« is too small to rule such shares out: at its upper end, 9 of the 20… »).

## À corriger

### C1. Contribution 3 : « volume excluded delegation whatever their error rate » est faux pour deux configurations
- Endroit : `article/atelier.md:7` ; PDF p. 2. Phrase nouvelle, reprise de la réécriture proposée par la relecture « affirmations » (I4).
- Preuve : la jugeabilité dépend de ρ̂, et ρ̂ dépend des erreurs. Règle du moteur (`classes.py:384-395`, et C.6.4 p. 26) : sous 10 erreurs, la configuration prend la valeur commune (0,402). Table 6 : WorkBench/Opus ECR, 182 écritures, n_eff(ρ=1) = 80,0, ρ̂ = 1,000, produit 0,606. Recalcul avec la formule de la section 5 : à ρ̂ = 0,402, n_eff ≈ 120, produit ≈ 0,91, au-dessus de 0,6905. Idem Sonnet (≈ 0,91). Le type serait jugeable pour tout ρ̂ ≤ 0,78 environ. Avec zéro erreur, il aurait donc été jugeable et délégable.
- Indice interne : p. 28, « under raw verdicts, WorkBench/Opus reversible writes become judgeable at 0.6930 ». La jugeabilité bouge avec les verdicts, pas avec le volume seul.
- Réserve : recalcul fait avec m̄ déduit de la table 6 (la même méthode redonne 97,7 pour Haiku). La valeur commune changerait un peu sans ces erreurs ; non recalculée.
- Même défaut, plus léger et plus ancien : « The other eleven had too little volume to conclude either way » (résumé), « lacked the volume to conclude » (section 9). Pour WorkBench/Opus et Sonnet, c'est le volume joint à des erreurs très groupées (ρ̂ = 1).
- Correction : « for nine of the other eleven, volume excluded delegation whatever their error rate; for Opus and Sonnet on WorkBench, the observed clustering of errors did (ρ̂ = 1; Table 6) ». À défaut : « for the other eleven, no type was judgeable (Section 6.2) ».

### C2. C.6.4 dit encore « the strong fact » et « same order » ; le corps dit l'inverse
- Endroit : `article/brouillon.md:290` et `:298` ; PDF p. 25 et p. 26.
- Preuve : p. 25, « The error rates themselves, 6.5 % to 13.3 %, are the strong fact. » ; p. 26, « Elsewhere the pooled rates stay of the same order ». Le corps (6.4, p. 5) a retiré « strong fact » et donne 1,2 à 7,7 % sur l'autre moitié.
- Constats visés : méthode I4, affirmations I6. Traités dans le corps seulement.
- Correction : en C.6.4, remplacer par la phrase du corps (deux moitiés, réserve entière 3,8 à 8,0 %, bornes hautes 20 à 51 %). Remplacer « same order » par les écarts chiffrés (1,1 à 5,6 fois entre moitiés, recalculé).

### C3. La note de la table X6 dit encore « engine estimator »
- Endroit : `outils/tables_exploratoires.py:98-99` ; `article/resultats/tables_exploratoires.md` (X6) ; PDF p. 48.
- Preuve : « Task-level bootstrap, 2,000 draws, seed 20261117, engine estimator classes.rho_anova ». Le corps (p. 4), C.6.2 (p. 23) et la limite 21 (p. 50) disent « a simpler estimator than the engine's ». Contradiction dans le même PDF.
- Constat visé : méthode I2. X6 n'a pas été refaite avec `rho_fc_strates` ; le « 9,6 % » reste dans la table, sans la mise en garde.
- Correction : dans le script, écrire « estimator `classes.rho_anova`, pooled over types, not the engine's stratified Fleiss–Cuzick; the share of draws above 0.885 likely understates the risk ».

### C4. La table 6 laisse toujours refaire le mauvais produit
- Endroit : PDF p. 31 ; `article/resultats/tables.md:134-138`.
- Preuve : colonnes « n_eff (ρ=1) 81.6 » et « n_eff × bar 0.740 », note inchangée. 81,6 × 0,007575 = 0,618 (recalculé). Ni colonne « n_eff (ρ̂) », ni phrase en note.
- Constats visés : méthode I1, affirmations I7. Traités dans le corps (6.2) et en C.6.2, pas dans la table.
- Correction : ajouter à la note « the product uses n_eff under ρ̂, not the ρ = 1 column ».

### C5. La règle de relecture des levées fortes est invoquée sans être décrite
- Endroit : `article/atelier.md:41` ; PDF p. 4. Annexes : B.4.3 (p. 18), C.6.1 (p. 23), limite 9 (p. 49).
- Preuve : le corps écrit « the pre-registered re-review of all lifted high-stakes alerts was not triggered ». Aucune occurrence de cette règle dans les annexes (recherche « high-stakes alert », « re-review »). Le niveau d'enjeu de l'alerte levée à tort n'est donné nulle part. Pas de ligne dans `sources_chiffres.csv`.
- Constat visé : méthode I7. Traité à moitié.
- Non vérifié : le fait lui-même. `SUIVI.md` cite `accord.json`, `drapeau_enjeu_fort` faux ; fichier hors de mon périmètre.
- Correction : une phrase en B.4.3 (la règle, plan 4.4) et une en C.6.1 (niveau de l'alerte, règle non déclenchée, fichier source). Ajouter la ligne au registre.

### C6. `n_eff` composé de deux façons dans la même phrase, et « ≥ about »
- Endroit : `article/atelier.md:35` et `:43` ; PDF p. 4 ; `article/latex/body.tex:35,43`.
- Preuve : le PDF affiche « n_eff × bar » en texte brut avec tiret bas, puis « n_eff = n/(1 + (m̄ − 1)ρ̂) » en mathématiques, dans la même phrase. En 6.2 : « n_eff = 97.7 », « n_eff = 81.6 » en texte brut.
- Anglais fautif : « n_eff × bar ≥ about ln 2; 0.6905 for the WorkBench low-stakes bar ».
- Constat visé : clarté B6, non traité dans le corps (la formule de B-regular, elle, est bien composée, p. 15).
- Correction : tout en mathématiques ; « $n_{\mathrm{eff}} \times \mathrm{bar}$ at least about ln 2 (0.6905 at the WorkBench low-stakes bar) ».

### C7. Conclusion et contributions de la version longue non alignées
- `article/brouillon.md:388` : « where it can be measured it is wide ». Affirmations I3, corrigé dans `atelier.md:69` seulement.
- `article/brouillon.md:32`, `:51`, `:172` (PDF p. 19, B.4.5) : « real error rate », « real reliability ». Affirmations M3, corrigé dans le corps seulement.
- `article/controle_fr.md:31` : « nos chiffres montrent ce qu'il coûte ». L'anglais dit maintenant « the budgets fix what it costs ». Le contrôle en français ne décrit plus le texte.
- Correction : reporter les trois phrases de `atelier.md`.

### C8. Contribution 3 : phrase cassée par le deux-points
- Endroit : `article/atelier.md:7` ; PDF p. 2.
- Preuve : « The plan stated in advance that […] the high-stakes run lengths exceed the data: plan, rule, code, seeds and labels were registered on OSF… ». Le deux-points relie deux idées sans rapport. « Its label was open for the one configuration » : l'étiquette est globale, pas par configuration.
- Constat visé : clarté I5, aggravé par l'ajout.
- Correction : point après « exceed the data ». Puis « Plan, rule, code, seeds and labels were registered… ».

## Remarques

- **R1. Nom de R4 cité de deux façons.** Section 5 (p. 4) : « nothing to delegate: unreliability established ». C.5.2 (p. 20, `brouillon.md:198`) : « nothing to delegate, unreliability established ». Une citation entre guillemets doit être identique.
- **R2. C.6.4 (p. 26) : « up to 63 % » toujours sans le 65 %.** La limite 23 et le corps font le rapprochement ; C.6.4 non.
- **R3. Méthode I3, troisième point non repris.** L'échantillon est de 5 confirmées par vague (232 alertes contre 2 529). Le corps dit « all environments pooled », pas « stratified by wave ».
- **R4. « these rates vary strongly between tasks » (6.4).** C'est une explication, pas une mesure. Plus sûr : « the two halves differ by up to a factor of five ».
- **R5. « rarely pay it » (section 7).** Flou. Aucun type n'a été délégué avec preuve. Proposer : « could not pay it at these volumes ».
- **R6. « a simulation at the engine before any data » (C.6.4, `brouillon.md:282`).** Calque. Écrire « a simulation run on the engine before any data ».
- **R7. Figure 1.** Légende : « descriptive intervals ». C.5.3 dit maintenant « nominal 95 % ». Aligner.
- **R8. Date.** `main.tex:55` : « Draft, 17 November 2026 ». Texte corrigé le 18.
- **R9. Résultats en bref : deux moitiés mêlées.** 8,6 % vient de la calibration ; 64 % et 95 à 97 % de la réserve entière ou des deux moitiés. Exact, mais non dit.
- **R10. 6.4 dit encore « 20 of 40 types ».** Le résumé et « Results in brief » disent « model–environment–type combinations ».
- **R11. Méthode I9.** Le plafond de 90,00 $ est expliqué en C.6.1, pas inscrit en annexe A. Acceptable si l'accord d'Otsoa précède la vague. Le « 90,78 $ » du plan : non retrouvé par ma recherche, non vérifié.

## Vérifié (réellement recalculé ou relu)

Chiffres, contre `tables.md` et `tables_exploratoires.md` :
- 11 en banque, 6 écritures d'argent (aviation 3, commerce 3), 3 WorkBench : compté dans X2 et la table 6. Juste.
- Confirmation, argent hors banque : 1,15 à 7,65 % (commerce/Opus 6/520 ; aviation/Opus 14/183). Réserve entière : 3,75 à 7,97 %. Juste (6 bis moins 6).
- WorkBench ECR, confirmation : 5,91 à 11,01 % (12/203 ; 110/999). Juste.
- Bornes hautes 20 à 51 % : 20,5 ; 20,5 ; 23,6 ; 44,6 ; 47,3 ; 50,7 (C.6.4, p. 25). Juste.
- X2 : 9 seuils sous 65 % (0, 30, 31, 41, 45, 47, 48, 55, 63) ; 63 % pour le type de R4 ; commerce 70, 71, 79 ; aviation 31, 48, 55. Juste.
- X3 : 63,9 ; 78,9 ; 81,8 %, soit « 64 % to 82 % ». Juste.
- Réussite Haiku WorkBench : 97,0 % et 94,9 %, soit « 95 % to 97 % ». Juste.
- n_eff : 914 / (1 + 10,2 × 0,819) = 97,7 ; 97,72 × 0,007575 = 0,740 ; 81,6 × 0,007575 = 0,618. Juste. La formule de la section 5 redonne bien les deux valeurs.
- 4,6 à 6,2 erreurs pour 100 écritures du type (X5). Juste. B-regular, 4 échecs sous delay10 (table 9). Juste.
- 0,549 = jackknife-t, première simulation ; 0,35 point ; 2,8 % : retrouvés dans `PLAN_EXPERIENCE.md:696,707` et `REGLE.md:287`.
- 14 266 : cohérence interne seulement. 1 185 + 13 081 = 14 266 (p. 22) ; table 1 bis 10 080 + 2 093 + 2 093 = 14 266 (p. 18) ; 13 623 = somme de la table des réussites. Aucun reste de « 14,265 » ni « 13,080 » dans le PDF, `atelier.md`, `brouillon.md`, les deux résumés. Le compte de la vague 2 lui-même : non vérifié.

Constats des relectures :
- Traités : affirmations B1 (corps, limite 23, résumé), I1, I2, I4 (hors C1), I5, I8, M1, M2, M4, M5, M6, M8 ; méthode I3 (sauf R3), I5, I6, I8, I9, M1, M2, M4, M6, M8, M9, M10, M11.
- Partiels : méthode I1, I2, I4, I7 ; affirmations I3, I6, I7, M3 (voir C2 à C7).
- Non regardé : le détail des constats de clarté B1 à B5, B7, I2 à I11 (hors points cités).

PDF :
- 52 pages. Aucun renvoi « ?? ». Aucun « Overfull », « undefined » dans `main.log`.
- Renvois nouveaux : Section 6.2, 6.3, 7, C.6.2, limitation 21, Table X2, Table 1 bis : cibles présentes.
- Restes de français cherchés (rate10, retard10, B-régulier, charge, résultat, au-dessus, indéterminé) : aucun, hors « B-tout » voulu et « Tranché par Claude » cité.
- Formule de B-regular (p. 15) et formule de n_eff (p. 4) : composées.

Résumé :
- 1 765 caractères (`article/arxiv/abstract.txt`), sous 1 920. Identique au PDF.
- Exact au regard des tableaux. Seule réserve : « too little volume » pour les onze autres (voir C1).
