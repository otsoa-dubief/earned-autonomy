"""Paires de tâches pour équilibrer les types d'action rares entre calibration et confirmation (plan, 3.4 et section 8).

Calcul figé, sans hasard, fait avant le gel sur les seules actions attendues des tâches, jamais sur des résultats
d'agents :
1. pour chaque tâche de la réserve, on compte ses écritures attendues par type (banc/table_outils.json ; lectures,
   doutes et préparations exclus, comme les outils absents de la table) ;
2. dans chaque strate (un environnement τ-bench, ou un fichier WorkBench), les types sont rangés du plus rare au plus
   courant : nombre de tâches qui en portent, puis nom ;
3. les tâches sont triées sur ce profil, le type le plus rare d'abord (le plus d'écritures de ce type en tête), puis
   sur le nombre total d'écritures attendues, puis sur l'identifiant ;
4. on apparie les voisines dans cet ordre : 1re et 2e, 3e et 4e, etc. Avec un effectif impair, la dernière reste
   seule ; elle ira à la confirmation.

Le tirage public départage ensuite chaque paire (tirage_public.partager) : chaque paire envoie une tâche dans chaque
moitié, donc les tâches qui portent un type rare se répartissent presque à égalité.

Usage : paires.py [--reserve banc/tirage/reserve.json] [--sortie banc/tirage/paires.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[1]
sys.path.insert(0, str(RACINE / "banc"))
sys.path.insert(0, str(ICI))
from verdicts import charger_taches_tau2, charger_taches_workbench  # noqa: E402
import tirage_public  # noqa: E402

TAU = {"aviation": "airline", "commerce": "retail", "banque": "banking_knowledge"}
EXCLUS = {"lecture", "doute", "préparation"}
TABLE = RACINE / "banc" / "table_outils.json"
EXTERNE = RACINE / "externe"
VERSION = "autonomie-meritee/paires/v1"


def carte_types(table: dict) -> dict:
    """{(domaine, outil): type} pour τ-bench ; {('workbench', outil): type} pour WorkBench."""
    carte = {}
    for o in table["outils"]:
        cle = ("workbench", o["outil"]) if o["banc"] == "workbench" else (o["domaine"], o["outil"])
        carte[cle] = o["type"]
    return carte


def _profil(attendues: list, domaine: str, carte: dict) -> Counter:
    types = (carte.get((domaine, a.nom)) for a in attendues)
    return Counter(t for t in types if t is not None and t not in EXCLUS)


def profils(reserve: dict, externe: Path = EXTERNE, table: dict | None = None) -> dict:
    """{strate: {identifiant: Counter(type -> écritures attendues)}}, sur les strates de tirage_public."""
    carte = carte_types(table or json.loads(TABLE.read_text(encoding="utf-8")))
    par_tache = {}
    for env, dom in TAU.items():
        taches = charger_taches_tau2(externe / "tau2-bench", dom)
        for i in reserve.get(env, []):
            par_tache[(env, i)] = _profil(taches[i], dom, carte)
    taches_wb = charger_taches_workbench(externe / "WorkBench")
    for i in reserve.get("WorkBench", []):
        par_tache[("WorkBench", i)] = _profil(taches_wb[i], "workbench", carte)
    sortie = {}
    for s, ids in tirage_public.strates(reserve).items():
        env = "WorkBench" if s.startswith("WorkBench:") else s
        sortie[s] = {i: par_tache[(env, i)] for i in ids}
    return sortie


def _cle_identifiant(ident: str) -> tuple:
    morceaux = ident.split(":")
    return tuple((0, int(m), "") if m.isdigit() else (1, 0, m) for m in morceaux)


def apparier(profils_strate: dict) -> list:
    """Paires de tâches voisines dans l'ordre du profil (types rares d'abord) ; une tâche au plus reste seule."""
    presence = Counter(t for p in profils_strate.values() for t, n in p.items() if n > 0)
    rarete = sorted(presence, key=lambda t: (presence[t], t))

    def cle(i):
        p = profils_strate[i]
        return tuple(-p[t] for t in rarete), -sum(p.values()), _cle_identifiant(i)

    ordre = sorted(profils_strate, key=cle)
    return [[ordre[k], ordre[k + 1]] for k in range(0, len(ordre) - 1, 2)]


def construire(reserve: dict, externe: Path = EXTERNE, chemin_table: Path = TABLE,
               chemin_reserve: Path | None = None) -> dict:
    table = json.loads(chemin_table.read_text(encoding="utf-8"))
    tous = profils(reserve, externe, table)
    paires = {s: apparier(p) for s, p in tous.items()}
    paires["_meta"] = {
        "version": VERSION,
        "empreinte_table_outils": hashlib.sha256(chemin_table.read_bytes()).hexdigest(),
        "empreinte_reserve": hashlib.sha256(chemin_reserve.read_bytes()).hexdigest() if chemin_reserve else None,
        "regle": "profil des écritures attendues par type, types rares d'abord ; voisines appariées ; une seule tâche seule au plus par strate",
    }
    return paires


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reserve", type=Path, default=tirage_public.RESERVE)
    p.add_argument("--sortie", type=Path, default=ICI / "paires.json")
    a = p.parse_args(argv)
    reserve = json.loads(a.reserve.read_text(encoding="utf-8"))
    paires = construire(reserve, chemin_reserve=a.reserve)
    a.sortie.write_text(json.dumps(paires, indent=1, ensure_ascii=False), encoding="utf-8")
    seules = {s: len(ids) - 2 * len(paires[s]) for s, ids in tirage_public.strates(reserve).items()}
    print(f"{sum(len(v) for k, v in paires.items() if k != '_meta')} paires dans {len(seules)} strates ; "
          f"tâches seules : {sum(seules.values())}")
    print(f"SHA-256 {a.sortie.name} : {hashlib.sha256(a.sortie.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
