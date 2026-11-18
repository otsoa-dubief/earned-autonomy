"""Builds the OSF results package (PLAN_SUITE T40; plan 3.4, point 6). Outside the frozen perimeter; copies only.

    python3 outils/construire_depot_resultats.py depots/2026-11-17_resultats

Contents: final replay outputs, exploratory analyses, draw files and draw log, replay log, SHA-256 lists, the note on
the in-memory fix, the identity check of the six tables, the paper (PDF) and a README. Nothing from donnees/,
pilote/, data/ or the wave folders. The zip and the copied files stay out of git; the README, the draw log and the
SHA256SUMS are committed.
"""
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "experience"
FILES = {
    "replay/": sorted((EXP / "rejeu_final").glob("*")),
    "exploratory/": sorted((EXP / "exploratoire").glob("*")),
    "draw/": [EXP / "tirage/impulsion.json", EXP / "tirage/partage.json"],
    "draw/frozen_inputs/": [EXP / "manifeste_verdicts.txt", ROOT / "banc/tirage/tirage_public.py",
                            ROOT / "banc/tirage/paires.json", ROOT / "banc/tirage/reserve.json"],
    "": [EXP / "journal_rejeu_final.jsonl", EXP / "SHA256_sorties_finales.txt", EXP / "rejeu_final_echec_1_SHA256.txt",
         EXP / "NOTE_CORRECTIF_REJEU_FINAL.md", ROOT / "revues/2026-11-17_identite_six_tables.md",
         ROOT / "outils/rejeu_final_correctif.py"],
}
RENAME = {EXP / "rejeu_final.log": "replay_run2_ok.log", EXP / "rejeu_final_echec_1/rejeu_final.log": "replay_run1_failed.log"}
FORBIDDEN = ("donnees", "pilote", "/data/", "vague1", "vague2", "anthropic.env", "scelle")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def journal_tirage() -> str:
    imp = json.loads((EXP / "tirage/impulsion.json").read_text())
    par = json.loads((EXP / "tirage/partage.json").read_text())
    return f"""# Draw log (public calibration / confirmation split)

- Verdict-freeze registration: OSF cusv6, `date_registered` 2026-11-14T08:17:47.424176 UTC (replaces u26kr, withdrawn).
- Designated time (72 hours later): {imp['heure_designee']}.
- Source: NIST Randomness Beacon 2.0, pulse {imp['url'].rsplit('/', 1)[1]} ({imp['url']}), pulse time {imp['heure_impulsion']}.
- Pulse value: `{imp['valeur']}`.
- Manifest of the frozen verdicts: SHA-256 `{par['empreinte_manifeste']}`.
- Seed: `{par['graine']}`; reserve hash `{par['empreinte_reserve']}`; pairs hash `{par['empreinte_paires']}`.
- Draw script: `banc/tirage/tirage_public.py`, SHA-256 `{sha(ROOT / 'banc/tirage/tirage_public.py')}` (frozen; the rule is in the pre-registered plan, section 3.4, and in the README of the verdict-freeze registration cusv6; `banc/tirage/TIRAGE.md` describes the earlier development-set draw).
- `draw/impulsion.json` SHA-256 `{sha(EXP / 'tirage/impulsion.json')}`; `draw/partage.json` SHA-256 `{sha(EXP / 'tirage/partage.json')}`.
- Draw run: recorded by commit ee0df60 (17 November 2026, 10:19:09 +01:00), after the designated time.
- Final replay outputs: see `SHA256SUMS.txt` of this package (authoritative); `SHA256_sorties_finales.txt` is the earlier list written at 13:28 the same day (see README).
- Inputs needed to redo the draw are copied in `draw/frozen_inputs/` (manifest, script, pairs, reserve). From the project repository:
  `python3 banc/tirage/tirage_public.py verifier --dossier experience/tirage --manifeste experience/manifeste_verdicts.txt --en-ligne`
  (answer on 17 November 2026: "tirage vérifié").
"""


README = """# Earned autonomy for AI agents: results of the pre-registered replay

Results deposit (Zenodo record) of the study pre-registered on OSF (priority record 7ju3c, preregistration vycge, verdict freeze cusv6).
Pre-registered label: R4. The paper is not part of this deposit (it may still be revised); it will be posted on OSF
Preprints with a link to this record (Zenodo; OSF no longer accepts research outputs in its registrations).

## How to read

- `replay/`: outputs of the final replay (decision, budget, delegation gap, loads, scenarios, guarantee, stress tests,
  symmetry, task success). `RESULTATS.md` and `decision.csv` are written by the frozen engine, in French. In them,
  "témoin ... battu" and "les trois témoins battus" are the wording of a criterion, not a result: under R4 the
  utility criterion (point 2) is not judged, and no comparator is beaten in the pre-registered sense.
- `exploratory/`: analyses run after the verdict, not pre-registered, dated 17 November 2026; no effect on the label.
- `draw/` and `JOURNAL_TIRAGE.md`: the public draw of the calibration/confirmation split, with the frozen inputs
  needed to redo it.
- `replay_run1_failed.log`, `replay_run2_ok.log`, `journal_rejeu_final.jsonl`: logs of the two runs of the final
  replay. The first run crashed while writing `resistance.csv` (a defect of the frozen code); the second run used
  `rejeu_final_correctif.py`, which replaces that one formatting function in memory and calls the frozen engine with
  the deposited arguments (`NOTE_CORRECTIF_REJEU_FINAL.md`). The label is computed before that function runs, and the
  six tables written by both runs are identical (`revues_2026-11-17_identite_six_tables.md`). The journal records
  two different repository commits (ee0df60, then 1a5b4c3): the second only adds the declaration of the failure and of
  the fix; the frozen code is unchanged (the engine refuses to run otherwise).
- `SHA256SUMS.txt` is authoritative for this package. `SHA256_sorties_finales.txt` is an earlier list written at
  13:28 on 17 November 2026, before `exploratory/RESUME.md` was completed and E, F and G were added; it does not match
  the current `RESUME.md`. `rejeu_final_echec_1_SHA256.txt` lists the partial outputs of the failed run.

## Exact command of the final replay (as deposited in cusv6; ROOT = repository root)

    cd ROOT/simulation; .venv/bin/python -m rejeu.bout_en_bout --experience \\
      --dossier ROOT/experience/vague1/2026-11-10_06-19-06 --dossier ROOT/experience/vague2/2026-11-10_19-53-13 \\
      --partage ROOT/experience/tirage/partage.json \\
      --vague 1=[wave-1 decisions.csv, alertes.json, accord.json] --vague 2=[same for wave 2] \\
      --retirees ROOT/experience/audit_sans_alerte/taches_retirees_audit.json \\
      --oppositions ROOT/experience/retraits_motif_a/oppositions_motif_a.json \\
      --manifeste-verdicts ROOT/experience/manifeste_verdicts.txt \\
      --sortie ROOT/experience/rejeu_final --processus 12

It was run through `rejeu_final_correctif.py` with exactly these arguments. The wave folders are covered by the
manifest (`draw/frozen_inputs/manifeste_verdicts.txt`) and published with the project repository.

## Notes

Most outputs are in French (column names and engine wording); the paper gives their English reading. Some files
(`meta.json`, `journal_rejeu_final.jsonl`, logs) contain the author's local paths; they carry no information beyond
the folder layout. Text and data under CC BY 4.0; code under MIT. Contact: Otsoa Dubief, otsoa.dubief@gmail.com.
"""


def main(dst: Path):
    pkg = dst / "paquet"
    if pkg.exists():
        shutil.rmtree(pkg)
    pkg.mkdir(parents=True)
    for sub, files in FILES.items():
        (pkg / sub).mkdir(parents=True, exist_ok=True)
        for f in files:
            if any(x in str(f) for x in FORBIDDEN):
                raise SystemExit(f"forbidden path: {f}")
            name = f.name if f.parent != ROOT / "revues" else "revues_" + f.name
            shutil.copy2(f, pkg / sub / name)
    for f, name in RENAME.items():
        shutil.copy2(f, pkg / name)
    (pkg / "README.md").write_text(README, encoding="utf-8")
    (pkg / "JOURNAL_TIRAGE.md").write_text(journal_tirage(), encoding="utf-8")
    (dst / "JOURNAL_TIRAGE.md").write_text(journal_tirage(), encoding="utf-8")
    sums = [f"{sha(p)}  {p.relative_to(pkg)}" for p in sorted(pkg.rglob("*")) if p.is_file()]
    (pkg / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    (dst / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    z = dst / "depot_osf_resultats_2026-11-17.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(pkg.rglob("*")):
            if p.is_file():
                zi = zipfile.ZipInfo(str(p.relative_to(pkg)), date_time=(2026, 11, 17, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(zi, p.read_bytes())
    print(f"{len(sums)} files; zip {z.name} SHA-256 {sha(z)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
