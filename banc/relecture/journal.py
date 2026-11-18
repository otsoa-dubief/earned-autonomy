"""Journal de la relecture d'une vague (plan, 4.4 et 4.5 ; relecture C13, P11).

Un fichier par vague, `relecture/journal_relecture.jsonl`, inscrit au manifeste du gel des verdicts. Chaque tirage
(page d'Otsoa, fortes levées, audit) et chaque lot d'alertes relu y laisse une ligne. Un tirage déjà inscrit ne se
refait pas, même dans un autre dossier de sortie ; un lot n'est relu qu'une fois, sauf relance notée pour une sortie
mal formée (`journal_lots.py`).
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

JOURNAL = "journal_relecture.jsonl"


def chemin(relecture) -> Path:
    return Path(relecture) / JOURNAL


def lire(relecture) -> list:
    c = chemin(relecture)
    if not c.is_file():
        return []
    return [json.loads(l) for l in c.read_text(encoding="utf-8").splitlines() if l.strip()]


def noter(relecture, ligne: dict) -> None:
    c = chemin(relecture)
    c.parent.mkdir(parents=True, exist_ok=True)
    with open(c, "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(heure=time.strftime("%Y-%m-%d %H:%M:%S %z"), **ligne), ensure_ascii=False) + "\n")


def sha256(fichier) -> str:
    return hashlib.sha256(Path(fichier).read_bytes()).hexdigest()
