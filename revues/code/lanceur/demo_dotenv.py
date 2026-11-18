"""R10 : un `.env` placé au-dessus de externe/tau2-bench est chargé par τ-bench, et verifier_pas_de_dotenv ne le voit pas.

τ-bench appelle `load_dotenv()` sans chemin à l'import (src/tau2/utils/utils.py, l. 14). python-dotenv cherche alors
le fichier en remontant depuis le dossier du module appelant jusqu'à la racine du disque. Le lanceur ne contrôle que
externe/tau2-bench/.env et externe/workbench-run/.env (pilote_etape1.verifier_pas_de_dotenv, appelé par lanceur.main).

Démonstration dans un dossier temporaire, avec le python-dotenv du venv de τ-bench, sans rien écrire dans le dépôt :

    cd ROOT
    env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY \
        externe/tau2-bench/.venv/bin/python revues/code/lanceur/demo_dotenv.py
"""
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RACINE / "banc"))
import pilote_etape1 as pe  # noqa: E402
from dotenv.main import _walk_to_root  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    externe = Path(tmp) / "externe"
    module = externe / "tau2-bench" / "src" / "tau2" / "utils" / "utils.py"
    module.parent.mkdir(parents=True)
    (externe / "workbench-run").mkdir()
    module.write_text("from dotenv import load_dotenv\nload_dotenv()\n")
    (externe / ".env").write_text("REVUE_VARIABLE_DOTENV=chargee\n")  # au-dessus du banc, comme externe/.env
    pe.verifier_pas_de_dotenv(externe / "tau2-bench", externe / "workbench-run")
    print("verifier_pas_de_dotenv : aucun refus")
    spec = importlib.util.spec_from_file_location("utils_factice", module)
    spec.loader.exec_module(importlib.util.module_from_spec(spec))
    print("variable chargée par load_dotenv() :", os.environ.get("REVUE_VARIABLE_DOTENV"))

reel = RACINE / "externe" / "tau2-bench" / "src" / "tau2" / "utils"
dossiers = list(_walk_to_root(str(reel)))
print("dossiers fouillés pour le vrai τ-bench :", len(dossiers), "; contrôlés par le lanceur : 1 (externe/tau2-bench)")
for d in dossiers:
    print(("  .env PRÉSENT : " if (Path(d) / ".env").exists() else "  ") + d)
