"""Tirage public du partage (banc/tirage/tirage_public.py ; PLAN_EXPERIENCE.md, 3.4). Aucun accès au réseau."""
import hashlib
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tirage"))
import tirage_public as tp  # noqa: E402

UTC = timezone.utc
MANIFESTE = hashlib.sha256(b"manifeste du gel, essai").hexdigest()
VALEUR = hashlib.sha512(b"impulsion, essai").hexdigest()
RESERVE_ESSAI = {
    "aviation": [str(i) for i in range(9)],
    "commerce": [str(i) for i in range(6)],
    "WorkBench": ["agenda:1", "agenda:2", "agenda:3", "mail:1", "mail:2"],
}


# --------------------------------------------------------------------------- calcul

def test_graine_deterministe_et_sensible_aux_deux_entrees():
    g = tp.graine(MANIFESTE, VALEUR)
    assert g == tp.graine(MANIFESTE, VALEUR)
    assert g != tp.graine(hashlib.sha256(b"autre").hexdigest(), VALEUR)
    assert g != tp.graine(MANIFESTE, hashlib.sha512(b"autre").hexdigest())


def test_graine_refuse_une_empreinte_mal_formee():
    with pytest.raises(ValueError):
        tp.graine("abcd", VALEUR)
    with pytest.raises(ValueError):
        tp.graine(MANIFESTE, "00" * 8)


def test_rang_depend_de_la_strate():
    g = tp.graine(MANIFESTE, VALEUR)
    assert tp.rang(g, "aviation", "5") != tp.rang(g, "commerce", "5")


def test_strates_workbench_par_fichier():
    s = tp.strates(RESERVE_ESSAI)
    assert set(s) == {"aviation", "commerce", "WorkBench:agenda", "WorkBench:mail"}
    assert s["WorkBench:mail"] == ["mail:1", "mail:2"]


def test_strates_refuse_les_doublons():
    with pytest.raises(ValueError):
        tp.strates({"aviation": ["1", "1"]})


def test_partage_moitie_par_strate_et_tache_en_plus_a_la_confirmation():
    part = tp.partager(RESERVE_ESSAI, tp.graine(MANIFESTE, VALEUR))
    for s, ids in tp.strates(RESERVE_ESSAI).items():
        cal, conf = part["calibration"][s], part["confirmation"][s]
        assert len(cal) == len(ids) // 2 and len(conf) == len(ids) - len(ids) // 2
        assert not set(cal) & set(conf) and sorted(cal + conf) == ids


def test_partage_reproduit_par_un_calcul_independant():
    """Le classement se refait avec hashlib seul : aucune bibliothèque de hasard n'intervient."""
    g = tp.graine(MANIFESTE, VALEUR)

    def champ(b):
        return len(b).to_bytes(4, "big") + b

    ids = RESERVE_ESSAI["aviation"]
    ordre = sorted(ids, key=lambda i: hashlib.sha256(champ(g) + champ(b"aviation") + champ(i.encode())).hexdigest())
    assert tp.partager(RESERVE_ESSAI, g)["calibration"]["aviation"] == sorted(ordre[: len(ids) // 2])


def test_partage_independant_de_l_ordre_d_entree():
    g = tp.graine(MANIFESTE, VALEUR)
    melange = {k: random.Random(7).sample(v, len(v)) for k, v in RESERVE_ESSAI.items()}
    assert tp.partager(melange, g) == tp.partager(RESERVE_ESSAI, g)


def test_partage_change_avec_la_valeur_de_la_balise():
    a = tp.partager(RESERVE_ESSAI, tp.graine(MANIFESTE, VALEUR))
    b = tp.partager(RESERVE_ESSAI, tp.graine(MANIFESTE, hashlib.sha512(b"autre impulsion").hexdigest()))
    assert a != b


def test_paires_departagees_et_tache_seule_a_la_confirmation():
    paires = {"aviation": [["0", "1"], ["2", "3"], ["4", "5"], ["6", "7"]]}
    part = tp.partager(RESERVE_ESSAI, tp.graine(MANIFESTE, VALEUR), paires)
    cal, conf = part["calibration"]["aviation"], part["confirmation"]["aviation"]
    for a, b in paires["aviation"]:
        assert (a in cal) != (b in cal)
    assert "8" in conf and len(cal) == 4 and len(conf) == 5


@pytest.mark.parametrize("paires", [
    {"aviation": [["0", "1"], ["1", "2"]]},          # une tâche dans deux paires
    {"aviation": [["0", "99"]]},                      # tâche hors de la strate
    {"aviation": [["0", "1"], ["2", "3"]]},          # cinq tâches restent seules
    {"aviation": [["0", "1", "2"]]},                  # paire de trois
])
def test_paires_invalides_refusees(paires):
    with pytest.raises(ValueError):
        tp.partager(RESERVE_ESSAI, tp.graine(MANIFESTE, VALEUR), paires)


def test_reserve_reelle_couverte_entierement():
    reserve = json.loads(tp.RESERVE.read_text(encoding="utf-8"))
    part = tp.partager(reserve, tp.graine(MANIFESTE, VALEUR))
    assert len(part["calibration"]["aviation"]) == 20 and len(part["confirmation"]["aviation"]) == 20
    assert len(part["calibration"]["commerce"]) == 45 and len(part["confirmation"]["commerce"]) == 46
    assert len(part["calibration"]["banque"]) == 38 and len(part["confirmation"]["banque"]) == 39
    wb = [i for s in part["calibration"] if s.startswith("WorkBench:")
          for i in part["calibration"][s] + part["confirmation"][s]]
    assert sorted(wb) == sorted(reserve["WorkBench"])


# --------------------------------------------------------------------------- balises

class FausseBalise:
    """Archive du NIST simulée : impulsions à la minute pile, sauf les minutes manquantes."""

    def __init__(self, debut, minutes, manquantes=(), tricher_uri=False):
        self.impulsions = []
        for k in range(minutes):
            t = debut + timedelta(minutes=k)
            if t in manquantes:
                continue
            self.impulsions.append({
                "uri": f"https://beacon.nist.gov/beacon/2.0/chain/2/pulse/{k}",
                "timeStamp": tp.iso(t),
                "outputValue": hashlib.sha512(tp.iso(t).encode()).hexdigest().upper(),
            })
        self.tricher_uri = tricher_uri
        self.appels = []

    def _temps(self, p):
        return tp.lire_iso(p["timeStamp"])

    def _brut(self, p):
        return json.dumps({"pulse": p}).encode()

    def __call__(self, url):
        self.appels.append(url)
        if "/chain/" in url:
            p = next(p for p in self.impulsions if p["uri"] == url)
            if self.tricher_uri:
                p = {**p, "outputValue": "00" * 64}
            return self._brut(p)
        ms = int(url.rsplit("/", 1)[1])
        t = datetime.fromtimestamp(ms / 1000, tz=UTC)
        if "/time/previous/" in url:
            avant = [p for p in self.impulsions if self._temps(p) < t]
            if not avant:
                raise tp.AbsentDeLArchive(url)
            return self._brut(avant[-1])
        if "/time/next/" in url:
            apres = [p for p in self.impulsions if self._temps(p) > t]
            if not apres:
                raise tp.AbsentDeLArchive(url)
            return self._brut(apres[0])
        if not self.impulsions:
            raise tp.AbsentDeLArchive(url)
        return self._brut(min(self.impulsions, key=lambda p: abs((self._temps(p) - t).total_seconds())))


HEURE = datetime(2026, 12, 2, 10, 0, 20, tzinfo=UTC)
APRES = HEURE + timedelta(hours=2)


def test_heure_designee_est_le_depot_plus_72_heures():
    """C13, P2 : un enregistrement OSF reste annulable 48 heures ; l'impulsion tombe 72 heures après la soumission."""
    depot = datetime(2026, 11, 29, 10, 0, 20, tzinfo=UTC)
    assert tp.DELAI == timedelta(hours=72) and tp.heure_designee(depot) == HEURE


def test_nist_premiere_impulsion_a_la_minute_suivante():
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240)
    imp = tp.impulsion_nist(HEURE, balise, APRES)
    assert imp["source"] == "nist" and imp["heure_impulsion"] == "2026-12-02T10:01:00.000Z"
    assert imp["valeur"] == hashlib.sha512(b"2026-12-02T10:01:00.000Z").hexdigest()


def test_nist_heure_pile_prend_l_impulsion_de_cette_minute():
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240)
    pile = datetime(2026, 12, 2, 10, 0, tzinfo=UTC)
    assert tp.impulsion_nist(pile, balise, APRES)["heure_impulsion"] == "2026-12-02T10:00:00.000Z"


def test_nist_trou_dans_l_archive_prend_la_premiere_impulsion_apres():
    trou = {datetime(2026, 12, 2, 10, k, tzinfo=UTC) for k in range(1, 6)}
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240, manquantes=trou)
    assert tp.impulsion_nist(HEURE, balise, APRES)["heure_impulsion"] == "2026-12-02T10:06:00.000Z"


def test_nist_aucune_impulsion_dans_l_heure_renvoie_au_secours():
    trou = {datetime(2026, 12, 2, 10, 0, tzinfo=UTC) + timedelta(minutes=k) for k in range(1, 62)}
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240, manquantes=trou)
    assert tp.impulsion_nist(HEURE, balise, APRES) is None


def test_nist_trop_tot_tant_que_la_fenetre_n_est_pas_close():
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240)
    with pytest.raises(tp.TropTot):
        tp.impulsion_nist(HEURE, balise, HEURE + timedelta(minutes=30))


def test_nist_erreur_reseau_ne_bascule_jamais_sur_le_secours():
    def panne(url):
        raise OSError("réseau coupé")

    with pytest.raises(OSError):
        tp.impulsion_nist(HEURE, panne, APRES)


def test_nist_incoherence_entre_deux_adresses_detectee():
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240, tricher_uri=True)
    with pytest.raises(RuntimeError):
        tp.impulsion_nist(HEURE, balise, APRES)


def test_drand_tour_et_heure_du_tour():
    heure = datetime(2026, 11, 5, 15, 0, 30, tzinfo=UTC)
    assert tp.tour_drand(heure) == 33695822  # vérifié sur l'API publique le 05/11/2026
    r = tp.tour_drand(HEURE)
    assert tp.heure_tour_drand(r) >= HEURE > tp.heure_tour_drand(r - 1)


def test_drand_hasard_egal_au_sha256_de_la_signature():
    """Valeurs réelles du tour 33695822 de quicknet, lues le 05/11/2026."""
    brut = json.dumps({
        "round": 33695822,
        "randomness": "7f98f960e75bf93de6d1e2529165c2fc8a01e62d0cc7e61147ead4591c99ad25",
        "signature": "93236b2a63bc5e6f8954ed1d0f2fe2aef75b852740d3fcfe95895b34a7d84b144626b3d1c7ea3abf6867e076aded136f",
    }).encode()
    heure = datetime(2026, 11, 5, 15, 0, 30, tzinfo=UTC)
    imp = tp.impulsion_drand(heure, lambda url: brut, heure + timedelta(hours=2))
    assert imp["valeur"] == "7f98f960e75bf93de6d1e2529165c2fc8a01e62d0cc7e61147ead4591c99ad25"
    falsifie = json.loads(brut)
    falsifie["randomness"] = "00" * 32
    with pytest.raises(RuntimeError):
        tp.impulsion_drand(heure, lambda url: json.dumps(falsifie).encode(), heure + timedelta(hours=2))


# --------------------------------------------------------------------------- bout en bout

def _reserve_sur_disque(tmp_path):
    chemin = tmp_path / "reserve.json"
    chemin.write_text(json.dumps(RESERVE_ESSAI), encoding="utf-8")
    return chemin


def test_tirer_ecrire_verifier(tmp_path):
    chemin = _reserve_sur_disque(tmp_path)
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240)
    depot = HEURE - tp.DELAI
    imp, g, part = tp.tirer(MANIFESTE, depot, RESERVE_ESSAI, lire=balise, maintenant=APRES)
    dossier = tmp_path / "tirage"
    empreintes = tp.ecrire(dossier, MANIFESTE, imp, g, part, chemin, None)
    assert set(empreintes) == {"impulsion.json", "partage.json"}
    assert tp.verifier(dossier, chemin) == []


def test_verifier_detecte_un_partage_retouche(tmp_path):
    chemin = _reserve_sur_disque(tmp_path)
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240)
    imp, g, part = tp.tirer(MANIFESTE, HEURE - tp.DELAI, RESERVE_ESSAI, lire=balise, maintenant=APRES)
    dossier = tmp_path / "tirage"
    tp.ecrire(dossier, MANIFESTE, imp, g, part, chemin, None)
    partage = json.loads((dossier / "partage.json").read_text(encoding="utf-8"))
    cal, conf = partage["calibration"]["aviation"], partage["confirmation"]["aviation"]
    cal[0], conf[0] = conf[0], cal[0]
    (dossier / "partage.json").write_text(json.dumps(partage), encoding="utf-8")
    assert "le jeu de calibration ne se recalcule pas" in tp.verifier(dossier, chemin)


def test_verifier_detecte_une_impulsion_retouchee(tmp_path):
    chemin = _reserve_sur_disque(tmp_path)
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240)
    imp, g, part = tp.tirer(MANIFESTE, HEURE - tp.DELAI, RESERVE_ESSAI, lire=balise, maintenant=APRES)
    dossier = tmp_path / "tirage"
    tp.ecrire(dossier, MANIFESTE, imp, g, part, chemin, None)
    impulsion = json.loads((dossier / "impulsion.json").read_text(encoding="utf-8"))
    impulsion["valeur"] = hashlib.sha512(b"autre").hexdigest()
    (dossier / "impulsion.json").write_text(json.dumps(impulsion), encoding="utf-8")
    assert tp.verifier(dossier, chemin)


def test_secours_drand_bout_en_bout(tmp_path):
    trou = {datetime(2026, 12, 2, 10, 0, tzinfo=UTC) + timedelta(minutes=k) for k in range(1, 62)}
    nist = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240, manquantes=trou)
    signature = "ab" * 48

    def lire(url):
        if "drand" in url:
            tour = int(url.rsplit("/", 1)[1])
            return json.dumps({"round": tour, "signature": signature,
                               "randomness": hashlib.sha256(bytes.fromhex(signature)).hexdigest()}).encode()
        return nist(url)

    imp, g, part = tp.tirer(MANIFESTE, HEURE - tp.DELAI, RESERVE_ESSAI, lire=lire, maintenant=APRES)
    assert imp["source"] == "drand"
    chemin = _reserve_sur_disque(tmp_path)
    tp.ecrire(tmp_path / "t", MANIFESTE, imp, g, part, chemin, None)
    assert tp.verifier(tmp_path / "t", chemin) == []


# --------------------------------------------------------------------------- C13 : paires, manifestes, OSF

REEL = Path(__file__).resolve().parents[1] / "tirage"


def _manifeste_gel(tmp_path, fichiers, retouche=None):
    """Un manifeste du gel du plan au format « sha256  chemin », chemins relatifs à la racine du dépôt."""
    racine = Path(__file__).resolve().parents[2]
    lignes = []
    for f in fichiers:
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        if retouche == f.name:
            h = "0" * 64
        lignes.append(f"{h}  {f.resolve().relative_to(racine)}")
    chemin = tmp_path / "MANIFESTE_SHA256.txt"
    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return chemin


def test_ecarts_gel(tmp_path):
    reserve, paires = REEL / "reserve.json", REEL / "paires.json"
    assert tp.ecarts_gel(_manifeste_gel(tmp_path, [reserve, paires]), [reserve, paires]) == []
    assert any("diffère" in e for e in tp.ecarts_gel(_manifeste_gel(tmp_path, [reserve, paires], "paires.json"),
                                                     [reserve, paires]))
    assert any("absent du manifeste" in e for e in tp.ecarts_gel(_manifeste_gel(tmp_path, [reserve]),
                                                                 [reserve, paires]))
    assert any("manifeste du gel" in e for e in tp.ecarts_gel(tmp_path / "rien.txt", [reserve]))


def test_cli_tirer_paires_par_defaut_manifeste_fichier_et_osf(tmp_path, monkeypatch):
    """La ligne de commande prend les paires figées par défaut, lit le manifeste des verdicts comme un fichier, note
    l'enregistrement OSF ; elle refuse sans manifeste du gel du plan conforme, et ne réécrit jamais un tirage."""
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240)
    monkeypatch.setattr(tp, "lire_url", balise)
    monkeypatch.setattr(tp, "_maintenant", lambda: APRES)
    verdicts = tmp_path / "manifeste_verdicts.txt"
    verdicts.write_text("ab" * 32 + "  vague1/actions_typees.csv\n", encoding="utf-8")
    gel = _manifeste_gel(tmp_path, [REEL / "reserve.json", REEL / "paires.json"])
    sortie = tmp_path / "tirage"
    args = ["tirer", "--manifeste", str(verdicts), "--depot", tp.iso(HEURE - tp.DELAI), "--osf", "abcd1",
            "--sortie", str(sortie), "--manifeste-gel", str(gel)]
    assert tp.main(args) == 0
    partage = json.loads((sortie / "partage.json").read_text(encoding="utf-8"))
    impulsion = json.loads((sortie / "impulsion.json").read_text(encoding="utf-8"))
    assert partage["empreinte_paires"] == hashlib.sha256((REEL / "paires.json").read_bytes()).hexdigest()
    assert partage["empreinte_manifeste"] == hashlib.sha256(verdicts.read_bytes()).hexdigest()
    assert impulsion["enregistrement_osf"] == "abcd1"
    assert tp.main(args) == 2                                  # un tirage ne se refait pas dans le même dossier
    assert tp.main(["verifier", "--dossier", str(sortie), "--manifeste-gel", str(gel),
                    "--manifeste", str(verdicts)]) == 0
    autre = _manifeste_gel(tmp_path, [REEL / "reserve.json", REEL / "paires.json"], "reserve.json")
    assert tp.main(args[:-4] + ["--sortie", str(tmp_path / "t2"), "--manifeste-gel", str(autre)]) == 2


def test_cli_verifier_refuse_un_tirage_sans_paires(tmp_path, monkeypatch):
    reserve = REEL / "reserve.json"
    balise = FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=UTC), 240)
    imp, g, part = tp.tirer(MANIFESTE, HEURE - tp.DELAI, json.loads(reserve.read_text(encoding="utf-8")),
                            lire=balise, maintenant=APRES)
    dossier = tmp_path / "tirage"
    tp.ecrire(dossier, MANIFESTE, imp, g, part, reserve, None)
    gel = _manifeste_gel(tmp_path, [reserve, REEL / "paires.json"])
    assert tp.main(["verifier", "--dossier", str(dossier), "--manifeste-gel", str(gel)]) == 1
