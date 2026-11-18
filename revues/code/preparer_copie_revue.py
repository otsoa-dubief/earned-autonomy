"""Copie propre du dépôt pour une revue de code dans le cloud (`/code-review ultra`).

Cette revue envoie le dépôt de la session avec tout son historique. Or `donnees/` (fichier scellé, données
confidentielles du terrain) figure dans l'historique du dépôt de recherche. La copie est donc un dépôt neuf :
- sans historique du dépôt de recherche ;
- seulement le code, la règle, le plan, le journal et les revues de code (liste INCLUS) ;
- jamais `donnees/`, ni les notes de terrain, ni le suivi personnel (liste INTERDITS, vérifiée après extraction).

La revue « ultra » relit le diff de la branche courante par rapport à la branche par défaut, dans la limite de 500
fichiers et 8 000 lignes modifiées (doc de Claude Code, lue le 06/11 : code.claude.com/docs/en/ultrareview). Le dépôt
entier en compte bien plus. D'où des lots (LOTS) : `main` porte tout sauf le lot, comme contexte (spécification,
tests, autres modules, résultats) ; la branche `revue`, où la copie est laissée, ajoute seulement le lot. Une copie et
une revue par lot. `--lot tout` garde l'ancien comportement (un seul commit), trop grand pour la revue « ultra ».

Usage :
    simulation/.venv/bin/python revues/code/preparer_copie_revue.py --lot moteur [--commit HEAD] [--dossier …]
Puis Otsoa ouvre une session Claude Code dans le dossier créé (par défaut ../autonomie-meritee-revue-<lot>) et tape
`/code-review ultra`.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import io
import subprocess
import sys
import tarfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
INCLUS = ["REGLE.md", "PLAN_EXPERIENCE.md", "JOURNAL_CHANGEMENTS.md", "banc", "simulation", "gel", "revues/code",
          ".gitignore"]
INTERDITS = ("donnees", "notes", "lectures", "pilote", "research_notes", "depots", "ATTENTE.md", "CADRE.md",
             "SUIVI.md", "externe")
AUTEUR = ["-c", "user.name=Otsoa Dubief", "-c", "user.email=recherche@autonomie-meritee.local"]
LIMITE_FICHIERS = 500     # /code-review ultra, valeurs par défaut (doc lue le 06/11)
LIMITE_LIGNES = 8000

# Motifs relatifs à la racine ; `*` ne traverse pas les dossiers (les tests restent dans `main`, comme contexte).
LOTS = {
    "moteur": ("simulation/rejeu/*.py", "gel/*.py"),
    "banc": ("banc/lanceur.py", "banc/verdicts.py", "banc/verdicts_csv.py", "banc/typage.py", "banc/reussite*.py",
             "banc/relecture/*.py", "banc/tirage/*.py", "banc/outils_agent.py", "banc/usage_*.py", "banc/cout_v2.py",
             "banc/tau2_sans_juge.py"),
}

PORTEE = {
    "moteur": """La branche `revue` ajoute à `main` le moteur de rejeu, qui calcule le verdict (`simulation/rejeu/*.py`, hors
tests : `decision.py`, `maxt.py`, `intervalles.py`, `analyse.py`, `pipeline.py`, `classes.py`, `moteur.py`,
`suites.py`, `temoins.py`, `epreuves.py`…), et le manifeste du gel (`gel/`) : {n} fichiers, {l} lignes. `main`
contient tout le reste comme contexte : la spécification, les tests du moteur (`simulation/rejeu/tests/`), le banc,
le contrôle 3 et les résultats des simulations. La revue porte sur ce que `revue` ajoute ; le reste sert à comprendre
et à reproduire.""",
    "banc": """La branche `revue` ajoute à `main` le cœur du banc : le lanceur de l'expérience, qui dépense de l'argent réel
(son plafond codé est le seul mur ; `banc/lanceur.py`), l'instrument et la relecture (`banc/verdicts.py`,
`banc/typage.py`, `banc/relecture/`), le tirage public (`banc/tirage/`) et leurs petits modules (`reussite*.py`,
`usage_*.py`, `cout_v2.py`, `outils_agent.py`, `tau2_sans_juge.py`, `verdicts_csv.py`) : {n} fichiers, {l} lignes.
`main` contient tout le reste comme contexte, dont le moteur de rejeu (`simulation/rejeu/`), qui lit les sorties du
banc, et les tests (`banc/tests/`). La revue porte sur ce que `revue` ajoute ; le reste sert à comprendre et à
reproduire.""",
    "tout": """- `simulation/rejeu/` : le moteur de rejeu, qui calcule le verdict (`decision.py`, `maxt.py`, `intervalles.py`,
  `analyse.py`, `pipeline.py`, `classes.py`, `moteur.py`, `suites.py`, `temoins.py`, `epreuves.py`) ;
- `banc/lanceur.py` : le lanceur de l'expérience, qui dépense de l'argent réel (son plafond codé est le seul mur) ;
- `banc/relecture/`, `banc/tirage/`, `banc/verdicts.py`, `banc/typage.py` : l'instrument, le tirage public, la relecture ;
- `gel/manifeste.py` : le manifeste du gel.""",
}

LISEZMOI = """# Copie pour la revue de code ({lot})

Copie partielle du dépôt de recherche « autonomie méritée », commit d'origine {commit}, préparée le {date} par
`revues/code/preparer_copie_revue.py`. Dépôt neuf, sans l'historique du dépôt de recherche.

## Ce qu'il faut relire
{portee}

La spécification est `PLAN_EXPERIENCE.md` (sections 2, 3.4, 4 et 5, surtout 5.13 et 5.14) et `REGLE.md`. Les choix
d'implémentation sont notés dans `simulation/rejeu/CHOIX_PHASE*.md` et `banc/CHOIX_LANCEUR.md` ; les revues déjà
faites sont dans `revues/code/`.

Derniers changements du moteur. N1 (06/11) : la délégabilité se lit sur le taux médian (`classes.mediane_haute`,
`estime_sous`, `jugeable`), l'oracle suit la même règle. N3 (06/11) : ρ̂ par couple (tâche, type), Fleiss–Cuzick
stratifié (`classes.rho_fc_strates`), preuves à 95 % à ρ = 1. Amendement de R4 (07/11, décidé par Otsoa) : R4 exige,
dans chaque configuration jugeable, un type jugeable dont le dépassement est établi à ρ = 1 ; sinon « preuves
insuffisantes », qui remplace « volume insuffisant », avec son motif (`classes.depassement_etabli`,
`statut_configuration`, `decision.point4` ; `simulation/rejeu/CHOIX_AMENDEMENT_R4.md`) ; sans configuration
délégable, les configurations sans type jugeable sont nommées, hors du constat. Cellule non testable (07/11, décidé
par Otsoa) : une cellule à moins de deux tâches porteuses, ou d'écart type bootstrap nul ou non défini, sort du
max-T et n'établit aucun dépassement, pour B-tout comme pour les témoins (`maxt.depassement_etabli`,
`decision.cellules`, `depassement_temoin` ; `simulation/rejeu/CHOIX_CELLULES_NON_TESTABLES.md`).
`simulation/controle3/` rejoue
toute la chaîne sur des mondes fictifs dont la vérité est connue ; `simulation/controle3/RAPPORT.md` dit ce qu'elle
donne, passage par passage.

## Ce qui manque, volontairement
Les bancs (`externe/`), les sorties brutes du pilote (`pilote/`), les données de terrain et les notes. Les tests qui
en dépendent ne tourneront pas ici. Aucun appel réel à une API ne doit être fait.
Restent seulement, en plus des résultats des simulations (mondes fictifs) : les sorties agrégées du moteur sur le
pilote (`simulation/rejeu/sorties_pilote/`, `simulation/rejeu/essai_a_blanc_pilote/`) et deux courtes traces
WorkBench qui servent de fixtures aux tests (`banc/tests/fixtures/pilote_workbench/`).
"""


def git(*args: str, cwd: Path = RACINE) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True).stdout


def extraire(commit: str, cible: Path) -> list:
    archive = subprocess.run(["git", "-C", str(RACINE), "archive", "--format=tar", commit, "--", *INCLUS],
                             capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        noms = [m.name for m in tar.getmembers() if m.isfile()]
        interdits = [n for n in noms if n.split("/")[0] in INTERDITS]
        if interdits:
            raise SystemExit(f"refus : chemins interdits dans l'archive : {interdits[:5]}")
        tar.extractall(cible, filter="data")
    return noms


def correspond(nom: str, motif: str) -> bool:
    """Le chemin correspond au motif segment par segment (`*` ne traverse pas les dossiers)."""
    a, b = nom.split("/"), motif.split("/")
    return len(a) == len(b) and all(fnmatch.fnmatchcase(x, y) for x, y in zip(a, b))


def fichiers_du_lot(noms, lot: str) -> list:
    return sorted(n for n in noms if any(correspond(n, m) for m in LOTS[lot]))


def lignes(cible: Path, noms) -> int:
    """Lignes des fichiers, comptées comme git les compte dans un diff d'ajout."""
    total = 0
    for n in noms:
        with open(cible / n, "rb") as f:
            total += sum(1 for _ in f)
    return total


def preparer(commit: str, cible: Path, lot: str) -> dict:
    if cible.exists() and any(cible.iterdir()):
        raise SystemExit(f"refus : {cible} existe et n'est pas vide")
    sha = git("rev-parse", commit).strip()
    cible.mkdir(parents=True, exist_ok=True)
    noms = extraire(sha, cible)
    date = git("log", "-1", "--format=%cd", "--date=format:%Y-%m-%d %H:%M", sha).strip()
    du_lot = fichiers_du_lot(noms, lot) if lot != "tout" else []
    if lot != "tout" and not du_lot:
        raise SystemExit(f"refus : aucun fichier dans le lot {lot}")
    n_lignes = lignes(cible, du_lot)
    if lot != "tout" and (len(du_lot) > LIMITE_FICHIERS or n_lignes > LIMITE_LIGNES):
        raise SystemExit(f"refus : lot {lot} trop grand pour la revue « ultra » ({len(du_lot)} fichiers, {n_lignes} "
                         f"lignes ; limites {LIMITE_FICHIERS} et {LIMITE_LIGNES})")
    portee = PORTEE[lot].format(n=len(du_lot), l=n_lignes)
    (cible / "LISEZMOI_REVUE.md").write_text(LISEZMOI.format(lot=lot, commit=sha[:12], date=date, portee=portee),
                                             encoding="utf-8")
    present = sorted({p.name for p in cible.iterdir()})
    if any(p in INTERDITS for p in present):
        raise SystemExit(f"refus : entrée interdite à la racine de la copie : {present}")
    git("init", "-q", "-b", "main", cwd=cible)
    git(*AUTEUR, "add", "-A", cwd=cible)
    if lot == "tout":
        git(*AUTEUR, "commit", "-q", "-m", f"Copie pour revue de code (origine {sha[:12]})", cwd=cible)
    else:
        git("rm", "-q", "--cached", "--", *du_lot, cwd=cible)
        git(*AUTEUR, "commit", "-q", "-m", f"Contexte de la revue, sans le lot {lot} (origine {sha[:12]})", cwd=cible)
        git("checkout", "-q", "-b", "revue", cwd=cible)
        git(*AUTEUR, "add", "-A", cwd=cible)
        git(*AUTEUR, "commit", "-q", "-m", f"Lot à relire : {lot} (origine {sha[:12]})", cwd=cible)
        stat = [ligne.split("\t") for ligne in git("diff", "--numstat", "main", "revue", cwd=cible).splitlines()]
        n_diff = sum(int(a) + int(s) for a, s, _ in stat)
        if sorted(c for _, _, c in stat) != du_lot or n_diff != n_lignes:
            raise SystemExit(f"refus : le diff de `revue` ne correspond pas au lot ({len(stat)} fichiers, {n_diff} "
                             f"lignes ; attendu {len(du_lot)} et {n_lignes})")
    if git("status", "--porcelain", cwd=cible).strip():
        raise SystemExit("refus : fichiers non suivis dans la copie (la revue les refuserait)")
    empreinte = hashlib.sha256("".join(sorted(noms)).encode()).hexdigest()
    return {"commit_origine": sha, "fichiers": len(noms), "racine": present, "empreinte_liste": empreinte,
            "lot": lot, "fichiers_lot": len(du_lot), "lignes_lot": n_lignes,
            "branche": git("branch", "--show-current", cwd=cible).strip(),
            "commit_copie": git("rev-parse", "HEAD", cwd=cible).strip()}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lot", choices=(*LOTS, "tout"), required=True)
    p.add_argument("--commit", default="HEAD")
    p.add_argument("--dossier", type=Path, default=None)
    a = p.parse_args(argv)
    dossier = (a.dossier or RACINE.parent / f"autonomie-meritee-revue-{a.lot}").resolve()
    r = preparer(a.commit, dossier, a.lot)
    print(f"Copie prête : {dossier} ({r['fichiers']} fichiers, origine {r['commit_origine'][:12]}, "
          f"branche {r['branche']}, commit {r['commit_copie'][:12]})")
    if r["lot"] != "tout":
        print(f"Lot {r['lot']} : {r['fichiers_lot']} fichiers, {r['lignes_lot']} lignes ajoutées à `main`")
    print(f"À la racine : {', '.join(r['racine'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
