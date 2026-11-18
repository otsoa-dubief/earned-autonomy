# Fiche de lecture : Zhang et Zhang, autorité méritée sous plafond fixe

## 1. Référence
- **Auteurs** : Zhaoxi Zhang (University of Technology Sydney) et Xiaomei Zhang (Griffith University).
- **Titre** : « Are You Still the Agent I Authorized? Earned Authority under a Fixed Ceiling for Evolving Agents ».
- **arXiv** : 2607.23586 [cs.AI] (aussi coté cs.CR), **v1 du 26 juillet 2026**. C'est la seule version : la page de résumé arXiv (consultée le 17 novembre 2026) n'en liste aucune autre. DOI 10.48550/arXiv.2607.23586.
- **Lien** : https://arxiv.org/abs/2607.23586 (PDF https://arxiv.org/pdf/2607.23586).
- **Accès** : PDF v1 lu en entier (15 pages : corps pp.1-7 y compris références, annexe pp.8-15), texte extrait avec `pdftotext`, page par page. Le texte n'est pas lu de mémoire.
- **Pagination** : le PDF n'imprime pas de numéros de page. « p. N » = Nième page du PDF. Les sections sont citées avec leur numéro (I à IX ; annexe A à G, sous-sections B1 à B5) quand c'est utile. Les figures et tableaux sont extraits sans mise en page (Fig. 1 à 3, Tableaux I et II) : lus par leurs légendes et cellules, pas visuellement.
- **Nature** : formalisation sans données (« formalization rather than ... an empirical claim », p. 6). Définitions, propositions, théorèmes 1 à 3, contre-exemple (Prop. 7).

## 2. Ce que propose l'article, section par section

**Résumé et I Introduction (pp.1-2).** Problème : un agent qui évolue après déploiement (mémoire, outils, workflows, délégation, phase de tâche) sous un octroi (« grant ») d'autorisation qui reste actif. Trois questions séparées (p. 2) : l'agent ou la tâche ont-ils changé de façon pertinente ; si l'octroi reste valide, quelle autorité est active ; quelle autorité aucune preuve d'exécution ne peut dépasser. Deux garde-fous indépendants : une **enveloppe de transition** (quelles mutations l'octroi peut survivre) et un **plafond d'effets immuable**.
- « We formulate authorization continuity: when does an existing grant remain valid, how may active authority change, and what boundary must never move? » (p. 1)
- « Agent-produced evidence may allocate authority below the ceiling but cannot raise it. » (p. 1)
- « A system may condition authority on demonstrated performance only if it also fixes a bound that no performance can move. » (p. 2, « central design obligation »)
- « descent is free, ascent is evidence-gated, and no runtime evidence can move the user-issued boundary. » (p. 2, contributions)
- Ni la compétence ni les succès passés ne règlent le problème : « Neither higher competence nor successful past behavior resolves this problem. » (p. 2) Les preuves (tests, taux d'erreur) sont produites par la session qui profite de l'augmentation : « gives the beneficiary partial control over its own privilege » (p. 2).
- Ils ne revendiquent pas l'antériorité du narrowing libre : « Existing privilege-control work correspondingly treats automatic narrowing differently from policy expansion, which requires a stronger approval path [25] » (p. 2, [25] = Progent).

**II Agents qui évoluent, III Modèle de système et de menace (pp.2-3).** Le « sujet autorisé » est modèle + harnais (consignes, boucle de planification, mémoire, outils, skills, hooks, délégation) (II.A). Trois dimensions : compétence, affordance (ce que le harnais rend exprimable), autorité. « An increase in competence does not itself justify an increase in the security boundary. » (II.A, pp.2-3) Moniteur externe, hors de portée de l'agent, qui voit une abstraction de l'état ; obligation de solidité : Eff(St, a) ⊆ Req(a) (éq. 1, III.C, p. 3). Attaquant : contrôle contenus, skills, outils distants, mémoire ; ne contrôle ni moniteur ni plafonds (III.D, p. 3).

**IV Quand l'évolution change l'autorité (p. 3).** Le besoin d'autorité d'une tâche peut monter, baisser, devenir incomparable ou rester égal : « Need may rise, fall, become incomparable, or remain unchanged. » (p. 3) Il peut changer sans aucune mutation du sujet (passage de l'édition au push : même modèle, même harnais, même manifeste d'outils). Prop. 3 (annexe B1, p. 9).

**V Modèle minimal lié à l'état (pp.4-5 selon colonnes ; p. 4 pour V.A-C).**
- V.A : un octroi fixe un plafond B, une autorité initiale P0 ⊆ B et une enveloppe de transition. « Contraction is always permitted. An expansion or an incomparable change requires the grant's evidence condition. » Clamp : Pt = Pt^prop ∩ B (éq. 2). « Only a new user grant can replace B. » (p. 4) Si une mutation sort de l'enveloppe, « the monitor suspends the grant before the next protected action, even when Pt ⊆ B still holds » (p. 4).
- V.B : Théorème 1 (non-amplification, forme compacte) : sous médiation complète, solidité de l'éq. 1, délégation atténuante et intégrité du moniteur, tout effet protégé appartient à un plafond émis par l'utilisateur (p. 4). Résultat de frontière : il ne dit rien de l'intention ni des flux d'information.
- V.C : ce que l'ascension conditionnelle peut revendiquer. « A test pass, low error rate, or successful task history may be useful evidence that more of B should be active. » Mais si l'agent produit lui-même la preuve : « The evidence rule then improves expected exposure or reliability, not the adversarial upper bound. » Une borne plus serrée exige une prémisse que la session ne peut pas produire : attestation externe, évaluateur indépendant, contresignature humaine (p. 4).

**VI Mutations pertinentes pour l'autorisation (pp.4-5).** Tableau I : six classes (non disjointes, « a sensitivity checklist »). Control state (changement de modèle/fournisseur, consignes, skill, hook, harnais, **mise à jour de mémoire persistante**) ; Capability (nouvel outil, réseau, identifiants) ; Delegation ; Task or phase ; Trust context ; Enforcement. Réponses typiques : control state, « Re-measure the subject; continue only within an approved transition class » ; capability, « Recompute active authority and its effect bound; contract or request a scoped grant » (p. 5). Enforcement : « Such changes require a higher-authority path outside the agent's current ceiling. » (p. 5)

**VII Positionnement (pp.5-6).** Tableau II : politiques existantes vues comme choix de règle de continuité et de plafond.
- VII.a « Earned autonomy » : « Our objection is not to gradual allocation beneath a limit. It is to allowing performance evidence to raise the limit itself. » « The ladder must also terminate beneath a boundary that no rung can move. » (p. 5) Cibles : cadres praticiens/gouvernance [31]-[34] (AWS, KnowBe4, CSA).
- Tableau II : « Earned-autonomy ladder | Performance evidence may raise the terminal boundary | No fixed ceiling remains unless the ladder terminates below one » (p. 6).
- VII.b-e : Progent, ConLeash, AgenticRei, LBAC, SkillGuard, CaMeL ; ils disent que leurs langages de politique « can instantiate the effect ceiling B and active authority Pt » (p. 5).

**VIII Évaluation et limites (p. 6).** Voir section 4 ci-dessous. Trois limites centrales : choix de B, mécanisme d'application concret de l'éq. 1, révocation inter-générations non résolue.

**IX Conclusion (p. 6).** « This distinction turns "earned autonomy" into a usable allocation policy without mistaking agent-produced evidence for a security boundary. »

**Annexe (pp.8-15).** A : baux (« leases ») L = ⟨CG ; g, p, R, E, τ⟩ (but, phase, ressources, **types d'effets E**, budget d'actions protégées τ), ordre d'autorité, semi-treillis (p. 8). B : portée, plafond, Prop. 3 ; Déf. 5 plafond et ascension gardée ; B3 : borne dépendante de la porte, clôture d'escalade, Théorème 2, Prop. 4-5 ; B4 : pourquoi la règle de preuve n'a pas besoin de robustesse adverse, Déf. 8 (obligation de séparation), Prop. 6 ; B5 : autorité effective. C : enveloppes sur chemins, dérive compositionnelle (Remarque 9). D-E : prédicat de validité, continuité d'autorisation. F : Théorème 3. G : nécessité de la solidité de clôture (Prop. 7). Compléments : Remarque 5 (cliquet sans décroissance) et Remarque 7-8 (deux enveloppes, deux gardes) p. 12.

## 3. La « evidence relation » : abstraite ou instanciée ?
**Laissée abstraite. Aucune instanciation chiffrée.** Elle apparaît comme relation ⊢ dans l'octroi : « A grant fixes a context CG, a ceiling Lmax in that context, an initial active lease L0 ⪯ Lmax, and an evidence relation ⊢. » (Déf. 5, p. 9). Toute proposition qui n'est pas une descente « is admitted only if Evid(t) ⊢ Lprop holds, where Evid(t) is the evidence derivable from the execution prefix up to t » (p. 9). Rien ne dit comment ⊢ est calculée.
- Aucun nombre de succès, aucun seuil, aucune borne d'erreur, aucune fenêtre, aucun budget d'erreur : les recherches de « consecutive », « threshold », « error budget », « first error », « AOQL », « sampling » ne donnent rien dans le texte.
- Seuls exemples de signaux, non quantifiés : « A test pass, low error rate, or successful task history » (V.C, p. 4) ; « test pass rates or historical error rates » (B4, p. 11 : « For reliability-only allocation it may use signals that would be unacceptable as security boundaries, including test pass rates or historical error rates »). Candidats de prémisse externe : « Attestation, an independent countersignature, or a rate condition are candidates, but their interaction cost and actual independence from the agent remain open. » (p. 14, Limites b)
- Ce qui est précisé est la **classe** de ⊢, pas sa valeur : preuve « réalisable » par la session (Déf. 6, p. 9-10) contre preuve avec prémisse hors de portée causale (Prop. 5, p. 11). Règle de conception : « a gate can support a security bound below the ceiling only through premises that the session cannot itself realize » (Remarque 2, p. 11).
- Ils reconnaissent explicitement ne pas savoir quel signal choisir : « That question requires future measurement of which signals predict safe handling at which scope and with what decay. » (p. 14, Limites b) Et l'ascension gardée « does not show that any particular signal improves expected exposure or reliability » (id.).
- Seule règle opérationnelle donnée, en exemple et sans valeur de k : une règle de décroissance (« dropping any component of Lt not exercised within k steps or since the last phase boundary », Remarque 5, p. 12). C'est une décroissance par inactivité, pas une preuve.

## 4. Évaluation empirique
**Aucune.** « The present paper formalizes authorization drift but does not yet measure its frequency or operational cost. We therefore present it as a formalization rather than as an empirical claim about deployed-system prevalence. » (VIII, p. 6)

**Étude de rejeu esquissée, non réalisée** : « A first empirical study should replay tasks across controlled mutations and record: whether an old grant persists, whether a post-mutation action escapes its original effect set, whether benign changes cause unnecessary suspension, and how often users must reauthorize. These correspond to grant persistence rate, post-mutation unauthorized-effect rate, false invalidation rate, and interaction cost. » (p. 6)
- Nuance importante : le rejeu esquissé porte sur les **mutations et l'enveloppe** (persistance de l'octroi, fuite d'effets, fausses invalidations, coût d'interaction), **pas** sur la règle de preuve ⊢ ni sur la fiabilité réelle des modèles.
- Autre mention d'instrument : toute mesure devrait « avoid the oracle rather than approximate it, by fixing goals and phases in advance so that a benchmark policy rather than a language model's judgment determines the ground truth » (D, p. 13).
- Les « witnesses » de la Prop. 3 (coding agent, test runner, push de branche) et la construction de la Prop. 7 sont des constructions théoriques, pas des mesures.

## 5. Plafond fixe et ré-examen après mutation
**Plafond.**
- « The ceiling is fixed: no runtime signal whatsoever, including evidence about the agent's competence or track record, may raise it, and raising it requires a fresh user grant. » (Déf. 5, p. 9)
- Clamp mécanique, sans événement utilisateur : « A ceiling violation is handled mechanically, by the clamp, with no user event. » (Remarque 8, p. 12)
- Obligation de séparation : « An authorization system satisfies the separation obligation if every grant fixes a bound Lmax at grant time such that no signal admissible as an input to ⊢ can raise it. » (Déf. 8, p. 11)
- Même si la preuve est entièrement compromise : « the worst outcome of a fully compromised evidence channel is that Lt rises to Lmax, which is the bound the system already guarantees » (B4, p. 11).
- Cible directe des échelles de maturité : « Maturity models in which demonstrated performance removes the last ceiling at an unsupervised stage violate Definition 8 by construction. » (p. 12)
- Limite : « a high ceiling weakens the result, while a low ceiling interrupts useful work » ; pas de méthode générale pour choisir B (VIII, p. 6 ; Limites a, p. 14).
- La garantie est conditionnelle à cinq hypothèses de runtime (A1 médiation complète, A2 vue du moniteur solide en clôture, A3 admission solide, A4 délégation atténuante, A5 intégrité du moniteur) et à l'attribution à un seul bail (Hyp. 2) (p. 13) ; A2 est nécessaire (Prop. 7, p. 14).

**Ré-examen après mutation (mémoire, outils, workflows).**
- L'enveloppe est fixée à l'octroi et est indépendante du plafond : « M is indexed by transition labels and asks whether the grant survives a change; the ceiling is indexed by authority and asks how much of it may be in force. Neither implies the other » (Remarque 8, p. 12).
- Sortie de l'enveloppe : suspension de l'octroi, même sous le plafond (p. 4, voir ci-dessus). « The appropriate response is consequently grant-relative: recompute active authority when required effects change, suspend when a continuity condition fails, and otherwise preserve the grant. » (IV, p. 3)
- Mémoire : classe « Control state », « persistent-memory update » ; réponse « Re-measure the subject; continue only within an approved transition class ». Outils : classe « Capability », « New tool or service » ; réponse « Recompute active authority and its effect bound; contract or request a scoped grant ». Workflows : « instruction, skill, hook, harness » (Control state), et « workflow code » dans l'état (I, p. 1-2) (Tableau I, p. 5).
- « The relevant boundary is not whether bytes changed, but whether the changed component can influence a protected action under the current grant. » (VI.a, p. 4-5)
- Limite : « Bitwise identity is too strict and session identity too weak, leaving sound envelopes and a computable A# as central open problems » (p. 14) ; dérive compositionnelle (Remarque 9, p. 12) ; révocation inter-générations non résolue (VIII, p. 6).
- Ils ne prescrivent donc pas de remise à zéro des preuves : la réponse dépend de l'octroi (continuer, contracter, suspendre, redemander).

## 6. Vérification des affirmations du brouillon (`article/brouillon.md`, lignes 52, 54, 84)

### Ligne 52 (« Earned authority »)
| # | Affirmation | Verdict | Preuve et reformulation |
|---|---|---|---|
| 52a | L'article « formalises an agent's authority that may decrease freely, grows only under evidence conditions » | **Exacte** | Déf. 5, p. 9 : « Descent is free ... Every other proposal counts as ascent ... and is gated ». Aussi p. 4 (V.A). |
| 52b | « never exceeds a ceiling fixed by the principal » | **À nuancer** | Fond exact (p. 4, p. 9 : « Only a new user grant can replace B »), mais **« principal » désigne l'agent** dans l'article (« This is the security principal », II.A, pp.2-3 : le sujet autorisé = modèle + harnais). Le plafond est fixé par l'**utilisateur**. Aussi : la garantie est conditionnelle aux hypothèses A1 à A5 (Théorème 1, p. 4 ; Théorème 3, p. 14). Proposition : « never exceeds a ceiling issued by the user at grant time (under the assumptions of its non-amplification theorem) ». |
| 52c | « is re-examined after mutations of the agent (memory, tools, workflows) » | **À nuancer** | Exact comme couverture : mémoire, outils, workflows sont dans les classes Control state et Capability (Tableau I, p. 5). Mais l'article ne pose pas un ré-examen systématique : une enveloppe fixée à l'octroi dit quelles mutations l'octroi survit ; hors enveloppe, **suspension** (p. 4) ; dedans, continuité, contraction ou nouvelle demande selon l'octroi (p. 5, VI). La phase de tâche, la délégation, le contexte de confiance et l'application sont aussi des classes. Proposition : « and in which a grant survives a mutation of the agent (memory, tools, workflows, ...) only if the mutation class belongs to a transition envelope fixed at grant time; otherwise the grant is suspended ». |
| 52d | « Our caps (Section 3.2) borrow the fixed ceiling directly from this work » | **À nuancer** | Voir 84c : l'idée générale (narrowing libre, expansion approuvée, privilège minimal) préexiste et ils la citent (p. 2, p. 5, Saltzer-Schroeder [23]). Ce qui est à eux : la formulation explicite (Déf. 8, p. 11) et la preuve que la preuve de compétence ne peut pas porter la borne de sécurité (Prop. 4-6, pp.10-12). Dire « adopt the separation between a fixed ceiling and evidence-driven allocation beneath it from ». |
| 52e | « Zhang and Zhang provide a formal framework » | **Exacte** | Déf. 1 à 13, Prop. 1 à 7, Théorèmes 1 à 3 (pp.8-15). |
| 52f | leur relation de preuve est « (abstract) » | **Exacte** | Déf. 5, p. 9 : ⊢ sans instanciation. Voir section 3. Nuance à garder en tête : ils donnent des exemples de signaux non chiffrés et une règle de décroissance avec k libre (pp. 4, 11, 12). |
| 52g | « Their paper presents itself as a formalisation without empirical evaluation (we read it in full) » | **Exacte** | VIII, p. 6 : « We therefore present it as a formalization rather than as an empirical claim ». Lecture intégrale v1 faite ici (15 pages). Préciser « (v1, 26 July 2026) ». |

### Ligne 54 (« How this work differs from Zhang and Zhang »)
| # | Affirmation | Verdict | Preuve et reformulation |
|---|---|---|---|
| 54a | « formalise authorization continuity for evolving agents » | **Exacte** | Résumé, p. 1. |
| 54b | « a transition envelope decides whether a grant survives a mutation » | **Exacte** | Résumé p. 1 ; V.A p. 4 ; Remarque 8, p. 12. |
| 54c | « an immutable effect ceiling bounds all authority » | **Exacte** | Déf. 5, p. 9 ; p. 2 : « An immutable effect ceiling bounds all authority available under the grant ». |
| 54d | « active authority may fall freely but rise only when an evidence relation holds » | **Exacte** | Déf. 5, p. 9. |
| 54e | « That relation is left abstract » | **Exacte** | Section 3. |
| 54f | « the paper is a formalisation with no empirical evaluation » | **Exacte** | p. 6. |
| 54g | « it outlines a replay study without running it » | **Exacte, à préciser** | p. 6 : « A first empirical study should replay tasks across controlled mutations and record ... ». Le rejeu esquissé mesure persistance de l'octroi, fuite d'effets, fausses invalidations, coût d'interaction ; il ne teste pas de règle de preuve. À ne pas laisser croire que leur rejeu ressemble au nôtre. Proposition : « it outlines, without running it, a replay study of controlled mutations that would measure grant persistence, post-mutation unauthorized effects, false invalidations and interaction cost ». |
| 54h | « Their ceiling protects against adversarial amplification » | **Exacte, à nuancer** | p. 9 : « The ceiling is a security boundary and holds against an adversary », et l'abstract/Théorème 1 (non-amplification). Nuances : (i) sous les hypothèses A1-A5 (p. 13) ; (ii) elle borne les **effets**, pas l'intention ni les flux d'information (Remarque 11, p. 14) ; (iii) l'article dit lui-même que la preuve sous le plafond est un mécanisme de **fiabilité** (« reliability mechanism », p. 9), ce qui rejoint exactement notre « authority by reliability beneath such a ceiling ». |
| 54i | « our rule allocates authority by reliability beneath such a ceiling » | **Exacte (notre apport)** | Cohérent avec « The evidence relation ⊢ governs position beneath that boundary and is a reliability mechanism » (p. 9) et « For reliability-only allocation it may use signals ... including test pass rates or historical error rates » (p. 11). Danger à signaler dans les limites : leur Remarque 2 (p. 11) dit qu'une porte dont la preuve est réalisable par la session « is a reliability mechanism and should not be described as a tighter adversarial bound ». Notre garantie 1/(1+Nd) doit donc rester présentée comme bornant des erreurs en espérance, pas un risque adverse. |

### Ligne 84 (§ plafonds)
| # | Affirmation | Verdict | Preuve et reformulation |
|---|---|---|---|
| 84a | « Some actions are always validated, whatever the evidence: modifying a guardrail or the agent's own rights ... » (analogie avec leur cadre) | **Compatible** (non attribué à eux dans le texte de la ligne 84) | L'article place en classe « Enforcement » tout changement du moniteur, de la politique d'approbation, du sandbox : « Such changes require a higher-authority path outside the agent's current ceiling » (p. 5) ; Hyp. A5 : intégrité du moniteur (p. 13). On peut citer en appui, sans leur prêter la liste d'actions de notre brouillon. |
| 84b | Plafonds d'argent (2 500, 500, 400 USD) et premier message à un inconnu | **Non couvert par l'article** (ne pas leur attribuer) | Leur plafond est un ensemble d'effets protégés (types d'effets et ressources), avec « budgets » portés à côté (p. 4) ; τ est un nombre d'actions protégées, pas un montant (p. 8). Aucun montant ni catégorie « argent » ou « destinataire inconnu » dans le texte. |
| 84c | « Only the human changes a cap, by a dated decision. The idea of a ceiling that evidence cannot lift comes from Zhang and Zhang (2026). » | **À nuancer** | « Only the human changes a cap » : conforme à « raising it requires a fresh user grant » (p. 9) ; « by a dated decision » est de nous. « comes from » est trop fort : (i) l'article cite l'existant : narrowing libre / expansion sous approbation chez Progent (p. 2 et p. 5), privilège minimal (Saltzer-Schroeder [23], p. 5-6) ; (ii) leur apport propre est la formulation « separation obligation » (Déf. 8, p. 11) et la démonstration que la preuve réalisable par la session ne peut pas serrer la borne (Prop. 4-6, pp.10-12). Proposition : « The separation between a ceiling that evidence cannot lift and an evidence-gated allocation beneath it is formalised by Zhang and Zhang (2026) as a separation obligation (Definition 8). » |

**Affirmations inexactes strictes** : aucune. **À nuancer** : 52b (« principal »), 52c (« re-examined » vs suspension sous enveloppe), 52d et 84c (« borrow » / « comes from », antériorité de l'idée), 54g (nature du rejeu esquissé), 54h (hypothèses A1-A5, effets et non intentions). **À ne pas attribuer** : les montants et catégories de plafonds (84b).

## 7. Part d'antériorité

**Ce que leur texte contient déjà de notre idée.**
- **Plafond fixe, que la preuve ne peut pas lever** : oui, complètement, y compris la critique des échelles de maturité sans plafond (Déf. 5 p. 9, Déf. 8 p. 11, Remarque sur les « maturity models » p. 12, VII.a p. 5, Tableau II p. 6). C'est leur cœur.
- **Descente libre, montée sur preuve** : oui (Déf. 5, p. 9). Notre retrait est un cas particulier de leur « descent is free », mais ils ne le déclenchent pas sur une erreur.
- **Preuve = signal de fiabilité, pas de sécurité** : oui (B4, p. 11 ; V.C p. 4).
- **Réexamen sur mutation** (mémoire, outils, workflows, phase) : oui comme enveloppe et suspension (pp.3-5). Notre remise à zéro est plus précise sur ce qui est conservé, mais ils ont l'idée que l'octroi ne survit pas à tout.
- **Autorité à grain fin** : leur bail est un tuple (but, phase, ressources, **types d'effets**, budget) avec ordre et intersection (Déf. 1-3, p. 8) ; l'autorité active est donc une partie du plafond par type d'effet. La structure permet une règle par type, mais ils n'en donnent pas.
- **Décroissance** : règle d'exemple par inactivité (k pas), Remarque 5, p. 12, et son rôle : sans elle, l'autorité « ratchets upward » jusqu'à Lmax (p. 12).

**Ce qu'il ne contient pas** (recherches par mots-clés dans le texte extrait, aucun résultat pour « consecutive », « threshold », « error budget », « first error », « AOQL », « sampling »).
- **Règle par type d'action** : non. Rien ne dit que la preuve est comptée par type d'action ; la question « which signals predict safe handling at which scope » est renvoyée à de futures mesures (p. 14).
- **N tiré d'un budget d'erreur** : non. Aucune longueur de série, aucun budget d'erreur. Le seul « budget » est τ, un compteur d'actions protégées servant de borne de cycle de vie (p. 8, « a usage budget rather than a wall-clock deadline »), sans rapport avec un taux d'erreur.
- **Retrait à la première erreur** : non. Une erreur n'est jamais un déclencheur ; la contraction est permise à tout moment (p. 4) mais pas prescrite par un événement d'erreur. La suspension se déclenche sur **mutation hors enveloppe** (p. 4), pas sur un échec constaté.
- **Garantie de type AOQL** : non. Leur garantie est une inclusion d'ensembles d'effets (Théorème 1 p. 4, Théorème 3 p. 14), pas une borne sur un taux ou un nombre d'erreurs. Ils reconnaissent même qu'une porte de fiabilité « improves expected exposure or reliability, not the adversarial upper bound » (p. 4) et que savoir si un signal réduit réellement l'exposition attendue est une question ouverte (p. 14). Notre borne 1/(1+Nd) en espérance est donc hors de leur formalisme.
- **Préenregistrement et évaluation sur épisodes réels** : non (section 4).
- **Distinction de gravité/réversibilité** : seulement évoquée (« consequences and irreversibility of the next action », Tableau I, p. 5 ; « irreversible stage », p. 9), sans mécanisme de calibrage.

**Conséquence pour l'article** : le brouillon revendique à juste titre l'instanciation de la relation de preuve, la dérivation de N depuis un budget, le retrait à la première erreur, la garantie en espérance, le test empirique. Il doit être précis sur ce qui est repris d'eux (le plafond que la preuve ne lève pas, la séparation fiabilité/sécurité, la descente libre, l'idée de réexamen sur mutation) et utiliser leur Remarque 2 (p. 11) comme borne d'interprétation de notre garantie : sous plafond, elle borne des erreurs en espérance, elle n'est pas une borne adverse.

## Points ouverts
- Lecture sans mise en page des Fig. 1-3 et des Tableaux I-II : légendes et cellules lues, pas la disposition visuelle.
- Versions ultérieures : aucune au 17 novembre 2026 (page de résumé). À revérifier avant dépôt.
