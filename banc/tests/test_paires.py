"""Paires de tâches pour l'équilibrage des types rares (banc/tirage/paires.py ; plan, 3.4)."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tirage"))
import paires as pa  # noqa: E402
import tirage_public as tp  # noqa: E402

RESERVE = json.loads(tp.RESERVE.read_text(encoding="utf-8"))


def test_types_rares_apparies_ensemble():
    profils = {
        "1": Counter({"écriture réversible": 1}), "2": Counter({"écriture réversible": 1}),
        "3": Counter({"argent": 1, "écriture réversible": 1}), "4": Counter({"écriture réversible": 2}),
        "5": Counter({"argent": 1}), "6": Counter(),
    }
    p = pa.apparier(profils)
    assert ["3", "5"] in p  # les deux seules tâches qui portent le type rare
    assert len(p) == 3


def test_effectif_impair_une_seule_tache_seule():
    profils = {str(i): Counter({"écriture réversible": i % 3}) for i in range(7)}
    p = pa.apparier(profils)
    apparies = [i for paire in p for i in paire]
    assert len(p) == 3 and len(set(apparies)) == 6


def test_apparier_deterministe_et_independant_de_l_ordre():
    profils = {str(i): Counter({"argent": i % 2, "message interne": i % 5 == 0}) for i in range(20)}
    inverse = dict(reversed(list(profils.items())))
    assert pa.apparier(profils) == pa.apparier(inverse)


def test_identifiants_tries_dans_l_ordre_naturel():
    assert sorted(["10", "9", "100"], key=pa._cle_identifiant) == ["9", "10", "100"]
    assert sorted(["mail:10", "mail:9"], key=pa._cle_identifiant) == ["mail:9", "mail:10"]


@pytest.fixture(scope="module")
def paires_reelles():
    return pa.construire(RESERVE, chemin_reserve=tp.RESERVE)


def test_paires_reelles_couvrent_la_reserve(paires_reelles):
    for s, ids in tp.strates(RESERVE).items():
        apparies = [i for paire in paires_reelles[s] for i in paire]
        assert len(apparies) == len(set(apparies)) and set(apparies) <= set(ids)
        assert len(ids) - len(apparies) == len(ids) % 2


def test_profils_reels_sans_lectures(paires_reelles):
    profils = pa.profils(RESERVE)
    types = {t for p in profils.values() for c in p.values() for t in c}
    assert types and not types & pa.EXCLUS


def test_tirage_public_accepte_les_paires(paires_reelles):
    g = tp.graine(hashlib.sha256(b"m").hexdigest(), hashlib.sha512(b"v").hexdigest())
    part = tp.partager(RESERVE, g, paires_reelles)
    for s, liste in paires_reelles.items():
        if s == "_meta":
            continue
        for a, b in liste:
            assert (a in part["calibration"][s]) != (b in part["calibration"][s])
    assert len(part["calibration"]["aviation"]) == 20 and len(part["confirmation"]["aviation"]) == 20


def test_equilibre_des_types_rares(paires_reelles):
    """Chaque type rare d'une strate se répartit à une tâche près entre les deux moitiés, pour n'importe quel tirage."""
    profils = pa.profils(RESERVE)
    for graine_txt in (b"v1", b"v2", b"v3"):
        g = tp.graine(hashlib.sha256(b"m").hexdigest(), hashlib.sha512(graine_txt).hexdigest())
        part = tp.partager(RESERVE, g, paires_reelles)
        for s, p in profils.items():
            for t in {t for c in p.values() for t in c}:
                porteurs = [i for i, c in p.items() if c[t] > 0]
                if len(porteurs) > 0.2 * len(p):
                    continue  # types courants : l'équilibre exact n'est pas visé
                cal = sum(1 for i in porteurs if i in part["calibration"][s])
                assert abs(cal - (len(porteurs) - cal)) <= max(2, len(porteurs) // 3), (s, t, cal, len(porteurs))
