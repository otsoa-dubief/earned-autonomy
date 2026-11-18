"""Cellule non testable (plan, 5.14, point 2, décidé par Otsoa le 07/11) : la répétition 24 du monde V, où l'ancienne
règle donnait un faux R1 tiré d'une seule tâche (rapport du contrôle 3, 9.3, point 5, et 10.7). Réglages du contrôle 3."""
import numpy as np
import pytest

from controle3 import harnais as HA
from controle3 import lancer as LA
from controle3 import mondes as MD
from rejeu import analyse as AN
from rejeu import config_rejeu as CR
from rejeu import decision as DE
from rejeu import maxt as MX
from rejeu import pipeline as PL
from rejeu import preuves as PR


@pytest.fixture(scope="module")
def v24():
    m, p, cfg = MD.MONDES_PAR_NOM["V"], LA.parametres(), HA.config()
    g_gen, g_moteur = HA.graine_repetition(p, m, 24).spawn(2)
    g = MD.generer(m, np.random.default_rng(g_gen), cfg)
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    G0 = int(g_moteur.generate_state(1, np.uint64)[0] >> np.uint64(1))
    reg = AN.Reglages(G0=G0, R0=p.R0, B=p.B, K=p.K, tranche=p.tranche, valeurs_e=(CR.E_PRINCIPAL,),
                      noms_regles=("B-tout",), choix=HA.choix_methode())
    an = PL.analyser(e, prep, cfg, reg, g["conf"], g["cal"], processus=1, regles_imposees=HA.regles_monde(m, cfg))
    return an, DE.decider(an, DE.point0(e, prep))


def test_plus_de_faux_r1_tire_d_une_seule_tache(v24):
    _an, dec = v24
    assert dec["point1"]["tenu"] and not dec["point1"]["echecs"]
    assert dec["etiquette"] == DE.PREUVES_INSUFFISANTES and dec["mention"] == DE.MOTIF_AUCUN_JUGEABLE


def test_cellules_non_testables_publiees_avec_leur_motif(v24):
    _an, dec = v24
    jug = [c for c in dec["point1"]["cellules"] if c["statut"] == DE.JUGEE]
    assert len(jug) == 11 and all(c["verdict"] == DE.NON_REFUTEE for c in jug)
    assert all(c["porteuses"] == 1 and c["non_testable"] == MX.motif_porteuses() for c in jug)
    assert all(np.isnan(c["borne_maxt"]) for c in jug)


def test_temoins_portent_le_nombre_de_taches_et_le_motif(v24):
    an, _dec = v24
    vus = 0
    for t in ("liste_fixe", "tri_risque"):
        for l in DE.depassement_temoin(an, t)["cellules"]:
            vus += 1
            assert l["porteuses"] >= 1 and "non_testable" in l
            if l["porteuses"] < MX.PORTEUSES_MIN:
                assert not l["etabli"] and l["non_testable"] == MX.motif_porteuses()
    assert vus


def test_resume_compte_les_cellules_non_testables():
    a = HA.repetition("V", 24, LA.parametres())
    assert a["etiquette"] == DE.PREUVES_INSUFFISANTES and a["p1"]["tenu"] and not a["p1"]["etablies"]
    assert a["p1"]["non_testables"] == 11
    v = a["p1"]["max_borne_sur_budget"]          # aucune borne définie : None (`harnais._f`), jamais NaN
    assert v is None or np.isfinite(v)


# --------------------------------------------------------------------------
# Relecture C13 du code du verdict : M2, M3, M4, M5 (sur la même répétition, et sur des cas construits)
# --------------------------------------------------------------------------
def test_point1_non_calcule_sans_bootstrap_complet(v24):
    """M3 : si une cellule jugée n'a pas ses B répétitions, le point 1 n'est pas « tenu » mais non calculé, et
    l'étiquette refuse de se calculer."""
    import copy
    import dataclasses
    an, dec = v24
    an2 = copy.copy(an)
    an2.reglages = dataclasses.replace(an.reglages, B=an.reglages.B + 1)
    p1 = DE.point1(an2)
    assert p1["tenu"] is None and not p1["calcule"]
    with pytest.raises(ValueError, match="non calculé"):
        DE.decider(an2, dec["point0"])


def test_resume_r0_incomplet_refuse(v24):
    """M5 : une part du palier 3 absente pour une cellule qui a des écritures est une erreur, pas une cellule jugée."""
    import copy
    an, _dec = v24
    an2 = copy.copy(an)
    an2.resume_r0 = copy.deepcopy(an.resume_r0)
    jug = next(c for c in DE.cellules(an, "B-tout") if c["statut"] == DE.JUGEE)
    del an2.resume_r0[jug["famille"]]["p3"][("B-tout", jug["niveau"])]
    with pytest.raises(ValueError, match="palier 3"):
        DE.cellules(an2, "B-tout")


def test_fragile_du_point_2_publie(v24):
    """M2 : une divergence entre la méthode retenue et la seconde méthode est publiée dans decision.csv."""
    import copy
    from rejeu import sorties as SO
    _an, dec = v24
    d = copy.deepcopy(dec)
    for v in d["point2"]["temoins"].values():
        v["methodes_divergent"] = True
    lignes = SO.lignes_decision(dict(principale=d, etiquette=d["etiquette"], mention=d["mention"], fragiles=[],
                                     desaccords={}, etiquettes_secondaires={}, motif_etiquette="", alertes=[]))
    texte = " ".join(str(l) for l in lignes)
    assert "méthodes divergentes" in texte and "seconde méthode" in texte and "trois témoins" in texte


def _dec(et, mention, battus=(True, True, True), p1_tenu=True, p4_tenu=True, motif=""):
    return dict(etiquette=et, mention=mention, point1=dict(tenu=p1_tenu, echecs=[]),
                point2=dict(temoins={t: dict(battu=b) for t, b in zip(DE.TEMOINS_POINT2, battus)}),
                point4=dict(tenu=p4_tenu, motif=motif))


def test_desaccord_persistant_etiquettes_differentes_et_egales():
    """M4 : deux étiquettes différentes, la moins favorable et sa mention ; deux étiquettes égales, la mention de
    l'analyse principale, celle des verdicts bruts publiée à côté."""
    c = DE.combiner_b2(_dec("confirmée", ""), _dec("R2", DE.R2_AUCUNE, battus=(False, True, True)))
    assert (c["etiquette"], c["mention"]) == ("R2", DE.R2_AUCUNE)
    assert c["points_bruts_vague"]["point2"]["tout_valider"] is False
    c = DE.combiner_b2(_dec("R2", DE.R2_INFERIEURE), _dec("R2", DE.R2_AUCUNE))
    assert (c["etiquette"], c["mention"], c["mention_bruts_vague"]) == ("R2", DE.R2_INFERIEURE, DE.R2_AUCUNE)
    c = DE.combiner_b2(_dec("R1", ""), _dec("confirmée", ""))
    assert c["etiquette"] == "R1" and c["etiquette_bruts_vague"] == "confirmée"

