"""Relecture des alertes d'une vague par des instances de Claude au contexte vierge (plan, 4.3 ; journal_lots.py).

Hors du périmètre figé. Reprend l'invite de la vague 1 mot pour mot, avec les chemins de la vague.
Chaque lot est ouvert au journal (journal_lots.py ouvrir), relu par un `claude -p` neuf (abonnement, pas de clé API,
sans les réglages ni les instructions personnelles de l'utilisateur), vérifié par decisions.py, puis fermé. Une
tentative sans sortie valide (limite d'usage, sortie mal formée) est relancée, et la raison est notée à la fermeture.
Le modèle et l'heure de chaque tentative vont dans lots/execution.jsonl.

    python3 outils/relecture_lots.py composer --relecture <dossier>
    python3 outils/relecture_lots.py lancer   --relecture <dossier> [--paralleles 6] [--modele opus]
    python3 outils/relecture_lots.py fusionner --relecture <dossier>
    python3 outils/relecture_lots.py etat     --relecture <dossier>
"""
import argparse
import csv
import io
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PY = RACINE / "simulation/.venv/bin/python"
JOURNAL_LOTS = RACINE / "banc/relecture/journal_lots.py"
DECISIONS = RACINE / "banc/relecture/decisions.py"
CONSIGNE = RACINE / "banc/relecture/CONSIGNE_RELECTURE.md"
TAILLE_MAX = 120_000   # octets de fiches par lot ; une fiche plus grosse forme un lot à elle seule
FICHES_MAX = 15
ATTENTE_LIMITE = 900   # secondes d'attente après une limite d'usage
verrou = threading.Lock()

INVITE = """Tu es un relecteur d'alertes pour une expérience scientifique préenregistrée. Lot {n}.

1. Lis d'abord la consigne, en entier : {consigne}
2. Puis lis chacune de ces fiches, en entier (lis-les par morceaux avec offset/limit si elles sont longues) :
{fiches}

Tu n'ouvres aucun autre fichier, tu ne cherches rien sur le web, tu ne compares pas les fiches entre elles et tu ne fais aucun décompte. Tu ne cherches pas à savoir quel modèle a joué.

3. Écris ta sortie dans ce fichier, et nulle part ailleurs : {sortie}
   Format exact de la consigne : première ligne `alerte_id,decision,motif,justification,preuve`, puis une ligne CSV par fiche (guillemets doubles autour des champs qui contiennent une virgule, des guillemets ou un retour à la ligne ; guillemets internes doublés). `alerte_id` = l'identifiant opaque de la fiche, recopié tel quel. `decision` = confirmée ou levée. Dans le doute, confirmée.
4. Vérifie ton fichier avec : {py} {decisions} {sortie}
   Corrige-le s'il est refusé.

Ta réponse finale tient en une ligne : « lot {n} écrit, <nombre de lignes> lignes, format valide » ou la raison d'un échec. Ne résume aucun cas, ne donne aucune décision dans ta réponse.
"""


def maintenant():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def nom(n):
    return f"{n:02d}" if n < 100 else str(n)


def composer(rel: Path):
    lots_dir = rel / "lots"
    if (lots_dir / "composition.json").exists():
        sys.exit("composition déjà écrite : on ne recompose pas une relecture commencée")
    alertes = json.loads((rel / "alertes.json").read_text(encoding="utf-8"))
    ids = sorted(a["id"] for a in alertes)
    taille = {i: (rel / "fiches/claude" / f"{i}.md").stat().st_size for i in ids}
    lots, cour, t = [], [], 0
    for i in ids:  # ordre fixe (identifiants opaques triés), découpage par taille
        if cour and (t + taille[i] > TAILLE_MAX or len(cour) >= FICHES_MAX):
            lots.append(cour)
            cour, t = [], 0
        cour.append(i)
        t += taille[i]
    if cour:
        lots.append(cour)
    lots_dir.mkdir(exist_ok=True)
    (lots_dir / "composition.json").write_text(json.dumps(lots, indent=1), encoding="utf-8")
    for n, lot in enumerate(lots, 1):
        fiches = "\n".join(f"- {rel.resolve() / 'fiches/claude' / f'{i}.md'}" for i in lot)
        sortie = (lots_dir / f"lot_{nom(n)}.csv").resolve()
        (lots_dir / f"invite_{nom(n)}.txt").write_text(
            INVITE.format(n=n, consigne=CONSIGNE, fiches=fiches, sortie=sortie, py=PY, decisions=DECISIONS),
            encoding="utf-8")
    print(f"{len(ids)} alertes, {len(lots)} lots")


def journal_lots(*args):
    return subprocess.run([str(PY), str(JOURNAL_LOTS), *args], capture_output=True, text=True)


def etat_journal(rel: Path):
    ouverts, fermes = set(), set()
    f = rel / "journal_relecture.jsonl"
    if f.exists():
        for l in f.read_text(encoding="utf-8").splitlines():
            r = json.loads(l)
            if r.get("type") == "lot":
                (ouverts if r["etape"] == "ouverture" else fermes).add(int(r["lot"]))
    return ouverts, fermes


def valide(sortie: Path, attendus: list) -> bool:
    if not sortie.exists():
        return False
    if subprocess.run([str(PY), str(DECISIONS), str(sortie)], capture_output=True).returncode != 0:
        return False
    lignes = list(csv.DictReader(io.StringIO(sortie.read_text(encoding="utf-8"))))
    return sorted(l["alerte_id"] for l in lignes) == sorted(attendus)


def noter(rel, **d):
    with verrou, open(rel / "lots/execution.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"heure": maintenant(), **d}, ensure_ascii=False) + "\n")


def relire(rel: Path, n: int, lot: list, modele: str, ouverts: set):
    lots_dir = rel / "lots"
    invite = lots_dir / f"invite_{nom(n)}.txt"
    sortie = (lots_dir / f"lot_{nom(n)}.csv").resolve()
    if n not in ouverts:
        r = journal_lots("ouvrir", "--relecture", str(rel), "--lot", str(n), "--alertes", ",".join(lot),
                         "--invite", str(invite))
        if r.returncode:
            noter(rel, lot=n, erreur="ouverture refusée", detail=r.stderr[-300:])
            return
    raisons, essai = [], 0
    while True:
        essai += 1
        if sortie.exists() and not valide(sortie, lot):
            sortie.unlink()  # sortie mal formée d'une tentative précédente : relance notée
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        t0 = time.time()
        p = subprocess.run(
            ["claude", "-p", invite.read_text(encoding="utf-8"), "--model", modele,
             "--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence",
             "--allowedTools", "Read", "Write", "Edit", f"Bash({PY} {DECISIONS}:*)",
             "--output-format", "json"],
            cwd=str(rel), env=env, capture_output=True, text=True, timeout=3600)
        try:
            res = json.loads(p.stdout)
        except ValueError:
            res = {}
        modeles = list((res.get("modelUsage") or {}).keys())
        ok = valide(sortie, lot)
        noter(rel, lot=n, essai=essai, ok=ok, duree_s=round(time.time() - t0), code=p.returncode,
              modeles=modeles, equivalent_api_usd=res.get("total_cost_usd"),
              erreur=None if ok else (res.get("result") or p.stderr or "")[-300:])
        if ok:
            break
        texte = ((res.get("result") or "") + p.stderr).lower()
        limite = any(m in texte for m in ("limit", "usage", "quota", "rate", "overloaded", "529", "429"))
        raisons.append("limite d'usage ou surcharge, sans sortie valide" if limite else "sortie absente ou mal formée")
        if essai >= 6 and not limite:
            noter(rel, lot=n, erreur="abandon après 6 essais : lot laissé ouvert, à traiter à la main")
            return
        time.sleep(ATTENTE_LIMITE if limite else 30)
    args = ["fermer", "--relecture", str(rel), "--lot", str(n), "--sortie", str(sortie)]
    if raisons:
        args += ["--relance", " ; ".join(raisons)]
    r = journal_lots(*args)
    if r.returncode:
        noter(rel, lot=n, erreur="fermeture refusée", detail=r.stderr[-300:])


def lancer(rel: Path, paralleles: int, modele: str):
    lots = json.loads((rel / "lots/composition.json").read_text(encoding="utf-8"))
    ouverts, fermes = etat_journal(rel)
    a_faire = [(n, lot) for n, lot in enumerate(lots, 1) if n not in fermes]
    print(f"{len(a_faire)} lots à relire sur {len(lots)}, {paralleles} en parallèle, modèle {modele}", flush=True)
    with ThreadPoolExecutor(paralleles) as ex:
        for f in [ex.submit(relire, rel, n, lot, modele, ouverts) for n, lot in a_faire]:
            f.result()


def fusionner(rel: Path):
    lots = json.loads((rel / "lots/composition.json").read_text(encoding="utf-8"))
    sortie = rel / "decisions.csv"
    lignes = []
    for n in range(1, len(lots) + 1):
        lignes += list(csv.DictReader(io.StringIO((rel / "lots" / f"lot_{nom(n)}.csv").read_text(encoding="utf-8"))))
    with open(sortie, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["alerte_id", "decision", "motif", "justification", "preuve"])
        w.writeheader()
        for l in lignes:
            w.writerow({k: l.get(k, "") for k in w.fieldnames})
    v = subprocess.run([str(PY), str(DECISIONS), str(sortie)], capture_output=True, text=True)
    j = journal_lots("verifier", "--relecture", str(rel), "--decisions", str(sortie))
    print(f"{len(lignes)} lignes ; decisions.py code {v.returncode} ; verifier code {j.returncode} {j.stdout[-200:]}{j.stderr[-200:]}")


def etat(rel: Path):
    lots = json.loads((rel / "lots/composition.json").read_text(encoding="utf-8"))
    ouverts, fermes = etat_journal(rel)
    print(f"lots fermés {len(fermes)} / {len(lots)} ; ouverts non fermés {len(ouverts - fermes)}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["composer", "lancer", "fusionner", "etat"])
    p.add_argument("--relecture", required=True)
    p.add_argument("--paralleles", type=int, default=6)
    p.add_argument("--modele", default="opus")
    a = p.parse_args()
    rel = Path(a.relecture).resolve()
    {"composer": lambda: composer(rel), "lancer": lambda: lancer(rel, a.paralleles, a.modele),
     "fusionner": lambda: fusionner(rel), "etat": lambda: etat(rel)}[a.action]()
