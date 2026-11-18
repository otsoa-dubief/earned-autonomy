# Recherche de secrets (PLAN_SUITE T45, 17/11/2026)

Aucune valeur n'est reproduite ici ; seuls les noms de fichiers et les comptes. La clé API n'a jamais été lue ni affichée.

## Motifs cherchés

Clés et jetons : `sk-ant-(api|admin)NN-…`, `ghp_…`, `github_pat_…`, `AKIA…` (AWS), `AIza…` (Google), `xox…` (Slack), en-têtes de clés privées. Puis : adresses électroniques, chemins `/Users/…`, mentions « password » / « mot de passe ».

## Résultats

| Périmètre | Clés et jetons | Autres constats |
|---|---|---|
| Arbre suivi par git (`git ls-files`) | 0 | adresses : utilisateurs fictifs des bancs (atlas.com, example.com, et quelques gmail/yahoo/outlook fictifs dans les sorties du pilote) ; `otsoa.dubief@gmail.com` (choisie par Otsoa) ; une adresse de chercheur dans `revues/dossier_relecteur_exterieur/` (non publié) ; chemins `HOME/…` dans 63 fichiers (sans risque, à nettoyer dans les textes en T48) |
| Historique complet (214 commits, toutes branches) | 0 | voir « Bloquant » ci-dessous |
| Traces des parties (68 990 fichiers du manifeste) | 0 vraie clé ; 3 fichiers avec des correspondances `AKIA…`/`AIza…` à l'intérieur de longues chaînes base64 (signatures de blocs), faux positifs | adresses des utilisateurs fictifs des bancs |

## Bloquant pour la publication de l'historique (Q9)

L'historique git contient des fichiers qui ne doivent pas être publiés : `donnees/` (21 fichiers, dont le fichier scellé, ajoutés au premier commit b5e76cc du 04/11), `notes/` (dont `messages_diffusion.md`, avec des adresses de personnes, et `terrain_2026-11.md`), `CADRE.md` et `ATTENTE.md` (notes personnelles), `pilote/` (592 fichiers, non publié par défaut). Publier l'historique tel quel les rendrait publics. Conformément à la fiche de T45, la publication de l'historique est arrêtée et la question Q9 revient à Otsoa.

Options : (1) copie propre sans historique, avec empreintes ; (2) réécrire l'historique pour en retirer ces fichiers (les identifiants des commits changent, donc les commits cités sur OSF, comme a8eb1aae, ne seraient plus vérifiables dans la version publiée ; la version de travail les garde).

Décision d’Otsoa : copie propre + table d’ancres + archive chiffrée de l’historique (voir `publication/INVENTAIRE.md`). Les chemins `/Users/…` des textes seront retirés en T48.
