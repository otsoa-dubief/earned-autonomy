"""Fige les définitions d'outils exactement telles que l'agent les reçoit, banc par banc.

τ-bench 2.0 ne les enregistre pas dans ses résultats (runner/helpers.py appelle get_environment_info avec
include_tool_info=False, en dur) ; WorkBench non plus. Ce script se lance dans l'environnement Python du banc, sans
clé ni appel réseau, et écrit un fichier par environnement dans banc/outils_agent/ avec une empreinte SHA-256.
Au lancement de l'expérience, on le relance et on compare les empreintes : toute différence arrête tout.

    cd externe/tau2-bench && env -u ANTHROPIC_API_KEY .venv/bin/python ../../banc/outils_agent.py --banc tau2
    cd externe/WorkBench && env -u ANTHROPIC_API_KEY .venv/bin/python ../../banc/outils_agent.py --banc workbench

Schémas : τ-bench, `tool.openai_schema` de chaque outil de `environment.get_tools()` (llm_utils.py les envoie
ainsi) ; banque avec la recherche `bm25_grep`, comme au pilote. WorkBench, `_sanitized_tool_schemas` sur tous les
outils (`--tool_selection all --structured_outputs`, comme au pilote).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent / "outils_agent"
DOMAINES_TAU2 = {"airline": "aviation", "retail": "commerce", "banking_knowledge": "banque"}
REGLAGES_TAU2 = {"banking_knowledge": {"retrieval_variant": "bm25_grep"}}


def empreinte(outils: list) -> str:
    return hashlib.sha256(json.dumps(outils, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def commit(racine: Path) -> str:
    return subprocess.run(["git", "-C", str(racine), "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


def outils_tau2() -> dict:
    from tau2.registry import registry

    sortie = {}
    for domaine, env in DOMAINES_TAU2.items():
        reglages = REGLAGES_TAU2.get(domaine, {})
        environnement = registry.get_env_constructor(domaine)(**reglages)
        sortie[env] = {"domaine": domaine, "reglages": reglages,
                       "outils": [t.openai_schema for t in environnement.get_tools()]}
    return sortie


def outils_workbench() -> dict:
    from src.evals.agent import _sanitized_tool_schemas
    from src.evals.inference import _TOOLKIT_MAP, get_toolkits

    schemas, _ = _sanitized_tool_schemas(get_toolkits(list(_TOOLKIT_MAP)))
    return {"workbench": {"domaine": "tous", "reglages": {"tool_selection": "all", "structured_outputs": True},
                          "outils": schemas}}


def ecrire(banc: str, par_env: dict, racine: Path, dossier: Path = DOSSIER) -> list:
    dossier.mkdir(exist_ok=True)
    ecrits = []
    for env, d in par_env.items():
        contenu = {"banc": banc, "commit": commit(racine), "environnement": env, **d,
                   "nombre_outils": len(d["outils"]), "empreinte_sha256": empreinte(d["outils"])}
        chemin = dossier / f"{env}.json"
        chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        ecrits.append((chemin, contenu["nombre_outils"], contenu["empreinte_sha256"]))
    return ecrits


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--banc", required=True, choices=("tau2", "workbench"))
    p.add_argument("--dossier", default=str(DOSSIER),
                   help="dossier où écrire (défaut : banc/outils_agent/). Le lanceur (banc/lanceur.py) y passe un dossier "
                        "temporaire, puis compare les empreintes à celles de banc/outils_agent/.")
    a = p.parse_args(argv)
    sys.path.insert(0, str(Path.cwd()))
    par_env = outils_tau2() if a.banc == "tau2" else outils_workbench()
    for chemin, n, h in ecrire(a.banc, par_env, Path.cwd(), Path(a.dossier)):
        print(f"{chemin.name} : {n} outils, empreinte {h[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
