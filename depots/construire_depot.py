"""Construit un paquet de dépôt OSF à partir d'un commit git du projet.

Usage :
    python3 depots/construire_depot.py --commit <sha> --dossier depots/2026-11-05_anteriorite
    python3 depots/construire_depot.py --type gel --commit <sha> --etiquette <tag> --date "<date>" --dossier depots/<date>_gel

Le paquet contient les fichiers publiables extraits du commit (INCLUS), un README en anglais, la licence MIT du code,
les mentions des bancs tiers (licences MIT de τ-bench et de WorkBench) et un manifeste SHA-256. Les autres entrées du
commit sont seulement citées par leur empreinte git. Le zip et les fichiers extraits restent hors git.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
INCLUS_ANTERIORITE = ["REGLE.md", "PLAN_EXPERIENCE.md", "JOURNAL_CHANGEMENTS.md", "simulation", "banc", "reports"]
INCLUS_GEL = INCLUS_ANTERIORITE[:5] + ["gel", "reports"]   # gel : C13, P12
INCLUS = INCLUS_GEL
EXCLUS = {  # entrée -> description (anglais)
    "ATTENTE.md": "personal planning notes",
    "CADRE.md": "framing, budget, earlier field study",
    "SUIVI.md": "working log",
    "donnees": "sealed file and confidential field data",
    "lectures": "reading notes",
    "notes": "field note on confidential logs",
    "pilote": "pilot outputs, development tasks only",
    "research_notes": "raw research notes",
    "revues": "independent reviews of the protocol",
}
# Entrées citées par empreinte seulement au gel, en plus d'EXCLUS, quand le commit les contient. Le dépôt
# d'antériorité les taisait (depots/ existait déjà) : il se refait à l'identique, le gel n'en tait plus aucune.
OPTIONNELS = {
    "depots": "OSF deposit records (sheets and package builder)",
    "presentation": "presentation material (slides, one-page summaries)",
    "experience": "experiment outputs (none at the freeze)",
}
FICHIERS_GEL = ["gel/GEL.json", "gel/MANIFESTE_SHA256.txt"]
TIERS = [  # (banc, dépôt, commit, fichier de licence, fichiers du paquet qui en dérivent)
    ("τ-bench 2.0", "sierra-research/tau2-bench", "033bf08", RACINE / "externe" / "tau2-bench" / "LICENSE",
     ["banc/outils_agent/aviation.json", "banc/outils_agent/commerce.json", "banc/outils_agent/banque.json",
      "banc/refus_banque.json"]),
    ("WorkBench", "olly-styles/WorkBench", "49c7dfd", RACINE / "externe" / "WorkBench" / "LICENSE",
     ["banc/outils_agent/workbench.json", "banc/tests/fixtures/pilote_workbench/"]),
]
MIT = """MIT License

Copyright (c) 2026 Otsoa Dubief

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RACINE), *args], capture_output=True, text=True, check=True).stdout


def sha256(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as fh:
        for bloc in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def objets(commit: str) -> dict:
    sortie = {}
    for ligne in git("ls-tree", commit).splitlines():
        meta, nom = ligne.split("\t", 1)
        _, typ, sha = meta.split()
        sortie[nom] = (typ, sha)
    return sortie


def verifier_entrees(obj: dict, inclus: list) -> None:
    """Au gel, toute entrée du commit doit être incluse ou citée par son empreinte : rien ne disparaît en silence."""
    inconnues = sorted(n for n in obj if n not in inclus and n not in EXCLUS and n not in OPTIONNELS
                       and n != ".gitignore")
    if inconnues:
        raise SystemExit(f"entrée inconnue du commit, ni incluse ni citée : {inconnues} (EXCLUS ou OPTIONNELS)")


def readme(commit: str, arbre: str, obj: dict, date: str, type_depot: str = "anteriorite", etiquette: str = "",
           manifeste_sha: str = "", g0=None) -> str:
    if type_depot == "gel":
        return readme_gel(commit, arbre, obj, date, etiquette, manifeste_sha, g0)
    lignes = [f"| `{nom}{'/' if obj[nom][0] == 'tree' else ''}` ({desc}) | {obj[nom][0]} `{obj[nom][1]}` |"
              for nom, desc in EXCLUS.items()]
    tiers = "\n".join(f"  - {b} ({d}, commit {c}): " + ", ".join(f"`{f}`" for f in fs) + "."
                      for b, d, c, _, fs in TIERS)
    court = commit[:7]
    return f"""# Earned autonomy for AI agents: priority record of the working state ({date})

**This is not the preregistration of the experiment.** It is a timestamped record of the state of the project on {date}. The frozen experiment plan will be registered separately, before any confirmatory data are collected (planned for 18 November 2026).

- Author: Otsoa Dubief (ORCID [0009-0002-7322-7575](https://orcid.org/0009-0002-7322-7575)).
- Code and documents were written with the help of Claude (Anthropic), under the author's direction.
- Working language of the documents: French. The article will be in English.

## Research question

Which open protocol would let any organisation delegate progressively to an AI agent, per type of action, on verified evidence, with guarantees that can be checked and revoked?

The rule under test grants autonomy on an action type after a run of verified successes whose length is computed in advance from an error budget, and withdraws it at the first error. It is replayed offline on recorded agent episodes from public benchmarks (τ-bench 2.0, WorkBench). Every write action is judged by exact comparison with the task's expected actions, without any AI judge.

## What this record contains

| Path | Content |
|---|---|
| `REGLE.md` | The rule and all dated design decisions (4 and 5 November 2026). |
| `PLAN_EXPERIENCE.md` | Draft experiment plan (**not frozen**): open questions, replay engine specification, cost estimate. |
| `JOURNAL_CHANGEMENTS.md` | Every change made after the pilot, with its reason and who decided it. |
| `simulation/` | Exploratory simulation E1 (plan, code, results) that selected the rule family before any real data. |
| `banc/` | Benchmark instrumentation: per-action verdicts, action typing table, cost accounting, pilot launchers, alert review tools, frozen tool definitions, tests. |
| `reports/` | Literature reports written for the project. |

The pilot (`pilote/` in the repository) used only development tasks, drawn by a separate agent and excluded from any confirmatory analysis.

## What is committed by hash only

The project is versioned with git. This record is extracted from commit:

- commit `{commit}`
- tree `{arbre}`

The commit hash commits to the whole repository. The following entries of that commit are **not** included here; their git object hashes commit to their exact content, which can be revealed and checked later (`git ls-tree {court}`):

| Entry | Git object |
|---|---|
{chr(10).join(lignes)}

`MANIFEST_SHA256.txt` gives the SHA-256 of every file extracted from the commit (all files here except this README, `LICENSE-CODE.txt`, `THIRD_PARTY_NOTICES.txt` and the manifest itself).

## Licence

- Documents and data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Code (`banc/`, `simulation/`): MIT License, see `LICENSE-CODE.txt`.
- Files derived from the public benchmarks remain under their own MIT licenses, reproduced in `THIRD_PARTY_NOTICES.txt`:
{tiers}

## Résumé en français

Dépôt d'antériorité, daté du {date_fr(date)} : ce n'est pas le préenregistrement. Il contient la règle, le plan d'expérience en projet (non figé), la simulation exploratoire E1, le code de l'instrument et les rapports de lecture. Le reste du dépôt git est engagé par ses empreintes. Les fichiers tirés de τ-bench et de WorkBench gardent leur licence MIT d'origine. Le plan figé sera déposé à part, avant toute donnée de confirmation.
"""


def readme_gel(commit: str, arbre: str, obj: dict, date: str, etiquette: str, manifeste_sha: str, g0) -> str:
    cites = {**EXCLUS, **{n: d for n, d in OPTIONNELS.items() if n in obj}}
    lignes = [f"| `{nom}{'/' if obj[nom][0] == 'tree' else ''}` ({desc}) | {obj[nom][0]} `{obj[nom][1]}` |"
              for nom, desc in cites.items()]
    tiers = "\n".join(f"  - {b} ({d}, commit {c}): " + ", ".join(f"`{f}`" for f in fs) + "."
                      for b, d, c, _, fs in TIERS)
    court = commit[:7]
    return f"""# Earned autonomy for AI agents: preregistration of the frozen experiment plan ({date})

**This is the preregistration of the experiment.** The plan, the rule, the replay engine, the benchmark instrumentation and the freeze manifest are frozen at git tag `{etiquette}` (commit `{commit}`), before any confirmatory data are collected. An earlier priority record of the working state was registered on OSF on 5 November 2026 (https://osf.io/7ju3c/).

- Author: Otsoa Dubief (ORCID [0009-0002-7322-7575](https://orcid.org/0009-0002-7322-7575)).
- Code and documents were written with the help of Claude (Anthropic), under the author's direction.
- Working language of the documents: French. The article will be in English.

## Research question

Which open protocol would let any organisation delegate progressively to an AI agent, per type of action, on verified evidence, with guarantees that can be checked and revoked?

The rule under test grants autonomy on an action type after a run of verified successes whose length is computed in advance from an error budget, and withdraws it at the first error. It is replayed offline on recorded agent episodes from public benchmarks (τ-bench 2.0, WorkBench). Every write action is judged by exact comparison with the task's expected actions, without any AI judge.

## The freeze

- Git tag: `{etiquette}`; commit `{commit}`; tree `{arbre}`.
- Master seed G0, drawn once at the freeze and written in the plan: `{g0}`.
- SHA-256 of `gel/MANIFESTE_SHA256.txt` (the freeze manifest, which lists the SHA-256 of every frozen file): `{manifeste_sha}`.
- The commits of the two benchmarks (τ-bench 2.0 `033bf08`, WorkBench `49c7dfd`) and the Python environments are recorded in `gel/GEL.json` and `gel/environnements/`, not in the manifest.
- Check: the manifest lines outside `externe/` can be checked in this deposit (`shasum -a 256 -c` on those lines, from the deposit root). The `externe/` lines need clones of the benchmarks at commits `033bf08` (sierra-research/tau2-bench) and `49c7dfd` (olly-styles/WorkBench), placed under `externe/`; the `externe/workbench-run/` lines are local run files of the WorkBench benchmark, outside both git repositories, checked on the author's machine and revealed on request. In a full checkout of the tag with those clones, `gel/manifeste.py --verifier` also compares the packages of the three Python environments (`gel/environnements/`) and the files of `externe/workbench-run/`: it reports no difference only with the same environments and the same run files; otherwise it lists them as differences.

## What this deposit contains

| Path | Content |
|---|---|
| `REGLE.md` | The rule and all dated design decisions. |
| `PLAN_EXPERIENCE.md` | The **frozen** experiment plan: hypotheses, analysis, decision rules, replay engine specification, budget. |
| `JOURNAL_CHANGEMENTS.md` | Every change made after the pilot, with its reason and who decided it (state at the freeze). |
| `simulation/` | Simulations (E1 and the control-3 checks of the verdict) and the replay engine that computes the confirmatory analysis. |
| `banc/` | Benchmark instrumentation: per-action verdicts, action typing, cost accounting, launcher, review tools, tests. |
| `gel/` | Freeze manifest, Python environments and the freeze script. |
| `reports/` | Literature reports written for the project. |

The pilot (`pilote/` in the repository) used only development tasks, excluded from any confirmatory analysis.

## What is committed by hash only

The following entries of the tagged commit are **not** included here; their git object hashes commit to their exact content (`git ls-tree {court}`):

| Entry | Git object |
|---|---|
{chr(10).join(lignes)}

`MANIFEST_SHA256.txt` gives the SHA-256 of every file extracted from the commit (all files here except this README, `LICENSE-CODE.txt`, `THIRD_PARTY_NOTICES.txt` and the manifest itself).

## Licence

- Documents and data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Code (`banc/`, `simulation/`, `gel/`): MIT License, see `LICENSE-CODE.txt`.
- Files derived from the public benchmarks remain under their own MIT licenses, reproduced in `THIRD_PARTY_NOTICES.txt`:
{tiers}

## Résumé en français

Préenregistrement, daté du {date_fr(date)} : plan d'expérience figé, règle, moteur de rejeu, instrument et manifeste du gel, à l'étiquette git `{etiquette}`, avant toute donnée de confirmation. Le reste du dépôt git est engagé par ses empreintes. Les fichiers tirés de τ-bench et de WorkBench gardent leur licence MIT d'origine.
"""


def date_fr(date: str) -> str:
    return date.replace("November", "novembre")


def mentions_tiers() -> str:
    blocs = ["This record contains material derived from two public benchmarks, both under the MIT License. "
             "These files remain under their original licenses, reproduced below; the CC BY 4.0 and MIT terms of this "
             "record do not apply to them.\n"]
    for banc, depot, commit, licence, fichiers in TIERS:
        blocs.append(f"## {banc} ({depot}, commit {commit})\n\nDerived files in this record:\n"
                     + "\n".join(f"- {f}" for f in fichiers) + "\n\n" + licence.read_text(encoding="utf-8").strip() + "\n")
    return "\n".join(blocs)


def construire(commit: str, dossier: Path, date: str, type_depot: str = "anteriorite", etiquette: str = "") -> tuple:
    commit = git("rev-parse", commit).strip()
    arbre = git("rev-parse", f"{commit}^{{tree}}").strip()
    obj = objets(commit)
    inclus = INCLUS_GEL if type_depot == "gel" else INCLUS_ANTERIORITE
    manquants = [n for n in list(EXCLUS) + inclus if n not in obj]
    if manquants:
        raise SystemExit(f"entrées absentes du commit : {manquants}")
    manifeste_sha, g0 = "", None
    if type_depot == "gel":
        verifier_entrees(obj, inclus)
        absents = [f for f in FICHIERS_GEL if subprocess.run(["git", "-C", str(RACINE), "cat-file", "-e",
                                                               f"{commit}:{f}"]).returncode]
        if absents:
            raise SystemExit(f"fichiers du gel absents du commit : {absents} (gel/manifeste.py --ecrire d'abord)")
        if not etiquette or git("rev-parse", f"{etiquette}^{{commit}}").strip() != commit:
            raise SystemExit(f"l'étiquette {etiquette!r} ne désigne pas le commit {commit}")
        manifeste_sha = hashlib.sha256(subprocess.run(
            ["git", "-C", str(RACINE), "show", f"{commit}:gel/MANIFESTE_SHA256.txt"],
            capture_output=True, check=True).stdout).hexdigest()
        config = subprocess.run(["git", "-C", str(RACINE), "show", f"{commit}:simulation/rejeu/config_rejeu.json"],
                                capture_output=True, check=False).stdout
        g0 = json.loads(config)["graines"]["G0"] if config else None
        if g0 is None:
            raise SystemExit("G0 n'est pas tirée dans ce commit")
    contenu = dossier / "contenu"
    if contenu.exists():
        shutil.rmtree(contenu)
    contenu.mkdir(parents=True)
    archive = subprocess.run(["git", "-C", str(RACINE), "archive", "--format=tar", commit, *inclus],
                             capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(contenu)], input=archive, check=True)
    for _, _, _, _, fichiers in TIERS:
        for f in fichiers:
            if not (contenu / f).exists():
                raise SystemExit(f"fichier tiers annoncé mais absent : {f}")
    extraits = sorted(p for p in contenu.rglob("*") if p.is_file())
    manifeste = "".join(f"{sha256(p)}  {p.relative_to(contenu).as_posix()}\n" for p in extraits)
    (contenu / "MANIFEST_SHA256.txt").write_text(manifeste, encoding="utf-8")
    (contenu / "README_DEPOT.md").write_text(readme(commit, arbre, obj, date, type_depot, etiquette, manifeste_sha, g0),
                                             encoding="utf-8")
    (contenu / "LICENSE-CODE.txt").write_text(MIT, encoding="utf-8")
    (contenu / "THIRD_PARTY_NOTICES.txt").write_text(mentions_tiers(), encoding="utf-8")
    # Zip reproductible (audit du gel, O2) : chaque fichier et dossier du paquet prend la date du commit et des droits
    # fixes, et les fichiers entrent dans le zip dans l'ordre trié, sans entrée de dossier.
    t = int(git("show", "-s", "--format=%ct", commit).strip())
    for chemin in sorted(contenu.rglob("*"), reverse=True) + [contenu]:
        if chemin.is_file():
            chemin.chmod(0o644)
        os.utime(chemin, (t, t))
    zipf = dossier / f"depot_osf_{dossier.name.split('_')[0]}.zip"
    if zipf.exists():
        zipf.unlink()
    liste = "".join(p.relative_to(contenu).as_posix() + "\n" for p in sorted(contenu.rglob("*")) if p.is_file())
    # zip écrit l'heure locale : TZ=UTC rend le zip indépendant du fuseau de la machine (contre-vérification).
    subprocess.run(["zip", "-q", "-X", "-D", str(zipf.resolve()), "-@"], cwd=contenu, input=liste.encode(), check=True,
                   env={**os.environ, "TZ": "UTC"})
    return commit, arbre, len(extraits), zipf, sha256(zipf)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--commit", required=True)
    p.add_argument("--dossier", required=True, help="par exemple depots/2026-11-05_anteriorite")
    p.add_argument("--date", default="5 November 2026")
    p.add_argument("--type", choices=["anteriorite", "gel"], default="anteriorite")
    p.add_argument("--etiquette", default="", help="au gel : l'étiquette git du commit figé")
    a = p.parse_args(argv)
    commit, arbre, n, zipf, h = construire(a.commit, (RACINE / a.dossier).resolve(), a.date, a.type, a.etiquette)
    print(f"commit {commit}\narbre {arbre}\n{n} fichiers extraits\n{zipf} ({zipf.stat().st_size} octets)\nSHA-256 {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
