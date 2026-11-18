"""Tirage public du partage calibration / confirmation, après le gel (PLAN_EXPERIENCE.md, 3.4 ; REGLE.md, pièce 9).

Le partage n'existe pas avant le gel des verdicts confirmés. Il se déduit, par un calcul figé :
- de l'empreinte SHA-256 du manifeste du gel (verdicts confirmés, tâches retirées, script final) ;
- de la valeur publiée par une balise de hasard publique : la première impulsion du NIST (Randomness Beacon 2.0)
  datée d'au moins 72 heures après l'horodatage de la soumission de l'enregistrement OSF du gel des verdicts (un
  enregistrement OSF reste annulable 48 heures : relecture C13, P2 ; un seul enregistrement compte). Si le NIST ne publie aucune impulsion dans
  l'heure qui suit cette heure désignée, on prend le premier tour de drand (réseau quicknet de la League of Entropy)
  publié à partir de la même heure. Une panne de notre réseau ne déclenche jamais ce secours : seule compte
  l'archive publique du NIST. Le tirage se lance donc au plus tôt une heure après l'heure désignée.

Le calcul n'utilise aucune bibliothèque de hasard, pour se refaire dans n'importe quel langage :
- graine = SHA-256(champ(ETIQUETTE) ‖ champ(empreinte du manifeste) ‖ champ(valeur de la balise)),
  où champ(x) = longueur de x sur 4 octets (gros-boutiste) suivie de x ;
- rang d'une tâche = SHA-256(champ(graine) ‖ champ(strate) ‖ champ(identifiant)), en hexadécimal ;
- dans chaque strate (un environnement τ-bench, ou un fichier WorkBench), les tâches sont classées par rang ; la
  première moitié, arrondie à l'inférieur, va à la calibration, le reste à la confirmation ;
- avec des paires figées d'avance (équilibrage des types rares), le plus petit rang de chaque paire va à la
  calibration, l'autre à la confirmation ; une tâche restée seule va à la confirmation.

Usage :
    tirage_public.py heure --depot 2026-12-01T10:00:00Z
    tirage_public.py tirer --manifeste <manifeste_verdicts.txt> --depot <horodatage ISO> --osf <identifiant>
                           --sortie <dossier neuf>
    tirage_public.py verifier --dossier <dossier> [--manifeste <manifeste_verdicts.txt>]
                              [--en-ligne]   (relit l'archive publique : l'impulsion est bien la première désignée)
La réserve et les paires sont celles du dépôt (`banc/tirage/`), comparées au manifeste du gel du plan
(`gel/MANIFESTE_SHA256.txt`) : le tirage refuse de partir au moindre écart (C13, P4).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ETIQUETTE = b"autonomie-meritee/partage/v1"
# Tranché par Claude (plan 3.4) ; porté de 24 à 72 heures le 07/11 (relecture C13, P2) : un enregistrement OSF reste
# annulable 48 heures après sa soumission (aide d'OSF, « Submit your draft registration »)
DELAI = timedelta(hours=72)
FENETRE_NIST = timedelta(hours=1)
NIST = "https://beacon.nist.gov/beacon/2.0"
DRAND_URL = "https://api.drand.sh"
DRAND_CHAINE = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"  # quicknet, lu le 05/11/2026
DRAND_GENESE = 1692803367  # secondes UNIX, /info du réseau quicknet
DRAND_PERIODE = 3  # secondes
RESERVE = Path(__file__).resolve().parent / "reserve.json"
PAIRES = Path(__file__).resolve().parent / "paires.json"   # obligatoires (C13, P4)
RACINE = Path(__file__).resolve().parents[2]
MANIFESTE_GEL = RACINE / "gel" / "MANIFESTE_SHA256.txt"
AGENT_HTTP = "autonomie-meritee-tirage/1.0"


class TropTot(RuntimeError):
    """L'impulsion désignée, ou la fin de la fenêtre du NIST, n'est pas encore passée."""


class AbsentDeLArchive(LookupError):
    """La balise répond qu'aucune impulsion ne correspond à la demande (HTTP 404)."""


# --------------------------------------------------------------------------- calcul

def _champ(octets: bytes) -> bytes:
    return len(octets).to_bytes(4, "big") + octets


def graine(empreinte_manifeste: str, valeur_balise: str) -> bytes:
    e = bytes.fromhex(empreinte_manifeste)
    v = bytes.fromhex(valeur_balise)
    if len(e) != 32:
        raise ValueError("empreinte du manifeste : 64 caractères hexadécimaux attendus (SHA-256)")
    if len(v) < 32:
        raise ValueError("valeur de la balise : au moins 32 octets attendus")
    return hashlib.sha256(_champ(ETIQUETTE) + _champ(e) + _champ(v)).digest()


def rang(g: bytes, strate: str, ident: str) -> str:
    return hashlib.sha256(_champ(g) + _champ(strate.encode("utf-8")) + _champ(ident.encode("utf-8"))).hexdigest()


def strates(reserve: dict) -> dict:
    """{strate: [identifiants triés]} : un environnement τ-bench par strate ; WorkBench, une strate par fichier."""
    sortie: dict = {}
    for env, ids in reserve.items():
        if len(set(ids)) != len(ids):
            raise ValueError(f"identifiant en double dans {env}")
        if env == "WorkBench":
            for i in ids:
                sortie.setdefault(f"WorkBench:{i.split(':')[0]}", []).append(i)
        else:
            sortie[env] = list(ids)
    return {k: sorted(v) for k, v in sorted(sortie.items())}


def _verifier_paires(strate: str, ids: list, groupes: list) -> None:
    vus: list = [i for paire in groupes for i in paire]
    if any(len(p) != 2 for p in groupes):
        raise ValueError(f"{strate} : chaque paire doit compter deux tâches")
    if len(set(vus)) != len(vus):
        raise ValueError(f"{strate} : une tâche figure dans deux paires")
    inconnues = set(vus) - set(ids)
    if inconnues:
        raise ValueError(f"{strate} : tâches hors de la strate : {sorted(inconnues)[:5]}")
    if len(ids) - len(vus) > 1:
        raise ValueError(f"{strate} : plus d'une tâche reste sans paire")


def partager(reserve: dict, g: bytes, paires: dict | None = None) -> dict:
    """{"calibration": {strate: [...]}, "confirmation": {strate: [...]}}."""
    cal, conf = {}, {}
    for s, ids in strates(reserve).items():
        r = {i: rang(g, s, i) for i in ids}
        if paires and s in paires:
            groupes = [list(p) for p in paires[s]]
            _verifier_paires(s, ids, groupes)
            c, f = [], []
            for a, b in groupes:
                petit, grand = sorted((a, b), key=lambda i: r[i])
                c.append(petit)
                f.append(grand)
            apparies = {i for p in groupes for i in p}
            f += [i for i in ids if i not in apparies]
        else:
            ordre = sorted(ids, key=lambda i: r[i])
            k = len(ids) // 2
            c, f = ordre[:k], ordre[k:]
        cal[s], conf[s] = sorted(c), sorted(f)
    return {"calibration": cal, "confirmation": conf}


# --------------------------------------------------------------------------- balises

def _maintenant() -> datetime:
    return datetime.now(timezone.utc)


def ecarts_gel(manifeste_gel: Path, fichiers) -> list:
    """Écarts entre des fichiers du dépôt et le manifeste du gel du plan (« sha256  chemin », chemins relatifs à la
    racine du dépôt) : la réserve et les paires du tirage doivent être celles qui ont été figées (C13, P4)."""
    if not Path(manifeste_gel).is_file():
        return [f"manifeste du gel du plan absent : {manifeste_gel}"]
    attendu = {}
    for ligne in Path(manifeste_gel).read_text(encoding="utf-8").splitlines():
        if ligne.strip():
            h, _, chemin = ligne.partition("  ")
            attendu[chemin.strip()] = h.strip().lower()
    ecarts = []
    for f in fichiers:
        try:
            rel = str(Path(f).resolve().relative_to(RACINE))
        except ValueError:
            ecarts.append(f"{f} est hors du dépôt, donc absent du manifeste du gel")
            continue
        if rel not in attendu:
            ecarts.append(f"{rel} absent du manifeste du gel")
        elif _sha256_fichier(Path(f)) != attendu[rel]:
            ecarts.append(f"{rel} diffère du manifeste du gel")
    return ecarts


def lire_iso(texte: str) -> datetime:
    d = datetime.fromisoformat(texte.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError(f"horodatage sans fuseau : {texte}")
    return d.astimezone(timezone.utc)


def iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def heure_designee(depot: datetime) -> datetime:
    return depot + DELAI


def _ms(d: datetime) -> int:
    return math.ceil(d.timestamp() * 1000)


def _plafond_minute(d: datetime) -> datetime:
    base = d.replace(second=0, microsecond=0)
    return base if base == d else base + timedelta(minutes=1)


def lire_url(url: str) -> bytes:
    requete = urllib.request.Request(url, headers={"User-Agent": AGENT_HTTP})
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            return reponse.read()
    except urllib.error.HTTPError as erreur:
        if erreur.code == 404:
            raise AbsentDeLArchive(url) from erreur
        raise


def _impulsion(lire, url: str) -> tuple:
    brut = lire(url)
    return json.loads(brut)["pulse"], brut


def impulsion_nist(heure: datetime, lire=lire_url, maintenant: datetime | None = None) -> dict | None:
    """Première impulsion du NIST datée d'au moins `heure`, si elle tombe dans l'heure qui suit ; sinon None.

    Le tirage se lance au plus tôt une heure après l'heure désignée : la fenêtre est alors close, et l'absence
    d'impulsion se lit dans l'archive publique. Toute erreur de réseau, ou une archive illisible, lève une exception :
    seule une absence constatée dans l'archive renvoie au secours drand.
    """
    maintenant = maintenant or datetime.now(timezone.utc)
    if maintenant < heure + FENETRE_NIST:
        raise TropTot(f"attendre {iso(heure + FENETRE_NIST)} : la fenêtre du NIST doit être close")
    m = _plafond_minute(heure)  # les impulsions tombent à la minute pile
    candidat = None
    try:
        p, brut = _impulsion(lire, f"{NIST}/pulse/time/{_ms(m)}")
        if lire_iso(p["timeStamp"]) == m:
            candidat = (p, brut)  # cas courant : l'impulsion de la minute désignée existe
    except AbsentDeLArchive:
        pass
    if candidat is None:  # cas rare : partir de la dernière impulsion avant la fin de la fenêtre, puis reculer
        try:
            p, brut = _impulsion(lire, f"{NIST}/pulse/time/previous/{_ms(heure + FENETRE_NIST)}")
        except AbsentDeLArchive as erreur:
            raise RuntimeError("balise du NIST : archive illisible autour de l'heure désignée ; réessayer") from erreur
        if lire_iso(p["timeStamp"]) < heure:
            return None  # aucune impulsion dans la fenêtre : secours drand
        candidat = (p, brut)
    p, brut = candidat
    t = lire_iso(p["timeStamp"])
    for _ in range(61):  # reculer tant qu'une impulsion antérieure tombe encore après l'heure désignée
        try:
            q, brut_q = _impulsion(lire, f"{NIST}/pulse/time/previous/{_ms(t)}")
        except AbsentDeLArchive:
            break
        t_q = lire_iso(q["timeStamp"])
        if t_q >= t:
            raise RuntimeError("balise du NIST : réponse « previous » non décroissante")
        if t_q < heure:
            break
        p, brut, t = q, brut_q, t_q
    else:
        raise RuntimeError("balise du NIST : plus de 60 impulsions dans la fenêtre, réponse incohérente")
    p_uri, _ = _impulsion(lire, p["uri"])
    if p_uri.get("outputValue") != p["outputValue"] or p_uri.get("timeStamp") != p["timeStamp"]:
        raise RuntimeError("balise du NIST : l'impulsion lue par son adresse de chaîne diffère")
    return {"source": "nist", "url": p["uri"], "heure_impulsion": p["timeStamp"],
            "valeur": p["outputValue"].lower(), "brut": brut.decode("utf-8")}


def tour_drand(heure: datetime) -> int:
    return max(1, math.ceil((heure.timestamp() - DRAND_GENESE) / DRAND_PERIODE) + 1)


def heure_tour_drand(tour: int) -> datetime:
    return datetime.fromtimestamp(DRAND_GENESE + (tour - 1) * DRAND_PERIODE, tz=timezone.utc)


def impulsion_drand(heure: datetime, lire=lire_url, maintenant: datetime | None = None) -> dict:
    """Premier tour de drand (quicknet) publié à partir de `heure` ; le hasard vaut SHA-256(signature)."""
    tour = tour_drand(heure)
    maintenant = maintenant or datetime.now(timezone.utc)
    if maintenant < heure_tour_drand(tour):
        raise TropTot(f"tour drand {tour} pas encore publié")
    url = f"{DRAND_URL}/{DRAND_CHAINE}/public/{tour}"
    brut = lire(url)
    d = json.loads(brut)
    if d.get("round") != tour:
        raise RuntimeError(f"drand : tour {d.get('round')} reçu, {tour} attendu")
    if hashlib.sha256(bytes.fromhex(d["signature"])).hexdigest() != d["randomness"].lower():
        raise RuntimeError("drand : le hasard publié n'est pas le SHA-256 de la signature")
    return {"source": "drand", "url": url, "heure_impulsion": iso(heure_tour_drand(tour)),
            "valeur": d["randomness"].lower(), "brut": brut.decode("utf-8")}


def valeur_depuis_brut(impulsion: dict) -> str:
    d = json.loads(impulsion["brut"])
    return (d["pulse"]["outputValue"] if impulsion["source"] == "nist" else d["randomness"]).lower()


# --------------------------------------------------------------------------- tirage et vérification

def _sha256_fichier(chemin: Path | None) -> str | None:
    return hashlib.sha256(chemin.read_bytes()).hexdigest() if chemin else None


def tirer(empreinte_manifeste: str, depot: datetime, reserve: dict, paires: dict | None = None,
          lire=lire_url, maintenant: datetime | None = None) -> tuple:
    heure = heure_designee(depot)
    impulsion = impulsion_nist(heure, lire, maintenant)
    if impulsion is None:
        impulsion = impulsion_drand(heure, lire, maintenant)
    impulsion = {"horodatage_depot": iso(depot), "heure_designee": iso(heure), **impulsion}
    g = graine(empreinte_manifeste, impulsion["valeur"])
    return impulsion, g, partager(reserve, g, paires)


def ecrire(dossier: Path, empreinte_manifeste: str, impulsion: dict, g: bytes, partage: dict,
           chemin_reserve: Path, chemin_paires: Path | None) -> dict:
    dossier.mkdir(parents=True, exist_ok=True)
    contenu = {
        "version": ETIQUETTE.decode(),
        "empreinte_manifeste": empreinte_manifeste.lower(),
        "source": impulsion["source"],
        "valeur_balise": impulsion["valeur"],
        "graine": g.hex(),
        "empreinte_reserve": _sha256_fichier(chemin_reserve),
        "empreinte_paires": _sha256_fichier(chemin_paires),
        "effectifs": {s: [len(partage["calibration"][s]), len(partage["confirmation"][s])] for s in partage["calibration"]},
        **partage,
    }
    (dossier / "impulsion.json").write_text(json.dumps(impulsion, indent=1, ensure_ascii=False), encoding="utf-8")
    (dossier / "partage.json").write_text(json.dumps(contenu, indent=1, ensure_ascii=False), encoding="utf-8")
    return {nom: _sha256_fichier(dossier / nom) for nom in ("impulsion.json", "partage.json")}


def ecarts_impulsion(impulsion: dict, confirmee_en_ligne: bool = False) -> list:
    """Écarts entre l'impulsion brute et l'impulsion désignée, sans réseau (revue « ultra » du 06/11, constat 4).
    NIST : l'impulsion brute est celle déclarée (heure, adresse), dans l'heure qui suit l'heure désignée, et celle de
    la première minute ; si cette minute manque à l'archive, seule la vérification en ligne peut le confirmer. drand :
    le tour brut est le tour désigné, sur quicknet, et son hasard est le SHA-256 de sa signature. Sans la signature de
    la balise vérifiée, une impulsion fabriquée de toutes pièces ne se voit qu'en ligne (`verifier --en-ligne`)."""
    ecarts = []
    heure = lire_iso(impulsion["heure_designee"])
    brut = json.loads(impulsion["brut"])
    if impulsion["source"] == "nist":
        p = brut["pulse"]
        t = lire_iso(p["timeStamp"])
        if t != lire_iso(impulsion["heure_impulsion"]):
            ecarts.append("l'heure de l'impulsion brute n'est pas celle déclarée")
        if p.get("uri") != impulsion.get("url"):
            ecarts.append("l'adresse de l'impulsion brute n'est pas celle déclarée")
        if not heure <= t < heure + FENETRE_NIST:
            ecarts.append("l'impulsion brute du NIST tombe hors de l'heure qui suit l'heure désignée")
        elif t != _plafond_minute(heure) and not confirmee_en_ligne:
            ecarts.append(f"l'impulsion brute du NIST ({iso(t)}) n'est pas celle de la première minute "
                          f"({iso(_plafond_minute(heure))}) : confirmer avec verifier --en-ligne qu'aucune impulsion "
                          f"ne la précède dans la fenêtre")
    elif impulsion["source"] == "drand":
        tour = tour_drand(heure)
        if brut.get("round") != tour:
            ecarts.append(f"le tour drand de l'impulsion brute ({brut.get('round')}) n'est pas le tour désigné ({tour})")
        try:
            lie = hashlib.sha256(bytes.fromhex(brut["signature"])).hexdigest() == str(brut["randomness"]).lower()
        except (KeyError, ValueError, TypeError):
            lie = False
        if not lie:
            ecarts.append("drand : le hasard brut n'est pas le SHA-256 de la signature")
        if impulsion.get("url") != f"{DRAND_URL}/{DRAND_CHAINE}/public/{tour}":
            ecarts.append("drand : l'adresse n'est pas celle du tour désigné sur quicknet")
        if lire_iso(impulsion["heure_impulsion"]) != heure_tour_drand(tour):
            ecarts.append("drand : l'heure déclarée n'est pas celle du tour désigné")
    else:
        ecarts.append(f"source de balise inconnue : {impulsion['source']}")
    return ecarts


def verifier(dossier: Path, chemin_reserve: Path, chemin_paires: Path | None = None, lire=None,
             maintenant: datetime | None = None) -> list:
    """Refait le tirage à partir des fichiers écrits ; renvoie la liste des écarts (vide si tout concorde). Avec
    `lire` (en ligne), refait aussi la sélection de l'impulsion dans les archives publiques, comme `tirer`."""
    impulsion = json.loads((dossier / "impulsion.json").read_text(encoding="utf-8"))
    partage = json.loads((dossier / "partage.json").read_text(encoding="utf-8"))
    confirmee, ecart_en_ligne = False, None
    if lire is not None:  # revue « ultra » du 06/11, constat 4 : l'impulsion est bien la première désignée
        heure = lire_iso(impulsion["heure_designee"])
        attendu = impulsion_nist(heure, lire, maintenant) or impulsion_drand(heure, lire, maintenant)
        confirmee = (attendu["source"], attendu["valeur"]) == (impulsion["source"], impulsion["valeur"])
        if not confirmee:
            ecart_en_ligne = (f"l'impulsion désignée relue dans l'archive publique ({attendu['source']}, "
                              f"{attendu['heure_impulsion']}) n'est pas celle du tirage")
    ecarts = ecarts_impulsion(impulsion, confirmee) + ([ecart_en_ligne] if ecart_en_ligne else [])
    if partage["empreinte_reserve"] != _sha256_fichier(chemin_reserve):
        ecarts.append("la réserve n'est pas celle du tirage")
    if partage["empreinte_paires"] != _sha256_fichier(chemin_paires):
        ecarts.append("les paires ne sont pas celles du tirage")
    valeur = valeur_depuis_brut(impulsion)
    if valeur != impulsion["valeur"] or valeur != partage["valeur_balise"]:
        ecarts.append("la valeur de la balise ne correspond pas à l'impulsion brute")
    if impulsion["source"] == "nist" and lire_iso(impulsion["heure_impulsion"]) < lire_iso(impulsion["heure_designee"]):
        ecarts.append("l'impulsion est antérieure à l'heure désignée")
    if lire_iso(impulsion["heure_designee"]) != heure_designee(lire_iso(impulsion["horodatage_depot"])):
        ecarts.append("l'heure désignée n'est pas l'horodatage du dépôt plus 72 heures")
    g = graine(partage["empreinte_manifeste"], valeur)
    if g.hex() != partage["graine"]:
        ecarts.append("la graine ne se recalcule pas")
    reserve = json.loads(chemin_reserve.read_text(encoding="utf-8"))
    paires = json.loads(chemin_paires.read_text(encoding="utf-8")) if chemin_paires else None
    refait = partager(reserve, g, paires)
    for jeu in ("calibration", "confirmation"):
        if refait[jeu] != partage[jeu]:
            ecarts.append(f"le jeu de {jeu} ne se recalcule pas")
    return ecarts


# --------------------------------------------------------------------------- ligne de commande

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = p.add_subparsers(dest="commande", required=True)
    h = sous.add_parser("heure", help="heure désignée et adresses à lire, pour le texte du dépôt du gel")
    h.add_argument("--depot", required=True, help="horodatage du dépôt du gel sur OSF (ISO 8601, avec fuseau)")
    t = sous.add_parser("tirer", help="lit la balise et écrit le partage")
    t.add_argument("--manifeste", required=True, type=Path,
                   help="fichier du manifeste du gel des verdicts (gel/manifeste_verdicts.py) : son SHA-256 entre "
                        "dans la graine")
    t.add_argument("--depot", required=True, help="horodatage de la soumission de l'enregistrement OSF")
    t.add_argument("--osf", required=True, help="identifiant de l'enregistrement OSF du gel des verdicts (un seul)")
    t.add_argument("--sortie", required=True, type=Path, help="dossier neuf : un tirage ne se refait pas")
    t.add_argument("--reserve", type=Path, default=RESERVE)
    t.add_argument("--paires", type=Path, default=PAIRES)
    t.add_argument("--manifeste-gel", type=Path, default=MANIFESTE_GEL)
    v = sous.add_parser("verifier", help="refait le tirage à partir des fichiers écrits")
    v.add_argument("--dossier", required=True, type=Path)
    v.add_argument("--manifeste", type=Path, help="fichier du manifeste des verdicts, comparé à son empreinte")
    v.add_argument("--reserve", type=Path, default=RESERVE)
    v.add_argument("--paires", type=Path, default=PAIRES)
    v.add_argument("--manifeste-gel", type=Path, default=MANIFESTE_GEL)
    v.add_argument("--en-ligne", action="store_true",
                   help="relit aussi l'archive publique (NIST, sinon drand) pour confirmer l'impulsion désignée")
    a = p.parse_args(argv)

    if a.commande == "heure":
        heure = heure_designee(lire_iso(a.depot))
        print(f"heure désignée : {iso(heure)}")
        print(f"NIST : première impulsion datée d'au moins cette heure ({NIST}/pulse/time/{_ms(_plafond_minute(heure))})")
        print(f"secours drand : tour {tour_drand(heure)} ({DRAND_URL}/{DRAND_CHAINE}/public/{tour_drand(heure)})")
        return 0
    if a.commande == "tirer":
        if a.sortie.exists() and any(a.sortie.iterdir()):
            print(f"REFUS : {a.sortie} n'est pas vide ; un tirage ne se refait pas")
            return 2
        ecarts = ecarts_gel(a.manifeste_gel, [a.reserve, a.paires])
        if ecarts:
            for e in ecarts:
                print(f"REFUS : {e}")
            return 2
        empreinte = _sha256_fichier(a.manifeste)
        reserve = json.loads(a.reserve.read_text(encoding="utf-8"))
        paires = json.loads(a.paires.read_text(encoding="utf-8"))
        impulsion, g, partage = tirer(empreinte, lire_iso(a.depot), reserve, paires, lire=lire_url,
                                      maintenant=_maintenant())
        impulsion = {"enregistrement_osf": a.osf, **impulsion}
        empreintes = ecrire(a.sortie, empreinte, impulsion, g, partage, a.reserve, a.paires)
        print(f"source : {impulsion['source']} ({impulsion['heure_impulsion']})")
        for nom, valeur in empreintes.items():
            print(f"SHA-256 {nom} : {valeur}")
        return 0
    ecarts = verifier(a.dossier, a.reserve, a.paires, lire=lire_url if a.en_ligne else None,
                      maintenant=_maintenant() if a.en_ligne else None)
    ecarts += ecarts_gel(a.manifeste_gel, [a.reserve, a.paires])
    partage = json.loads((a.dossier / "partage.json").read_text(encoding="utf-8"))
    if partage.get("empreinte_paires") is None:
        ecarts.append("tirage sans paires : le plan les rend obligatoires (C13, P4)")
    if a.manifeste is not None and _sha256_fichier(a.manifeste) != partage["empreinte_manifeste"]:
        ecarts.append("le manifeste des verdicts donné n'est pas celui du tirage")
    for e in ecarts:
        print(f"ÉCART : {e}")
    print("tirage vérifié" if not ecarts else f"{len(ecarts)} écart(s)")
    return 1 if ecarts else 0


if __name__ == "__main__":
    sys.exit(main())
