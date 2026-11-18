# Formulation de référence du verdict (adoptée par Otsoa le 17/11/2026, PLAN_SUITE T04, Q1 : option (a) en trois temps)

Cette page fixe la façon de dire le résultat dans l'article, le résumé, les messages et les publications. Sources : `experience/rejeu_final/decision.csv`, `experience/rejeu_final/ecart.csv` (version « principal », moitié de calibration), et l'audit du 17/11 (`revues/2026-11-17_audit_fable_resultats.md`).

## Phrase du résumé (recommandée par la recherche « Formuler un verdict préenregistré mixte », adoptée)

**Français.** Aucune des douze configurations n'a atteint le niveau de preuve fixé à l'avance pour qu'on lui délègue des actions (verdict préenregistré R4). Une seule avait assez d'actions pour être jugée : son taux d'erreurs, 8,6 % (borne basse 4,1 %), est établi au-dessus du seuil de 0,76 %. Pour les onze autres, le volume est trop faible pour conclure, dans un sens comme dans l'autre. À titre descriptif, 20 types d'actions sur 40 ont un taux établi au-dessus de leur seuil ; 13 n'ont aucune erreur observée, mais trop peu de volume pour conclure.

**English.** No configuration reached the pre-registered level of evidence required for delegation (pre-registered verdict R4). Only one of twelve configurations had enough volume to be judged; its error rate, 8.6% (lower bound 4.1%), is established above the 0.76% threshold. The other eleven had too little volume to conclude either way. Descriptively, 20 of 40 action types have an error rate established above their threshold; 13 show no observed error but too little volume to conclude.

**Précision obligatoire dans l'article** : la borne basse (4,1 %) est une borne de Clopper-Pearson unilatérale à 95 % par type d'action, sur la taille effective à ρ = 1, sans correction pour les douze configurations (règle figée, `simulation/rejeu/classes.py`, `depassement_etabli`). L'écart avec le seuil (plus de cinq fois) rend le hasard peu plausible, mais l'article le dit.

**Ligne de diffusion** (le dénominateur « 12 » reste toujours dans la phrase) : « Étude préenregistrée : aucune de nos 12 configurations d'agents n'a mérité qu'on lui délègue des actions. La seule mesurable fait 8,6 % d'erreurs pour un seuil de 0,76 % ; les 11 autres manquent de données pour trancher. » / "Pre-registered study: none of our 12 agent configurations earned delegation. The only one we could measure errs 8.6% of the time (threshold: 0.76%); the other 11 lack data to decide."

## La phrase principale (version longue, pour le corps de l'article)

**Français.** Sur quatre bancs publics et trois modèles Claude 5.5, aucune configuration n'a atteint, sur la moitié de calibration, le niveau de preuve exigé pour déléguer un type d'action sous le budget d'erreurs fixé d'avance. Dans la seule configuration assez jouée pour être jugée (Haiku sur WorkBench, écritures réversibles), le taux d'erreurs confirmées, 8,6 %, est établi au-dessus de la barre de 0,76 %. Dans les onze autres, le volume ne permet pas de conclure (étiquette préenregistrée R4).

**English.** In a preregistered offline replay on four public benchmarks and three Claude 5.5 models, no configuration qualified as delegable on the calibration half under an error budget fixed in advance. In the only configuration with enough volume to be judged (Haiku on WorkBench, reversible writes), the confirmed error rate, 8.6%, is established above its 0.76% bar. The other eleven configurations lack the volume to conclude (preregistered label R4).

## Les trois phrases qui suivent

1. **The delegation gap.** 20 of the 40 observed action types have a confirmed error rate proven above their bar; 13 have no observed error but too little volume; none can be proven below its bar at these volumes. *(FR : 20 des 40 types observés ont un taux d'erreurs confirmées prouvé au-dessus de leur barre ; 13 n'ont aucune erreur observée mais trop peu de volume ; aucun ne peut être prouvé en dessous à ces volumes.)*
2. **The rule.** The rule was not refuted, but it was hardly put to the test, and its usefulness could not be judged. *(FR : la règle n'a pas été réfutée, mais elle n'a presque pas été mise à l'épreuve, et son utilité n'a pas pu être jugée.)*
3. **What an error is here.** These rates count action errors confirmed by review against a single expected path per task; in a blind sample reviewed by the author, 3 of 10 confirmed alerts were lifted. *(FR : ces taux comptent des erreurs d'action confirmées par relecture, avec un seul chemin attendu par tâche ; sur un échantillon relu à l'aveugle par l'auteur, 3 alertes confirmées sur 10 ont été levées.)*

## Définitions et chiffres de contrôle

- **Délégable** : une configuration l'est si au moins un de ses types a un taux médian (borne haute de Clopper-Pearson à 50 %) au plus égal à sa barre, sur la moitié de calibration (plan 5.14, point 4 ; Q14).
- **Jugeable** : un type l'est si n_eff × barre ≥ 0,6905 (environ ln 2, critère exact 1 − 2^(−1/n_eff) ≤ barre), c'est-à-dire si zéro erreur suffirait à le faire compter. WorkBench/Haiku ECR : n_eff = 97,72 et barre = 0,007575, soit **0,740**.
- **Les chiffres du type qui porte R4** (`ecart.csv`) : 914 écritures, 79 erreurs confirmées, taux 8,64 %, barre 0,757 %, borne basse à ρ = 1 de 4,14 %, 134 tâches porteuses.
- **Fragilité de la jugeabilité** : ρ̂ mesuré = 0,819 ; le type reste jugeable tant que ρ̂ ≤ 0,885 (calcul de l'audit). Au-delà, aucun type n'est jugeable, et l'étiquette deviendrait « preuves insuffisantes ».
- **R4 ne compare pas les modèles** et ne dit rien des onze configurations sans type jugeable (plan 1.5).

## Formulations interdites (règle R8 de PLAN_SUITE)

« non-fiabilité établie » sans dire où ; « rien à déléguer » ou « nothing to delegate » sans définition ; « B-tout tient le budget » ; « bat la liste fixe et le tri par le risque » ; « de 7 à 2 400 fois la barre » ; tout classement des trois modèles.

## Correction de ce qui a été dit le 17/11

La formule « rien à déléguer : non-fiabilité établie », employée le 17/11 au moment du verdict, est remplacée par la phrase principale ci-dessus.

- **Fragilité découverte le 18/11 (exploratoire)** : 48 des 79 erreurs du type jugé sont un même écart de date sur des graphiques, tranché dans les deux sens par les relecteurs ; levé partout, il reste 31 erreurs (établi à deux erreurs près) ; en levant aussi quatre fenêtres décalées d'un jour, 27 (non établi : « preuves insuffisantes »). À dire chaque fois que le verdict est cité (article, section 6.7, tableau X8, limite 32).
