"""Relecture des 20 fiches de l'audit des tâches sans alerte (plan, 4.5) par des instances de Claude neuves.

Hors du périmètre figé. Une instance `claude -p` par fiche (abonnement, sans clé API, sans les réglages personnels),
modèle noté dans reponses/execution.jsonl. Chaque instance écrit reponses/<id>.csv (en-tête + une ligne) ; `fusionner`
assemble reponses.csv au format de banc/relecture/audit_sans_alerte.py.

    python3 outils/audit_relecture.py lancer    --audit experience/audit_sans_alerte [--paralleles 4] [--modele opus]
    python3 outils/audit_relecture.py fusionner --audit experience/audit_sans_alerte
"""
import argparse
import csv
import io
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CONSIGNE = RACINE / "banc/relecture/CONSIGNE_RELECTURE.md"
COLONNES = ["tache", "defectueuse", "cas", "preuve", "erreurs_invisibles", "ecritures_lues"]

INVITE = """Tu es un relecteur pour une expérience scientifique préenregistrée : audit d'une tâche sans alerte.

1. Lis d'abord la consigne, en entier : {consigne} (la section « Audit d'une tâche sans alerte » est ta tâche ; le reste te donne les définitions, en particulier le motif (a), cas a1 à a4).
2. Puis lis cette fiche, en entier (par morceaux avec offset/limit si elle est longue) : {fiche}

Tu n'ouvres aucun autre fichier, tu ne cherches rien sur le web et tu ne cherches pas à savoir quel modèle a joué.

3. Écris ta réponse dans ce fichier, et nulle part ailleurs : {sortie}
   Première ligne exactement `tache,defectueuse,cas,preuve,erreurs_invisibles,ecritures_lues`, puis une seule ligne CSV pour la fiche (guillemets doubles autour des champs qui contiennent une virgule, des guillemets ou un retour à la ligne ; guillemets internes doublés), au format décrit dans la consigne. `tache` = {id}.

Ta réponse finale tient en une ligne : « fiche écrite » ou la raison d'un échec. Ne résume pas le cas.
"""


def lancer(audit: Path, paralleles: int, modele: str):
    rep = audit / "reponses"
    rep.mkdir(exist_ok=True)
    ids = sorted(p.stem for p in (audit / "fiches").glob("*.md"))

    def un(i):
        sortie = (rep / f"{i}.csv").resolve()
        if sortie.exists():
            return
        invite = INVITE.format(consigne=CONSIGNE, fiche=(audit / "fiches" / f"{i}.md").resolve(), sortie=sortie, id=i)
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        p = subprocess.run(["claude", "-p", invite, "--model", modele, "--setting-sources", "project",
                            "--strict-mcp-config", "--no-session-persistence", "--allowedTools", "Read", "Write",
                            "--output-format", "json"], cwd=str(audit), env=env, capture_output=True, text=True,
                           timeout=3600)
        try:
            res = json.loads(p.stdout)
        except ValueError:
            res = {}
        with open(rep / "execution.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"heure": datetime.now().astimezone().isoformat(timespec="seconds"), "fiche": i,
                                 "ok": sortie.exists(), "code": p.returncode,
                                 "modeles": list((res.get("modelUsage") or {}).keys()),
                                 "equivalent_api_usd": res.get("total_cost_usd")}, ensure_ascii=False) + "\n")

    with ThreadPoolExecutor(paralleles) as ex:
        list(ex.map(un, ids))
    print(f"{sum(1 for i in ids if (rep / f'{i}.csv').exists())} / {len(ids)} fiches rendues")


def fusionner(audit: Path):
    lignes = []
    for f in sorted((audit / "reponses").glob("*.csv")):
        lignes += list(csv.DictReader(io.StringIO(f.read_text(encoding="utf-8"))))
    with open(audit / "reponses.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLONNES)
        w.writeheader()
        for l in lignes:
            w.writerow({k: l.get(k, "") for k in COLONNES})
    print(f"{len(lignes)} lignes dans reponses.csv")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["lancer", "fusionner"])
    p.add_argument("--audit", required=True)
    p.add_argument("--paralleles", type=int, default=4)
    p.add_argument("--modele", default="opus")
    a = p.parse_args()
    d = Path(a.audit).resolve()
    lancer(d, a.paralleles, a.modele) if a.action == "lancer" else fusionner(d)
