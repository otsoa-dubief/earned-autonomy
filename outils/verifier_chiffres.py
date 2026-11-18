"""Automatic check of the paper's figures (PLAN_SUITE T33). Outside the frozen perimeter; reads only.

    python3 outils/verifier_chiffres.py [texte.tex ...] > article/verif_chiffres.txt

For each row of article/sources_chiffres.csv:
  1. when a recomputation is defined below, the value is recomputed from its source file and compared;
  2. every number of the value (French decimal commas and thin-space thousands normalised) is searched in the
     LaTeX text of the paper, in the forms the paper uses (8.6 % for 0.08643, 14,266 for 14266...).
Exit code 1 if any gap is found. With file arguments, those files are searched instead of article/latex/*.tex
(used to check that a deliberately altered copy is caught).
"""
import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RF = ROOT / "experience" / "rejeu_final"
EX = ROOT / "experience" / "exploratoire"


def lire(p: Path):
    return list(csv.DictReader(io.StringIO("".join(l for l in open(p, encoding="utf-8") if not l.startswith("#")))))


def ecart(**k):
    return [r for r in lire(RF / "ecart.csv") if r["version"] == "principal" and r["n"] not in ("", "0")
            and all(r[a] == b for a, b in k.items())]


def btout(**k):
    return [r for r in lire(RF / "budget.csv") if r["regle"] == "B-tout" and r["analyse"] == "principale"
            and r["e"] == "0.05" and all(r[a] == b for a, b in k.items())]


def decision(elem):
    return next(r for r in lire(RF / "decision.csv") if r[list(r)[0]].startswith(elem))


R4 = lambda: ecart(environnement="WorkBench", modele="claude-haiku-5-5", type="ECR")[0]
RECALC = {
    "etiquette": lambda: decision("étiquette finale")[list(decision("étiquette finale"))[1]],
    "R4_ecritures": lambda: int(R4()["n"]),
    "R4_erreurs": lambda: int(R4()["x"]),
    "R4_taux": lambda: round(float(R4()["taux"]), 5),
    "R4_barre": lambda: round(float(R4()["barre"]), 6),
    "R4_borne_basse_rho1": lambda: round(float(R4()["borne_basse"]), 5),
    "R4_neff_rho1": lambda: round(float(R4()["n_eff_preuve"]), 2),
    "R4_rho_chapeau": lambda: float(R4()["rho"]),
    "R4_taches_porteuses": lambda: int(R4()["taches_porteuses"]),
    "types_observes": lambda: len(ecart()),
    "types_etablis": lambda: sum(r["classe"] == "au-dessus" for r in ecart()),
    "types_zero_erreur": lambda: sum(r["x"] == "0" for r in ecart()),
    "types_indetermines": lambda: sum(r["classe"] == "indéterminé" for r in ecart()),
    "types_avec_erreurs_non_etablis": lambda: sum(r["classe"] == "indéterminé" and r["x"] != "0" for r in ecart()),
    "etablis_sous_rho_chapeau": lambda: sum(r["classe_sous_hypothese"] == "au-dessus" for r in ecart()),
    "erreurs_confirmees_calibration": lambda: sum(int(r["x"]) for r in ecart()),
    "cellules_jugees": lambda: len(btout(statut="non réfutée")),
    "cellules_non_eprouvees": lambda: len(btout(statut="tenue, non mise à l'épreuve")),
    "cellules_sans_objet": lambda: len(btout(statut="sans objet")),
    "exclusions_total": lambda: len(lire(EX / "A_parties_exclues.csv")),
    "exclusions_message_vide": lambda: len(lire(EX / "A_parties_exclues.csv")),
    "exclusions_banque_haiku": lambda: sum(r["environnement"] == "banque" and "haiku" in r["modele"]
                                           for r in lire(EX / "A_parties_exclues.csv")),
    "parties_analysees": lambda: sum(int(r["parties"]) for r in lire(RF / "reussite_taches.csv")),
    "impulsion_nist": lambda: int(json.load(open(ROOT / "experience/tirage/impulsion.json"))["url"].rsplit("/", 1)[1]),
    "derive_periodes_autonomie": lambda: int(max(float(r["periodes_moy"] or 0) for r in lire(RF / "derive.csv")
                                                 if r["analyse"] == "principale" and r["regle"] == "B-tout")),
    "retrait_periodes": lambda: int(max(float(r["max_constatees"] or 0) for r in lire(RF / "derive.csv")
                                        if r["regle"] == "B-tout")),
    "mentions_fragile": lambda: sum(1 for r in lire(RF / "decision.csv") if r[list(r)[0]] == "mention « fragile »"),
}

FORMS = {  # value as written in the paper, when it differs from the registry value
    "R4_taux": ["8.6"], "R4_barre": ["0.76"], "R4_borne_basse_rho1": ["4.1"], "R4_neff_rho1": [],
    "R4_rho_chapeau": ["0.819"], "couverture_instrument": ["98.7"], "R4_neff_fois_barre": ["0.740"],
    "R4_taches_porteuses": ["134"], "c_etoile_btout": ["7.0"], "etiquette": ["R4"], "erreurs_confirmees_calibration": ["1,067"],
    "retrait_periodes": [], "derive_periodes_autonomie": [], "types_observes": ["40"],
}


def nombres(v: str):
    v = re.sub(r"(\d) (\d{3})", r"\1\2", v)
    v = re.sub(r"(\d),(\d)", r"\1.\2", v)
    return re.findall(r"\d+(?:\.\d+)?", v)


def formes(n: str):
    out = {n}
    if re.fullmatch(r"\d{4,}", n):
        out.add(f"{int(n):,}")
    if re.fullmatch(r"\d+\.\d*0", n):
        out.add(n.rstrip("0").rstrip("."))
    return out


def main(files):
    tex = " ".join(Path(f).read_text(encoding="utf-8") for f in files)
    tex = tex.replace("{,}", ",").replace("\\%", "%")
    rows = list(csv.DictReader(open(ROOT / "article/sources_chiffres.csv", encoding="utf-8")))
    gaps, lines = 0, []
    for r in rows:
        ident, val = r["identifiant"], r["valeur"]
        msg = []
        if ident in RECALC:
            try:
                got = RECALC[ident]()
            except Exception as e:  # noqa: BLE001
                got = f"erreur {e}"
            want = val
            try:
                ok = abs(float(got) - float(want)) <= 1e-9 * max(1, abs(float(want))) or str(got) == want
            except (TypeError, ValueError):
                ok = str(got) == want
            msg.append(f"recalculé {got}" + ("" if ok else f" ≠ registre {want}"))
            gaps += not ok
        else:
            msg.append("source non recalculée (valeur textuelle ou fichier hors script)")
        nums = FORMS.get(ident, nombres(val))
        missing = [n for n in nums if not any(re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", tex) for f in formes(n))]
        if missing:
            msg.append("absent du texte : " + ", ".join(missing))
            gaps += 1
        lines.append(f"{'OK ' if not missing and 'registre' not in msg[0] else 'ÉCART'} {ident}: " + " ; ".join(msg))
    print(f"Contrôle des chiffres ({len(rows)} lignes du registre ; texte : {', '.join(Path(f).name for f in files)})")
    print("\n".join(lines))
    print(f"\nÉcarts : {gaps}")
    return gaps


if __name__ == "__main__":
    fs = sys.argv[1:] or sorted(str(p) for p in list((ROOT / "article/latex").glob("*.tex"))
                                + list((ROOT / "article/latex/tables").glob("*.tex")) if p.name != "main.tex")
    sys.exit(1 if main(fs) else 0)
