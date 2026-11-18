"""Manifeste du gel (gel/manifeste.py) : dépôt git factice, bancs factices, environnements = l'interpréteur courant."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manifeste as mf  # noqa: E402

RACINE_VRAIE = Path(__file__).resolve().parents[2]


def sh(dossier, *args):
    return subprocess.run(["git", "-C", str(dossier), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout


def ecrire(chemin: Path, texte: str):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")


ANCRE = "   - une graine maîtresse G0, tirée par `secrets.randbits(64)` au gel et écrite dans le plan figé ;\n"
PLAN_AVANT = "4. **Graines** :\n" + ANCRE + "   - des sous-graines ;\n"


def plan_avec(g0):
    return "4. **Graines** :\n" + ANCRE + f"     - valeur tirée au gel : G0 = {g0}\n" + "   - des sous-graines ;\n"


@pytest.fixture
def depot(tmp_path, monkeypatch):
    r = tmp_path / "depot"
    for nom, texte in {"REGLE.md": "règle\n", "PLAN_EXPERIENCE.md": PLAN_AVANT, "SUIVI.md": "suivi\n",
                       "JOURNAL_CHANGEMENTS.md": "journal\n", "CADRE.md": "hors périmètre\n",
                       "donnees/scelle.md": "secret\n", "banc/a.py": "A = 1\n", "banc/tirage/paires.json": "{}\n",
                       "gel/manifeste.py": "# copie\n", ".gitignore": "externe/\n",
                       mf.CONFIG_REJEU: '{\n "graines": {\n  "G0": null,\n  "G0_developpement": 20261105\n },\n'
                                        ' "liste": [\n  "G0"\n ]\n}\n'}.items():
        ecrire(r / nom, texte)
    for b in ("tau2-bench", "WorkBench"):
        ecrire(r / "externe" / b / "f.txt", b)
        sh(r / "externe" / b, "init", "-q")
        sh(r / "externe" / b, "add", ".")
        sh(r / "externe" / b, "commit", "-qm", "banc")
    ecrire(r / "externe" / "workbench-run" / "data.csv", "x\n")
    sh(r, "init", "-q")
    sh(r, "add", ".")
    sh(r, "commit", "-qm", "départ")
    monkeypatch.setattr(mf, "ENVIRONNEMENTS", {n: sys.executable for n in mf.ENVIRONNEMENTS})
    return r


def preparer(r):
    g0 = mf.tirer_g0(r)
    ecrire(r / "PLAN_EXPERIENCE.md", plan_avec(g0))
    sh(r, "commit", "-qam", "G0")
    return g0


def test_tirer_g0_une_seule_fois(depot):
    g0 = mf.tirer_g0(depot)
    cfg = json.loads((depot / mf.CONFIG_REJEU).read_text())
    assert cfg["graines"] == {"G0": g0, "G0_developpement": 20261105} and cfg["liste"] == ["G0"]
    assert 0 <= g0 < 2 ** 64
    with pytest.raises(mf.GelInvalide, match="qu'une fois"):
        mf.tirer_g0(depot)


def test_prealables_bloquent_le_gel(depot):
    assert any("G0 n'est pas tirée" in p for p in mf.prealables(depot))
    g0 = mf.tirer_g0(depot)
    p = mf.prealables(depot)
    assert any("à commiter" in x and mf.CONFIG_REJEU in x for x in p)
    assert any(f"G0 = {g0} n'est pas écrite" in x for x in p)
    with pytest.raises(mf.GelInvalide, match="gel refusé"):
        mf.ecrire(depot)
    ecrire(depot / "PLAN_EXPERIENCE.md", plan_avec(g0))
    sh(depot, "commit", "-qam", "G0")
    assert mf.prealables(depot) == []
    ecrire(depot / "externe" / "tau2-bench" / "f.txt", "modifié")
    assert mf.prealables(depot) == ["externe/tau2-bench a des modifications locales"]


def test_ecrire_puis_verifier(depot):
    preparer(depot)
    r = mf.ecrire(depot, date="2026-11-18 10:00:00 +0100")
    lignes = (depot / mf.MANIFESTE).read_text().splitlines()
    noms = [l.split("  ", 1)[1] for l in lignes]
    assert all(re.fullmatch(r"[0-9a-f]{64}  \S.*", l) for l in lignes) and r["fichiers"] == len(noms)
    for n in ("REGLE.md", "PLAN_EXPERIENCE.md", "banc/a.py", "banc/tirage/paires.json", mf.CONFIG_REJEU,
              "gel/manifeste.py", mf.GEL, "gel/environnements/simulation.txt", "externe/workbench-run/data.csv"):
        assert n in noms
    assert not any(n.startswith(("donnees", "CADRE", "SUIVI", "JOURNAL")) for n in noms)
    gel = json.loads((depot / mf.GEL).read_text())
    assert set(gel["etat_au_gel"]) == {"JOURNAL_CHANGEMENTS.md", "SUIVI.md", "CADRE.md"} and gel["G0"] == mf.g0_config(depot)
    assert gel["plateforme"]["machine"] and "systeme" in gel["plateforme"]   # C13, P14
    assert gel["environnements"]["simulation"]["python"] == sys.version.split()[0]
    assert subprocess.run(["shasum", "-a", "256", "-c", mf.MANIFESTE], cwd=depot, capture_output=True).returncode == 0
    sh(depot, "add", "gel")
    sh(depot, "commit", "-qm", "gel")
    assert mf.verifier(depot) == [] and mf.main(["--verifier"], racine=depot) == 0
    ecrire(depot / "SUIVI.md", "suite\n")  # les journaux vivants continuent après le gel
    assert mf.verifier(depot) == []
    with pytest.raises(mf.GelInvalide, match="déjà commité"):
        mf.ecrire(depot)


def test_verifier_trouve_les_ecarts(depot):
    preparer(depot)
    mf.ecrire(depot)
    sh(depot, "add", "gel")
    sh(depot, "commit", "-qm", "gel")
    ecrire(depot / "banc" / "a.py", "A = 2\n")
    ecrire(depot / "banc" / "b.py", "B = 1\n")
    sh(depot, "add", "banc/b.py")
    ecrire(depot / "externe" / "WorkBench" / "g.txt", "nouveau")
    sh(depot / "externe" / "WorkBench", "add", ".")
    sh(depot / "externe" / "WorkBench", "commit", "-qm", "suite")
    ecrire(depot / "gel" / "environnements" / "simulation.txt", "python 0.0\n")
    e = mf.verifier(depot)
    assert "modifié ou absent : banc/a.py" in e and "nouveau, hors gel : banc/b.py" in e
    assert "modifié ou absent : gel/environnements/simulation.txt" in e
    assert any(x.startswith("externe/WorkBench : commit") for x in e)
    assert any(x.startswith("environnement simulation") for x in e)
    assert mf.main(["--verifier"], racine=depot) == 1


def test_verifier_trouve_les_fichiers_ajoutes_hors_git(depot):
    """Revue « ultra » du 06/11, constat 1 : un fichier ajouté aux entrées des bancs (externe/workbench-run/, hors git)
    ou un fichier non suivi dans le périmètre (un module importable) fait échouer la vérification."""
    preparer(depot)
    mf.ecrire(depot)
    sh(depot, "add", "gel")
    sh(depot, "commit", "-qm", "gel")
    assert mf.verifier(depot) == []
    ecrire(depot / "externe" / "workbench-run" / "nouveau.csv", "y\n")
    ecrire(depot / "banc" / "module_non_suivi.py", "X = 1\n")
    e = mf.verifier(depot)
    assert "nouveau, hors gel : externe/workbench-run/nouveau.csv" in e
    assert "nouveau, non suivi par git : banc/module_non_suivi.py" in e
    assert mf.main(["--verifier"], racine=depot) == 1


def test_donnees_jamais_lues(depot):
    with pytest.raises(mf.GelInvalide, match="jamais lu"):
        mf.sha256(depot / "donnees" / "scelle.md")


def test_apercu_du_vrai_depot():
    r = mf.apercu(RACINE_VRAIE)
    assert {"REGLE.md", "PLAN_EXPERIENCE.md", "banc/tirage/paires.json", "banc/tirage/tirage_public.py",
            mf.CONFIG_REJEU} <= set(r["fichiers"])
    assert not any(n.startswith("donnees") for n in r["fichiers"])


def test_fichiers_d_entree_des_bancs_et_verrou(depot):
    """C13, P13 et P14 : les fichiers de tâches, de données et d'outils des bancs sont figés par leur SHA-256 ; un
    verrou vide de workbench-run ne l'est pas ; un fichier non suivi dans un banc empêche le gel."""
    t = depot / "externe" / "tau2-bench"
    ecrire(t / "data" / "tau2" / "domains" / "airline" / "tasks.json", "[]\n")
    ecrire(t / "data" / "tau2" / "results" / "r.json", "{}\n")          # sorties publiées : jamais figées
    sh(t, "add", ".")
    sh(t, "commit", "-qm", "domaines")
    ecrire(depot / "externe" / "workbench-run" / "data" / "results.verrou", "")
    preparer(depot)
    mf.ecrire(depot)
    noms = [l.split("  ", 1)[1] for l in (depot / mf.MANIFESTE).read_text().splitlines()]
    assert "externe/tau2-bench/data/tau2/domains/airline/tasks.json" in noms
    assert not any("results" in n for n in noms if n.startswith("externe/tau2-bench"))
    assert "externe/workbench-run/data/results.verrou" not in noms
    sh(depot, "add", "gel")
    sh(depot, "commit", "-qm", "gel")
    ecrire(t / "data" / "tau2" / "domains" / "airline" / "tasks.json", "[1]\n")
    e = mf.verifier(depot)
    assert "modifié ou absent : externe/tau2-bench/data/tau2/domains/airline/tasks.json" in e
    ecrire(depot / "externe" / "WorkBench" / "nouveau.txt", "x")
    assert any("WorkBench : modifications locales" in x for x in mf.verifier(depot))


@pytest.mark.parametrize("plan", [
    lambda g0: PLAN_AVANT + f"Note : {g0}\n",                                     # le nombre ailleurs ne suffit pas
    lambda g0: f"     - valeur tirée au gel : G0 = {g0}\n" + PLAN_AVANT,          # avant la puce de la graine
    lambda g0: plan_avec(g0) + f"     - valeur tirée au gel : G0 = {g0}\n",       # écrite deux fois
    lambda g0: plan_avec(g0 + 1),                                                  # autre valeur
])
def test_g0_a_l_endroit_prevu_seulement(depot, plan):
    g0 = mf.tirer_g0(depot)
    ecrire(depot / "PLAN_EXPERIENCE.md", plan(g0))
    sh(depot, "commit", "-qam", "G0")
    assert any("n'est pas écrite" in x for x in mf.prealables(depot))
