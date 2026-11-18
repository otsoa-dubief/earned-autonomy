"""Tirage de la relecture à l'aveugle d'Otsoa (REGLE.md, 5 novembre, point 7).

Tire 10 alertes levées et 5 alertes confirmées parmi les décisions de Claude (decisions.csv), les mélange, et
produit une page HTML autonome (relecture_otsoa.html) avec les fiches en version aveugle (une par conversation).
- La graine vient de `secrets` ; elle est inscrite dans tirage_aveugle.json APRÈS le tirage.
- Au plus une alerte tirée par conversation (partie). Les 10 levées sont réparties entre les motifs présents : au
  moins une par motif, le reste au prorata des levées de chaque motif (voir `tirer`).
- Moins de 10 levées ou moins de 5 confirmées utilisables : on prend tout ce qui existe (un par conversation) et on
  le signale.
- L'ordre des fiches est tiré au sort ; la graine permet de le refaire.
- La correspondance fiche -> alerte (avec l'avis de Claude) est dans tirage_aveugle.json, que la page ne montre pas.
- Un tirage ne se refait pas : le programme refuse d'écraser une page ou une correspondance déjà écrite.

Second tour (décision B2 d'Otsoa, 5 novembre ; accord.py) : `--exclure tirage_aveugle.json` écarte les alertes déjà
montrées à Otsoa et toutes les alertes de leurs conversations. Les fiches sont numérotées à la suite du premier tour
(16 à 30) ; sortie dans relecture_otsoa_tour2.html et tirage_aveugle_tour2.json. Deux tours au plus par vague.

Drapeau (alerte forte levée par Claude, jugée vraie erreur par Otsoa) : `--fortes` prépare la relecture de toutes les
alertes fortes levées qu'Otsoa n'a pas encore jugées (relecture_fortes_levees.html, fortes_levees.json) ; sa décision
l'emporte (accord.py --fortes). Un second tour tiré ensuite écarte aussi ces alertes et leurs conversations
(`--exclure fortes_levees.json`).

Usage :
    python banc/relecture/tirage_aveugle.py --relecture DOSSIER --decisions decisions.csv [--sortie DOSSIER]
    ... --exclure DOSSIER/tirage_aveugle.json                    (second tour)
    ... --fortes --exclure DOSSIER/tirage_aveugle.json           (après le drapeau)
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import journal  # noqa: E402
import decisions  # noqa: E402
import fiches  # noqa: E402

N_LEVEES = 10
N_CONFIRMEES = 5
TOURS_MAX = 2
TIRAGE = "tirage"          # tour à l'aveugle : 10 levées et 5 confirmées tirées au sort
FORTES = "fortes levées"   # après le drapeau : toutes les alertes fortes levées pas encore jugées par Otsoa
FICHIERS = {  # (nature, tour) -> (page, correspondance)
    (TIRAGE, 1): ("relecture_otsoa.html", "tirage_aveugle.json"),
    (TIRAGE, 2): ("relecture_otsoa_tour2.html", "tirage_aveugle_tour2.json"),
    (FORTES, None): ("relecture_fortes_levees.html", "fortes_levees.json"),
}


class TirageInvalide(ValueError):
    pass


def _repartir(effectifs: dict, plafonds: dict, total: int) -> dict:
    """Quotas par motif. Une place par motif présent d'abord (dans la limite du plafond et du total), puis le reste au
    prorata des effectifs : à chaque place, le motif qui a le plus grand déficit sur sa part théorique (à égalité, l'ordre
    alphabétique). `plafonds` : ce que le motif peut fournir au plus (alertes de conversations distinctes)."""
    quotas = {m: 0 for m in effectifs}
    motifs = sorted(effectifs)
    for m in motifs:
        if sum(quotas.values()) < total and plafonds[m] > 0:
            quotas[m] = 1
    somme = sum(effectifs.values()) or 1
    while sum(quotas.values()) < total:
        ouverts = [m for m in motifs if quotas[m] < plafonds[m]]
        if not ouverts:
            break
        m = max(ouverts, key=lambda x: (effectifs[x] * total / somme - quotas[x], -motifs.index(x)))
        quotas[m] += 1
    return quotas


def _un_par_conversation(ids, conversation_de, rng, deja) -> list:
    """Parcourt `ids` dans un ordre tiré au sort et garde la première alerte de chaque conversation non encore prise."""
    ordre = list(ids)
    rng.shuffle(ordre)
    vus, gardes = set(deja), []
    for i in ordre:
        c = conversation_de(i)
        if c not in vus:
            vus.add(c)
            gardes.append(i)
    return gardes


def tirer(levees, confirmees, rng, motif_de=None, conversation_de=None, conversations_exclues=()) -> tuple:
    """(ids tirés dans un ordre mélangé, signalements). Entrées triées avant tirage : reproductible avec la graine.

    - `motif_de` {id: motif} et `conversation_de` {id: clé de conversation} ; sans eux, tous les motifs sont confondus et
      chaque alerte est sa propre conversation.
    - Au plus une alerte par conversation sur l'ensemble des cas tirés. Les levées sont tirées d'abord, les confirmées
      ensuite dans les conversations restantes.
    - Les N_LEVEES levées sont réparties entre les motifs présents (`_repartir`). Les motifs les moins fournis sont servis
      en premier ; une place qu'un motif ne peut pas remplir (conversations déjà prises) passe aux autres.
    - Moins de N_LEVEES levées (ou de N_CONFIRMEES confirmées) utilisables : on prend tout ce qui existe, un par
      conversation, et on le signale (comportement d'origine).
    - `conversations_exclues` : conversations déjà montrées à Otsoa dans la vague (second tour) ; aucune de leurs
      alertes n'est tirée."""
    motif_de = motif_de or {}
    conv = (lambda i: conversation_de[i]) if conversation_de else (lambda i: i)
    signalements = []
    exclues = set(conversations_exclues)
    levees = sorted(i for i in levees if conv(i) not in exclues)
    confirmees = sorted(i for i in confirmees if conv(i) not in exclues)
    par_motif: dict = {}
    for i in levees:
        par_motif.setdefault(motif_de.get(i, ""), []).append(i)
    # une alerte par conversation dans chaque motif : plafond = conversations distinctes du motif
    plafonds = {m: len({conv(i) for i in ids}) for m, ids in par_motif.items()}
    quotas = _repartir({m: len(ids) for m, ids in par_motif.items()}, plafonds, N_LEVEES)
    pris, convs = [], set()
    for m in sorted(par_motif, key=lambda x: (len(par_motif[x]), x)):  # les moins fournis d'abord
        dispo = _un_par_conversation(par_motif[m], conv, rng, convs)
        choix_m = dispo[:quotas[m]]
        pris += choix_m
        convs |= {conv(i) for i in choix_m}
    # places laissées vides par les conflits de conversation : on complète avec les autres levées possibles
    manque = N_LEVEES - len(pris)
    if manque > 0:
        reste = [i for i in levees if i not in pris]
        pris += _un_par_conversation(reste, conv, rng, convs)[:manque]
        convs = {conv(i) for i in pris}
    confs = _un_par_conversation(confirmees, conv, rng, convs)[:N_CONFIRMEES]
    for nom, dispo, n, voulu in (("levées", levees, len(pris), N_LEVEES), ("confirmées", confirmees, len(confs), N_CONFIRMEES)):
        if n < voulu:
            texte = f"seulement {n} alertes {nom} sur {voulu} demandées : tout est pris"
            if len(dispo) > n:
                texte += " (au plus une alerte par conversation)"
            if exclues:
                texte += " ; conversations déjà montrées à Otsoa écartées"
            signalements.append(texte)
    choix = pris + confs
    rng.shuffle(choix)
    return choix, signalements


# ---------------------------------------------------------------------------
# Page HTML
# ---------------------------------------------------------------------------
CSS = """
:root{--fond:#f7f6f1;--texte:#1b1d1f;--discret:#5b6166;--ligne:#d7d5cc;--carte:#fff;--accent:#0d7a4f;--code:#efede5}
@media (prefers-color-scheme:dark){:root{--fond:#16181a;--texte:#e8e6df;--discret:#9aa0a5;--ligne:#33373a;--carte:#1e2123;--accent:#4fd197;--code:#262a2c}}
*{box-sizing:border-box}
body{margin:0;background:var(--fond);color:var(--texte);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:56rem;margin:0 auto;padding:1rem 16px 4rem}
h1{font-size:1.5rem;margin:1rem 0 .5rem}h2{font-size:1.2rem;margin:0 0 .5rem}h3{font-size:1rem;margin:.75rem 0 .25rem}
.intro,.fiche{background:var(--carte);border:1px solid var(--ligne);border-radius:3px;padding:1rem;margin:1rem 0}
.fiche dl{display:grid;grid-template-columns:max-content 1fr;gap:.2rem 1rem;margin:0 0 .5rem}
.fiche dt{color:var(--discret)}.fiche dd{margin:0}
details{border-top:1px solid var(--ligne);padding:.5rem 0}summary{cursor:pointer;font-weight:600}
pre{background:var(--code);border-radius:3px;padding:.6rem;margin:.4rem 0;white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.45 ui-monospace,Menlo,Consolas,monospace}
.role{font-weight:600;color:var(--accent)}
fieldset{border:1px solid var(--ligne);border-radius:3px;margin:1rem 0 0;padding:.6rem}
legend{font-weight:600}
label{display:block;padding:.4rem 0}
input[type=radio]{width:1.2rem;height:1.2rem;margin-right:.5rem;vertical-align:middle}
input[type=text]{width:100%;font:inherit;padding:.5rem;border:1px solid var(--ligne);border-radius:3px;background:var(--fond);color:var(--texte)}
button,textarea{font:inherit}button{padding:.6rem 1rem;border-radius:3px;border:1px solid var(--accent);background:var(--accent);color:#fff}
textarea{width:100%;min-height:9rem;background:var(--code);color:var(--texte);border:1px solid var(--ligne);padding:.5rem}
.signal{border-left:4px solid #b26a00;padding-left:.75rem}
.encadre{border-left:4px solid var(--accent);background:var(--code);padding:.5rem 1rem;margin:.5rem 0;border-radius:3px}
.encadre ul{margin:0;padding-left:1.1rem}.encadre li{margin:.25rem 0}
.defile{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border:1px solid var(--ligne);padding:.3rem .5rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}
h3.signale{border-left:4px solid #b26a00;padding-left:.5rem}
"""

SCRIPT = """
(function(){
  var b=document.getElementById('generer');if(!b)return;
  b.hidden=false;
  b.addEventListener('click',function(){
    var lignes=['fiche,reponse,motif'];
    document.querySelectorAll('.fiche').forEach(function(f){
      var n=f.getAttribute('data-numero');
      var r=f.querySelector('input[type=radio]:checked');
      var m=f.querySelector('input[type=text]').value.replace(/"/g,'""');
      lignes.push(n+','+(r?r.value:'')+',"'+m+'"');
    });
    document.getElementById('sortie').value=lignes.join('\\n');
  });
})();
"""


def _pre(texte: str) -> str:
    return f"<pre>{html.escape(texte if texte else '(vide)')}</pre>"


def _tableau_html(d: dict) -> str:
    if not d.get("lignes"):
        return f"<p>{html.escape(d.get('note') or '(rien à comparer)')}</p>"
    corps = "".join(
        "<tr><td><code>{c}</code></td><td>{a}</td><td>{t}</td><td>{e}</td></tr>".format(
            c=html.escape(l["champ"]), a=html.escape(l["agent"]), t=html.escape(l["attendu"]),
            e=html.escape(l["etat"] + ("" if l["compare"] else " (champ non comparé)") + (" (texte libre)" if l["libre"] else "")))
        for l in d["lignes"])
    return (f"<p>Action attendue la plus proche (n°{d['indice']}) : <code>{html.escape(d['attendue'])}</code></p>"
            f"<div class=\"defile\"><table><thead><tr><th>Champ</th><th>Appel de l'agent</th><th>Action attendue</th><th>Écart</th></tr></thead>"
            f"<tbody>{corps}</tbody></table></div>")


def rendre_fiche_html(f: dict, numero: int, total: int) -> str:
    """Ordre : encadré, différence champ par champ, énoncé, règles du domaine, actions attendues, conversation.
    Aucun avis, aucun modèle, aucune partie, aucun décompte."""
    r = f.get("reglement") or {}
    classe_signale = ' class="signale"'
    conv = "".join(
        f"<h3{classe_signale if m.get('signale') else ''}>{k}. <span class=\"role\">{html.escape(m['role'])}</span></h3>{_pre(m['texte'])}"
        for k, m in enumerate(f["conversation"], 1)
    ) or "<p>(aucun message retrouvé)</p>"
    regl = ""
    if r.get("chemin"):
        regl += f"<p>Fichier : <code>{html.escape(r['chemin'])}</code><br>Recherche : {html.escape(r['recherche'])}</p>"
    if r.get("note"):
        regl += f"<p>{html.escape(r['note'])}</p>"
    for p in r.get("paragraphes", []):
        regl += f"<h3>{html.escape(p['section'] or '(sans titre)')}</h3>{_pre(p['texte'])}"
    if not r.get("paragraphes"):
        regl += "<p>Aucun paragraphe du règlement ne cite cet outil.</p>"
    avert = "".join(f"<p class=\"signal\">Attention : {html.escape(a)}</p>" for a in f.get("avertissements", []))
    encadre = "".join(f"<li>{html.escape(x)}</li>" for x in f.get("encadre", []))
    return f"""<article class="fiche" id="fiche-{numero}" data-numero="{numero}">
<h2>Fiche {numero} sur {total}</h2>
<aside class="encadre"><ul>{encadre}</ul></aside>
{avert}
<details open><summary>Différence champ par champ</summary>{_tableau_html(f.get('difference') or {})}</details>
<details open><summary>Énoncé de la tâche</summary>{_pre(f['consigne'])}</details>
<details open><summary>Règles du domaine utiles à l'outil</summary>{regl}</details>
<details open><summary>Actions attendues de la tâche</summary>{_pre(chr(10).join(f.get('attendues_lisibles', [])))}</details>
<details open><summary>Conversation entière</summary>{conv}</details>
<fieldset><legend>Ton avis sur la fiche {numero}</legend>
<label><input type="radio" name="r{numero}" value="vraie erreur">Vraie erreur</label>
<label><input type="radio" name="r{numero}" value="fausse alerte">Fausse alerte</label>
<label>Motif (en quelques mots)<input type="text" name="m{numero}" autocomplete="off"></label>
</fieldset>
</article>"""


def rendre_page(fiches_aveugles: list, premier: int = 1, nature: str = TIRAGE, tour: int | None = 1) -> str:
    """`premier` : numéro de la première fiche (au second tour, à la suite du premier) ; « Fiche k sur N » compte aussi
    les fiches du premier tour. `nature` : tour à l'aveugle, ou relecture des fortes levées après le drapeau."""
    n = len(fiches_aveugles)
    total = premier - 1 + n
    corps = "\n".join(rendre_fiche_html(f, k, total) for k, f in enumerate(fiches_aveugles, premier))
    if nature == FORTES:
        titre = "Relecture des alertes fortes"
        tete = ("<p>Ces fiches sont toutes les alertes à enjeu fort de la vague que le premier relecteur a jugées "
                "fausses alertes et que tu n'as pas encore vues. Pour chacune, ta décision l'emporte sur la sienne.</p>\n")
        avis = "Tu ne vois ni les motifs du premier relecteur, ni le modèle de l'agent."
    else:
        titre = "Relecture à l'aveugle" + (", second tour" if tour == 2 else "")
        tete = (f"<p>Second tour de cette vague : {n} nouvelles fiches, numérotées à la suite du premier tour. Aucune "
                "ne reprend une conversation que tu as déjà vue.</p>\n") if tour == 2 else ""
        avis = "Tu ne vois ni l'avis du premier relecteur, ni le modèle de l'agent."
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre}</title>
<style>{CSS}</style>
</head>
<body>
<main>
<h1>{titre} : {n} fiches</h1>
<section class="intro">
{tete}<p>Chaque fiche est une conversation entre un agent et un client. Dans cette conversation, le contrôle automatique a
marqué une écriture de l'agent comme douteuse (ligne « ACTION SIGNALÉE »). Pour chaque fiche, dis si c'est une
<strong>vraie erreur</strong> ou une <strong>fausse alerte</strong>.</p>
<p>Lis dans l'ordre : le résumé en tête, la différence champ par champ avec l'action attendue la plus proche
(calculée par le programme), l'énoncé de la tâche, les règles du domaine, les actions attendues, puis la conversation.
{avis}</p>
<p>Une fausse alerte, c'est : tâche défectueuse prouvée, simple reformulation d'un champ libre, autre chemin permis
par le règlement, ou défaut de notre code de comparaison. Sinon, c'est une vraie erreur. Les extraits restent en anglais.</p>
<p>Pour rendre tes réponses, écris un fichier CSV avec les colonnes <code>fiche,reponse,motif</code> (une ligne par fiche,
<code>reponse</code> = « vraie erreur » ou « fausse alerte »). Le bouton ci-dessous le prépare, si ton navigateur
exécute le JavaScript.</p>
</section>
{corps}
<section class="intro">
<h2>Tes réponses</h2>
<button type="button" id="generer" hidden>Préparer le CSV</button>
<noscript><p>JavaScript est désactivé : recopie tes réponses à la main dans le format ci-dessus.</p></noscript>
<textarea id="sortie" aria-label="Réponses au format CSV" readonly placeholder="fiche,reponse,motif"></textarea>
</section>
</main>
<script>{SCRIPT}</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Production
# ---------------------------------------------------------------------------
def _lire_precedents(chemins, par_id) -> tuple:
    """Fichiers déjà montrés à Otsoa dans cette vague : ([(nature, tour, ids)], [source avec SHA-256])."""
    lus, sources = [], []
    for c in chemins or ():
        brut = Path(c).read_bytes()
        t = json.loads(brut)
        if not isinstance(t, dict) or "fiches" not in t:
            raise TirageInvalide(f"{Path(c).name} : ce n'est pas un fichier de tirage (pas de « fiches »)")
        ids = [f["alerte_id"] for f in t["fiches"]]
        inconnues = sorted(set(ids) - set(par_id))
        if inconnues:
            raise TirageInvalide(f"{Path(c).name} : alertes absentes de cette vague : {inconnues[:3]}")
        nature = t.get("nature", TIRAGE)
        lus.append((nature, t.get("tour", 1) if nature == TIRAGE else None, ids))
        sources.append({"fichier": Path(c).name, "sha256": hashlib.sha256(brut).hexdigest(), "nature": nature,
                        "fiches": len(ids)})
    tours = sorted(tr for n, tr, _ in lus if n == TIRAGE)
    if tours != list(range(1, len(tours) + 1)):
        raise TirageInvalide(f"tours déjà faits incohérents : {tours}")
    if sum(1 for n, _, _ in lus if n == FORTES) > 1:
        raise TirageInvalide("deux relectures des fortes levées pour une même vague")
    return lus, sources


def produire(relecture, decisions_csv, sortie=None, rng=None, graine=None, exclure=(), fortes=False) -> dict:
    """rng/graine : seulement pour les tests. En usage normal, la graine vient de `secrets`.

    `exclure` : fichiers déjà montrés à Otsoa dans la vague (tirage_aveugle.json, fortes_levees.json). Un second tour
    écarte leurs alertes et leurs conversations ; ses fiches sont numérotées à la suite du premier tour.
    `fortes` : relecture de toutes les alertes fortes levées (après le drapeau), sauf celles qu'Otsoa a déjà jugées."""
    relecture = Path(relecture)
    sortie = Path(sortie) if sortie else relecture
    alertes = json.loads((relecture / "alertes.json").read_text(encoding="utf-8"))
    par_id = {a["id"]: a for a in alertes}
    registre = decisions.lire(decisions_csv, ids_attendus=par_id)
    levees = [i for i, d in registre.items() if d["decision"] == decisions.LEVEE]
    confirmees = [i for i, d in registre.items() if d["decision"] == decisions.CONFIRMEE]
    precedents, sources = _lire_precedents(exclure, par_id)
    deja = {i for _, _, ids in precedents for i in ids}
    tours_faits = [ids for n, _, ids in precedents if n == TIRAGE]
    if rng is None:
        graine = secrets.randbits(64)
        rng = random.Random(graine)
    motif_de = {i: registre[i]["motif"] for i in levees}
    conversation_de = {i: par_id[i].get("partie") or i for i in registre}  # une partie = une conversation
    exclues = set()
    if fortes:
        if any(n == FORTES for n, _, _ in precedents):
            raise TirageInvalide("la relecture des fortes levées de cette vague est déjà faite")
        nature, tour, premier = FORTES, None, 1
        choix = sorted(i for i in levees if par_id[i].get("enjeu") == "fort" and i not in deja)
        rng.shuffle(choix)
        signalements = [] if choix else ["aucune alerte forte levée à relire"]
    else:
        nature, tour = TIRAGE, len(tours_faits) + 1
        if tour > TOURS_MAX:
            raise TirageInvalide(f"une vague compte {TOURS_MAX} tours de relecture au plus")
        premier = 1 + sum(len(ids) for ids in tours_faits)
        exclues = {conversation_de[i] for i in deja}
        choix, signalements = tirer(levees, confirmees, rng, motif_de, conversation_de, exclues)
    nom_page, nom_json = FICHIERS[(nature, tour)]
    deja_ecrits = [str(sortie / n) for n in (nom_page, nom_json) if (sortie / n).exists()]
    if deja_ecrits:
        raise TirageInvalide(f"déjà tiré : {', '.join(deja_ecrits)} ; un tirage ne se refait pas")
    # relecture C13, P11 : le journal de la vague fait foi, quel que soit le dossier de sortie
    inscrits = [l for l in journal.lire(relecture) if l.get("type") == "tirage"]
    if any((l["nature"], l.get("tour")) == (nature, tour) for l in inscrits):
        raise TirageInvalide(f"déjà tiré selon le journal de la vague ({nature}, tour {tour}) ; un tirage ne se refait pas")
    if sum(1 for l in inscrits if l["nature"] == TIRAGE) != len(tours_faits):
        raise TirageInvalide("le journal de la vague compte des tirages qui ne sont pas passés en --exclure")
    aveugles = [json.loads((relecture / "fiches" / "aveugle" / f"{i}.json").read_text(encoding="utf-8")) for i in choix]
    page = rendre_page(aveugles, premier, nature, tour)
    noms = {a.get("modele", "") for a in alertes}
    noms = {n for n in noms if n} | {n.split("/")[-1] for n in noms if n}
    parties = {str(a["partie"]) for a in alertes if a.get("partie")}
    if fiches.contient_modele(page, noms) or any(i in page for i in par_id) or any(x in page for x in parties):
        raise AssertionError("la page révèle un nom de modèle, un identifiant d'alerte ou une partie")
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / nom_page).write_text(page, encoding="utf-8")
    resultat = {
        "nature": nature,
        "tour": tour,
        "premier_numero": premier,
        "tirage": {"levees": sum(1 for i in choix if i in levees), "confirmees": sum(1 for i in choix if i in confirmees)},
        "repartition_motifs": {m: sum(1 for i in choix if motif_de.get(i) == m) for m in sorted(set(motif_de.values()))},
        "signalements": signalements,
        "precedents": sources,
        "exclues": {"alertes": len(deja), "conversations": len(exclues)},
        "fiches": [
            {"numero": k, "alerte_id": i, "decision_claude": registre[i]["decision"], "motif_claude": registre[i]["motif"],
             "enjeu": par_id[i].get("enjeu", ""), "verdict": par_id[i]["verdict"]}
            for k, i in enumerate(choix, premier)
        ],
        "graine": graine,  # inscrite après le tirage
    }
    (sortie / nom_json).write_text(json.dumps(resultat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    journal.noter(relecture, dict(type="tirage", nature=nature, tour=tour, graine=graine, alertes=list(choix),
                                  sortie=str(sortie), page_sha256=journal.sha256(sortie / nom_page),
                                  json_sha256=journal.sha256(sortie / nom_json)))
    return resultat


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--relecture", required=True, help="dossier relecture/ produit par fiches.py")
    p.add_argument("--decisions", required=True, help="decisions.csv de Claude")
    p.add_argument("--sortie", help="défaut : le dossier relecture")
    p.add_argument("--exclure", action="append", default=[],
                   help="fichier déjà montré à Otsoa dans la vague (tirage_aveugle.json, fortes_levees.json) ; répétable")
    p.add_argument("--fortes", action="store_true", help="relecture de toutes les alertes fortes levées (après le drapeau)")
    a = p.parse_args(argv)
    try:
        r = produire(a.relecture, a.decisions, a.sortie, exclure=a.exclure, fortes=a.fortes)
    except (decisions.DecisionInvalide, ValueError, FileNotFoundError) as e:
        print(f"erreur: {e}", file=sys.stderr)
        return 2
    if r["nature"] == FORTES:
        print(f"{len(r['fiches'])} alertes fortes levées à relire par Otsoa")
    else:
        print(f"{r['tirage']['levees']} levées + {r['tirage']['confirmees']} confirmées")
        if r["tour"] > 1:
            print(f"Tour {r['tour']} : fiches {r['premier_numero']} à {r['premier_numero'] + len(r['fiches']) - 1} ; "
                  f"écartées : {r['exclues']['alertes']} alertes déjà montrées, {r['exclues']['conversations']} conversations")
    for s in r["signalements"]:
        print(f"SIGNALEMENT : {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
