"""Manifeste du gel des verdicts confirmés (PLAN_EXPERIENCE.md, 3.4, point 3, et 5.2 ; relecture C13, P1).

Écrit une fois, après la dernière vague, l'audit des tâches sans alerte et la réponse d'Otsoa sur les retraits du
motif a, avant le dépôt OSF du gel des verdicts et avant le tirage public. Son SHA-256 entre dans la graine du partage
(`banc/tirage/tirage_public.py tirer --manifeste`). Le rejeu final refuse toute entrée qui n'y figure pas ou dont
l'empreinte diffère (`simulation/rejeu/bout_en_bout.py --experience --manifeste-verdicts`).

Format : une ligne « sha256  chemin » par fichier, triée, chemins relatifs à la racine de l'expérience (le dossier
qui contient le manifeste), comme `shasum -a 256`. Contenu (plan, 5.2) :
- chaque dossier de vague du lanceur, en entier : traces des parties, `actions_typees.csv`, `actions.csv`,
  `cout.json`, `tentatives.jsonl`, `plan_de_jeu.json`, et `reussite.csv`, calculé ici s'il manque (sans affichage) ;
- les bilans de relecture de chaque vague (`decisions.csv`, `alertes.json`, `accord.json`), avec les tirages de la
  relecture et son journal des lots ;
- l'audit des tâches sans alerte (`audit_tirage.json`, `audit_conclusion.json`, `taches_retirees_audit.json`) ;
- la liste des retraits du motif a et le fichier des oppositions d'Otsoa ;
- `gel_plan.json` : commit et étiquette du gel du plan, SHA-256 de `gel/MANIFESTE_SHA256.txt`.
`donnees/` n'est jamais lu.

Usage (depuis la racine du dépôt) :
    simulation/.venv/bin/python gel/manifeste_verdicts.py ecrire --racine <expérience> --vague <dossier> […]
        --chemin <fichier ou dossier> […] [--sortie manifeste_verdicts.txt]
    simulation/.venv/bin/python gel/manifeste_verdicts.py verifier --manifeste <expérience>/manifeste_verdicts.txt
        --chemin <fichier ou dossier lu par le rejeu> […]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[1]
GEL_PLAN = "gel_plan.json"
INTERDITS = ("donnees",)


def sha256(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def _relatif(racine: Path, chemin: Path) -> str:
    rel = Path(chemin).resolve().relative_to(Path(racine).resolve())   # ValueError hors de la racine
    if rel.parts and rel.parts[0] in INTERDITS:
        raise ValueError(f"{chemin} : `donnees/` n'est jamais lu")
    return rel.as_posix()


def fichiers_sous(racine: Path, chemins) -> dict:
    """{chemin relatif : chemin absolu} des fichiers donnés, dossiers parcourus en entier."""
    out = {}
    for c in chemins:
        c = Path(c)
        liste = sorted(p for p in c.rglob("*") if p.is_file()) if c.is_dir() else [c]
        for p in liste:
            out[_relatif(racine, p)] = p
    return out


def gel_plan_courant() -> dict:
    """Commit et étiquette du dépôt, SHA-256 du manifeste du gel du plan (s'il existe)."""
    def git(*args):
        return subprocess.run(["git", "-C", str(DEPOT), *args], capture_output=True, text=True).stdout.strip()
    m = DEPOT / "gel" / "MANIFESTE_SHA256.txt"
    return dict(commit=git("rev-parse", "HEAD"), etiquette=git("describe", "--tags", "--exact-match") or None,
                manifeste_gel=sha256(m) if m.is_file() else None)


def ecrire(racine: Path, chemins, sortie: Path, gel_plan: dict | None = None) -> str:
    """Écrit le manifeste et rend son SHA-256. Refuse d'écraser un manifeste existant."""
    racine, sortie = Path(racine), Path(sortie)
    if sortie.exists():
        raise FileExistsError(f"{sortie} existe déjà : le gel des verdicts ne se refait pas")
    fichiers = fichiers_sous(racine, chemins)
    if gel_plan is not None:
        (racine / GEL_PLAN).write_text(json.dumps(gel_plan, indent=1, ensure_ascii=False), encoding="utf-8")
        fichiers[GEL_PLAN] = racine / GEL_PLAN
    fichiers.pop(_relatif(racine, sortie), None)
    lignes = sorted(f"{sha256(p)}  {rel}" for rel, p in fichiers.items())
    sortie.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return sha256(sortie)


def lire(manifeste: Path) -> dict:
    out = {}
    for ligne in Path(manifeste).read_text(encoding="utf-8").splitlines():
        if ligne.strip():
            h, _, rel = ligne.partition("  ")
            out[rel] = h
    return out


def ecarts(manifeste: Path, chemins_lus) -> list:
    """Écarts entre ce que lit le rejeu final et le manifeste : fichier absent du manifeste, empreinte différente,
    fichier du manifeste disparu d'un dossier lu, chemin hors de la racine de l'expérience."""
    manifeste = Path(manifeste)
    racine = manifeste.parent
    attendu = lire(manifeste)
    out, prefixes = [], []
    for c in chemins_lus:
        c = Path(c)
        try:
            rel_c = _relatif(racine, c)
        except ValueError:
            out.append(f"{c} est hors de la racine de l'expérience ({racine})")
            continue
        if c.is_dir():
            prefixes.append(rel_c.rstrip("/") + "/")
        for rel, p in fichiers_sous(racine, [c]).items():
            if rel not in attendu:
                out.append(f"{rel} absent du manifeste")
            elif sha256(p) != attendu[rel]:
                out.append(f"{rel} diffère du manifeste")
    for rel in attendu:
        if any(rel.startswith(px) for px in prefixes) and not (racine / rel).is_file():
            out.append(f"{rel} manque (inscrit au manifeste)")
    return sorted(set(out))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sous = p.add_subparsers(dest="commande", required=True)
    e = sous.add_parser("ecrire")
    e.add_argument("--racine", required=True, type=Path, help="dossier de l'expérience (hors du dépôt)")
    e.add_argument("--vague", action="append", default=[], type=Path, help="dossier d'une vague du lanceur")
    e.add_argument("--chemin", action="append", default=[], type=Path,
                   help="autre fichier ou dossier : bilans, tirages et journal de la relecture, audit, retraits, "
                        "oppositions")
    e.add_argument("--sortie", type=Path, default=None)
    v = sous.add_parser("verifier")
    v.add_argument("--manifeste", required=True, type=Path)
    v.add_argument("--chemin", action="append", default=[], type=Path)
    a = p.parse_args(argv)
    if a.commande == "ecrire":
        if a.vague:   # réussite des tâches calculée avant le gel des verdicts (5.2), sans affichage
            sys.path.insert(0, str(DEPOT / "simulation"))
            from rejeu import bout_en_bout as BE
            BE.preparer_reussite([str(d) for d in a.vague])
        sortie = a.sortie or a.racine / "manifeste_verdicts.txt"
        h = ecrire(a.racine, list(a.vague) + list(a.chemin), sortie, gel_plan_courant())
        print(f"manifeste du gel des verdicts : {sortie}\nSHA-256 : {h}")
        return 0
    ec = ecarts(a.manifeste, a.chemin)
    for x in ec:
        print(f"ÉCART : {x}")
    print("conforme" if not ec else f"{len(ec)} écart(s)")
    return 1 if ec else 0


if __name__ == "__main__":
    sys.exit(main())
