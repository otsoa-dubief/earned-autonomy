"""Rejeu, phase 4 : Q14 (délégabilité sur le taux estimé), règle de ρ̂ du contrôle 3 (G1), Q15 (« tout faire valider »
en troisième témoin, testé d'abord), m1 (« garantie hors hypothèse » pour les seules cellules jugées), 5.16 point 9
(règle inerte), et les deux défauts du contrôle 3 dont les tests `xfail(strict=True)` sont recopiés ici sans la marque
(G1, M1 ; `simulation/controle3/tests/test_controle3_defauts.py` n'est pas modifié).
"""
import os
import sys

import numpy as np
import pytest

from rejeu import analyse as AN
from rejeu import classes as CL
from rejeu import config_rejeu as CR
from rejeu import decision as DE
from rejeu import pipeline as PL
from rejeu import preuves as PR
from rejeu import regles as RG
from rejeu import suites as SU
from rejeu import types_regle as TY

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                "controle3", "tests"))
from aide_controle3 import entrees_main, taches_wb  # noqa: E402

H, S, O = CR.MODELES
ENV = "WorkBench"
TACHES = taches_wb(200)
ORDRE_CLASSES = {CL.SOUS: 0, CL.INDETERMINE: 1, CL.AU_DESSUS: 2, CL.SANS_DONNEE: 2}


def classes_wb(erreurs: dict) -> dict:
    """Comme le contrôle 3 : WorkBench sur 200 tâches, Haiku 5 passages, Sonnet et Opus 1 passage."""
    specs = {m: dict(passages=5 if m == H else 1, taches=TACHES, erreurs=erreurs.get(m, set())) for m in CR.MODELES}
    e = entrees_main(ENV, specs)
    prep = PR.preparer(e)
    jk = {m: SU.jeu_configuration(prep, e, ENV, m, TACHES, "calibration") for m in CR.MODELES}
    return CL.classes_environnement(jk, CR.charger_config())


# --------------------------------------------------------------------------
# G1 (copie du test xfail du contrôle 3, sans la marque) et règle de ρ̂
# --------------------------------------------------------------------------
def test_g1_propriete_attendue_monotonie():
    zero = classes_wb({})[H][TY.ECR]
    une = classes_wb({H: {(TACHES[0], 1)}})[H][TY.ECR]
    assert ORDRE_CLASSES[zero["classe"]] <= ORDRE_CLASSES[une["classe"]]


def test_g1_rho_plancher_et_configuration_riche():
    """Depuis N3 (06/11) : la règle de ρ̂ est commune à toutes les configurations ; mêmes propriétés (plancher,
    configuration riche)."""
    zero = classes_wb({})[H][TY.ECR]
    assert zero["rho"] == pytest.approx(0.3) and zero["source_rho"] == CL.SOURCES_G1[2]   # plancher
    une = classes_wb({H: {(TACHES[0], 1)}})[H][TY.ECR]
    assert une["rho"] >= 0.3 and une["source_rho"] in CL.SOURCES_G1[1:]
    # Haiku avec 12 erreurs groupées dans 6 tâches : configuration riche, elle prend le plus grand des deux ρ̂
    err = {(t, p) for t in TACHES[:6] for p in (1, 2)}
    c = classes_wb({H: err})
    assert c[H][TY.ECR]["source_rho"] in (CL.SOURCES_G1[0], CL.SOURCES_G1[1])
    assert c[H][TY.ECR]["rho"] >= c[S][TY.ECR]["rho"]


# --------------------------------------------------------------------------
# M1 (copie du test xfail du contrôle 3, sans la marque) ; règle inerte → R2 (5.16, point 9)
# --------------------------------------------------------------------------
def decision_sans_delegation(palier2: bool = True):
    """Monde M1 du contrôle 3 : Haiku délégable ; Sonnet et Opus à 30 % d'erreurs sur l'écriture réversible, que les
    deux témoins délèguent ; B-tout rejouée avec N = 10 000 : jamais au palier 3. palier2 = False : la règle vraiment
    inerte (ni palier 3 ni palier 2)."""
    rng = np.random.default_rng(4)
    cal, conf = TACHES[:100], TACHES[100:]
    err = {H: {(cal[0], 1)},
           S: {(t, 1) for t in TACHES if rng.random() < 0.3}, O: {(t, 1) for t in TACHES if rng.random() < 0.3}}
    specs = {m: dict(passages=7 if m == H else 1, taches=TACHES, erreurs=err[m]) for m in CR.MODELES}
    e = entrees_main(ENV, specs)
    prep = PR.preparer(e)
    cfg = CR.charger_config()
    r = RG.regle("B-tout", ENV, cfg)
    import dataclasses
    params = r.params if palier2 else dataclasses.replace(r.params, a_palier2=np.zeros(TY.NT, dtype=bool))
    regles = {ENV: [RG.variante(r, "B-tout", N=np.where(TY.MERITE, 10_000, 0), params=params)]}
    reg = AN.Reglages(G0=5, R0=20, B=80, K=2, tranche=40, valeurs_e=(0.05,), noms_regles=("B-tout",),
                      choix=dict(methode="iii", repli=False, G_sur=20, methode_seconde="percentile"))
    an = PL.analyser(e, prep, cfg, reg, {ENV: conf}, {ENV: cal}, scenarios=False, regles_imposees=regles)
    return DE.decider(an, DE.point0(e, prep)), an


def test_n1_jugeables_par_configuration_dans_le_pipeline():
    """N1 (06/11) : « jugeable » se calcule configuration par configuration (au moins un type dont le volume suffirait,
    sans erreur, à le faire compter). Sonnet et Opus, avec dix écritures de calibration et aucune erreur, ne sont ni
    jugeables ni délégables ; Haiku, avec 700 écritures, l'est."""
    cal, conf = TACHES[:100], TACHES[100:]
    peu = TACHES[:10] + TACHES[100:110]
    specs = {H: dict(passages=7, taches=TACHES, erreurs=set()), S: dict(passages=1, taches=peu, erreurs=set()),
             O: dict(passages=1, taches=peu, erreurs=set())}
    e = entrees_main(ENV, specs)
    prep = PR.preparer(e)
    reg = AN.Reglages(G0=5, R0=4, B=4, K=2, tranche=4, valeurs_e=(0.05,), noms_regles=("B-tout",),
                      choix=dict(methode="iii", repli=False, G_sur=20, methode_seconde="percentile"))
    an = PL.analyser(e, prep, CR.charger_config(), reg, {ENV: conf}, {ENV: cal}, scenarios=False)
    assert an.jugeables == {(ENV, H): True, (ENV, S): False, (ENV, O): False}
    assert an.delegables == {(ENV, H): True, (ENV, S): False, (ENV, O): False}


@pytest.mark.xfail(strict=True, reason="contradiction (CHOIX_PHASE4.md) : la règle du monde M1 délègue au palier 2 "
                                      "(score de Wald, décision 7) : Q15 la juge délégante ; seul le palier 3 compte ici")
def test_m1_propriete_attendue_confirmee_exige_une_delegation():
    dec, _an = decision_sans_delegation()
    delegue = any(c["statut"] == DE.JUGEE for c in dec["point1"]["cellules"])
    assert dec["etiquette"] != "confirmée" or delegue


def test_monde_m1_b_tout_delegue_au_palier_2():
    """Ce que fait la règle du monde M1 : jamais le palier 3, mais 98 % des écritures réversibles de Haiku au palier 2
    (agir puis prévenir) : sa charge est bien plus basse que celle de « tout faire valider », qui est battu (Q15)."""
    dec, an = decision_sans_delegation()
    assert all(c["statut"] != DE.JUGEE for c in dec["point1"]["cellules"])
    p2 = {a["modele"]: a["part_p2"] for r in an.resume_r0.values() for a in r["autonomie"] if a["regle"] == "B-tout"}
    assert p2[H] > 0.9
    assert dec["point2"]["temoins"]["tout_valider"]["battu"] and dec["etiquette"] == "confirmée"


def test_regle_inerte_donne_r2_aucune_delegation_etablie():
    """5.16, point 9 : la règle qui ne délègue rien (ni palier 3 ni palier 2), deux témoins en dépassement : R2."""
    dec, an = decision_sans_delegation(palier2=False)
    assert all(c["statut"] != DE.JUGEE for c in dec["point1"]["cellules"])     # B-tout ne délègue rien
    assert (ENV, H) in dec["point4"]["delegables"]                             # Q14 et N1 : taux médian sous la barre
    assert dec["point4"]["jugeable"] and an.jugeables[(ENV, H)]                # garde-fou de R4 : un type jugeable
    assert an.jugeables == {c: any(CL.jugeable(v) for v in an.classes_cal[c].values()) for c in an.delegables}
    p2 = dec["point2"]
    assert list(p2["temoins"]) == ["tout_valider", "liste_fixe", "tri_risque"]  # Q15 : testé d'abord
    tv = p2["temoins"]["tout_valider"]
    assert not tv["battu"] and tv["depassement"]["m"] == 0                    # il ne délègue rien : m vide
    assert tv["diff_moyenne"] == pytest.approx(0.0) and tv["intervalle"][1] >= 0   # différence nulle : rien d'établi
    assert dec["etiquette"] == "R2" and dec["mention"] == DE.R2_AUCUNE
    assert all(p2["temoins"][t]["battu_partout"] for t in ("liste_fixe", "tri_risque"))   # sans que cela suffise


# --------------------------------------------------------------------------
# Q14 : délégabilité et oracle sur le taux estimé ; le classement prouvé reste publié
# --------------------------------------------------------------------------
def test_q14_delegable_sur_le_taux_estime():
    c = classes_wb({H: {(TACHES[0], 1)}})
    ecr = c[H][TY.ECR]
    assert ecr["estime_sous"] and ecr["p"] <= ecr["barre"]
    pal = AN.palier_par_type(c[H])
    assert pal[TY.ECR] == 3                                                   # l'oracle délègue le type estimé sous
    non = {TY.ECR: dict(n=10, p=0.5, barre=0.01, classe=CL.AU_DESSUS)}
    assert AN.palier_par_type(non)[TY.ECR] == 2 and not CL.estime_sous(non[TY.ECR])
    assert not CL.estime_sous(CL.classer(0, 0, 0.1))                          # sans donnée : pas délégable


# --------------------------------------------------------------------------
# m1 : « garantie hors hypothèse » seulement pour les cellules jugées
# --------------------------------------------------------------------------
def test_m1_garantie_hors_hypothese_seulement_si_jugee():
    _dec, an = decision_sans_delegation()
    cel = DE.cellules(an, "B-tout")
    assert all(not c.get("garantie_hors_hypothese") for c in cel if c["statut"] != DE.JUGEE)
    assert any(c.get("s_sur_q") is not None for c in cel)


# --------------------------------------------------------------------------
# Les deux vagues du lanceur, réunies en une seule entrée (point 6 de la phase 4)
# --------------------------------------------------------------------------
import csv as _csv  # noqa: E402
import json as _json  # noqa: E402
import shutil as _shutil  # noqa: E402

from rejeu import bout_en_bout as BE  # noqa: E402
from rejeu import entrees as EN  # noqa: E402


def _vague_lanceur(racine, num: int, choisies: list, pilote, relances=(), exclues=()):
    """Un dossier de vague au format du lanceur (banc/CHOIX_LANCEUR.md, choix 14, 15, 18 et 19), fait de parties du
    pilote : `parties/` (tentatives gardées seulement), `cout.json` (une ligne par tentative, champs du lanceur),
    `actions_typees.csv`, `reussite.csv`, `relecture/` (décisions et alertes de ces parties)."""
    d = racine / f"vague{num}" / f"2026-11-0{5 + num}_08-00-00-blanc"
    (d / "parties").mkdir(parents=True)
    (d / "relecture").mkdir()
    lignes, gardees, ids = [], [], set()
    with open(os.path.join(BE.DOSSIER_PILOTE, "cout.json"), encoding="utf-8") as f:
        meta = {p["id"]: p for p in _json.load(f)["parties"]}
    for rang, p in enumerate(choisies):
        pid = p.dossier.split("-", 1)[1]
        base = dict(meta[pid], partie=pid, passage=1, rang=rang, vague=num, finale=True, exclue=False,
                    motif_exclusion=None, terminaison=p.terminaison)
        if pid in exclues:
            lignes.append(dict(base, ok=False, statut="arrêtée sans trace exploitable", exclue=True,
                               motif_exclusion="arrêtée sans trace exploitable", tentative=1))
            continue
        tid, tent = (f"{pid}-t2", 2) if pid in relances else (pid, 1)
        nom = f"{p.dossier.split('-', 1)[0]}-{tid}"
        _shutil.copytree(os.path.join(BE.DOSSIER_PILOTE, "parties", p.dossier), d / "parties" / nom)
        lignes.append(dict(base, id=tid, ok=True, tentative=tent,
                           statut="arrêtée" if p.terminaison == "max_steps" else "terminée"))
        gardees.append((p, nom))
        ids.add(p.id)
    with open(d / "cout.json", "w", encoding="utf-8") as f:
        _json.dump(dict(etape=f"vague{num}", mode="blanc", parties=lignes), f, ensure_ascii=False)
    for src, dst, cle in (("actions_typees.csv", "actions_typees.csv", "partie"),):
        with open(os.path.join(BE.DOSSIER_PILOTE, src), newline="", encoding="utf-8") as fi, \
                open(d / dst, "w", newline="", encoding="utf-8") as fo:
            _csv.field_size_limit(2 ** 31 - 1)
            r = _csv.DictReader(fi)
            w = _csv.DictWriter(fo, fieldnames=r.fieldnames)
            w.writeheader()
            w.writerows(l for l in r if l[cle] in ids)
    with open(os.path.join(BE.DOSSIER_PILOTE, "reussite.csv"), newline="", encoding="utf-8") as fi, \
            open(d / "reussite.csv", "w", newline="", encoding="utf-8") as fo:
        r = _csv.DictReader(fi)
        w = _csv.DictWriter(fo, fieldnames=r.fieldnames)
        w.writeheader()
        par_nom = {p.dossier: nom for p, nom in gardees}
        w.writerows(dict(l, partie=par_nom[l["partie"]]) for l in r if l["partie"] in par_nom)
    rel = os.path.join(BE.DOSSIER_PILOTE, "relecture")
    with open(os.path.join(rel, "alertes.json"), encoding="utf-8") as f:
        alertes = [a for a in _json.load(f) if a["partie"] in ids]
    with open(d / "relecture" / "alertes.json", "w", encoding="utf-8") as f:
        _json.dump(alertes, f, ensure_ascii=False)
    noms = {a["id"] for a in alertes}
    with open(os.path.join(rel, "decisions.csv"), newline="", encoding="utf-8") as fi, \
            open(d / "relecture" / "decisions.csv", "w", newline="", encoding="utf-8") as fo:
        r = _csv.DictReader(fi)
        w = _csv.DictWriter(fo, fieldnames=r.fieldnames)
        w.writeheader()
        w.writerows(l for l in r if l["alerte_id"] in noms)
    return d


def _deux_vagues(tmp_path):
    pilote = EN.charger_entrees(BE.DOSSIER_PILOTE)
    ps = [p for p in pilote.parties if p.environnement in ("aviation", "commerce")]
    num = lambda p: int(p.dossier.rsplit("-", 1)[1])  # noqa: E731
    v1 = _vague_lanceur(tmp_path, 1, [p for p in ps if num(p) <= 5], pilote, exclues=("commerce-opus-3",))
    v2 = _vague_lanceur(tmp_path, 2, [p for p in ps if num(p) > 5], pilote, relances=("aviation-haiku-7",))
    vagues = [EN.VagueRelecture(str(i), str(d / "relecture" / "decisions.csv"), str(d / "relecture" / "alertes.json"),
                                None) for i, d in ((1, v1), (2, v2))]
    return pilote, ps, (v1, v2), vagues


def test_deux_vagues_reunies(tmp_path):
    pilote, ps, (v1, v2), vagues = _deux_vagues(tmp_path)
    e = EN.charger_entrees_vagues([str(v1), str(v2)], vagues)
    assert len(e.parties) == len(ps) - 1                                     # la partie exclue n'est pas lue
    assert {p.vague for p in e.parties} == {"1", "2"} and {p.passage for p in e.parties} == {1}
    rel = [p for p in e.parties if p.dossier == "tau2-aviation-haiku-7-t2"]
    assert len(rel) == 1 and rel[0].vague == "2" and rel[0].tentative == 2 and rel[0].reussie is not None
    assert all(p.statut_lanceur in ("terminée", "arrêtée") for p in e.parties)
    # mêmes actions et mêmes alertes que le pilote, sauf celles de la partie exclue
    exclue = next(p for p in ps if p.dossier == "tau2-commerce-opus-3")
    attendu = {k: v for k, v in pilote.jointure.alertes.items() if k[0] != exclue.id and
               any(p.id == k[0] for p in ps)}
    assert e.jointure.alertes == attendu and not e.jointure.sans_decision
    b = EN.bilan_lanceur([str(v1), str(v2)])
    assert b["exclues"] == {"arrêtée sans trace exploitable": 1} and b["relances"] == 1
    assert b["gardees_par_vague"] == {"1": 29, "2": 30}
    # une partie gardée dans les deux vagues est refusée
    with pytest.raises(EN.EntreeInvalide):
        EN.charger_entrees_vagues([str(v1), str(v1)], vagues[:1])


def test_rejeu_final_sur_deux_vagues(tmp_path):
    pilote, ps, (v1, v2), vagues = _deux_vagues(tmp_path)
    part = tmp_path / "partage.json"
    reserve = {}
    for p in ps:
        reserve.setdefault(p.environnement, set()).add(p.tache)
    import tirage_public as TP
    part.write_text(_json.dumps(TP.partager({k: sorted(v) for k, v in reserve.items()},
                                            TP.graine(BE.MANIFESTE_TEST, BE.BALISE_TEST))), encoding="utf-8")
    dec = BE.executer_experience([str(v1), str(v2)], str(part), vagues, str(tmp_path / "sortie"), essai=True,
                                 R0=4, B=4, K=2, tranche=4)
    assert set(dec["principale"]["point0"]["vagues"]) == {"1", "2"}
    with open(tmp_path / "sortie" / "meta.json", encoding="utf-8") as f:
        m = _json.load(f)
    assert m["entrees"]["lanceur"]["relances"] == 1 and len(m["entrees"]["dossiers"]) == 2
    assert "facteur_relance" not in m   # la relance ne s'applique plus (Q13 ; revue « ultra », 06/11)


# --------------------------------------------------------------------------
# reussite.csv calculé au rejeu final s'il manque (CHOIX_PHASE4.md, point 3)
# --------------------------------------------------------------------------
class _ReussiteFactice:
    """Remplace banc/reussite.py : écrit un reussite.csv (toutes réussies) et affiche des taux, comme le vrai."""
    appels: list = []

    @classmethod
    def main(cls, argv):
        d = argv[argv.index("--dossier") + 1]
        cls.appels.append(d)
        noms = sorted(os.listdir(os.path.join(d, "parties")))
        with open(os.path.join(d, "reussite.csv"), "w", newline="", encoding="utf-8") as f:
            w = _csv.writer(f)
            w.writerow(["partie", "environnement", "modele", "tache", "reussie", "source"])
            w.writerows([n, "", "", "", "oui", "factice"] for n in noms)
        print("Taux de tâches réussies : 100 %")


def test_reussite_calculee_si_elle_manque_sans_rien_afficher(tmp_path, monkeypatch, capsys):
    pilote, ps, (v1, v2), vagues = _deux_vagues(tmp_path)
    os.remove(v2 / "reussite.csv")
    _ReussiteFactice.appels = []
    monkeypatch.setattr(BE, "_module_reussite", lambda: _ReussiteFactice)
    assert BE.preparer_reussite([str(v1), str(v2)]) == [str(v2)]
    assert _ReussiteFactice.appels == [str(v2)] and (v2 / "reussite.csv").exists()
    assert "Taux" not in capsys.readouterr().out          # rien d'affiché pendant le rejeu
    e = EN.charger_entrees_vagues([str(v1), str(v2)], vagues)
    assert all(p.reussie is True for p in e.parties if p.vague == "2")
    assert BE.preparer_reussite([str(v1), str(v2)]) == []  # déjà là : pas recalculé


def test_rejeu_final_calcule_la_reussite_avant_de_lire_les_entrees(tmp_path, monkeypatch):
    pilote, ps, (v1, v2), vagues = _deux_vagues(tmp_path)
    part = tmp_path / "partage.json"
    part.write_text("{}", encoding="utf-8")
    ordre = []
    monkeypatch.setattr(BE, "partage_par_env", lambda p: ({}, {}))
    monkeypatch.setattr(BE, "preparer_reussite", lambda ds: ordre.append(("reussite", list(ds))))

    def lecture(*a, **k):
        ordre.append(("entrees",))
        raise RuntimeError("arrêt du test")
    monkeypatch.setattr(BE.EN, "charger_entrees_vagues", lecture)
    with pytest.raises(RuntimeError, match="arrêt du test"):
        BE.executer_experience([str(v1), str(v2)], str(part), vagues, str(tmp_path / "sortie"), essai=True)
    assert ordre == [("reussite", [str(v1), str(v2)]), ("entrees",)]
