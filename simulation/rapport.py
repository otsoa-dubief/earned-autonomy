"""Figures et calcul des verdicts à partir des tableaux de resultats/.

Usage : .venv/bin/python rapport.py
Écrit les figures PNG et resultats/verdict.csv, et rend les tableaux Markdown
utilisés par RESULTATS.md (fonction `tableaux()`).
"""
import csv
import math
import os
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import config as C  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.environ.get("AM_DOSSIER", os.path.join(ICI, "resultats"))
DOSSIER_V1 = os.path.join(ICI, "resultats_v1")  # première passe, archivée : lecture seule

# Palette catégorielle de référence (skill dataviz, mode clair), ordre fixe
BLEU, ORANGE, AQUA, JAUNE, MAGENTA, VERT, VIOLET, ROUGE = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
ENCRE, ENCRE2, GRILLE, FOND = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": FOND, "axes.facecolor": FOND, "savefig.facecolor": FOND,
    "axes.edgecolor": "#b9b8b2", "axes.labelcolor": ENCRE2, "xtick.color": ENCRE2, "ytick.color": ENCRE2,
    "text.color": ENCRE, "axes.grid": True, "grid.color": GRILLE, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 9, "axes.titlesize": 10,
    "axes.titleweight": "bold", "legend.frameon": False, "lines.linewidth": 2,
})

from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter  # noqa: E402


def _fr(v, pos=None):
    if v <= 0:
        return "0"
    if v >= 1:
        return f"{v:,.0f}".replace(",", "\u202f")
    return f"{v:.3g}".replace(".", ",")


def axe_log_fr(ax, axe="y", subs=(1.0, 2.0, 5.0)):
    a = ax.yaxis if axe == "y" else ax.xaxis
    a.set_major_locator(LogLocator(base=10, subs=subs))
    a.set_major_formatter(FuncFormatter(_fr))
    a.set_minor_formatter(NullFormatter())


E = C.E_PRINCIPAL
REG_MAIN = C.nom_reglage(*C.REGLAGE_PRINCIPAL)
REGLAGES = [C.nom_reglage(r, a) for (r, a) in C.REGLAGES]
MIXES = list(C.MELANGES_BRUTS)
AGENTS_PRINC = ["A1", "A2", "A3", "A4", "A5", "A6a", "A6b", "A7", "A8"]
AGENTS_DOUTE = ["A2-calibre", "A2-abusif", "A4-calibre", "A4-abusif"]
TOUS_AGENTS = AGENTS_PRINC + AGENTS_DOUTE
BONS = ["A1", "A2"]
NIV = C.NIVEAUX


# --------------------------------------------------------------------------
# Lecture
# --------------------------------------------------------------------------
def _conv(v):
    if v in ("", None):
        return None
    if v in ("True", "False"):
        return v == "True"
    try:
        return float(v)
    except ValueError:
        return v


_cache = {}


def lire(nom, dossier=None):
    dossier = DOSSIER if dossier is None else dossier
    cle = (dossier, nom)
    if cle not in _cache:
        with open(os.path.join(dossier, nom + ".csv")) as f:
            _cache[cle] = [{k: _conv(v) for k, v in r.items()} for r in csv.DictReader(f)]
    return _cache[cle]


def lire_v1(nom):
    return lire(nom, DOSSIER_V1)


def _eq(a, b):
    if isinstance(a, float) and isinstance(b, (int, float)):
        return abs(a - b) < 1e-9
    return a == b


def filtre(rows, **kw):
    return [r for r in rows if all(_eq(r.get(k), v) for k, v in kw.items())]


def un(rows, **kw):
    f = filtre(rows, **kw)
    if len(f) != 1:
        raise KeyError(f"{kw}: {len(f)} lignes")
    return f[0]


# --------------------------------------------------------------------------
# Format français
# --------------------------------------------------------------------------
def nb(x, nd=2):
    """Nombre au format français : virgule décimale, espace insécable pour les milliers."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    s = f"{x:,.{nd}f}".replace(",", "\u00a0").replace(".", ",").replace("-", "−")
    return s


def ic(m, lo, hi, nd=2):
    return f"{nb(m, nd)} [{nb(lo, nd)} ; {nb(hi, nd)}]"


def pc(p, nd=1):
    return "—" if p is None else nb(100 * p, nd) + " %"


def icp(p, lo, hi, nd=1):
    return f"{nb(100 * p, nd)} % [{nb(100 * lo, nd)} ; {nb(100 * hi, nd)}]"


# --------------------------------------------------------------------------
# Verdicts
# --------------------------------------------------------------------------
def verdict_seuil(lo, hi, seuil):
    if hi <= seuil + 1e-12:
        return "passe"
    if lo > seuil + 1e-12:
        return "échoue"
    return "indécis"


def diffs(mix, agent, reglage, contre, regle="regle", e=E):
    rows = filtre(lire("comparaisons"), melange=mix, agent=agent, reglage=reglage, contre=contre,
                  regle=regle, e=e)
    return {r["mesure"]: r for r in rows}


CLES_BAT = ["charge", "degats_faible", "degats_moyen", "degats_fort"]


def bat(d):
    """Domination appariée : mieux sur au moins une mesure (intervalle tout sous 0),
    pire sur aucune (aucun intervalle tout au-dessus de 0)."""
    mieux = [k for k in CLES_BAT if d[k]["hi"] < 0]
    pire = [k for k in CLES_BAT if d[k]["lo"] > 0]
    if mieux and not pire:
        return "bat", mieux, pire
    if pire and not mieux:
        return "perd", mieux, pire
    if pire and mieux:
        return "compromis", mieux, pire
    return "égalité", mieux, pire


NOMS_MESURES = {"charge": "charge", "degats_faible": "dégâts faibles", "degats_moyen": "dégâts moyens",
                "degats_fort": "dégâts forts", "charge_hors_lec": "charge hors lectures"}


def mesure(mix, agent, regle, reglage, e=E):
    return un(lire("mesures"), melange=mix, agent=agent, regle=regle, reglage=reglage, e=e)


def verdict_garantie(reglage, regle="regle"):
    rows = [r for r in filtre(lire("garantie"), regle=regle, reglage=reglage) if r["mauvais"]]
    rows = [r for r in rows if r["agent"] in TOUS_AGENTS]
    if not rows:
        return None
    k = sum(r["k3"] for r in rows)
    n = sum(r["n"] for r in rows)
    from mesures import ic_proportion
    p, lo, hi, _ = ic_proportion(int(k), int(n))
    pire = max(rows, key=lambda r: r["p3"])
    v = verdict_seuil(pire["p3_lo"], pire["p3_hi"], 0.05)
    return dict(n_couples=len(rows), k=int(k), n=int(n), p=p, lo=lo, hi=hi, pire=pire, verdict=v, rows=rows)


def verdict_charge(reglage, agents=BONS, e=E):
    out = {}
    for mix in MIXES:
        for a in agents:
            m = mesure(mix, a, "regle", reglage, e)
            out[(mix, a)] = dict(
                charge=(m["charge"], m["charge_lo"], m["charge_hi"]),
                hors=(m["charge_hors_lec"], m["charge_hors_lec_lo"], m["charge_hors_lec_hi"]),
                v_charge=verdict_seuil(m["charge_lo"], m["charge_hi"], 50.0),
                v_hors=verdict_seuil(m["charge_hors_lec_lo"], m["charge_hors_lec_hi"], 50.0))
    return out


def verdict_degats(reglage, agents, marge, e=E, regle="regle"):
    """Liste des (mélange, agent, niveau, verdict, diff) contre « tout faire valider »."""
    res = []
    for mix in MIXES:
        for a in agents:
            d = diffs(mix, a, reglage, "tout_valider", regle=regle, e=e)
            for niv in NIV:
                r = d[f"degats_{niv}"]
                res.append((mix, a, niv, verdict_seuil(r["lo"], r["hi"], marge), r))
    return res


def synthese_degats(res):
    ech = [x for x in res if x[3] == "échoue"]
    ind = [x for x in res if x[3] == "indécis"]
    if not ech and not ind:
        return "passe"
    if ech:
        return "échoue"
    return "indécis"


def verdict_reactivite(reglage, agent="A6b", regle="regle"):
    rows = filtre(lire("reactivite"), regle=regle, reglage=reglage, agent=agent, type="tous")
    return {r["melange"]: r for r in rows}


def tri3(vs):
    if all(v == "passe" for v in vs):
        return "passe"
    if any(v == "échoue" for v in vs):
        return "échoue"
    return "indécis"


def calcul_marges():
    """Verdict de dégâts sur la grille fine de marges (amendement A1), pour chaque réglage, mélange,
    agent et niveau d'enjeu ; et la plus petite marge de la grille qui passe."""
    longues, minimales = [], []
    for reg in REGLAGES:
        for mix in MIXES:
            for a in TOUS_AGENTS:
                d = diffs(mix, a, reg, "tout_valider")
                for niv in NIV:
                    r = d[f"degats_{niv}"]
                    vs = {mg: verdict_seuil(r["lo"], r["hi"], mg) for mg in C.MARGES}
                    for mg, v in vs.items():
                        longues.append(dict(reglage=reg, melange=mix, agent=a, niveau=niv, marge=mg, verdict=v,
                                            ecart=r["diff"], ecart_lo=r["lo"], ecart_hi=r["hi"], n_rep=r["n_rep"]))
                    passe = [mg for mg in C.MARGES if vs[mg] == "passe"]
                    minimales.append(dict(reglage=reg, melange=mix, agent=a, niveau=niv,
                                          marge_min_qui_passe=(min(passe) if passe else "aucune (> 1)"),
                                          ecart=r["diff"], ecart_lo=r["lo"], ecart_hi=r["hi"], n_rep=r["n_rep"]))
    for nom, lignes in (("marges", longues), ("marge_minimale", minimales)):
        with open(os.path.join(DOSSIER, nom + ".csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            for l in lignes:
                w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in l.items()})
    return minimales


def calcul_verdicts():
    """Une ligne par (réglage, critère) : resultats/verdict.csv."""
    lignes = []
    for reg in REGLAGES:
        g = verdict_garantie(reg)
        lignes.append(dict(reglage=reg, epreuve="1 garantie", critere="pire couple mauvais promu au palier 3",
                           detail=f"{g['pire']['agent']} {g['pire']['type']} {g['pire']['melange']}",
                           estimation=g["pire"]["p3"], lo=g["pire"]["p3_lo"], hi=g["pire"]["p3_hi"],
                           seuil=0.05, verdict=g["verdict"]))
        lignes.append(dict(reglage=reg, epreuve="1 garantie", critere="part groupée des couples mauvais promus",
                           detail=f"{g['n_couples']} couples", estimation=g["p"], lo=g["lo"], hi=g["hi"],
                           seuil=0.05, verdict=verdict_seuil(g["lo"], g["hi"], 0.05)))
        vc = verdict_charge(reg)
        for (mix, a), v in vc.items():
            lignes.append(dict(reglage=reg, epreuve="2 utilité", critere="charge ≤ 50 % de tout valider",
                               detail=f"{a} {mix}", estimation=v["charge"][0], lo=v["charge"][1],
                               hi=v["charge"][2], seuil=50.0, verdict=v["v_charge"]))
            lignes.append(dict(reglage=reg, epreuve="2 utilité", critere="charge hors lectures ≤ 50 %",
                               detail=f"{a} {mix}", estimation=v["hors"][0], lo=v["hors"][1],
                               hi=v["hors"][2], seuil=50.0, verdict=v["v_hors"]))
        for marge in C.MARGES:
            for agents, nom in ((BONS, "A1 et A2"), (TOUS_AGENTS, "tous les agents")):
                res = verdict_degats(reg, agents, marge)
                pire = max(res, key=lambda x: x[4]["diff"])
                lignes.append(dict(reglage=reg, epreuve="2 utilité",
                                   critere=f"dégâts ≤ tout valider + {marge} ({nom})",
                                   detail=f"pire : {pire[1]} {pire[2]} {pire[0]}", estimation=pire[4]["diff"],
                                   lo=pire[4]["lo"], hi=pire[4]["hi"], seuil=marge, verdict=synthese_degats(res)))
        for contre in ["liste_fixe", "tri_risque", "hasard"]:
            for mix in MIXES:
                for a in TOUS_AGENTS:
                    v, mieux, pire = bat(diffs(mix, a, reg, contre))
                    lignes.append(dict(reglage=reg, epreuve="2 utilité", critere=f"bat {contre}",
                                       detail=f"{a} {mix}", estimation=None, lo=None, hi=None, seuil=None,
                                       verdict=v, mieux=" ".join(mieux), pire=" ".join(pire)))
        for agent in ("A6b", "A6a"):
            for mix, r in verdict_reactivite(reg, agent).items():
                lignes.append(dict(reglage=reg, epreuve="3 réactivité", critere="délai p95 avant le palier 1",
                                   detail=f"{agent} {mix} ({int(r['n_promus'])} couples promus à t=1500)",
                                   estimation=r.get("delai_p95"), lo=r.get("delai_p95_lo"),
                                   hi=r.get("delai_p95_hi"), seuil=None,
                                   verdict=f"non retiré avant l'horizon : {pc(r.get('part_non_retire'))}"))
    with open(os.path.join(DOSSIER, "verdict.csv"), "w", newline="") as f:
        cles = ["reglage", "epreuve", "critere", "detail", "estimation", "lo", "hi", "seuil", "verdict", "mieux", "pire"]
        w = csv.DictWriter(f, fieldnames=cles)
        w.writeheader()
        for l in lignes:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in l.items()})
    return lignes


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------
STYLE_TEMOINS = {
    "tout_valider": ("tout faire valider", ORANGE, "s"),
    "liste_fixe": ("liste fixe", AQUA, "D"),
    "tri_risque": ("tri par le risque", JAUNE, "P"),
    "trois_reussites": ("trois réussites", MAGENTA, "X"),
    "oracle": ("oracle (pb de départ)", VERT, "*"),
    "hasard": ("hasard (même part du temps)", VIOLET, "h"),
    "tout_approuver": ("tout approuver", ROUGE, "p"),
}
MARQ_REG = {"stricte": "v", "depart": "o", "souple": "^"}


def fig_charge_degats(mix, agents=("A1", "A2", "A3", "A4", "A5")):
    fig, axes = plt.subplots(len(agents), 3, figsize=(11, 2.55 * len(agents)), constrained_layout=True)
    for i, a in enumerate(agents):
        for j, niv in enumerate(NIV):
            ax = axes[i, j]
            col = f"degats_{niv}"
            for cle, (lab, coul, mk) in STYLE_TEMOINS.items():
                reg = "-"
                if cle == "oracle":
                    reg = "pb depart"
                elif cle == "hasard":
                    reg = REG_MAIN
                m = mesure(mix, a, cle, reg)
                ax.errorbar(m["charge"], m[col], yerr=[[m[col] - m[col + "_lo"]], [m[col + "_hi"] - m[col]]],
                            fmt=mk, color=coul, ms=(10 if mk == "*" else (5 if cle == "hasard" else 7)),
                            mec=FOND, mew=0.8, elinewidth=1,
                            label=lab if (i == 0 and j == 0) else None, zorder=6 if cle == "hasard" else 3)
            for (r, al) in C.REGLAGES:
                reg = C.nom_reglage(r, al)
                m = mesure(mix, a, "regle", reg)
                plein = al == 0.05
                ax.errorbar(m["charge"], m[col], yerr=[[m[col] - m[col + "_lo"]], [m[col + "_hi"] - m[col]]],
                            fmt=MARQ_REG[r], color=BLEU, ms=7, mfc=BLEU if plein else FOND, mec=BLEU,
                            mew=1.3, elinewidth=1, zorder=4,
                            label=f"règle {reg.replace('depart', 'départ')}" if (i == 0 and j == 0) else None)
            ax.set_yscale("log")
            axe_log_fr(ax)
            ax.set_xlim(-4, 112)
            if i == 0:
                ax.set_title(f"dégâts à enjeu {niv}")
            if j == 0:
                ax.set_ylabel(f"{a} — dégâts / 100 actions")
            if i == len(agents) - 1:
                ax.set_xlabel("charge pour 100 actions")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower center", ncol=5, fontsize=8)
    fig.suptitle(f"Charge contre dégâts, mélange {C.NOMS_MELANGES[mix]}, validateur à 5 % "
                 f"(moyennes et IC 95 %, 5 000 répétitions ; réglages autres que départ α=5 % : 1 000)",
                 fontsize=10, color=ENCRE)
    out = os.path.join(DOSSIER, f"fig1_charge_degats_{mix}.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def fig_garantie(mix):
    rows = filtre(lire("garantie_courbe"), melange=mix)
    fig, axes = plt.subplots(2, 4, figsize=(12, 5.6), constrained_layout=True)
    coul = {"stricte": BLEU, "depart": ORANGE, "souple": AQUA}
    for k in range(C.N_MERITES):
        ax = axes.flat[k]
        t = C.TYPES[k]
        for (r, al) in C.REGLAGES:
            reg = C.nom_reglage(r, al)
            rr = sorted(filtre(rows, reglage=reg, type=t), key=lambda x: x["q"])
            q = [x["q"] * 100 for x in rr]
            p = [x["p3"] * 100 for x in rr]
            ax.plot(q, p, color=coul[r], ls="-" if al == 0.05 else (0, (1, 1.5)), lw=1.8 if al == 0.05 else 1.4,
                    marker="o" if al == 0.05 else None, ms=3, label=reg.replace("depart", "départ"))
            if al == 0.05:
                pm = rr[0]["pm3"] * 100
                ax.axvline(pm, color=coul[r], lw=0.8, alpha=0.5)
        ax.axhline(5, color=ENCRE2, lw=0.9)
        ax.text(0.22, 6.5, "5 %", color=ENCRE2, fontsize=7)
        ax.set_xscale("log")
        ax.set_xticks([0.25, 0.5, 1, 2, 5, 10, 20, 30])
        ax.set_xticklabels(["0,25", "0,5", "1", "2", "5", "10", "20", "30"])
        ax.set_ylim(-2, 102)
        ax.set_title(f"{t} · enjeu {C.NIVEAUX[C.ENJEU[k]]}")
        if k % 4 == 0:
            ax.set_ylabel("répétitions promues au palier 3 (%)")
        if k >= 3:
            ax.set_xlabel("taux d'erreur vrai q (%, échelle log)")
    ax = axes.flat[7]
    ax.axis("off")
    h, l = axes.flat[0].get_legend_handles_labels()
    ax.legend(h, l, loc="center", fontsize=9, title="réglage", title_fontsize=9)
    ax.text(0.5, 0.02, "traits verticaux : pm du palier 3 (α = 5 %)\n1 000 répétitions par point, horizon 3 000 actions",
            ha="center", va="bottom", fontsize=8, color=ENCRE2, transform=ax.transAxes)
    fig.suptitle(f"Garantie : part des agents à taux constant promus au palier 3 avant l'horizon, mélange "
                 f"{C.NOMS_MELANGES[mix]}", fontsize=10)
    out = os.path.join(DOSSIER, f"fig2_garantie_{mix}.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def fig_promotion():
    rows = lire("promotion")
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.2), constrained_layout=True)
    types = C.TYPES[:C.N_MERITES]
    x = np.arange(len(types))
    coul = {"stricte": BLEU, "depart": ORANGE, "souple": AQUA}
    for i, a in enumerate(BONS):
        for j, mix in enumerate(MIXES):
            ax = axes[i, j]
            for d, (r, al) in zip((-0.22, 0, 0.22), [("stricte", 0.05), ("depart", 0.05), ("souple", 0.05)]):
                reg = C.nom_reglage(r, al)
                med, p90, jam = [], [], []
                for t in types:
                    rr = un(rows, melange=mix, agent=a, regle="regle", reglage=reg, type=t, palier=3.0)
                    med.append(rr.get("delai_med") or np.nan)
                    p90.append(rr.get("delai_p90") or np.nan)
                    jam.append(rr["jamais"])
                med, p90 = np.array(med), np.array(p90)
                ax.vlines(x + d, med, p90, color=coul[r], lw=1.2)
                ax.plot(x + d, med, "o", color=coul[r], ms=6, mec=FOND,
                        label=f"{reg.replace('depart', 'départ')} : médiane (trait : 90e centile)")
                for xi, (mv, jv) in enumerate(zip(med, jam)):
                    if jv >= 0.005:
                        ax.text(xi + d, 3400, f"{round(100 * jv)}", ha="center", fontsize=6.5, color=coul[r])
            ax.set_yscale("log")
            ax.set_ylim(8, 6000)
            axe_log_fr(ax, subs=(1.0, 3.0))
            ax.axhline(3000, color=ENCRE2, lw=0.8)
            ax.set_xticks(x)
            ax.set_xticklabels(types)
            ax.set_title(f"{a} · {C.NOMS_MELANGES[mix]}")
            if j == 0:
                ax.set_ylabel("actions avant la 1re promotion au palier 3")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower center", ncol=3, fontsize=8)
    fig.suptitle("Délai de promotion des bons agents (parmi les répétitions promues). Chiffres en haut : "
                 "% des répétitions jamais promues au palier 3 avant l'horizon (3 000)", fontsize=10)
    out = os.path.join(DOSSIER, "fig3_delai_promotion.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def fig_reactivite():
    rows = lire("reactivite")
    regles = [("regle", REG_MAIN, "règle (départ α=5 %)", BLEU, "o"),
              ("regle", C.nom_reglage("stricte", 0.05), "règle (stricte α=5 %)", VIOLET, "v"),
              ("regle", C.nom_reglage("souple", 0.05), "règle (souple α=5 %)", AQUA, "^"),
              ("trois_reussites", "-", "trois réussites", MAGENTA, "X")]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    types = C.TYPES[:C.N_MERITES] + ["tous"]
    x = np.arange(len(types))
    for j, mix in enumerate(MIXES):
        ax = axes[j]
        for d, (regle, reg, lab, coul, mk) in zip((-0.24, -0.08, 0.08, 0.24), regles):
            med, p95, nonr = [], [], []
            for t in types:
                rr = filtre(rows, melange=mix, agent="A6b", regle=regle, reglage=reg, type=t)
                if rr and rr[0].get("delai_med") is not None and rr[0]["n_promus"] >= 20:
                    med.append(rr[0]["delai_med"])
                    p95.append(rr[0]["delai_p95"])
                    nonr.append(rr[0]["part_non_retire"])
                else:
                    med.append(np.nan)
                    p95.append(np.nan)
                    nonr.append(np.nan)
            med, p95 = np.array(med), np.array(p95)
            ax.vlines(x + d, np.maximum(med, 1), np.maximum(p95, 1), color=coul, lw=1.2)
            ax.plot(x + d, np.maximum(med, 1), mk, color=coul, ms=6, mec=FOND, label=lab)
        ax.set_yscale("log")
        ax.set_ylim(1, 3000)
        axe_log_fr(ax, subs=(1.0, 3.0))
        ax.axhline(1500, color=ENCRE2, lw=0.8)
        ax.text(len(types) - 0.6, 1650, "horizon", fontsize=7, color=ENCRE2, ha="right")
        ax.set_xticks(x)
        ax.set_xticklabels(types)
        ax.set_title(f"A6b (dérive silencieuse) · {C.NOMS_MELANGES[mix]}")
        if j == 0:
            ax.set_ylabel("actions entre la dérive et le palier 1")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower center", ncol=4, fontsize=8)
    fig.suptitle("Réactivité : médiane (point) et 95e centile (trait) du délai, types promus à t = 1 500 "
                 "(au moins 20 couples) ; non retiré = compté à l'horizon", fontsize=10)
    out = os.path.join(DOSSIER, "fig4_reactivite.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def fig_autonomie_temps():
    rows = lire("autonomie_temps")
    agents = [("A1", BLEU), ("A2", ORANGE), ("A3", AQUA), ("A4", JAUNE), ("A6a", VIOLET), ("A6b", MAGENTA),
              ("A7", VERT)]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for j, mix in enumerate(MIXES):
        ax = axes[j]
        for a, coul in agents:
            rr = sorted(filtre(rows, melange=mix, agent=a, regle="regle", reglage=REG_MAIN), key=lambda x: x["debut"])
            xs = [r["debut"] + 50 for r in rr]
            ys = [100 * r["part_palier2plus"] for r in rr]
            ax.plot(xs, ys, color=coul, lw=1.6, label=a)
        ax.axvline(1500, color=ENCRE2, lw=0.8)
        ax.set_ylim(0, 100)
        ax.set_xlim(0, 3000)
        ax.set_title(f"Règle (départ α=5 %) · {C.NOMS_MELANGES[mix]}")
        ax.set_xlabel("action (fenêtres de 100)")
        if j == 0:
            ax.set_ylabel("actions exécutées sans validation préalable (%)\n(palier 2 ou 3)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside right center", fontsize=8)
    fig.suptitle("Autonomie au fil du temps, règle au réglage de départ (moyenne sur 5 000 répétitions ; "
                 "trait vertical : t = 1 500 ; A6a et A6b confondus avec A2 avant t = 1 500)", fontsize=10)
    out = os.path.join(DOSSIER, "fig5_autonomie_temps.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def fig_v1_v2_autonomie():
    v2 = lire("autonomie_temps")
    v1 = lire_v1("autonomie_temps")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for j, mix in enumerate(MIXES):
        ax = axes[j]
        for a, coul in (("A1", BLEU), ("A2", ORANGE), ("A3", AQUA), ("A7", VERT)):
            for rows, ls, lab in ((v1, (0, (1, 1.5)), "v1"), (v2, "-", "v2")):
                rr = sorted(filtre(rows, melange=mix, agent=a, regle="regle", reglage=REG_MAIN), key=lambda x: x["debut"])
                ax.plot([r["debut"] + 50 for r in rr], [100 * r["part_palier2plus"] for r in rr], color=coul, ls=ls,
                        lw=1.6, label=f"{a}, {lab}")
        ax.axvline(1500, color=ENCRE2, lw=0.8)
        ax.set_ylim(0, 100)
        ax.set_xlim(0, 3000)
        ax.set_title(f"v1 (pointillés) contre v2 (traits) · {C.NOMS_MELANGES[mix]}")
        ax.set_xlabel("action (fenêtres de 100)")
        if j == 0:
            ax.set_ylabel("actions sans validation préalable (%)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside right center", fontsize=8)
    fig.suptitle("Extinction de l'autonomie : première passe (v1) contre amendement A1 (v2), réglage de départ "
                 "α=5 %, 5 000 répétitions", fontsize=10)
    out = os.path.join(DOSSIER, "fig6_v1_v2_autonomie.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def toutes_figures():
    outs = [fig_charge_degats(m) for m in MIXES]
    outs += [fig_garantie(m) for m in MIXES]
    outs += [fig_promotion(), fig_reactivite(), fig_autonomie_temps(), fig_v1_v2_autonomie()]
    return outs


if __name__ == "__main__":
    calcul_verdicts()
    calcul_marges()
    for o in toutes_figures():
        print(o)
