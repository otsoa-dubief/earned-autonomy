"""Builds the data package (PLAN_SUITE T50; Q8 = yes). Outside the frozen perimeter; copies and hashes only.

    python3 outils/construire_paquet_donnees.py ~/dev/autonomie-meritee-archives/paquet_donnees_2026-11-18

The archive holds exactly the 68,990 files of the verdict-freeze manifest (experience/manifeste_verdicts.txt, SHA-256
904aa8d3...f88d, registered on OSF cusv6), byte for byte, under `experience/<path>`, so that unzipping it at the root of
the code repository puts every file where the final-replay command expects it. Each file is hashed before it is
written and the archive is re-read and checked against the manifest afterwards. Nothing is opened or displayed.
"""
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "experience"
MANIFEST = EXP / "manifeste_verdicts.txt"
EXPECTED_MANIFEST_SHA = "904aa8d3829b890c147d548718fe3ae78cd088b9f4402b3af1d2aff3487ff88d"
NAME = "earned_autonomy_data_2026-11-18.zip"
DATE = (2026, 11, 18, 0, 0, 0)


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_manifest() -> list[tuple[str, str]]:
    rows = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        digest, path = line.split("  ", 1)
        rows.append((digest, path))
    return rows


def build(dst: Path) -> Path:
    if sha_file(MANIFEST) != EXPECTED_MANIFEST_SHA:
        raise SystemExit("manifest hash differs from the registered one")
    rows = sorted(read_manifest(), key=lambda r: r[1])
    dst.mkdir(parents=True, exist_ok=True)
    z = dst / NAME
    tmp = dst / (NAME + ".partial")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for i, (digest, rel) in enumerate(rows, 1):
            src = EXP / rel
            data = src.read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise SystemExit(f"hash mismatch before packing: {rel}")
            zi = zipfile.ZipInfo("experience/" + rel, date_time=DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zf.writestr(zi, data)
            if i % 10000 == 0:
                print(f"{i} files packed", flush=True)
    tmp.rename(z)
    return z


def check(z: Path) -> int:
    expected = {"experience/" + p: d for d, p in read_manifest()}
    seen = 0
    with zipfile.ZipFile(z) as zf:
        names = zf.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise SystemExit("archive entries differ from the manifest")
        for n in names:
            h = hashlib.sha256()
            with zf.open(n) as f:
                for b in iter(lambda: f.read(1 << 20), b""):
                    h.update(b)
            if h.hexdigest() != expected[n]:
                raise SystemExit(f"hash mismatch in archive: {n}")
            seen += 1
    return seen


def main(dst: Path):
    z = build(dst)
    n = check(z)
    shutil.copy2(MANIFEST, dst / "manifeste_verdicts.txt")
    for f in ("LICENSE-TEXT", "THIRD_PARTY_NOTICES"):
        shutil.copy2(ROOT / f, dst / f)
    print(f"{n} files checked against the manifest; {z.name} {z.stat().st_size} bytes SHA-256 {sha_file(z)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).expanduser().resolve())
