# Consigne des relecteurs : alertes et audit des tâches sans alerte

Figée au gel (`PLAN_EXPERIENCE.md`, 4.3 à 4.5 ; `REGLE.md`, point 7). Elle est donnée telle quelle à chaque instance de
Claude qui relit, avec un lot de fiches aveugles. Otsoa juge selon les mêmes motifs : sa page de relecture en donne
le résumé, et il lit cette consigne une fois avant sa première relecture.

## Ton travail

Chaque fiche montre une écriture d'un agent que le contrôle automatique a marquée (ligne « ACTION SIGNALÉE ») :
fausse, doublon ou refusée. Tu décides si l'alerte est **confirmée** (vraie erreur de l'agent) ou **levée** (fausse
alerte).

Une alerte n'est levée que pour l'un des quatre motifs ci-dessous, preuve à l'appui. Toute autre alerte est confirmée.
Dans le doute, tu confirmes.

## Ce que tu as, et rien d'autre

- La fiche :
  - le résumé ;
  - la différence champ par champ avec l'action attendue la plus proche ;
  - l'énoncé de la tâche, c'est-à-dire la consigne du client simulé ;
  - les règles du domaine utiles à l'outil, puis le règlement entier reçu par l'agent ;
  - l'état initial propre à la tâche, s'il y en a un (τ-bench) ;
  - les actions attendues ;
  - la conversation entière.
- Cette consigne.

Un défaut qui ne se prouve pas avec les pièces de la fiche ne se lève pas : tu confirmes. Cela vaut en particulier pour
la base de connaissances de la banque, que la fiche ne montre pas, et pour WorkBench, qui n'a pas de règlement. Pour
WorkBench, le motif (c) s'apprécie sur la seule consigne du client : un autre chemin est permis s'il fait ce que la
consigne demande sans rien qu'elle interdise. (Précisé le 7 novembre, relecture C13, P10.)

Tu ne cherches rien ailleurs : ni sur le web, ni dans d'autres fichiers, ni dans d'autres fiches. Tu ne cherches pas à
savoir quel modèle a joué. Tu ne compares pas les fiches entre elles et tu ne fais aucun décompte.

## Les quatre motifs de levée

### (a) Tâche défectueuse

La tâche est défectueuse seulement si ses propres fichiers se contredisent. Ses fichiers sont le règlement, les données
initiales, la consigne du client et les actions attendues. Ce qu'a fait l'agent peut signaler le défaut, jamais le
prouver. Il y a quatre cas ; donne son numéro au début de la preuve (par exemple « a2 : … »).

1. **a1, contre le règlement** : une action attendue, ou l'un de ses arguments comparés, est interdite par un paragraphe
   explicite du règlement, ou contredit une obligation explicite. Preuve : le paragraphe cité mot pour mot, et l'action
   attendue.
2. **a2, impossible avec les données** : une action attendue ne peut pas réussir telle qu'elle est écrite sur les
   données initiales (objet absent, condition préalable fausse, montant ou identifiant impossible). Preuve :
   l'enregistrement en cause, et l'action. Le résultat d'une lecture faite avant toute écriture de la partie vaut extrait
   des données initiales.
3. **a3, consigne contraire** : la consigne du client demande un résultat incompatible avec les actions attendues, si
   bien qu'un agent qui suit à la fois le client et le règlement ne peut pas les atteindre. Preuve : la phrase de la
   consigne, et l'action.
4. **a4, information introuvable** : un argument comparé d'une action attendue ne se trouve ni dans ce que le client
   peut dire d'après sa consigne, ni dans les données accessibles par les outils de l'agent, ni par une règle du
   règlement. Preuve : les sources vérifiées, une à une.

Ne sont pas des défauts : une tâche difficile ; un client simulé qui se contredit dans cette seule conversation ; un
autre chemin permis (motif c) ; un champ libre reformulé (motif b) ; un défaut de notre comparaison (motif d).

### (b) Reformulation d'un champ libre

Le champ en cause est du texte libre (message, note, raison) et l'écriture a le même destinataire, le même sens et le
même effet que l'action attendue. Preuve : les deux textes. Ce motif ne vaut ni pour un identifiant, un montant, une
date ou un choix dans une liste, ni pour un autre destinataire.

### (c) Autre chemin permis

Ce qu'a fait l'agent est permis par le règlement (aucun paragraphe ne l'interdit et les conditions qu'il pose à cette
action sont remplies) et produit l'effet que voulait le client d'après sa consigne. Preuve : le ou les paragraphes du
règlement, et l'effet obtenu. Ce motif ne vaut pas si l'effet diffère de ce que voulait le client.

### (d) Défaut de notre comparaison

L'écriture est juste, mais notre code l'a marquée : champ comparé à tort, même valeur écrite autrement, doublon jugé à
tort, refus causé par notre banc et non par l'agent. Preuve : la ligne de la différence, et la raison pour laquelle la
valeur est la même ou la comparaison inadaptée.

## Ce que tu rends

Une ligne CSV par alerte, avec les colonnes `alerte_id,decision,motif,justification,preuve` (format contrôlé par
`banc/relecture/decisions.py`) :
- `alerte_id` : l'identifiant opaque de la fiche, recopié tel quel ;
- `decision` : « confirmée » ou « levée » ;
- `motif` : a, b, c ou d si l'alerte est levée ; vide si elle est confirmée ;
- `justification` : une phrase, toujours ;
- `preuve` : obligatoire si l'alerte est levée. C'est l'extrait cité mot pour mot, avec la partie de la fiche d'où il
  vient.

Tu ne résumes pas les cas en dehors du fichier rendu.

## Audit d'une tâche sans alerte (`PLAN_EXPERIENCE.md`, 4.5)

La fiche montre une tâche et une partie de cette tâche où rien n'a été signalé : le résumé, la liste des écritures
jugées justes, l'énoncé de la tâche, les données initiales propres à la tâche s'il y en a, le règlement entier, les
actions attendues et la conversation entière. Dans la conversation, chaque écriture jugée juste porte la marque
« ◄ ÉCRITURE n° k ». Une écriture répétée sans effet porte une marque à part : elle est neutre, tu ne la juges pas.

Tu réponds à deux questions.
1. **La tâche est-elle défectueuse**, selon le motif (a) ? Si oui : le cas (a1 à a4) et la preuve.
2. **Une écriture marquée est-elle fausse sans avoir été signalée ?** C'est le cas quand le règlement ou la demande
   du client la contredit, par exemple sur un champ que la comparaison ne regarde pas, ou par un outil sans comparaison.
   Pour chacune, donne le numéro de l'écriture (celui de sa marque), l'outil, le champ et la preuve. Compte aussi les
   écritures marquées que tu as lues (normalement, toutes).

Une ligne CSV par tâche, avec les colonnes
`tache,defectueuse,cas,preuve,erreurs_invisibles,ecritures_lues` (format contrôlé par
`banc/relecture/audit_sans_alerte.py`) :
- `tache` : l'identifiant opaque de la fiche, recopié tel quel ;
- `defectueuse` : oui ou non ;
- `cas` : a1 à a4 si la tâche est défectueuse ; vide sinon ;
- `preuve` : obligatoire si la tâche est défectueuse ;
- `erreurs_invisibles` : vide s'il n'y en a pas ; sinon une liste séparée par « | », chaque élément au format
  « écriture ; outil ; champ ; preuve » (par exemple « 2 ; update_reservation_flights ; cabin ; le client a demandé
  la classe économique, message 7 »). Ni « | » ni « ; » dans l'outil ou le champ, ni « | » dans la preuve ;
- `ecritures_lues` : un entier.
