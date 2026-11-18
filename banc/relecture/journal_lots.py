"""Lots de la relecture des alertes par Claude (plan, 4.4 ; relecture C13, P11).

Chaque lot d'alertes n'est relu qu'une fois. Son ouverture note sa composition et l'empreinte de l'invite, sa
fermeture l'empreinte de la sortie, dans le journal de la vague (`journal.py`, inscrit au manifeste du gel des
verdicts). Une relance n'est permise que pour une sortie mal formée : elle est notée, avec sa raison. Une alerte
n'appartient qu'à un lot. Avant le gel des verdicts, `verifier` contrôle que chaque alerte de la vague est dans un lot
fermé.

Usage :
    journal_lots.py ouvrir --relecture <dossier> --lot N --alertes A,B,… --invite <fichier>
    journal_lots.py fermer --relecture <dossier> --lot N --sortie <fichier> [--relance "<raison>"]
    journal_lots.py verifier --relecture <dossier> --decisions decisions.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import journal  # noqa: E402


class LotInvalide(ValueError):
    pass


def _lots(relecture) -> list:
    return [l for l in journal.lire(relecture) if l.get("type") == "lot"]


def ouvrir(relecture, lot: int, alertes: list, invite) -> None:
    deja = _lots(relecture)
    if any(l["lot"] == lot and l["etape"] == "ouverture" for l in deja):
        raise LotInvalide(f"lot {lot} déjà ouvert : un lot n'est relu qu'une fois")
    for l in deja:
        if l["etape"] == "ouverture":
            communes = set(alertes) & set(l["alertes"])
            if communes:
                raise LotInvalide(f"alertes {sorted(communes)} déjà dans le lot {l['lot']}")
    journal.noter(relecture, dict(type="lot", etape="ouverture", lot=lot, alertes=list(alertes),
                                  invite_sha256=journal.sha256(invite)))


def fermer(relecture, lot: int, sortie, relance: str | None = None) -> None:
    deja = [l for l in _lots(relecture) if l["lot"] == lot]
    if not any(l["etape"] == "ouverture" for l in deja):
        raise LotInvalide(f"lot {lot} jamais ouvert")
    ferme = any(l["etape"] in ("fermeture", "relance") for l in deja)
    if ferme and not relance:
        raise LotInvalide(f"lot {lot} déjà fermé : une relance n'est permise que pour une sortie mal formée (--relance)")
    ligne = dict(type="lot", etape="relance" if ferme else "fermeture", lot=lot, sortie_sha256=journal.sha256(sortie))
    if ferme:
        ligne["raison"] = relance
    journal.noter(relecture, ligne)


def verifier(relecture, alertes_attendues) -> list:
    lots = _lots(relecture)
    ouverts = {l["lot"]: l["alertes"] for l in lots if l["etape"] == "ouverture"}
    fermes = {l["lot"] for l in lots if l["etape"] in ("fermeture", "relance")}
    ecarts = [f"lot {n} non fermé" for n in sorted(set(ouverts) - fermes)]
    dans = {a for ids in ouverts.values() for a in ids}
    ecarts += [f"alerte {a} dans aucun lot" for a in sorted(set(alertes_attendues) - dans)]
    return ecarts


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sous = p.add_subparsers(dest="commande", required=True)
    o = sous.add_parser("ouvrir")
    o.add_argument("--relecture", required=True)
    o.add_argument("--lot", required=True, type=int)
    o.add_argument("--alertes", required=True)
    o.add_argument("--invite", required=True)
    f = sous.add_parser("fermer")
    f.add_argument("--relecture", required=True)
    f.add_argument("--lot", required=True, type=int)
    f.add_argument("--sortie", required=True)
    f.add_argument("--relance")
    v = sous.add_parser("verifier")
    v.add_argument("--relecture", required=True)
    v.add_argument("--decisions", required=True)
    a = p.parse_args(argv)
    try:
        if a.commande == "ouvrir":
            ouvrir(a.relecture, a.lot, [x for x in a.alertes.split(",") if x], a.invite)
        elif a.commande == "fermer":
            fermer(a.relecture, a.lot, a.sortie, a.relance)
        else:
            import decisions
            ecarts = verifier(a.relecture, decisions.lire(a.decisions))
            for e in ecarts:
                print(f"ÉCART : {e}")
            return 1 if ecarts else 0
    except LotInvalide as e:
        print(f"REFUS : {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
