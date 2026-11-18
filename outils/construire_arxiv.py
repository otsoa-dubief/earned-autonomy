"""Builds the arXiv source package (PLAN_SUITE T55). Outside the frozen perimeter.

    python3 outils/construire_arxiv.py        # after construire_latex.py and a latexmk run (main.bbl must exist)

Copies the LaTeX sources into article/arxiv/src/ with the figures inside the package (arXiv compiles from the package
root and refuses parent paths), checks that the copy compiles alone with pdfLaTeX in an empty folder (no BibTeX: arXiv
uses main.bbl), and writes article/arxiv/paquet.tar.gz and the plain-text abstract with its length.
"""
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATEX = ROOT / "article" / "latex"
OUT = ROOT / "article" / "arxiv"
SRC = OUT / "src"
FILES = ["main.tex", "main.bbl", "abstract.tex", "body.tex", "appendix_abc.tex", "appendix_ef.tex"]
MAX_ABSTRACT = 1920


def abstract_text() -> str:
    t = (ROOT / "article" / "brouillon.md").read_text(encoding="utf-8")
    s = t.index("## Abstract") + len("## Abstract")
    a = t[s:].strip().split("\n\n")[0]
    a = re.sub(r"[*_`]", "", a)
    return " ".join(a.split())


def build() -> Path:
    if SRC.exists():
        shutil.rmtree(SRC)
    (SRC / "tables").mkdir(parents=True)
    (SRC / "figures").mkdir()
    for f in FILES:
        text = (LATEX / f).read_text(encoding="utf-8")
        text = text.replace("{../figures/", "{figures/")
        if f == "main.tex":  # internal comments (task numbers, build notes) stay out of the package
            text = "".join(l for l in text.splitlines(keepends=True) if not l.lstrip().startswith("%"))
        if "../" in text:
            raise SystemExit(f"parent path left in {f}")
        (SRC / f).write_text(text, encoding="utf-8")
    todo = re.findall(r"\\input\{tables/([\w.-]+?)(?:\.tex)?\}", (SRC / "main.tex").read_text(encoding="utf-8"))
    while todo:  # only the tables the paper inputs, directly or through tables/main.tex and tables/exp.tex
        name = todo.pop()
        dst = SRC / "tables" / f"{name}.tex"
        if dst.exists():
            continue
        shutil.copy2(LATEX / "tables" / f"{name}.tex", dst)
        todo += re.findall(r"\\input\{tables/([\w.-]+?)(?:\.tex)?\}", dst.read_text(encoding="utf-8"))
    used = set(re.findall(r"figures/([\w.-]+\.pdf)", " ".join((SRC / f).read_text(encoding="utf-8") for f in FILES)))
    for name in sorted(used):
        shutil.copy2(ROOT / "article" / "figures" / name, SRC / "figures" / name)
    return SRC


def compile_alone(src: Path) -> int:
    with tempfile.TemporaryDirectory() as d:
        shutil.copytree(src, d, dirs_exist_ok=True)
        for _ in range(3):
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=d,
                               capture_output=True, text=True)
            if r.returncode != 0:
                raise SystemExit("compilation failed:\n" + r.stdout[-2000:])
        log = Path(d, "main.log").read_text(errors="ignore")
        for bad in ("undefined references", "Citation `", "Overfull \\hbox"):
            if bad in log:
                raise SystemExit(f"log contains: {bad}")
        pages = re.search(r"Output written on main.pdf \((\d+) pages", log)
        return int(pages.group(1))


def main():
    src = build()
    pages = compile_alone(src)
    tgz = OUT / "paquet.tar.gz"
    with tarfile.open(tgz, "w:gz") as tf:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                info = tf.gettarinfo(str(p), arcname=str(p.relative_to(src)))
                info.mtime, info.uid, info.gid, info.uname, info.gname = 0, 0, 0, "", ""
                with open(p, "rb") as fh:
                    tf.addfile(info, fh)
    a = abstract_text()
    (OUT / "abstract.txt").write_text(a + "\n", encoding="utf-8")
    if len(a) > MAX_ABSTRACT:
        raise SystemExit(f"abstract has {len(a)} characters (> {MAX_ABSTRACT})")
    n = sum(1 for p in src.rglob("*") if p.is_file())
    print(f"{n} files; compiles alone, {pages} pages; abstract {len(a)} characters; {tgz.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
