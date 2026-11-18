"""O4 (b), décision d'Otsoa du 09/11 : quand la famille du max-T du point 1 (cellules jugées et testables de B-tout)
compte une ou deux cellules, la sortie porte d'office « niveau non mesuré pour cette taille de famille ». Aucune
étiquette ne change."""
from types import SimpleNamespace

import pytest

from rejeu import decision as DE
from rejeu import sorties as SO

MENTION = "niveau non mesuré pour cette taille de famille"


def cel(statut=DE.JUGEE, non_testable=False, verdict=DE.NON_REFUTEE):
    return dict(statut=statut, non_testable=non_testable, verdict=verdict)


@pytest.mark.parametrize("cellules,attendu", [
    ([], ""),                                                        # aucune cellule testable : pas de max-T
    ([cel()], MENTION),
    ([cel(), cel()], MENTION),
    ([cel(), cel(), cel()], ""),
    ([cel(), cel(non_testable=True), cel(non_testable=True)], MENTION),   # les non testables ne comptent pas
    ([cel(), cel(statut=DE.NON_EPROUVEE), cel(statut=DE.SANS_OBJET)], MENTION),
])
def test_mention_selon_la_taille_de_la_famille(cellules, attendu):
    assert DE.mention_famille(cellules) == attendu


def test_point1_porte_la_mention_sans_changer_tenu(monkeypatch):
    monkeypatch.setattr(DE, "cellules", lambda an, regle: [cel(), cel()])
    p1 = DE.point1(SimpleNamespace(resume_r0={}))
    assert p1["mention_famille"] == MENTION and p1["testables"] == 2 and p1["tenu"] is True
    monkeypatch.setattr(DE, "cellules", lambda an, regle: [cel(verdict=DE.ETABLI)])
    p1 = DE.point1(SimpleNamespace(resume_r0={}))
    assert p1["mention_famille"] == MENTION and p1["tenu"] is False                  # R1 inchangé


def test_la_sortie_publie_la_mention():
    base = dict(tenu=True, calcule=True, echecs=[], defauts_retrait=[])
    avec = SO.detail_point1(dict(base, cellules=[cel()], testables=1, mention_famille=MENTION))
    sans = SO.detail_point1(dict(base, cellules=[cel()] * 3, testables=3, mention_famille=""))
    assert MENTION in avec and "1 cellule(s) testable(s)" in avec and MENTION not in sans
