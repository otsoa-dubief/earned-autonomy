# Moteur de rejeu, phase 3 : choix d'implémentation

Rédigé le 5 novembre 2026 au soir par Claude, après la décision d'Otsoa sur Q13 (`REGLE.md`, décision 3, dernière lecture datée ; `PLAN_EXPERIENCE.md`, 1.4, 5.13, 5.14 et Q13). Mêmes principes qu'aux phases 1 et 2 : la lecture la plus simple qui respecte les textes, chaque choix contestable avant le gel. Ni le plan, ni `REGLE.md`, ni `SUIVI.md`, ni `JOURNAL_CHANGEMENTS.md`, ni `banc/` n'ont été modifiés ; `couverture.py` et `intervalles.py` non plus (la première simulation se vérifie toujours).

## 1. Choix

| n° | Section du plan | Choix | Raison |
|---|---|---|---|
| 1 | 5.14, point 1 (Q13) | m du max-T de B-tout = ses cellules jugées : B-tout atteint le palier 3 dans au moins une des R0 répétitions, et la cellule n'est pas « sans objet ». Statuts : « sans objet », « tenue, non mise à l'épreuve », « dépassement établi », « non réfutée ». R1 si au moins un dépassement est établi. | « Répétition » lu comme en M7 (« jamais » = dans aucune des R0 répétitions). |
| 2 | Q13 (« la même mesure pour toutes les règles ») | Les cellules de B-régulier, A½, A¼ et de la lettre d'origine sont jugées de même, chaque règle par son propre max-T (par valeur de e). Aucune cellule du budget n'a plus de verdict passe, échoue ou indécise ; la relance est supprimée du code (elle ne servait qu'aux cellules de B-tout). | Une seule balance pour les règles comme pour les témoins. |
| 3 | 5.13 ; Q13 | La méthode retenue par la nouvelle simulation sert à tous les intervalles : ceux qui décident (différences de charge, moyennes sur les configurations, hasard) et les descriptifs (cellules du budget, s ÷ q, garantie). La première simulation reste comme historique. | Une seule règle d'intervalle ; la première simulation montre seulement qu'aucune méthode ne couvre bien des dégâts rares aux petits G. |
| 4 | 1.4, RF3 | s = écritures au dénominateur, non plafonnées, du niveau ÷ écritures au dénominateur, dans la suite rejouée (scénario : X et Y). s ÷ q : valeur centrale, écart type linéarisé, bootstrap sur le même tirage commun des tâches, jackknife par tâche ; s ne dépend pas de la règle, il est calculé sans rejeu. Borne de construction : 0,95 × budget × s ÷ q (valeur centrale). | Définition de RF3 ; q figé au point 9 (`config_rejeu.json`). |
| 5 | 5.13 (Q13) | « Démontrée » : borne haute de Clopper-Pearson à 5 % unilatéral au plus le budget, avec x = dégâts en plus attendus (valeur centrale × n ÷ 100), n = écritures au dénominateur, m = écritures au dénominateur par tâche, x_eff = x × n_eff ÷ n. ρ̂ : celui de la calibration de la configuration (avec son repli) ; scénario : le plus grand de X et de Y ; sans calibration (toute la réserve) : celui du jeu rejoué ; échange des rôles : les tâches des deux plis. | « Calcul comme pour les taux par type ». |
| 6 | 5.14, point 1 (Q13) | « Garantie hors hypothèse » : borne basse de s ÷ q (méthode retenue) au-dessus de 1 ÷ 0,95 ; signalée, sans effet sur l'étiquette. | Tranché dans le plan. |
| 7 | 5.14, point 6 ; section 8 | « Fragile » pour une cellule jugée de B-tout : moins de 30 tâches porteuses du niveau ; ou statut « établi » qui change entre verdicts bruts et confirmés (Q11), ou entre l'analyse principale et toute la réserve ou l'échange des rôles ; ou nombre de tâches dans la zone qui échoue de la simulation du point 2 (vide aujourd'hui : (iii) passe partout). « Méthodes divergentes » ne s'applique plus qu'au point 2 et au hasard (jackknife-t contre percentile). | Les cellules de B-tout n'ont plus de décision par intervalle ; restent les sources de fragilité qui touchent leur statut. |
| 8 | 1.3, point 4 ; 5.11 | Règle de choix réappliquée : une règle « tient » si aucun dépassement n'est établi ; alerte de résistance : échecs = dépassements établis + périodes à plus d'une erreur constatée. « Pire cellule » et « marge » : borne haute de l'intervalle descriptif. | Même mesure ; la marge reste descriptive, comme dans E1. |
| 9 | 5.13 ; 5.16, point 5 | Nouvelle simulation (`couverture_charge.py`, `resultats_couverture_charge/`) : chaque écriture d'une tâche est validée par la règle seule (+1), par le témoin seul (−1) ou par les deux ou aucun (0) ; p⁺ ~ Bêta (moyenne μ⁺, corrélation ρ), p⁻ = (1 − p⁺) r, r ~ Bêta (moyenne μ⁻ ÷ (1 − μ⁺), corrélation ρ) ; quantité 100 × Σ (y⁺ − y⁻) ÷ Σ m, vraie valeur 100 (μ⁺ − μ⁻). Réglage qui décide : μ⁺ = 0,25, μ⁻ = 0,15 (40 % des écritures diffèrent) ; rapportés sans effet : (0,45 ; 0,05) et (0,10 ; 0,10). Mêmes tailles (1 à 32), 5 000 jeux par case, B = 2 000, graine 2026110531. Pas de composante d'ordre ni de validateur. | Une différence signée et fréquente, comme B-tout contre un témoin (plus de validations sur les réversibles, moins sur les messages internes) ; les validations au palier 1 ne dépendent pas du validateur, les corrections au palier 2 sont rares. |
| 10 | 5.13 | La simulation est un module nouveau ; son `--verifier` contrôle les deux dossiers (et `couverture --verifier` reste conforme). | Modifier `couverture.py` aurait invalidé l'empreinte de la première simulation. |
| 11 | Q8 (lecture A) ; `REGLE.md`, point 8 | Part des lectures, préparations et doutes mesurée à l'étape 2 du pilote (120 parties, tous modèles) : comptes entiers figés dans `config_rejeu.py` (`COMPTES_PILOTE`, recomptés par un test) et dans `config_rejeu.json` (« lettre_point_8 »). Part du niveau dans le flux = (1 − cette part) × q du point 9 (plafonnées exclues) ; niveau vide : barre du profil E1 sur le flux (`config_e1.barre`). Seul B-tout est rejoué (règle « B-tout-lettre »), dégâts en plus pour 100 actions, même mesure (max-T), en analyse secondaire (`budget.csv`, analyse « lettre d'origine (Q8 A) » ; `decision.csv`). | Demandé ; la précision C1 vaut aussi pour le point 8, sinon les N ne portent pas sur les mêmes écritures. Exemple : aviation, enjeu faible, N = 1 (« une erreur tolérée sur 1,3 », point 9). |
| 12 | 5.17 ; `REGLE.md`, pièce 9 | Parallélisation par familles : une tâche par environnement pour ses trois configurations (leurs influences par grappe s'additionnent pour les moyennes, tirage commun), une par scénario ; assemblage dans un ordre fixe ; sorties identiques avec 1 et N processus (testé). Les fournisseurs d'épreuves deviennent des objets (et non des fonctions anonymes) pour passer d'un processus à l'autre. | Les graines dépendent de la famille, pas du processus. |
| 13 | 5.14 ; 4.4 (B2) | Entrée de l'expérience réelle : `--experience --dossier … --partage partage.json --vague NOM=decisions.csv,alertes.json,accord.json` (une par vague) `[--retirees] [--processus N]`. G0 lue dans `config_rejeu.json`, refusée si elle vaut null. `accord.json` lu sans modification : `decisions_otsoa` (les fortes levées y sont déjà réunies par `accord.py`) l'emporte sur `decisions.csv` (`accord.decisions_retenues`) ; `desaccord_persistant` déclenche B2 ; `conclusion` sert au point 0 ; `fortes` est recopié dans `meta.json`. Essai à blanc : `--essai-a-blanc` (données du pilote, partage fictif écrit dans la sortie, graine de développement, avertissement). | Demandé. |

## 2. Contradictions et trous relevés dans le plan

1. **736 ou 598 écritures** (1.4, précision Q13). « À zéro dégât, il faudrait au moins 736 écritures indépendantes à enjeu faible » : c'est le seuil d'un Clopper-Pearson à 2,5 % unilatéral (ln 0,025 ÷ ln 0,995). Avec le risque de 5 % unilatéral écrit en 5.13 et repris pour « démontrée », il en faut 598. Le code suit 5.13.
2. **Sous-puces restées en 5.13** (« Verdict d'une cellule ») : la relance à 8 000 répétitions et « indécise = échec » ne s'appliquent plus à aucune cellule du budget (Q13 pour B-tout ; même mesure pour les autres règles). Le code n'a plus de relance ; le texte les garde.
3. **Point 8 et plafonnées** : la précision C1 (plafonnées exclues de q) est écrite pour le point 9 ; appliquée aussi à la lettre d'origine (choix 11).
4. **Borne de construction de la lettre d'origine** : RF3 définit s parmi les écritures ; pour les dégâts pour 100 actions (Q8 A), la borne demanderait une autre part (parmi les actions). Non calculée pour ces lignes.
5. **m et le bootstrap** (5.14, point 1, Q13) : une cellule « tenue, non mise à l'épreuve » dans R0 peut atteindre le palier 3 dans des répétitions bootstrap ; elle reste hors de m (lecture M7).

## 3. Simulation de couverture refaite (`resultats_couverture_charge/`, lancée une fois)

Couverture minimale sur les six valeurs de ρ, au réglage qui décide (μ⁺ = 0,25 ; μ⁻ = 0,15) :

| Méthode | G = 20 | G = 40 | G = 90 |
|---|---|---|---|
| (i) bootstrap par grappes, percentile réuni avec normal | 0,906 | 0,920 | 0,936 |
| (ii) bootstrap-t par grappes | 0,916 | 0,921 | 0,937 |
| (iii) jackknife-t par tâche | 0,933 | 0,935 | 0,940 |

- **(iii) passe partout** (pire 0,933, à ρ = 0,7 et G = 20) : retenue, sans repli, sans zone qui échoue ; seconde méthode de « fragile » : le percentile. La marge au seuil est mince (erreur de Monte-Carlo d'environ 0,35 point).
- Réglages rapportés : (0,45 ; 0,05) : (ii) passe (pire 0,940), (iii) 0,923 ; (0,10 ; 0,10) : (iii) passe (0,942), (ii) 0,880.
- Durée : 35 s sur 14 processus. La première simulation (`resultats_couverture/`) reste inchangée, comme historique.

## 4. Ce qui reste

- Contrôle 3 élargi (plan, section 7, étape 6) : vérifier que l'étiquette tombe juste dans des mondes fictifs où la vérité est connue (bonne règle et agents fiables, règle trop permissive, agents peu fiables, mélange qui dérive, volumes de l'expérience), et publier la fréquence de chaque étiquette. Non fait.
- Les entrées réelles viendront du lanceur (autre agent, `banc/`) : format du pilote, numéro de passage et vague notés (`CHOIX_PHASE1.md`, choix 2).
- Durée du rejeu final : voir la section 5.

## 5. Bout en bout et essai à blanc sur le pilote

Les chiffres de ces deux dossiers n'ont aucune valeur de preuve ; chaque sortie le dit en tête.

- `sorties_pilote/` : `python -m rejeu.bout_en_bout --pilote --processus 8` (R0 = B = 2 000, K = 10) ; toutes les tables sortent, lettre d'origine comprise ; étiquette de test R5 (vague sans bilan d'accord) ; B-tout n'atteint jamais le palier 3 (0 cellule jugée, aucun dépassement établi). Durée : 2 min 37 s avec 8 processus (14 min 13 s sur un cœur en phase 2).
- `essai_a_blanc_pilote/` : `python -m rejeu.bout_en_bout --essai-a-blanc --processus 8`, par le chemin du rejeu final (partage écrit dans `partage_essai.json`, vague lue par `--vague`) ; mêmes conclusions de test ; 2 min 40 s. Sans `--essai-a-blanc`, l'entrée `--experience` refuse de tourner tant que G0 vaut null.
- Durée du rejeu final : les suites de l'expérience seront environ cent fois plus longues qu'au pilote ; à 8 processus, compter plusieurs heures (estimation, non mesurée).
