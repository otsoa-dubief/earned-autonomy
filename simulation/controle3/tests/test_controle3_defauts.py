"""Contrôle 3 : défauts relevés, rendus exécutables (RAPPORT.md, « Défauts trouvés » et « Deuxième passage »).

Chaque défaut a un test qui décrit le comportement actuel (vert), et, quand la propriété attendue est claire, un test
marqué `xfail(strict=True)` qui l'énonce : il passera le jour où le défaut sera corrigé, et devra alors perdre sa
marque. Aucun de ces tests ne modifie le moteur.

Second passage (06/11) : G1 et M1 sont corrigés par le moteur (phase 4, commit 07ae30d ; décisions Q14 et Q15) ; leurs
tests décrivent désormais la règle du 06/11. Nouveau : N1 (R4 presque inatteignable), et le résidu de G1 sur les
grappes d'une écriture. Troisième passage (06/11) : N1 et le résidu de G1 sont corrigés (taux médian ; ρ̂ sur les tâches
d'au moins deux écritures) ; leurs tests décrivent la règle corrigée.
"""
import numpy as np
import pytest

from aide_controle3 import entrees_main, taches_wb
from controle3 import harnais as HA
from controle3 import mondes as MD
from rejeu import analyse as AN
from rejeu import classes as CL
from rejeu import config_rejeu as CR
from rejeu import decision as DE
from rejeu import pipeline as PL
from rejeu import preuves as PR
from rejeu import regles as RG
from rejeu import suites as SU
from rejeu import types_regle as TY

H, S, O = CR.MODELES
ENV = "WorkBench"
TACHES = taches_wb(200)
PLANCHER = CL.SOURCES_G1[2]
SOURCE_COMMUN = CL.SOURCES_G1[1]


def classes_wb(erreurs: dict) -> dict:
    """Classes de WorkBench sur 200 tâches : Haiku 5 passages, Sonnet et Opus 1 passage, une écriture réversible par
    partie ; erreurs = {modèle: {(tâche, passage)}}. Un seul environnement : sans erreur, ρ̂ prend le plancher."""
    specs = {m: dict(passages=5 if m == H else 1, taches=TACHES, erreurs=erreurs.get(m, set())) for m in CR.MODELES}
    e = entrees_main(ENV, specs)
    prep = PR.preparer(e)
    jk = {m: SU.jeu_configuration(prep, e, ENV, m, TACHES, "calibration") for m in CR.MODELES}
    return CL.classes_environnement(jk, CR.charger_config())


# --------------------------------------------------------------------------
# G1 (corrigé le 06/11) : ρ̂ par environnement, plancher 0,3 ; le classement prouvé est monotone
# --------------------------------------------------------------------------
def test_g1_regle_du_06_11_plancher_sans_erreur_et_avec_une_erreur():
    """Règle N3 (06/11, quatrième passage) : même plancher pour le taux médian ; la classe prouvée se lit sur la taille
    effective à ρ = 1 (200 tâches de 5 écritures : 200), la classe sous hypothèse sur ρ̂."""
    zero = classes_wb({})[H][TY.ECR]
    une = classes_wb({H: {(TACHES[0], 1)}})[H][TY.ECR]
    # zéro erreur : le plancher 0,3 pour le taux médian ; à ρ = 1, 200 tâches ne prouvent pas une barre de 1/132
    assert zero["source_rho"] == PLANCHER and zero["rho"] == pytest.approx(0.3)
    assert zero["n_eff"] == pytest.approx(1000 / (1 + 4 * 0.3)) and zero["n_eff_preuve"] == pytest.approx(200)
    assert zero["classe"] == CL.INDETERMINE and zero["classe_sous_hypothese"] == CL.SOUS
    # une erreur dans une tâche de 5 écritures : ρ̂ commun (≈ 0) relevé au plancher
    assert une["source_rho"] == SOURCE_COMMUN and une["rho"] == pytest.approx(0.3)
    assert une["n_eff"] == pytest.approx(zero["n_eff"]) and une["classe"] == CL.INDETERMINE
    assert une["classe_sous_hypothese"] == CL.INDETERMINE
    # Q14 : délégable sur la meilleure estimation, avec ou sans erreur
    assert CL.estime_sous(zero) and CL.estime_sous(une)


ORDRE_CLASSES = {CL.SOUS: 0, CL.INDETERMINE: 1, CL.AU_DESSUS: 2, CL.SANS_DONNEE: 2}


def test_g1_propriete_attendue_monotonie():
    """Corrigé le 06/11 (ce test était en xfail strict au premier passage) : une erreur de plus ne rend jamais la
    classe plus favorable."""
    for cle in ("classe", "classe_sous_hypothese"):
        classes = [classes_wb({H: {(t, 1) for t in TACHES[:x]}})[H][TY.ECR][cle] for x in (0, 1, 2, 5)]
        rangs = [ORDRE_CLASSES[c] for c in classes]
        assert rangs == sorted(rangs)


def test_g1_residu_corrige_les_grappes_d_une_ecriture_ne_comptent_plus_dans_rho():
    """Résidu de G1, corrigé le 06/11 (troisième passage) : ρ̂ ne se lit que sur les tâches d'au moins deux écritures.
    L'unique erreur de l'environnement, chez Sonnet dans une grappe d'une écriture (un passage), ne change plus ρ̂ :
    Haiku garde le plancher, sa taille effective et son classement « sous la barre » (au second passage : ρ̂ = 1,
    taille effective ramenée à 200, « indéterminé »)."""
    chez_sonnet = classes_wb({S: {(TACHES[0], 1)}})[H][TY.ECR]
    sans = classes_wb({})[H][TY.ECR]
    assert chez_sonnet["rho"] == pytest.approx(0.3) and chez_sonnet["source_rho"] == sans["source_rho"] == PLANCHER
    assert chez_sonnet["n_eff"] == pytest.approx(sans["n_eff"])
    assert chez_sonnet["classe_sous_hypothese"] == CL.SOUS == sans["classe_sous_hypothese"]   # N3 : classe à ρ = 1
    assert CL.estime_sous(chez_sonnet) and CL.jugeable(chez_sonnet)
    # les estimateurs seuls : une erreur dans une grappe d'une écriture ne suffit plus à donner ρ̂ = 1
    assert CL.rho_anova([1, 5, 5], [1, 0, 0]) is None
    assert CL.rho_fc_strates([(np.array([1.0, 5.0, 5.0]), np.array([1.0, 0.0, 0.0]))]) is None


def test_n3_corrige_les_temoins_en_defaut_ne_gonflent_plus_le_rho_des_autres():
    """N3 (troisième passage), corrigé le 06/11 : Sonnet se trompe beaucoup (deux passages : grappes de deux écritures),
    Haiku jamais. L'ancienne analyse de variance réunie lisait l'écart de taux comme une corrélation ; le Fleiss–Cuzick
    stratifié ne la voit plus, et Haiku garde le plancher."""
    rng = np.random.default_rng(7)
    err = {S: {(t, p) for t in TACHES for p in (1, 2) if rng.random() < 0.1}}
    specs = {m: dict(passages={H: 5, S: 2, O: 1}[m], taches=TACHES, erreurs=err.get(m, set())) for m in CR.MODELES}
    e = entrees_main(ENV, specs)
    prep = PR.preparer(e)
    jk = {m: SU.jeu_configuration(prep, e, ENV, m, TACHES, "calibration") for m in CR.MODELES}
    assert CL.rho_jeux(list(jk.values())) > 0.3                     # l'ancienne lecture, réunie : gonflée
    cl = CL.classes_environnement(jk, CR.charger_config())
    assert cl[H][TY.ECR]["rho"] == pytest.approx(0.3)                # la nouvelle : plancher


# --------------------------------------------------------------------------
# M1 (corrigé le 06/11) : « tout faire valider » en troisième témoin ; une règle inerte obtient R2
# --------------------------------------------------------------------------
def decision_regle(inerte: bool):
    """Haiku : 1 erreur sur 700 écritures de calibration (délégable). Sonnet et Opus : 30 % d'erreurs sur l'écriture
    réversible, que la liste fixe et le tri par le risque délèguent sans preuve. B-tout rejouée avec N = 10 000 (jamais
    au palier 3) ; inerte : en plus, aucun palier 2."""
    rng = np.random.default_rng(4)
    cal, conf = TACHES[:100], TACHES[100:]
    err = {H: {(cal[0], 1)},
           S: {(t, 1) for t in TACHES if rng.random() < 0.3}, O: {(t, 1) for t in TACHES if rng.random() < 0.3}}
    specs = {m: dict(passages=7 if m == H else 1, taches=TACHES, erreurs=err[m]) for m in CR.MODELES}
    e = entrees_main(ENV, specs)
    prep = PR.preparer(e)
    cfg = CR.charger_config()
    r = RG.regle("B-tout", ENV, cfg)
    params = None
    if inerte:
        p = r.params
        params = RG._params("B-tout", p.pb2, p.pm2, p.pb3, p.pm3, np.zeros(TY.NT, dtype=bool), alpha=p.alpha)
    regles = {ENV: [RG.variante(r, "B-tout", N=np.where(TY.MERITE, 10_000, 0), params=params)]}
    reg = AN.Reglages(G0=5, R0=20, B=80, K=2, tranche=40, valeurs_e=(0.05,), noms_regles=("B-tout",),
                      choix=dict(methode="iii", repli=False, G_sur=20, methode_seconde="percentile"))
    an = PL.analyser(e, prep, cfg, reg, {ENV: conf}, {ENV: cal}, scenarios=False, regles_imposees=regles)
    return DE.decider(an, DE.point0(e, prep))


def test_m1_regle_sans_palier_3_delegue_au_palier_2_et_obtient_confirmee():
    """Décision 4 (5.14, point 2, lecture du 06/11) : le palier 2 est une délégation. La règle du premier passage
    n'atteint jamais le palier 3 mais agit au palier 2 sur l'écriture réversible : elle bat « tout faire valider » par
    la charge, et « confirmée » est légitime quand les deux autres témoins dépassent le budget."""
    dec = decision_regle(inerte=False)
    assert all(c["statut"] != DE.JUGEE for c in dec["point1"]["cellules"])          # jamais au palier 3 : m = 0
    t = dec["point2"]["temoins"]
    assert set(t) == {"tout_valider", "liste_fixe", "tri_risque"}
    assert t["tout_valider"]["battu_charge"] and t["tout_valider"]["intervalle"][1] < 0
    assert t["liste_fixe"]["battu_partout"] and t["tri_risque"]["battu_partout"]
    assert dec["etiquette"] == "confirmée" and dec["mention"] == ""


def test_m1_propriete_attendue_regle_inerte_r2_aucune_delegation_etablie():
    """Corrigé le 06/11 (Q15 ; 5.16, point 9) : une règle qui ne quitte jamais le palier 1 ne bat pas « tout faire
    valider » (différence nulle partout), même quand les deux autres témoins dépassent le budget : R2, « aucune
    délégation établie »."""
    dec = decision_regle(inerte=True)
    t = dec["point2"]["temoins"]
    assert not t["tout_valider"]["battu"]
    assert t["liste_fixe"]["battu_partout"] and t["tri_risque"]["battu_partout"]
    assert dec["etiquette"] == "R2" and dec["mention"] == DE.R2_AUCUNE


def test_regle_inerte_du_harnais():
    """Le monde D-inerte rejoue B-tout sans palier 2 et avec un N jamais atteint."""
    regles = HA.regles_monde(MD.MONDES_PAR_NOM["D-inerte"], CR.charger_config())
    for env, (r,) in regles.items():
        assert r.nom == "B-tout" and not r.params.a_palier2.any()
        assert (r.N[list(TY.TYPES_SUITE)] == HA.N_INERTE).all()


# --------------------------------------------------------------------------
# N1 (second passage) : R4 presque inatteignable, la délégabilité vient des types à enjeu fort sans erreur
# --------------------------------------------------------------------------
def classes_monde_c(graine: int = 1) -> dict:
    """Classes calibrées (règle du rejeu : G1 et Q14) d'une répétition du monde C : tous les types à 5 × barre."""
    cfg = CR.charger_config()
    g = MD.generer(MD.MONDES_PAR_NOM["C"], np.random.default_rng(graine), cfg)
    e = g["entrees"]
    prep = PR.preparer(e)
    jks = {env: {m: SU.jeu_configuration(prep, e, env, m, g["cal"][env], "calibration") for m in CR.MODELES}
           for env in MD.ENVS}
    return CL.classes_tous_environnements(jks, cfg)


def test_n1_corrige_les_types_sans_volume_ne_rendent_plus_une_configuration_delegable():
    """N1, corrigé le 06/11 (délégabilité sur le taux médian, tranché par la recherche à la demande d'Otsoa) : dans le
    monde C, les types à enjeu moyen ou fort, sans erreur faute de volume, ne sont pas jugeables et ne comptent plus.
    Au second passage, leur taux observé (0) les mettait « sous la barre »."""
    cls = classes_monde_c()
    hauts = [(env, m, k) for env, par_mod in cls.items() for m, c in par_mod.items() for k, v in c.items()
             if TY.ENJEU[k] >= TY.MOYEN and v["n"] > 0]
    assert hauts
    for env, m, k in hauts:
        assert not CL.jugeable(cls[env][m][k]) and not CL.estime_sous(cls[env][m][k])
    v = next(cls[e][m][k] for e, m, k in hauts if cls[e][m][k]["x"] == 0)
    assert v["p"] <= v["barre"] < v["hi50"]      # le taux observé disait « sous la barre », le taux médian non


def test_n1_propriete_attendue_agents_nettement_peu_fiables_aucune_configuration_delegable():
    """Corrigé le 06/11 (ce test était en xfail strict au second passage) : agents à 5 × barre partout, aucun type ne
    compte, donc aucune configuration n'est délégable (R4)."""
    cls = classes_monde_c()
    assert not any(CL.estime_sous(v) for par_mod in cls.values() for c in par_mod.values() for v in c.values())


# --------------------------------------------------------------------------
# M4 : le mélange du pilote met la banque, à enjeu faible, hors de l'hypothèse de construction (2.4 ; 1.4, RF3)
# --------------------------------------------------------------------------
def test_m4_s_sur_q_de_la_banque_a_enjeu_faible_avec_le_melange_de_2_4():
    cfg = CR.charger_config()
    mel = MD.MELANGE["banque"]
    faibles = sum(r for k, r in mel.items() if TY.ENJEU[k] == TY.FAIBLE)
    s = faibles / sum(mel.values())                    # 2.4 : la banque n'écrit que des types faibles au pilote
    s_sur_q = s / float(cfg.q[("banque", "faible")])
    assert s == 1.0 and s_sur_q == pytest.approx(364 / 165)
    assert s_sur_q > 1 / 0.95                          # « garantie hors hypothèse » dès que B-tout y délègue
    budget = float(CR.BUDGET["faible"])
    assert 0.95 * budget * s_sur_q == pytest.approx(2.10 * budget, rel=0.01)   # borne de construction ≈ 2,1 × budget
    # pire agent régulier sous B-tout (N de la banque à enjeu faible) : AOQL régulier N^N ÷ (N + 1)^(N + 1), dégâts en
    # plus = 100 × 0,95 × s × AOQL, au plus environ 0,77 fois le budget même avec s = 1
    N = cfg.n_tout[("banque", "faible")]
    aoql = N ** N / (N + 1) ** (N + 1)
    assert 100 * 0.95 * s * aoql == pytest.approx(0.77 * budget, rel=0.01)
