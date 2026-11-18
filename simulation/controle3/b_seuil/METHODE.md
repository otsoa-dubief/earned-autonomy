# Monde B-seuil : étalonnage de la dérive (écrit avant le calcul)

Claude, 07/11/2026. Rapport du contrôle 3, 9.3, point 2 : aucun monde n'a de dépassement vrai d'exactement 1,0 fois le
budget, donc « 0 R1 à tort » est mesuré loin du seuil. Ce dossier fixe la dérive du monde B-seuil avant le contrôle 3
complet du cinquième passage. Données synthétiques seulement, aucun appel payant (`env -u ANTHROPIC_API_KEY`).

## 1. Monde

Comme E-fort (`mondes.py`) : témoins en défaut (écriture réversible de Sonnet et Opus dans WorkBench à 10 fois la
barre), tous les autres types à 0,2 fois la barre, écriture réversible du commerce au pire taux d'un agent régulier sous
B-tout (0,944 fois la barre), ρ = 0. Seule change la dérive du mélange en commerce : d écritures réversibles par partie
(E-fort : d = 4, valeurs centrales de 1,35 à 1,47 fois le budget). Le budget se compte pour 100 écritures : la relation
entre d et le dépassement n'est donc pas proportionnelle, d'où l'étalonnage.

## 2. Étalonnage

- **Mesure** : valeur centrale ÷ budget des trois cellules de configuration du commerce à enjeu faible (point 1 de
  B-tout, `decision.point1`), moyenne sur les trois cellules puis sur les répétitions. C'est la grandeur que le rapport
  appelle « dépassement vrai » pour E-fort.
- **Grille** : d ∈ {1 ; 1,75 ; 2,5 ; 3,25}, 6 répétitions chacune. Graine maîtresse 2026110702, distincte de celle du
  contrôle 3 (2026110503) et de la partie R4 (2026110701) ; graine d'une répétition : `SeedSequence([2026110702, rang
  de d, répétition])`. Mêmes réglages que le contrôle 3 (R0 = B = 200, K = 10, e = 5 %).
- **Choix** : d* par interpolation linéaire de la moyenne entre les deux points de la grille qui encadrent 1,0, arrondi
  à 0,01. Si 1,0 n'est pas encadré, la grille est prolongée d'un pas de 0,75 du côté manquant (rang suivant).
- **Vérification** : 12 répétitions à d* (rang 10). La moyenne est rapportée avec ± 1,96 erreur type (répétitions comme
  unités). Si elle s'écarte de 1,0 de plus de 0,03 : un pas de sécante depuis d* et le point de grille le plus proche,
  puis 12 répétitions de plus (rang 11), et l'on s'arrête là.
- Aucune de ces répétitions n'entre dans le contrôle 3 : B-seuil y a ses propres graines (son rang dans `MONDES`).

## 3. Ce qu'on attend du contrôle 3

B-seuil : R1 dans au plus 5 % des répétitions (niveau global du max-T, 5 %, unilatéral ; plan, 5.14, point 1, Q13). La
part est rapportée avec son intervalle de Wilson. Si elle dépasse 5 %, c'est signalé à Otsoa, sans changer de règle.
Sans R1, l'étiquette attendue est « confirmée » : témoins en défaut, comme dans A et E-fort.

## 4. Seconde mesure (ajoutée le 07/11 après le contrôle complet, avant tout calcul de cette mesure)

**Constat** (contrôle 3 complet, `resultats_v5/`). R1 sort dans 10 répétitions sur 120 (8,3 %, IC de Wilson 4,6–14,7 %),
au-dessus des 5 % attendus. La mesure de la section 2 est tenue en moyenne (1,016 ± 0,009 sur les trois cellules),
mais pas cellule par cellule :
- Haiku : 1,050 ± 0,009 ;
- Opus : 1,001 ± 0,013 ;
- Sonnet : 0,998 ± 0,012.

Les 10 R1 portent tous sur des cellules où Haiku intervient : sa configuration, ou les scénarios de changement de modèle
avec Haiku. B-tout dépasse donc vraiment son budget de 5 % chez Haiku. Ces R1 sont justes : le contrôle a mesuré la
puissance du max-T à 1,05 fois le budget, pas son niveau au seuil. La cause est la mesure de la section 2 : une moyenne
des trois cellules ne garantit pas qu'aucune cellule ne dépasse le budget. Le niveau d'un test global se lit quand
aucune cellule ne dépasse le budget et qu'au moins une l'atteint.

**Monde.** B-seuil avec une dérive d = 1,40 (« B-seuil-bis »), seule différence. La dérive vise la cellule la plus
haute, celle de Haiku, à 0,99–1,00 fois le budget. Ajustements sur les points de Haiku déjà calculés (grille, vérification
de la section 2, contrôle complet) :

| Ajustement | Haiku à 0,99 | Haiku à 1,00 |
|---|---|---|
| Linéaire local (1 ; 1,56 ; 1,75) | 1,40 | 1,43 |
| Quadratique local | 1,37 | 1,40 |
| Quadratique global | 1,38 | 1,41 |

1,40 est retenu, sans nouvelle grille. La cible est un peu sous 1,0 parce que les scénarios où Haiku intervient
semblent un peu plus hauts que sa configuration. Cette lecture vient des seules cellules établies, donc biaisée vers le
haut.

**Graines et calcul.**
- Graine maîtresse 2026110703 ; graine d'une répétition : `SeedSequence([2026110703, répétition])`.
- Mêmes réglages que le contrôle 3 (R0 = B = 200, K = 10, e = 5 %).
- Même chemin de calcul que `harnais.repetition`, désaccord persistant compris : un test le vérifie
  (`tests/test_controle3_b_seuil.py`).
- 120 répétitions, 12 processus. Script : `seconde_mesure.py`.

**Mesures.**
- Part de R1, avec son intervalle de Wilson.
- Pour chaque cellule jugée du commerce à enjeu faible (configurations et scénarios), la valeur centrale moyenne ÷
  budget, avec ± 1,96 erreur type. La plus haute est le « dépassement vrai » du monde.

**Lecture, fixée d'avance.**
- Si la plus haute cellule est entre 0,98 et 1,02, la part de R1 se lit comme le niveau du max-T au seuil : on attend
  au plus 5 %.
- Au-dessus de 1,02, elle se lit comme une puissance, comme la première mesure.
- Sous 0,98, elle se lit comme un niveau sous le seuil : on attend toujours au plus 5 %, mais la mesure dit moins.
- Pas d'autre itération.
- Si la part dépasse 5 % alors que la plus haute cellule est entre 0,98 et 1,02, c'est signalé à Otsoa, sans changer
  de règle.

Les deux mesures sont publiées. La première reste dans `resultats_v5/`, à son étiquette attendue.
