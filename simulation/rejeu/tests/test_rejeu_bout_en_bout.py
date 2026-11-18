"""Rejeu, phase 2 : bout en bout sur le pilote (PLAN_EXPERIENCE.md, 5.16, points 6 et 7), en petit : toutes les tables
sortent, chacune avec l'avertissement en tête, et les mêmes graines redonnent les mêmes sorties. Le lancement complet
(R0 = B = 2 000, K = 10) : `python -m rejeu.bout_en_bout --pilote`.
"""
import hashlib
import json
import os

from rejeu import analyse as AN
from rejeu import bout_en_bout as BE
from rejeu import decision as DE
from rejeu import sorties as SO

import tirage_public as TP


def _sous_partage(cal, conf, envs=("commerce", "WorkBench")):
    return {e: cal[e] for e in envs}, {e: conf[e] for e in envs}


def test_partage_fictif_tire_par_le_script_public():
    e = BE.entrees_et_partage_pilote()[0]
    part = BE.partage_pilote(e)
    reserve = {}
    for p in e.parties:
        reserve.setdefault(p.environnement, set()).add(p.tache)
    assert part == TP.partager({k: sorted(v) for k, v in reserve.items()}, TP.graine(BE.MANIFESTE_TEST,
                                                                                     BE.BALISE_TEST))
    cal, conf = BE.partage_par_env(part)
    for env in reserve:
        assert set(cal[env]).isdisjoint(conf[env]) and set(cal[env]) | set(conf[env]) == reserve[env]


def test_bout_en_bout_toutes_les_tables_et_determinisme(tmp_path):
    e, cal, conf, meta = BE.entrees_et_partage_pilote()
    cal, conf = _sous_partage(cal, conf)
    reg = AN.Reglages(G0=7, R0=6, B=6, K=2, tranche=3)
    empreintes = []
    for i in range(2):
        d = str(tmp_path / f"s{i}")
        dec = BE.executer(e, cal, conf, reg, d, BE.AVERTISSEMENT_PILOTE, meta_entrees=meta, journal=None)
        for n in SO.FICHIERS:
            chemin = os.path.join(d, n + ".csv")
            assert os.path.exists(chemin), n
            with open(chemin, encoding="utf-8") as f:
                assert f.readline().startswith("# AVERTISSEMENT"), n
        with open(os.path.join(d, "meta.json"), encoding="utf-8") as f:
            m = json.load(f)
        assert m["avertissement"] == BE.AVERTISSEMENT_PILOTE and m["entrees"]["partage_fictif"]["balise_test"]
        with open(os.path.join(d, "RESULTATS.md"), encoding="utf-8") as f:
            assert "AVERTISSEMENT" in f.read()
        assert dec["etiquette"] in DE.ORDRE_ETIQUETTES
        # le motif de « preuves insuffisantes » (ou la mention de R2) est publié avec l'étiquette (amendement R4, 07/11)
        assert dec["mention"] == DE.mention(dec["etiquette"], dec["principale"]["point2"],
                                            dec["principale"]["point4"])
        finale = next(l for l in SO.lire_csv(d, "decision") if l["element"] == "étiquette finale")
        assert finale["valeur"] == dec["etiquette"] + (f" ({dec['mention']})" if dec["mention"] else "")
        h = hashlib.sha256()
        for n in SO.FICHIERS:
            with open(os.path.join(d, n + ".csv"), "rb") as f:
                h.update(f.read())
        empreintes.append(h.hexdigest())
    assert empreintes[0] == empreintes[1]          # mêmes graines, mêmes sorties (5.16, point 7)
    budget = SO.lire_csv(str(tmp_path / "s0"), "budget")
    assert {l["analyse"] for l in budget} >= {"principale", "verdicts bruts", "toute la réserve", "échange des rôles",
                                               "ordre par_passage", "ordre reel"}
    assert sum(1 for l in budget if l["eliminatoire"] == "True") == 2 * 3 * 3 + 2 * 12 * 3   # 2 env. : 6 + 24 suites
    res = SO.lire_csv(str(tmp_path / "s0"), "resistance")
    assert {l["mode"] for l in res} >= {"rate10", "retard10", "groupees", "verdicts bruts", "e = 0", "e = 0.02",
                                         "e = 0.1"}
