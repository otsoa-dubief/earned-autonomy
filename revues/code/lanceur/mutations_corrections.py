"""Contre-vérification : chaque test de non-régression (banc/tests/test_lanceur_revue.py) détecte-t-il le retour du
défaut qu'il couvre ? Pour chaque correction, on défait la correction dans une COPIE de banc/lanceur.py (dossier
temporaire ; aucun fichier du dépôt n'est touché), on charge cette copie à la place du lanceur, et on relance les tests
du constat. « tuée » : au moins un test échoue (le test voit le défaut) ; « survivante » : tous passent.

    cd ROOT
    env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY \
        simulation/.venv/bin/python revues/code/lanceur/mutations_corrections.py
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[3]
BANC = RACINE / "banc"
SOURCE = (BANC / "lanceur.py").read_text(encoding="utf-8")

# (nom, constat, ancien texte, texte qui défait la correction, filtre -k des tests du constat)
MUTATIONS = [
    ("refus d'un second dossier réel", 1, "        if existants:  # constat 1", "        if False:  # constat 1", "test_c1_"),
    ("verrou : processus vivant ignoré", 1, "            if pid_vivant(pid):", "            if False:", "test_c1_"),
    ("WorkBench : arrêt non revérifié", 2, "        if compta is not None and compta.doit_arreter():",
     "        if False:", "test_c2_"),
    ("marqueur vague2.json non lu", 3,
     '        if vague == 1 and (rep["dossier"] / NOM_MARQUEUR_VAGUE2).is_file():  # constat 3', "        if False:", "test_c3_"),
    ("marqueur écrit quel que soit le mode", 3,
     '        if a.vague == 2 and prep["v1"]["plan"].get("mode") == plan["mode"]:', "        if a.vague == 2:", "test_c3_"),
    ("appels faits : seulement si error vide", 4, 'appels_faits=res["delai_depasse"] or ecrite,',
     'appels_faits=res["delai_depasse"] or (res["trace"] and not res["terminaison"]),', "test_c4_"),
    ("pas de majorant tiré des traces", 4, "    return cout_majorant(appels, modele) if appels else None",
     "    return None", "test_c4_"),
    ("exception d'outil = échec technique", 5, "        return ARRETEE, ARRET_EXCEPTION_OUTIL, None",
     '        return ECHEC, None, f"WorkBench : {term[:300]}"', "test_c5_"),
    ("pas d'arrêt sur la série d'exceptions", 5, "SERIE_EXCEPTIONS_OUTIL_MAX = 3", "SERIE_EXCEPTIONS_OUTIL_MAX = 99",
     "test_c5_"),
    ("« LLM call exceeded » hors des erreurs d'API", 5, ', "LLM call exceeded")', ")", "test_c5_"),
    ("τ-bench sans --max-retries 0", 6, '["--timeout", str(DELAI_PARTIE_S), "--max-retries", "0"]',
     '["--timeout", str(DELAI_PARTIE_S)]', "test_c6_"),
    ("contexte τ-bench = échec technique", 6,
     '    if term == "infrastructure_error" and r.get("type_erreur") == TYPE_ERREUR_CONTEXTE:\n'
     "        return ARRETEE, ARRET_CONTEXTE, None\n", "", "test_c6_"),
    ("référence de nom commune aux bancs", 7, "            d = f\"{banc}:{court(dem) or '?'}\"",
     '            d = court(dem) or "?"', "test_c7_"),
    ("filet : arrêtée même avec une trace", 8, '    if r.get("delai_depasse") and not r.get("trace"):',
     '    if r.get("delai_depasse"):', "test_c8_"),
    ("contexte WorkBench gardé", 9, "    if term and term != WB_MESSAGE_ARRET and not term.startswith(WB_ERREURS_API):",
     "    if term and term not in (WB_MESSAGE_ARRET, WB_MESSAGE_CONTEXTE) and not term.startswith(WB_ERREURS_API):",
     "test_c9_"),
    ("results.json n'est plus une preuve de départ", 10, "        if reel and (present or de_results or results_existe):",
     "        if reel and (present or de_results):", "test_c10_"),
    ("reprise sans montant retenu", 11,
     "        if manquants:  # constats 10, 11 et 13", "        if False:  # constats 10, 11 et 13", "test_c11_"),
    ("montant retenu hors du cumul", 11, "            deja += usd\n", "            pass\n", "test_c11_"),
    ("vague 2 malgré un coût inconnu en vague 1", 11, "        if inconnus_v1:", "        if False:", "test_c11_"),
    ("enfants sans PYTHON_DOTENV_DISABLED", 12, '    env["PYTHON_DOTENV_DISABLED"] = "1"', "    pass", "test_c12_"),
    ("orphelines illisibles non examinées d'avance", 13,
     "couts_inconnus_en_suspens(rep[\"lignes\"]) + orphelines_illisibles(rep[\"dossier\"], rep[\"orphelines\"])",
     'couts_inconnus_en_suspens(rep["lignes"])', "test_c13_"),
]

LANCEUR_TEST = """import importlib.util, sys
spec = importlib.util.spec_from_file_location("lanceur", sys.argv[1])
m = importlib.util.module_from_spec(spec)
sys.modules["lanceur"] = m
spec.loader.exec_module(m)
import pytest
sys.exit(pytest.main(["-q", "-p", "no:cacheprovider", "--tb=no", "-rf", "-k", sys.argv[2], sys.argv[3]]))
"""


def lancer(source: str, filtre: str) -> tuple:
    with tempfile.TemporaryDirectory() as d:
        copie = Path(d) / "lanceur.py"
        copie.write_text(source.replace("BANC = Path(__file__).resolve().parent", f"BANC = Path({str(BANC)!r})", 1),
                         encoding="utf-8")
        runner = Path(d) / "runner.py"
        runner.write_text(LANCEUR_TEST, encoding="utf-8")
        r = subprocess.run([sys.executable, str(runner), str(copie), filtre, str(BANC / "tests" / "test_lanceur_revue.py")],
                           cwd=str(RACINE), capture_output=True, text=True, env=dict(os.environ))
        derniere = [l for l in r.stdout.splitlines() if " passed" in l or " failed" in l or "error" in l]
        echecs = [l.split("::")[-1].split(" ")[0] for l in r.stdout.splitlines() if l.startswith("FAILED")]
        return r.returncode, (derniere[-1] if derniere else r.stdout[-300:]) + (f" ; échoue : {echecs}" if echecs else "")


rc, res = lancer(SOURCE, "test_c")
print(f"témoin (lanceur corrigé, sans mutation) : {res}")
for nom, constat, ancien, nouveau, filtre in MUTATIONS:
    assert SOURCE.count(ancien) == 1, f"texte introuvable ou ambigu pour la mutation « {nom} »"
    rc, res = lancer(SOURCE.replace(ancien, nouveau, 1), filtre)
    print(f"constat {constat:>2} | {nom:<48} | {'tuée' if rc else 'SURVIVANTE'} | {res}")
