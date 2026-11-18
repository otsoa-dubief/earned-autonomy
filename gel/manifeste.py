"""Manifeste du gel du plan (PLAN_EXPERIENCE.md, « Étape par étape », point 7 ; REGLE.md, pièce 9).

Ce qui est figé :
- la règle et le plan ;
- tout ce que git suit dans `banc/`, `simulation/` et `gel/` : instrument, lanceur, moteur de rejeu et sa
  configuration, réserve, paires, table des outils, définitions d'outils, tests ;
- le commit des deux bancs (`externe/`, hors git) et les fichiers de `externe/workbench-run/` ;
- la liste exacte des paquets des trois environnements Python (`gel/environnements/`).
`JOURNAL_CHANGEMENTS.md` et `SUIVI.md` continuent après le gel : leur empreinte au gel est notée dans `gel/GEL.json`,
sans être vérifiée ensuite. `donnees/` n'est jamais lu. Les sorties de l'expérience vont hors de ce périmètre.

Étapes du gel (18/11) :
  1. --tirer-g0 : tire G0 (`secrets.randbits(64)`, plan 5.5) et l'écrit dans config_rejeu.json, une seule fois ;
     écrire ensuite sa valeur dans PLAN_EXPERIENCE.md, puis commiter ;
  2. --ecrire : exige un dépôt propre, G0 écrite dans le plan et des bancs sans modification locale ; écrit
     gel/GEL.json, gel/environnements/*.txt et gel/MANIFESTE_SHA256.txt ; ensuite commit, étiquette git, dépôt OSF ;
  3. --verifier : compare le dépôt au manifeste (code de sortie 1 au moindre écart), y compris un fichier ajouté
     dans externe/workbench-run/ ou un fichier non suivi dans le périmètre.
--apercu montre ce qui serait figé et ce qui empêche le gel, sans rien écrire.
Sans ce script : `shasum -a 256 -c gel/MANIFESTE_SHA256.txt` vérifie les fichiers.

Usage : simulation/.venv/bin/python gel/manifeste.py (--apercu | --tirer-g0 | --ecrire | --verifier)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import secrets
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
PERIMETRE = ("REGLE.md", "PLAN_EXPERIENCE.md", "banc", "simulation", "gel")
VIVANTS = ("JOURNAL_CHANGEMENTS.md", "SUIVI.md", "CADRE.md")  # empreinte notée au gel, non vérifiée ensuite (CADRE.md : C13, P14)
INTERDITS = ("donnees/",)  # jamais lus, même pour une empreinte
BANCS = ("externe/tau2-bench", "externe/WorkBench")
EXTERNES = ("externe/workbench-run",)  # fichiers hors git lus par les bancs (verrous exclus : C13, P14)
# fichiers de tâches, de données et d'outils des bancs, figés par leur SHA-256 (plan 2.1 ; relecture C13, P13) ;
# jamais les sorties publiées (data/tau2/results, item_level_results, data/results)
ENTREES_BANCS = {
    "externe/tau2-bench": ("data/tau2/domains/airline", "data/tau2/domains/retail", "data/tau2/domains/banking_knowledge",
                           "src/tau2/domains/airline", "src/tau2/domains/retail", "src/tau2/domains/banking_knowledge"),
    "externe/WorkBench": ("data/processed", "data/raw", "src/tools"),
}
ENVIRONNEMENTS = {
    "simulation": "simulation/.venv/bin/python",
    "tau2-bench": "externe/tau2-bench/.venv/bin/python",
    "WorkBench": "externe/WorkBench/.venv/bin/python",
}
CONFIG_REJEU = "simulation/rejeu/config_rejeu.json"
PLAN = "PLAN_EXPERIENCE.md"
MANIFESTE = "gel/MANIFESTE_SHA256.txt"
GEL = "gel/GEL.json"
DOSSIER_ENV = "gel/environnements"
PRODUITS = (GEL, DOSSIER_ENV + "/", MANIFESTE)  # écrits par --ecrire
PAQUETS = (
    "import importlib.metadata as m, sys\n"
    "print('python ' + sys.version.split()[0])\n"
    "noms = {d.metadata['Name'] + '==' + d.version for d in m.distributions()}\n"
    "print('\\n'.join(sorted(noms, key=str.lower)))\n"
)


class GelInvalide(RuntimeError):
    pass


def git(dossier: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(dossier), *args], capture_output=True, text=True, check=True).stdout


def sha256(chemin: Path) -> str:
    if str(chemin).replace("\\", "/").find("/donnees/") >= 0:
        raise GelInvalide(f"refus de lire {chemin} : donnees/ n'est jamais lu")
    h = hashlib.sha256()
    with open(chemin, "rb") as fh:
        for bloc in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def fichiers_figes(racine: Path) -> list:
    """Fichiers suivis par git dans le périmètre (le manifeste lui-même excepté)."""
    noms = git(racine, "ls-files", "-z", "--", *PERIMETRE).split("\0")
    return sorted(n for n in noms if n and n != MANIFESTE and not n.startswith(INTERDITS) and (racine / n).is_file())


def fichiers_externes(racine: Path) -> list:
    sortie = []
    for d in EXTERNES:
        if (racine / d).is_dir():
            sortie += sorted(p.relative_to(racine).as_posix() for p in (racine / d).rglob("*")
                             if p.is_file() and ".git" not in p.parts and p.suffix != ".verrou")
    return sortie


def fichiers_bancs(racine: Path) -> list:
    """Fichiers suivis par git des bancs, dans les dossiers d'entrée (ENTREES_BANCS)."""
    out = []
    for d, sous in ENTREES_BANCS.items():
        if (racine / d).is_dir():
            noms = git(racine / d, "ls-files", "-z", "--", *sous).split("\0")
            out += sorted(f"{d}/{n}" for n in noms if n and (racine / d / n).is_file())
    return out


def non_suivis(racine: Path) -> list:
    """Fichiers non suivis (et non ignorés) dans le périmètre : un module ajouté sans commit changerait le code exécuté
    sans changer le manifeste."""
    entrees = git(racine, "status", "--porcelain", "-z", "--untracked-files=all", "--", *PERIMETRE).split("\0")
    return sorted(e[3:] for e in entrees if e.startswith("?? ") and not e[3:].startswith(INTERDITS))


def etat_bancs(racine: Path) -> dict:
    return {d: {"commit": git(racine / d, "rev-parse", "HEAD").strip(),
                "propre": not git(racine / d, "status", "--porcelain", "--untracked-files=normal").strip()}
            for d in BANCS}


def paquets(racine: Path, python: str) -> str:
    """Version de Python et paquets installés (nom==version), dans l'environnement donné."""
    return subprocess.run([str(racine / python), "-I", "-c", PAQUETS], capture_output=True, text=True,
                          check=True).stdout


def g0_config(racine: Path):
    return json.loads((racine / CONFIG_REJEU).read_text(encoding="utf-8"))["graines"]["G0"]


def tirer_g0(racine: Path) -> int:
    """Tire G0 une seule fois et l'écrit dans config_rejeu.json (le reste du fichier est inchangé)."""
    deja = g0_config(racine)
    if deja is not None:
        raise GelInvalide(f"G0 est déjà tirée ({deja}) : elle ne se tire qu'une fois")
    chemin = racine / CONFIG_REJEU
    texte = chemin.read_text(encoding="utf-8")
    if texte.count('"G0": null') != 1:
        raise GelInvalide(f'{CONFIG_REJEU} : « "G0": null » attendu une seule fois')
    g0 = secrets.randbits(64)
    chemin.write_text(texte.replace('"G0": null', f'"G0": {g0}', 1), encoding="utf-8")
    if g0_config(racine) != g0:
        raise GelInvalide("G0 relue différente de G0 tirée")
    return g0


ANCRE_G0 = "une graine maîtresse G0, tirée par `secrets.randbits(64)` au gel et écrite dans le plan figé"
LIGNE_G0 = "« - valeur tirée au gel : G0 = <valeur> », juste sous la puce de la graine maîtresse"
_LIGNE_G0 = re.compile(r"^\s*- valeur tirée au gel : G0 = (\d+)\s*$")


def g0_ecrite(racine: Path, g0: int) -> bool:
    """G0 écrite une seule fois, à l'endroit prévu (audit du gel, O5) : la ligne qui suit la puce de la graine
    maîtresse, au format LIGNE_G0, et nulle part ailleurs sous ce format."""
    lignes = (racine / PLAN).read_text(encoding="utf-8").splitlines()
    ancres = [i for i, l in enumerate(lignes) if ANCRE_G0 in l]
    valeurs = [i for i, l in enumerate(lignes) if _LIGNE_G0.match(l)]
    if len(ancres) != 1 or len(valeurs) != 1 or valeurs[0] != ancres[0] + 1:
        return False
    return int(_LIGNE_G0.match(lignes[valeurs[0]]).group(1)) == g0


def prealables(racine: Path) -> list:
    """Ce qui empêche le gel : dépôt pas propre, G0 absente du plan, banc modifié, gel déjà fait."""
    problemes = []
    sales = [l[3:] for l in git(racine, "status", "--porcelain", "--", *PERIMETRE, *VIVANTS).splitlines()]
    sales = [n for n in sales if not n.startswith(PRODUITS)]
    if sales:
        problemes.append(f"{len(sales)} fichiers modifiés ou non suivis, à commiter : {', '.join(sales[:5])}")
    g0 = g0_config(racine)
    if g0 is None:
        problemes.append("G0 n'est pas tirée (--tirer-g0)")
    elif not g0_ecrite(racine, g0):
        problemes.append(f"G0 = {g0} n'est pas écrite dans {PLAN} à l'endroit prévu (5.5, point 4 : {LIGNE_G0})")
    for d, e in etat_bancs(racine).items():
        if not e["propre"]:
            problemes.append(f"{d} a des modifications locales")
    if git(racine, "ls-files", "--", MANIFESTE).strip():
        problemes.append("le manifeste est déjà commité : le gel est fait")
    return problemes


def ecrire(racine: Path, date: str | None = None) -> dict:
    problemes = prealables(racine)
    if problemes:
        raise GelInvalide("gel refusé :\n- " + "\n- ".join(problemes))
    (racine / DOSSIER_ENV).mkdir(parents=True, exist_ok=True)
    envs = {}
    for nom, python in ENVIRONNEMENTS.items():
        texte = paquets(racine, python)
        fichier = f"{DOSSIER_ENV}/{nom}.txt"
        (racine / fichier).write_text(texte, encoding="utf-8")
        envs[nom] = {"python": texte.splitlines()[0].removeprefix("python "), "fichier": fichier}
    gel = {
        "date": date or time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "commit": git(racine, "rev-parse", "HEAD").strip(),
        "G0": g0_config(racine),
        "bancs": etat_bancs(racine),
        "environnements": envs,
        "etat_au_gel": {n: sha256(racine / n) for n in VIVANTS if (racine / n).is_file()},
        "plateforme": {"systeme": platform.platform(), "machine": platform.machine(),
                       "processeur": platform.processor()},   # C13, P14
        "verification": "simulation/.venv/bin/python gel/manifeste.py --verifier",
    }
    (racine / GEL).write_text(json.dumps(gel, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    noms = (sorted(set(fichiers_figes(racine)) | {GEL} | {e["fichier"] for e in envs.values()}) + fichiers_externes(racine)
            + fichiers_bancs(racine))
    (racine / MANIFESTE).write_text("".join(f"{sha256(racine / n)}  {n}\n" for n in noms), encoding="utf-8")
    return {"gel": gel, "fichiers": len(noms)}


def lire_manifeste(racine: Path) -> dict:
    attendu = {}
    for ligne in (racine / MANIFESTE).read_text(encoding="utf-8").splitlines():
        if ligne.strip():
            h, n = ligne.split("  ", 1)
            attendu[n] = h
    return attendu


def verifier(racine: Path) -> list:
    """Écarts entre le dépôt et le gel ; liste vide si tout est conforme."""
    if not (racine / MANIFESTE).is_file():
        return ["pas de manifeste : le gel n'est pas fait"]
    attendu = lire_manifeste(racine)
    ecarts = [f"modifié ou absent : {n}" for n, h in attendu.items()
              if not (racine / n).is_file() or sha256(racine / n) != h]
    ecarts += [f"nouveau, hors gel : {n}" for n in fichiers_figes(racine) + fichiers_externes(racine)
               + fichiers_bancs(racine) if n not in attendu]
    ecarts += [f"nouveau, non suivi par git : {n}" for n in non_suivis(racine)]   # revue « ultra », 06/11
    gel = json.loads((racine / GEL).read_text(encoding="utf-8"))
    for d, e in etat_bancs(racine).items():
        if e["commit"] != gel["bancs"][d]["commit"]:
            ecarts.append(f"{d} : commit {e['commit'][:7]} au lieu de {gel['bancs'][d]['commit'][:7]}")
        if not e["propre"]:
            ecarts.append(f"{d} : modifications locales")
    for nom, python in ENVIRONNEMENTS.items():
        if paquets(racine, python) != (racine / gel["environnements"][nom]["fichier"]).read_text(encoding="utf-8"):
            ecarts.append(f"environnement {nom} : paquets ou version de Python différents du gel")
    return ecarts


def apercu(racine: Path) -> dict:
    noms = fichiers_figes(racine) + fichiers_externes(racine) + fichiers_bancs(racine)
    return {"fichiers": noms, "par_dossier": dict(Counter(n.split("/")[0] for n in noms)),
            "G0": g0_config(racine), "bancs": etat_bancs(racine), "problemes": prealables(racine)}


def main(argv=None, racine: Path = RACINE) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    for option in ("--apercu", "--tirer-g0", "--ecrire", "--verifier"):
        g.add_argument(option, action="store_true")
    a = p.parse_args(argv)
    try:
        if a.apercu:
            r = apercu(racine)
            print(f"{len(r['fichiers'])} fichiers seraient figés : {r['par_dossier']}")
            print(f"G0 : {r['G0'] if r['G0'] is not None else 'pas encore tirée'}")
            for d, e in r["bancs"].items():
                print(f"{d} : {e['commit'][:7]}{'' if e['propre'] else ' (modifications locales)'}")
            print("Prêt pour le gel." if not r["problemes"] else "Empêche le gel :\n- " + "\n- ".join(r["problemes"]))
        elif a.tirer_g0:
            g0 = tirer_g0(racine)
            print(f"G0 = {g0} (écrite dans {CONFIG_REJEU}). À écrire dans {PLAN} (5.5, point 4) : {LIGNE_G0} ; puis commiter.")
        elif a.ecrire:
            r = ecrire(racine)
            print(f"Gel écrit : {r['fichiers']} fichiers dans {MANIFESTE} ; commit de base {r['gel']['commit'][:7]}.")
            print(f"SHA-256 du manifeste : {sha256(racine / MANIFESTE)}")
            print("Ensuite : commit de gel/, étiquette git, dépôt OSF.")
        else:
            ecarts = verifier(racine)
            if ecarts:
                print("ÉCARTS AU GEL :\n- " + "\n- ".join(ecarts))
                return 1
            print("Conforme au gel.")
    except GelInvalide as e:
        print(f"erreur: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
