"""Contre-vérification (choix 27) : le majorant WorkBench tiré des traces couvre-t-il le coût réel ?

Sur les 30 parties WorkBench du pilote (pilote/etape2/2026-11-05_07-50-58 : traces `--log_traces` et JSONL d'usage
réel), compare le coût facturé (cv.bilan du JSONL) au majorant du lanceur (lanceur.cout_majorant_workbench), et, appel
par appel, les jetons facturés aux bornes en octets. Lecture seule ; ni verdict ni résultat de tâche n'est lu.

    cd ROOT
    env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY \
        simulation/.venv/bin/python revues/code/lanceur/verif_majorant_workbench_pilote.py
"""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RACINE / "banc"))
import cout_v2 as cv  # noqa: E402
import lanceur as L  # noqa: E402

PILOTE = RACINE / "pilote" / "etape2" / "2026-11-05_07-50-58"
outils = json.loads((L.DOSSIER_OUTILS / "workbench.json").read_text(encoding="utf-8"))["outils"]
lignes, pire = [], None
for d in sorted((PILOTE / "parties").glob("workbench-*")):
    pid = d.name[len("workbench-"):]
    copies = [str(p) for p in d.iterdir()]
    modele = json.loads(next(d.glob("*_meta.json")).read_text())["model_name"]
    appels, _ = L.lire_usage(PILOTE / "usage" / f"{pid}.jsonl")
    reel = cv.bilan(appels)["cout_usd"]
    majorant = L.cout_majorant_workbench(copies, modele, outils)
    etapes = [e for t in json.loads(next(d.glob("*_traces.json")).read_text()) for e in t["steps"]]
    sortie_max = max(a["completion_tokens"] for a in appels)
    borne_sortie = max(L._octets(e.get("llm_output") or "") for e in etapes) + L.MARGE_SORTIE_JETONS if etapes else None
    lignes.append((pid, modele, len(appels), len(etapes), reel, majorant, sortie_max, borne_sortie))
print(f"{'partie':<24} {'appels':>6} {'étapes':>6} {'réel $':>10} {'majorant $':>11} {'rapport':>8} "
      f"{'sortie max (jetons)':>19} {'borne':>6}")
for pid, m, na, ne, reel, maj, smax, bs in lignes:
    print(f"{pid:<24} {na:>6} {ne:>6} {reel:>10.5f} {maj if maj is None else round(maj, 5)!s:>11} "
          f"{'—' if not maj else round(maj / reel, 1)!s:>8} {smax:>19} {bs!s:>6}")
sous = [x for x in lignes if x[5] is None or x[5] < x[4]]
print(f"parties où le majorant est sous le coût réel (ou absent) : {len(sous)} sur {len(lignes)}")
print(f"plus petit rapport majorant / réel : {min(x[5] / x[4] for x in lignes if x[5] and x[4]):.2f}")

print("\nAppel par appel, parties où un appel a produit plus de jetons de sortie que la borne en octets :")
for pid, m, na, ne, reel, maj, smax, bs in lignes:
    if bs is not None and smax > bs:
        d = PILOTE / "parties" / f"workbench-{pid}"
        appels, _ = L.lire_usage(PILOTE / "usage" / f"{pid}.jsonl")
        etapes = [e for t in json.loads(next(d.glob("*_traces.json")).read_text()) for e in t["steps"]]
        print(f"  {pid} : jetons de sortie facturés par appel {[a['completion_tokens'] for a in appels]} ; "
              f"octets de sortie tracés par étape {[L._octets(e.get('llm_output') or '') for e in etapes]} ; "
              f"marge {L.MARGE_SORTIE_JETONS}")
