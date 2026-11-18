"""Converts the generated Markdown tables (tables.md, tables_exploratoires.md) into LaTeX booktabs tables, one .tex
file per table, so that the paper never holds a hand-copied number (PLAN_SUITE T30). Outside the frozen perimeter.

    python3 outils/tables_latex.py article/resultats article/latex/tables

Each "## Title" section followed by a pipe table becomes tables/<slug>.tex; prose between the title and the table
becomes the caption note. Cell text is escaped, never edited.
"""
import re
import sys
from pathlib import Path

ESC = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{",
       "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
UNI = {"ρ": r"$\rho$", "ρ̂": r"$\hat\rho$", "×": r"$\times$", "≥": r"$\geq$", "≤": r"$\leq$", "−": r"$-$",
       "–": "--", "½": r"$\frac12$", "¼": r"$\frac14$", "→": r"$\to$", "≈": r"$\approx$", "÷": r"$\div$",
       "…": r"\ldots{}", "’": "'"}  # accented letters pass through: pdfLaTeX reads UTF-8 with T1 fonts


FR = {"aviation": "airline", "banque": "banking", "commerce": "retail", "au-dessus": "above",
      "indéterminé": "undetermined", "scénario": "scenario", "annoncé": "announced", "silencieux": "silent",
      "B-régulier": "B-regular", "retard10": "delay10", "groupees": "grouped misses", "faible": "low",
      "moyen": "medium", "fort": "high", "configuration constante": "constant configuration",
      "après la jonction": "after the junction", "avant la jonction": "before the junction", "oui": "yes",
      "non": "no", "tenue, non mise à l'épreuve": "held, not put to the test", "non réfutée": "not refuted",
      "sans objet": "without object", "verdicts bruts": "raw verdicts", "toute la réserve": "whole reserve",
      "échange des rôles": "role swap", "principale": "main", "rate10": "miss10", "(résultat)": "(result)",
      "charge moyenne non calculable (aucune configuration délégable)": "mean load not computable (no delegable configuration)"}


def esc(s: str) -> str:
    s = s.strip()
    s = FR.get(s, s)
    out = "".join(ESC.get(c, c) for c in s)
    out = out.replace("ρ̂", UNI["ρ̂"])
    for k, v in UNI.items():
        if k != "ρ̂":
            out = out.replace(k, v)
    out = re.sub(r"`([^`]*)`", r"\\texttt{\1}", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", out)
    out = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"\\emph{\1}", out)
    return out


def slug(title: str) -> str:
    m = re.match(r"(Table\s+[0-9A-Za-z]+(?:\s+bis)?)", title)
    base = m.group(1) if m else title[:40]
    return re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")


def convert(md: Path, dst: Path, prefix: str):
    text = md.read_text(encoding="utf-8")
    sections = re.split(r"^## ", text, flags=re.M)[1:]
    written = []
    for sec in sections:
        title, _, body = sec.partition("\n")
        lines = body.split("\n")
        rows = [l for l in lines if l.startswith("|")]
        if len(rows) < 3 or title.startswith("Decision table"):  # engine wording in French: kept in tables.md only
            continue
        note = " ".join(l.strip() for l in lines if l.strip() and not l.startswith("|"))
        cells = [[c for c in r.strip().strip("|").split("|")] for r in rows]
        head, data = cells[0], [r for r in cells[2:]]
        ncol = len(head)
        name = prefix + slug(title)
        if name in {w[0] for w in written}:
            name += f"_{len(written)}"
        body = [" & ".join(esc(c) for c in (r + [""] * ncol)[:ncol]) + r" \\" for r in data]
        headrow = " & ".join(esc(h) for h in head) + r" \\"
        if len(data) > 40:  # long tables break across pages
            spec = "".join(r">{\raggedright\arraybackslash\hspace{0pt}}p{%.3f\linewidth}" % (0.94 / ncol) for _ in range(ncol))  # \hspace{0pt}: lets the first word of a cell hyphenate
            tex = [r"{\tiny\setlength{\tabcolsep}{1pt}", rf"\begin{{longtable}}{{{spec}}}", rf"\caption*{{{esc(title)}}}\label{{tab:{name}}}\\",
                   r"\toprule", headrow, r"\midrule", r"\endfirsthead", r"\toprule", headrow, r"\midrule",
                   r"\endhead", r"\bottomrule", r"\endlastfoot"] + body + [r"\end{longtable}"]
            if note:
                tex.append(rf"\par {esc(note)}\par")
            tex.append("}")
        else:
            tex = [r"\begin{table}[htbp]", r"\centering\scriptsize", rf"\caption*{{{esc(title)}}}",
                   rf"\label{{tab:{name}}}", r"\resizebox{\linewidth}{!}{%", rf"\begin{{tabular}}{{{'l' * ncol}}}",
                   r"\toprule", headrow, r"\midrule"] + body + [r"\bottomrule", r"\end{tabular}}"]
            if note:
                tex.append(rf"\par\smallskip\parbox{{\linewidth}}{{\tiny {esc(note)}}}")
            tex.append(r"\end{table}")
        (dst / f"{name}.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")
        written.append((name, title, len(data)))
    return written


def main(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    m = convert(src / "tables.md", dst, "")
    x = convert(src / "tables_exploratoires.md", dst, "exp_")
    for fname, ws in (("main.tex", m), ("exp.tex", x)):
        (dst / fname).write_text("".join(f"\\input{{tables/{n}}}\n\\clearpage\n" for n, _, _ in ws), encoding="utf-8")
    w = m + x
    for n, t, k in w:
        print(f"{n}: {k} rows ({t[:60]})")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
