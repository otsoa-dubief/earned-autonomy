"""Audit indépendant du moteur (09/11, sections 5.5 à 5.13) : écarts mineurs sur des mesures descriptives ou
secondaires, corrigés avant le gel. Aucun ne touche le chemin du verdict."""
import numpy as np

from rejeu import config_rejeu as CR
from rejeu import epreuves as EP
from rejeu import moteur as MO
from rejeu import regles as RG
from rejeu import suites as SU
from rejeu import types_regle as TY


def _petite_regle():
    cfg = CR.charger_config()
    r = RG.regle("B-tout", "banque", cfg)
    return RG.variante(r, "B-petit", N=np.where(r.N > 0, 2, 0))


def _periodes(avec_plaf: bool):
    """Cas de l'audit (periodes.py) : deux erreurs au palier 3, séparées ou non par une écriture plafonnée."""
    A = TY.DUR
    seq = [("ok", False)] * 14 + [("ko", False)] + ([("ok", True)] if avec_plaf else []) + [("ko", False)] \
        + [("ok", False)] * 12
    typ = np.full(len(seq), A)
    errp = np.array([s == "ko" for s, _ in seq])
    plaf = np.array([p for _, p in seq])
    s = SU.suite_depuis_tableaux(typ, plaf=plaf, errp=errp)
    res = MO.simuler(s, [_petite_regle()], EP.FournisseurConstant(EP.REUSSIE), jonction=np.array([0]), annonce=False,
                     retard=10, garder_P=True)
    return int(res.max_constatees[0, A]), int(res.n_periodes[0, A])


def test_point1_une_plafonnee_ne_coupe_pas_une_periode_d_autonomie():
    # forcée au palier 1, l'écriture plafonnée n'est pas une sortie de l'autonomie du type
    assert _periodes(True) == _periodes(False) == (2, 1)


# ---- point 2 : la configuration figée vérifie aussi R0, B, K, e, épreuves et codes de graines
import json  # noqa: E402

import pytest  # noqa: E402


@pytest.mark.parametrize("chemin,valeur", [
    (("R0",), 200), (("B",), 200), (("K",), 3),
    (("e", "principal"), 0.1), (("epreuves", "variantes"), 4), (("epreuves", "attente"), 10),
    (("graines", "usages", "ordre"), 9), (("graines", "jeux", "confirmation"), 5),
    (("graines", "couches", "bootstrap"), 7),
])
def test_point2_config_figee_verifie_tous_les_reglages(tmp_path, chemin, valeur):
    brut = json.loads(open(CR.CHEMIN_CONFIG, encoding="utf-8").read())
    d = brut
    for k in chemin[:-1]:
        d = d[k]
    d[chemin[-1]] = valeur
    f = tmp_path / "config.json"
    f.write_text(json.dumps(brut, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(CR.ConfigInvalide):
        CR.charger_config(str(f))


def test_point2_constantes_du_moteur_egales_au_json():
    import config as C
    brut = CR.charger_config().brut
    assert EP.N_VARIANTES == brut["epreuves"]["variantes"] and C.EPREUVE_ATTENTE == brut["epreuves"]["attente"]
    assert (CR.E_PRINCIPAL, list(CR.E_COMPLEMENTS)) == (brut["e"]["principal"], brut["e"]["complements"])


def test_point2_calculer_ecrit_le_statut_decide():
    assert CR.calculer()["statut"].startswith("Décidé")


# ---- point 3 : en jackknife, les variantes ne viennent jamais de la tâche retirée
from types import SimpleNamespace  # noqa: E402

from rejeu import analyse as AN  # noqa: E402


def _jeu_vivier():
    """Six parties d'une écriture du type DUR, même outil : trois de la tâche a (dont la fautive, 0), trois de b."""
    taches = ["a", "a", "a", "b", "b", "b"]
    parties = [SimpleNamespace(partie=SimpleNamespace(tache=t)) for t in taches]
    n = len(taches)
    return SimpleNamespace(n_parties=n, parties=parties, debut=np.arange(n + 1), typ=np.full(n, TY.DUR, np.int8),
                           outil=np.zeros(n, np.int64), rang=np.zeros(n, np.int64), outils=("o",),
                           attrs=dict(reu=np.ones(n, bool), errp=np.zeros(n, bool)))


def test_point3_jackknife_exclut_la_tache_retiree_a_tous_les_niveaux():
    pool = EP.PoolEpreuves(_jeu_vivier())
    lot = SimpleNamespace(couche="jackknife", groupe=np.array([0, 1]), taches=("a", "b"),
                          suite=SimpleNamespace(cles_epreuves=(11, 12)))
    f = AN.FabriqueConfig(pool)(lot, None)
    cas = EP.Cas(0, 0, 0)
    for tentative in range(20):
        v0 = f.issue(0, 0, 0, TY.DUR, cas, tentative).variantes     # colonne 0 : tâche a retirée
        v1 = f.issue(0, 0, 1, TY.DUR, cas, tentative).variantes     # colonne 1 : tâche b retirée
        assert v0 and all(pool.tache[i] == "b" for i in v0)
        assert v1 is None or v1 == () or all(pool.tache[i] == "a" for i in v1)


def test_point3_hors_jackknife_rien_n_est_exclu():
    pool = EP.PoolEpreuves(_jeu_vivier())
    lot = SimpleNamespace(couche="R0", groupe=np.array([0]), taches=("a", "b"),
                          suite=SimpleNamespace(cles_epreuves=(11,)))
    v = AN.FabriqueConfig(pool)(lot, None).issue(0, 0, 0, TY.DUR, EP.Cas(0, 0, 0), 0).variantes
    assert sum(pool.tache[i] == "a" for i in v) == 2      # les deux autres parties de la tâche, puis une de b


# ---- point 4 : garantie après la jonction, types déjà au palier 3 qui y restent (mode silencieux)
from rejeu import classes as CL  # noqa: E402


def _garantie_apres(seq_apres_ko: bool):
    A = TY.DUR
    errp = np.zeros(30, bool)
    if seq_apres_ko:
        errp[20] = True                                   # une erreur après la jonction : le palier 3 est perdu
    s = SU.suite_depuis_tableaux(np.full(30, A), plaf=np.zeros(30, bool), errp=errp)
    r = _petite_regle()
    res = MO.simuler(s, [r], EP.FournisseurConstant(EP.RATEE), jonction=np.array([15]), annonce=False)
    rl = SimpleNamespace(moteur=res, lot=SimpleNamespace(n_groupes=1), regles=[r])
    return float(AN.garantie_groupes(rl, {A: dict(classe=CL.AU_DESSUS)}, apres=True)[(r.nom, A)][0])


def test_point4_type_deja_au_palier_3_a_la_jonction_compte_dans_la_garantie():
    assert _garantie_apres(False) == 1.0


def test_point4_type_qui_perd_le_palier_3_sans_le_retrouver_ne_compte_pas():
    assert _garantie_apres(True) == 0.0


# ---- point 5 : retard10, les preuves en attente de l'ancien modèle ne passent pas la jonction annoncée
def _premier3_apres(ko_avant: bool):
    A = TY.DUR
    errp = np.zeros(40, bool)
    errp[14] = ko_avant                                   # dernière écriture avant la jonction
    s = SU.suite_depuis_tableaux(np.full(40, A), plaf=np.zeros(40, bool), errp=errp)
    res = MO.simuler(s, [_petite_regle()], EP.FournisseurConstant(EP.REUSSIE), jonction=np.array([15]), annonce=True,
                     retard=10)
    return int(res.premier3_apres[0, A]), int(res.prom3_apres[0, A]), int(res.n_retraits3[0, A])


def test_point5_le_tampon_de_retard_est_vide_a_la_jonction_annoncee():
    assert _premier3_apres(True) == _premier3_apres(False)


# ---- point 6 : taux de tâches réussies, bootstrap stratifié et graine du schéma SeedSequence
from rejeu import sorties as SO  # noqa: E402


def _entrees_reussite():
    m = CR.MODELES[0]
    taches = [f"a:{i}" for i in range(4)] + [f"b:{i}" for i in range(4)]     # deux fichiers WorkBench
    parties = [SimpleNamespace(environnement="WorkBench", modele=m, tache=t, statut_ok=True,
                               reussie=t.startswith("a")) for t in taches]
    return SimpleNamespace(parties=parties, retiree=lambda p: False), {"confirmation": {"WorkBench": taches}}


def test_point6_bootstrap_stratifie_par_fichier():
    ent, jeux = _entrees_reussite()
    l = SO.lignes_reussite(ent, jeux, B=200, graine=123)[0]
    assert l["lo_bootstrap"] == l["hi_bootstrap"] == 0.5     # chaque fichier garde ses 4 tâches : taux constant


def test_point6_graine_du_schema_seedsequence():
    assert CR.USAGES["reussite"] == 7 and CR.charger_config().brut["graines"]["usages"]["reussite"] == 7
