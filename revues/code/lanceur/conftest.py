"""Reproductions de la revue du lanceur (2026-11-06). Rend importables banc/ et les aides de banc/tests/test_lanceur.py."""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, "..", "..", ".."))
for d in (os.path.join(RACINE, "banc"), os.path.join(RACINE, "banc", "tests")):
    if d not in sys.path:
        sys.path.insert(0, d)
