"""Accord entre la relecture à l'aveugle d'Otsoa et les décisions de Claude (REGLE.md, 5 novembre, point 7).

Entrées :
- tirage_aveugle.json (fiche -> alerte, avis de Claude, enjeu), produit par tirage_aveugle.py ;
- un CSV simple d'Otsoa : fiche,reponse,motif ; reponse = « vraie erreur » ou « fausse alerte ».
Correspondance : vraie erreur = alerte confirmée ; fausse alerte = alerte levée.

Règle : au moins 13 accords sur 15 -> la relecture est gardée. Sinon : « Otsoa relit 15 cas de plus ».
Drapeau spécial : Claude a levé une alerte à enjeu fort qu'Otsoa juge vraie erreur -> « relire toutes les alertes
fortes levées ». Si moins de 15 fiches ont été tirées, le seuil est ramené au prorata (13/15, arrondi au supérieur).

Second tour (décision d'Otsoa du 5 novembre, B2 du contrôle 1) : on cumule les deux tours ; au moins 26 accords
sur 30 (au prorata si moins de cas) -> relecture gardée au second tour. Sinon, le désaccord persiste : pour cette
vague, le verdict est calculé deux fois, avec les décisions retenues et avec les verdicts bruts, et l'on garde
l'étiquette la moins favorable. Dans tous les cas, la décision d'Otsoa l'emporte sur les cas qu'il a relus
(`decisions_retenues`). Aucun motif n'est réécrit après le gel.

Drapeau : Otsoa relit toutes les alertes fortes levées qu'il n'a pas encore jugées (tirage_aveugle.py --fortes) ;
`--fortes` et `--reponses-fortes` ajoutent ses décisions, qui l'emportent. Elles ne comptent pas dans l'accord : ce
n'est pas un tirage à l'aveugle. Cette relecture n'est acceptée qu'après un drapeau.

Usage :
    python banc/relecture/accord.py --tirage tirage_aveugle.json --reponses reponses.csv [--decisions decisions.csv]
    python banc/relecture/accord.py --tirage t1.json --reponses r1.csv --tirage t2.json --reponses r2.csv \
        [--fortes fortes_levees.json --reponses-fortes rf.csv] [--decisions decisions.csv] [--sortie accord.json]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decisions  # noqa: E402
from tirage_aveugle import FORTES, TIRAGE  # noqa: E402

SEUIL = 13
TOTAL = 15
SEUIL_CUMULE = 26
TOTAL_CUMULE = 30
GARDEE = "Relecture gardée"
PLUS = "Otsoa relit 15 cas de plus"
GARDEE_SECOND_TOUR = "Relecture gardée au second tour"
PERSISTANT = ("Désaccord persistant : pour cette vague, étiquette la moins favorable des deux calculs "
              "(décisions retenues, verdicts bruts)")
DRAPEAU = "relire toutes les alertes fortes levées"


class ReponsesInvalides(ValueError):
    pass


def normaliser_reponse(brut: str):
    n = decisions.sans_accent(brut)
    if n in ("vraie erreur", "erreur", "vraie"):
        return decisions.CONFIRMEE
    if n in ("fausse alerte", "fausse", "alerte levee", "fausse alerte."):
        return decisions.LEVEE
    return None


def lire_reponses(chemin) -> dict:
    """{numéro de fiche (int): (décision équivalente, motif)}."""
    with open(chemin, newline="", encoding="utf-8") as fh:
        lecteur = csv.DictReader(fh)
        champs = [c.strip().lower() for c in (lecteur.fieldnames or [])]
        if champs[:2] != ["fiche", "reponse"]:
            raise ReponsesInvalides(f"en-tête attendu : fiche,reponse,motif ; trouvé : {lecteur.fieldnames}")
        lecteur.fieldnames = champs
        rep, erreurs = {}, []
        for n, l in enumerate(lecteur, start=2):
            try:
                num = int((l.get("fiche") or "").strip().lower().removeprefix("fiche").strip())
            except ValueError:
                erreurs.append(f"ligne {n} : numéro de fiche illisible : {l.get('fiche')!r}")
                continue
            dec = normaliser_reponse(l.get("reponse") or "")
            if dec is None:
                erreurs.append(f"ligne {n} (fiche {num}) : réponse inconnue : {l.get('reponse')!r}")
                continue
            if num in rep:
                erreurs.append(f"ligne {n} : fiche {num} en double")
                continue
            rep[num] = (dec, (l.get("motif") or "").strip())
    if erreurs:
        raise ReponsesInvalides("\n".join(erreurs))
    return rep


def comparer(tirage: dict, reponses: dict, registre: dict | None = None) -> dict:
    fiches = tirage["fiches"]
    numeros = {f["numero"] for f in fiches}
    manquantes = sorted(numeros - set(reponses))
    inconnues = sorted(set(reponses) - numeros)
    if manquantes or inconnues:
        raise ReponsesInvalides(f"fiches sans réponse : {manquantes} ; fiches inconnues : {inconnues}")
    total = len(fiches)
    seuil = SEUIL if total == TOTAL else math.ceil(SEUIL * total / TOTAL)
    accords, desaccords, fortes_levees, drapeau = 0, [], [], []
    for f in fiches:
        claude = registre[f["alerte_id"]]["decision"] if registre and f["alerte_id"] in registre else f["decision_claude"]
        otsoa, motif = reponses[f["numero"]]
        if claude == decisions.LEVEE and f.get("enjeu") == "fort":
            fortes_levees.append(f["alerte_id"])
        if claude == otsoa:
            accords += 1
        else:
            desaccords.append({"fiche": f["numero"], "alerte_id": f["alerte_id"], "claude": claude, "otsoa": otsoa,
                               "motif_claude": f.get("motif_claude", ""), "motif_otsoa": motif, "enjeu": f.get("enjeu", "")})
            if claude == decisions.LEVEE and otsoa == decisions.CONFIRMEE and f.get("enjeu") == "fort":
                drapeau.append(f["alerte_id"])
    gardee = accords >= seuil
    return {
        "accords": accords, "total": total, "seuil": seuil,
        "conclusion": GARDEE if gardee else PLUS,
        "drapeau_enjeu_fort": bool(drapeau), "drapeau": DRAPEAU if drapeau else "",
        "alertes_a_relire": drapeau,
        "desaccords": desaccords,
        "note": "" if total == TOTAL else f"seulement {total} fiches tirées : seuil ramené au prorata ({seuil}/{total})",
    }


def _seuil(total: int, seuil_ref: int, total_ref: int) -> int:
    return seuil_ref if total == total_ref else math.ceil(seuil_ref * total / total_ref)


def _fortes(fortes: tuple, deja_jugees: dict, drapeau: bool) -> dict:
    """Décisions d'Otsoa sur les fortes levées relues après le drapeau ({alerte_id: décision})."""
    tirage_f, reponses_f = fortes
    if tirage_f.get("nature") != FORTES:
        raise ReponsesInvalides("--fortes attend fortes_levees.json (tirage_aveugle.py --fortes)")
    if not drapeau:
        raise ReponsesInvalides("relecture des fortes levées sans drapeau : elle n'a lieu qu'après un drapeau")
    numeros = {f["numero"] for f in tirage_f["fiches"]}
    if set(reponses_f) != numeros:
        raise ReponsesInvalides(f"fortes levées : fiches sans réponse {sorted(numeros - set(reponses_f))} ; "
                                f"fiches inconnues {sorted(set(reponses_f) - numeros)}")
    communs = sorted({f["alerte_id"] for f in tirage_f["fiches"]} & set(deja_jugees))
    if communs:
        raise ReponsesInvalides(f"fortes levées déjà jugées dans un tour : {communs[:3]}")
    return {f["alerte_id"]: reponses_f[f["numero"]][0] for f in tirage_f["fiches"]}


def conclure(tours: list, registre: dict | None = None, fortes: tuple | None = None) -> dict:
    """Bilan d'une vague, sur un ou deux tours : [(tirage, réponses), ...] ; `fortes` : (fortes_levees.json, réponses).

    Renvoie aussi `decisions_otsoa` ({alerte_id: décision}), qui l'emportent sur celles de Claude (fortes levées
    relues comprises), et `desaccord_persistant`, qui déclenche le calcul « le moins favorable » dans le rejeu final.
    """
    if not 1 <= len(tours) <= 2:
        raise ReponsesInvalides("une vague compte un ou deux tours de relecture")
    for k, (t, _) in enumerate(tours, 1):
        if t.get("nature", TIRAGE) != TIRAGE:
            raise ReponsesInvalides(f"le fichier du tour {k} n'est pas un tirage à l'aveugle ({t.get('nature')})")
        if t.get("tour", k) != k:
            raise ReponsesInvalides(f"le fichier donné pour le tour {k} est celui du tour {t.get('tour')}")
    ids = [f["alerte_id"] for t, _ in tours for f in t["fiches"]]
    if len(ids) != len(set(ids)):
        raise ReponsesInvalides("une même alerte figure dans les deux tours")
    bilans = [comparer(t, r, registre) for t, r in tours]
    if len(tours) == 1:
        accords, total, seuil, conclusion = (bilans[0][k] for k in ("accords", "total", "seuil", "conclusion"))
        persistant = False
    else:
        if bilans[0]["conclusion"] == GARDEE:
            raise ReponsesInvalides("second tour inutile : le premier a gardé la relecture")
        accords = sum(b["accords"] for b in bilans)
        total = sum(b["total"] for b in bilans)
        seuil = _seuil(total, SEUIL_CUMULE, TOTAL_CUMULE)
        persistant = accords < seuil
        conclusion = PERSISTANT if persistant else GARDEE_SECOND_TOUR
    decisions_otsoa = {f["alerte_id"]: r[f["numero"]][0] for t, r in tours for f in t["fiches"]}
    drapeau = any(b["drapeau_enjeu_fort"] for b in bilans)
    bilan_fortes = None
    if fortes is not None:
        ajout = _fortes(fortes, decisions_otsoa, drapeau)
        decisions_otsoa.update(ajout)
        bilan_fortes = {"relues": len(ajout),
                        "jugees_vraies_erreurs": sum(1 for d in ajout.values() if d == decisions.CONFIRMEE)}
    return {
        "tours": bilans, "accords": accords, "total": total, "seuil": seuil, "conclusion": conclusion,
        "desaccord_persistant": persistant, "decisions_otsoa": decisions_otsoa,
        "drapeau_enjeu_fort": drapeau,
        "alertes_a_relire": sorted({a for b in bilans for a in b["alertes_a_relire"]}),
        "fortes": bilan_fortes,
    }


def decisions_retenues(registre: dict, decisions_otsoa: dict) -> dict:
    """{alerte_id: décision} : celle de Claude, sauf sur les cas relus par Otsoa, où la sienne l'emporte."""
    retenues = {a: v["decision"] for a, v in registre.items()}
    inconnues = sorted(set(decisions_otsoa) - set(retenues))
    if inconnues:
        raise ReponsesInvalides(f"décisions d'Otsoa sur des alertes absentes du registre : {inconnues[:5]}")
    retenues.update(decisions_otsoa)
    return retenues


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tirage", required=True, action="append", help="une fois par tour (deux au plus)")
    p.add_argument("--reponses", required=True, action="append", help="dans le même ordre que --tirage")
    p.add_argument("--decisions", help="decisions.csv à jour (sinon : l'avis de Claude noté au tirage)")
    p.add_argument("--sortie", help="écrit le bilan en JSON (décisions d'Otsoa et désaccord persistant compris)")
    p.add_argument("--fortes", help="fortes_levees.json : relecture des fortes levées après le drapeau")
    p.add_argument("--reponses-fortes", help="CSV d'Otsoa pour --fortes (fiche,reponse,motif)")
    a = p.parse_args(argv)
    try:
        if len(a.tirage) != len(a.reponses):
            raise ReponsesInvalides("autant de --reponses que de --tirage")
        if bool(a.fortes) != bool(a.reponses_fortes):
            raise ReponsesInvalides("--fortes et --reponses-fortes vont ensemble")
        registre = decisions.lire(a.decisions) if a.decisions else None
        tours = [(json.loads(Path(t).read_text(encoding="utf-8")), lire_reponses(r)) for t, r in zip(a.tirage, a.reponses)]
        fortes = ((json.loads(Path(a.fortes).read_text(encoding="utf-8")), lire_reponses(a.reponses_fortes))
                  if a.fortes else None)
        bilan = conclure(tours, registre, fortes)
    except (ReponsesInvalides, decisions.DecisionInvalide, ValueError, FileNotFoundError) as e:
        print(f"erreur: {e}", file=sys.stderr)
        return 2
    for k, r in enumerate(bilan["tours"], start=1):
        entete = f"Tour {k} : " if len(bilan["tours"]) > 1 else ""
        print(f"{entete}Accord : {r['accords']} sur {r['total']} (seuil {r['seuil']})")
        if r["note"]:
            print(r["note"])
        for d in r["desaccords"]:
            print(f"- fiche {d['fiche']} ({d['alerte_id']}) : Claude {d['claude']} / Otsoa {d['otsoa']}")
    if len(bilan["tours"]) > 1:
        print(f"Cumul : {bilan['accords']} sur {bilan['total']} (seuil {bilan['seuil']})")
    print(bilan["conclusion"])
    if bilan["drapeau_enjeu_fort"] and bilan["fortes"]:
        print(f"Fortes levées relues par Otsoa : {bilan['fortes']['relues']}, dont "
              f"{bilan['fortes']['jugees_vraies_erreurs']} jugées vraies erreurs ; ses décisions l'emportent")
    elif bilan["drapeau_enjeu_fort"]:
        print(f"DRAPEAU : {DRAPEAU} ({', '.join(bilan['alertes_a_relire'])}) ; Otsoa les relit, sa décision l'emporte "
              "(tirage_aveugle.py --fortes --exclure <fichiers de la vague>, puis accord.py --fortes)")
    if a.sortie:
        Path(a.sortie).write_text(json.dumps(bilan, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
