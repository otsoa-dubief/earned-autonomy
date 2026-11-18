# Tirage des tâches de développement

- Date et heure : 2026-11-05 07:11
- Méthode : `random.Random(graine).sample` sur la liste triée des identifiants, 20 % par environnement, arrondi au supérieur. WorkBench est stratifié par fichier de tâches. Les environnements sont tirés dans l'ordre aviation, commerce, banque, puis les fichiers WorkBench par ordre alphabétique, avec un seul générateur.
- Graine (`secrets.randbits(64)`, tirée avant le tirage) : 2960877271009010073
- Refaire le tirage : `simulation/.venv/bin/python banc/tirage/tirer.py 2960877271009010073 <dossier>`

## Effectifs

| Environnement | Total | Développement | Réserve |
|---|---|---|---|
| aviation | 50 | 10 | 40 |
| commerce | 114 | 23 | 91 |
| banque | 97 | 20 | 77 |
| WorkBench | 690 | 138 | 552 |

### WorkBench par fichier

| Fichier | Total | Développement |
|---|---|---|
| analytics | 120 | 24 |
| calendar | 110 | 22 |
| customer_relationship_manager | 80 | 16 |
| email | 90 | 18 |
| multi_domain | 210 | 42 |
| project_management | 80 | 16 |

Le jeu de confirmation sera tiré plus tard parmi les tâches réservées, par un agent séparé, puis chiffré ; Otsoa en garde la clé (CADRE.md, point 5).
