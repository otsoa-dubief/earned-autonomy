"""Non-régression des constats de la revue « ultra » du banc (06/11 ; copie `autonomie-meritee-revue-banc`) : chaque
test affirme le comportement corrigé. Aucun appel réel : exécuteur factice ou enfant simulé, dossiers temporaires."""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

import cout_v2 as cv
import lanceur as L
import pilote_etape1 as pe
import test_lanceur as T
import test_lanceur_revue as TR


# ======================================================================== #2 : exception de l'exécuteur après le jeu
def test_u2_exception_de_l_executeur_apres_le_jeu_cout_lu_dans_l_usage_et_arret(tmp_path):
    """L'exécuteur lève après le run enfant (disque plein en copiant la trace) : la dépense de l'usage est comptée, le
    lanceur s'arrête avant toute nouvelle partie, et la partie n'est pas rejouée en silence."""
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    (ctx["sortie"] / "usage").mkdir()

    def ex(t, c):
        T.ecrire_usage(c["sortie"] / "usage" / f"{t['id']}.jsonl", [("claude-opus-5-5", "claude-opus-5-5", 10_000, 0)])
        raise OSError(28, "No space left on device")

    file = [(TR.partie_tau(), 1), (TR.partie_tau(tache="2"), 1)]
    L.lancer_vague(file, 1, compta, ctx, journal, ex)
    assert [l["id"] for l in reg.lignes] == [file[0][0]["id"]]  # ni relance, ni partie suivante
    attendu = cv.bilan(L.lire_usage(ctx["sortie"] / "usage" / f"{file[0][0]['id']}.jsonl")[0])["cout_usd"]
    assert reg.lignes[0]["cout_usd"] == pytest.approx(attendu) and attendu > 0
    assert compta.cumul == pytest.approx(attendu)
    assert compta.arret and "exception" in compta.arret and not reg.lignes[0]["cout_inconnu"]


def test_u2_exception_de_l_executeur_sans_usage_lisible_cout_inconnu_et_arret(tmp_path):
    """Sans usage lisible, la dépense est inconnue : arrêt, et la reprise exigera un montant retenu (--cout-retenu)."""
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)

    def ex(t, c):
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "octet invalide")

    L.lancer_vague([(TR.partie_tau(), 1), (TR.partie_tau(tache="2"), 1)], 1, compta, ctx, journal, ex)
    assert len(reg.lignes) == 1 and reg.lignes[0]["cout_inconnu"] and reg.lignes[0]["cout_usd"] is None
    assert compta.arret and "--cout-retenu" in compta.arret
    assert L.couts_inconnus_en_suspens(reg.lignes) == [reg.lignes[0]["id"]]


# ======================================================================== #3 : reprise pendant que des enfants tournent
def test_u3_executer_enfant_note_le_pid_pendant_le_jeu_et_l_efface_apres(tmp_path):
    """Avec PILOTE_FICHIER_PID, le PID de l'enfant est noté pendant qu'il tourne, puis effacé ; la variable n'est pas
    transmise à l'enfant ; le délai dépassé tue l'enfant et efface aussi le fichier."""
    f = tmp_path / "enfants" / "x.json"
    code_enfant = ("import json, os, sys, time; time.sleep(0.3); d = json.load(open(sys.argv[1])); "
                   "print(d['pid'] == os.getpid(), os.environ.get('PILOTE_FICHIER_PID'))")
    env = dict(os.environ, PILOTE_FICHIER_PID=str(f))
    log = tmp_path / "log.txt"
    assert pe.executer_enfant([sys.executable, "-c", code_enfant, str(f)], env, tmp_path, log) == 0
    assert log.read_text().startswith("True None") and not f.exists()
    lent = [sys.executable, "-c", "import time; time.sleep(30)"]
    assert pe.executer_enfant(lent, env, tmp_path, log, delai=1) == -1 and not f.exists()


def test_u3_reprise_refusee_tant_qu_un_enfant_de_l_arret_precedent_vit_encore(tmp_path, monkeypatch, capsys):
    """Le lanceur a été tué ; l'enfant d'une tentative orpheline tourne encore (il dépense toujours, et son usage
    grandit) : la reprise est refusée sans rien toucher. Une fois l'enfant fini, la reprise compte son usage."""
    T.neutraliser(monkeypatch, tmp_path)
    assert L.main(T.argv(tmp_path, "--limite", "2"), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    d = T.dossier_unique(tmp_path)
    tid = TR.orpheline(d, 2, lisible=True)
    enfant = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        (d / "enfants").mkdir()
        (d / "enfants" / f"{tid}.json").write_text(json.dumps({"pid": enfant.pid, "machine": L.socket.gethostname(),
                                                                 "debut": L.maintenant()}))
        capsys.readouterr()
        assert L.main(T.argv(tmp_path, "--reprendre", str(d)), executeur=T.executeur_factice(), base_env={},
                      extracteur=T.extracteur_ok) == 2
        err = capsys.readouterr().err
        assert "REFUS" in err and "tourne" in err and str(enfant.pid) in err and tid not in err
        _, orphelines = L.lire_tentatives(d / "tentatives.jsonl")
        assert [o["id"] for o in orphelines] == [tid] and (d / "usage" / f"{tid}.jsonl").exists()
    finally:
        enfant.kill()
        enfant.wait()
    assert L.main(T.argv(tmp_path, "--reprendre", str(d), "--limite", "1"), executeur=T.executeur_factice(),
                  base_env={}, extracteur=T.extracteur_ok) == 0
    assert not (d / "enfants" / f"{tid}.json").exists()
    assert any(l["id"].startswith(f"{tid}-interrompue-") for l in T.lignes_cout(d))


def test_u3_pid_reutilise_n_est_pas_pris_pour_une_partie(tmp_path):
    """Relecture de la correction (06/11) : après un redémarrage, le PID noté peut appartenir à un autre processus.
    Le fichier garde l'interpréteur et le script de l'enfant ; un PID vivant dont la commande diffère est périmé."""
    d = tmp_path / "vague"
    (d / "enfants").mkdir(parents=True)
    script = tmp_path / "partie_factice.py"
    script.write_text("import time; time.sleep(60)\n")
    enfant = subprocess.Popen([sys.executable, str(script)])
    try:
        machine = L.socket.gethostname()
        (d / "enfants" / "a.json").write_text(json.dumps({"pid": enfant.pid, "machine": machine, "debut": "x",
                                                          "commande": [sys.executable, str(tmp_path / "autre.py")]}))
        assert L.enfants_vivants(d) == []
        (d / "enfants" / "b.json").write_text(json.dumps({"pid": enfant.pid, "machine": machine, "debut": "x",
                                                          "commande": [sys.executable, str(script)]}))
        assert L.enfants_vivants(d) == [enfant.pid]
    finally:
        enfant.kill()
        enfant.wait()
    f = tmp_path / "enfants" / "c.json"
    lire = "import json, sys; print(json.dumps(json.load(open(sys.argv[1]))['commande']))"
    log = tmp_path / "log.txt"
    assert pe.executer_enfant([sys.executable, "-c", lire, str(f)], dict(os.environ, PILOTE_FICHIER_PID=str(f)),
                              tmp_path, log) == 0
    assert json.loads(log.read_text().split("\n")[0]) == [sys.executable, "-c"]


def test_u2_usage_mal_forme_ne_fait_pas_lever_le_chemin_d_erreur(tmp_path):
    """Relecture de la correction (06/11) : une ligne d'usage lisible mais mal formée ne lève pas une seconde
    exception pendant le traitement de la première ; le coût devient inconnu."""
    sortie = tmp_path / "vague"
    (sortie / "usage").mkdir(parents=True)
    (sortie / "usage" / "t1.jsonl").write_text('{"inattendu": 1}\n', encoding="utf-8")
    r = L.resultat_exception({"id": "t1"}, {"sortie": sortie}, OSError(28, "No space left on device"))
    assert r["exception_executeur"] and r["cout_inconnu"]


def test_u3_executer_partie_donne_a_l_enfant_son_fichier_de_pid(tmp_path, monkeypatch):
    vus = []

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        vus.append(env.get(pe.VAR_FICHIER_PID))
        return 0

    monkeypatch.setattr(pe, "executer_enfant", faux)
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")
    ctx, _, _, _ = T.contexte(tmp_path, 100.0)
    t = L.tentative(TR.partie_tau(), 1, 1)
    L.executer_partie(t, ctx)
    assert vus == [str(ctx["sortie"] / "enfants" / f"{t['id']}.json")]


# ======================================================================== #1 : motif d'arrêt sans masque
_ID_WB = __import__("re").compile(r"WorkBench-(?:haiku|sonnet|opus)-p\d+")


def test_u1_motif_d_arret_masque_au_journal_visible_et_a_la_console_complet_a_part(tmp_path, capsys):
    """Le coût d'une tentative WorkBench ne se compte pas : le motif d'arrêt nomme la partie. Au journal visible et à
    la console, ni partie ni modèle WorkBench ; le motif complet est au journal complet (constat E)."""
    ctx, compta, reg, _ = T.contexte(tmp_path, 100.0)
    journal = L.JournalVague(ctx["sortie"])
    wb = {"id": L.id_partie("WorkBench", "claude-sonnet-5-5", 1, "email:1"), "env": "WorkBench",
          "modele": "claude-sonnet-5-5", "tache": "email:1", "passage": 1, "rang": 1, "n_config": 1}
    ex = T.executeur_factice(plus=lambda t: {"cout_inconnu": True})
    L.lancer_vague([(wb, 1), (TR.partie_tau(), 1)], 1, compta, ctx, journal, ex)
    assert compta.arret and wb["id"] in compta.arret
    visible = (ctx["sortie"] / "journal.log").read_text()
    assert "ARRÊT : tentative <partie WorkBench>" in visible
    assert not _ID_WB.search(visible) and "sonnet" not in visible and not _ID_WB.search(capsys.readouterr().out)
    complet = (ctx["sortie"] / L.NOM_JOURNAL_COMPLET).read_text()
    assert f"ARRÊT : {compta.arret}" in complet


def test_u1_motif_d_arret_masque_dans_le_rapport_de_vague(tmp_path, monkeypatch, capsys):
    """Même motif dans rapport_vague.txt, rapport_vague.json et le rapport imprimé à la fin : la ligne ARRÊT ne nomme
    ni partie ni modèle WorkBench."""
    T.neutraliser(monkeypatch, tmp_path)
    ex = T.executeur_factice(plus=lambda t: {"cout_inconnu": True} if t["env"] == "WorkBench" else None)
    assert L.main(T.argv(tmp_path), executeur=ex, base_env={}, extracteur=T.extracteur_ok) == 4
    d = T.dossier_unique(tmp_path)
    r = json.loads((d / "rapport_vague.json").read_text())
    assert r["arret"] and "<partie WorkBench>" in r["arret"] and not _ID_WB.search(r["arret"])
    arrets = [l for l in (d / "rapport_vague.txt").read_text().splitlines() + capsys.readouterr().out.splitlines()
              if "ARRÊT" in l]
    assert arrets and not any(_ID_WB.search(l) or "claude-" in l for l in arrets)


# ======================================================================== #6 et #7 : fiches de relecture (C11)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "relecture"))
import audit_sans_alerte as AU  # noqa: E402
import fiches  # noqa: E402
import test_relecture as TRL  # noqa: E402


def _textes_des_fiches(sortie: Path):
    for sous in ("aveugle", "claude"):
        for f in sorted((sortie / "fiches" / sous).iterdir()):
            yield f.read_text(encoding="utf-8")


def test_u6_fiches_sans_identifiant_d_action_qui_porte_la_tache(tmp_path):
    """τ-bench numérote ses actions attendues « <tâche>_<n> » : ni la version aveugle ni celle de Claude ne gardent
    action_id (C11 : pas de tâche dans les fiches) ; les actions attendues restent, avec leurs arguments."""
    d = TRL.pilote_tau2(tmp_path)
    fiches.produire(d)
    textes = list(_textes_des_fiches(d / "relecture"))
    assert textes and not any("21_1" in t or "action_id" in t for t in textes)
    assert all("gift_card_A" in t for t in textes)  # l'action attendue est toujours là


def test_u7_avertissements_des_fiches_sans_rang(tmp_path):
    """Écriture au rang hors des appels, ou outil incohérent : l'avertissement ne donne pas le rang (C11) ; le rang
    reste dans alertes.json, que les relecteurs ne voient pas."""
    d = TRL.pilote_tau2(tmp_path)
    TRL.ecrire_csv(d / "actions_typees.csv", [
        TRL.ligne(partie="sim-1", tache="21", rang="7", outil="update_reservation_baggages", verdict="fausse"),
        TRL.ligne(partie="sim-1", tache="21", rang="0", outil="update_reservation_baggages", verdict="fausse")])
    resume = fiches.produire(d)
    avert = [a for r in resume for a in r["avertissements"]]
    assert any("hors des" in a for a in avert) and any("incohérence" in a for a in avert)
    textes = list(_textes_des_fiches(d / "relecture"))
    assert any("ATTENTION" in t for t in textes)
    assert not any(__import__("re").search(r"rang \d", t) for t in textes)
    assert sorted(r["rang"] for r in resume) == [0, 7]


def test_u7_avertissements_de_l_audit_sans_rang():
    f = {"avertissements": []}
    AU._verifier_outil(f, 3, "send_email", {"outil": "delete_email"})
    assert f["avertissements"] and not any(__import__("re").search(r"\b3\b", a) for a in f["avertissements"])
    assert fiches.avertissement_hors(5, "appels de la partie") and "4" not in fiches.avertissement_hors(5, "appels")


# ======================================================================== #4 : tirage public lié à l'impulsion désignée
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tirage"))
import tirage_public as tp  # noqa: E402
import test_tirage_public as TTP  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402


def _tirage_nist(tmp_path, manquantes=(), debut=datetime(2026, 12, 2, 9, 0, tzinfo=timezone.utc), heure=TTP.HEURE,
                 apres=TTP.APRES):
    chemin = TTP._reserve_sur_disque(tmp_path)
    balise = TTP.FausseBalise(debut, 240, manquantes=manquantes)
    imp, g, part = tp.tirer(TTP.MANIFESTE, heure - tp.DELAI, TTP.RESERVE_ESSAI, lire=balise, maintenant=apres)
    dossier = tmp_path / "tirage"
    tp.ecrire(dossier, TTP.MANIFESTE, imp, g, part, chemin, None)
    return dossier, chemin, balise, imp


def _reecrire(dossier, chemin, impulsion):
    """Falsification cohérente : autre impulsion brute, valeur, graine et partage recalculés (choix a posteriori)."""
    g = tp.graine(TTP.MANIFESTE, tp.valeur_depuis_brut(impulsion))
    tp.ecrire(dossier, TTP.MANIFESTE, dict(impulsion, valeur=tp.valeur_depuis_brut(impulsion)), g,
              tp.partager(TTP.RESERVE_ESSAI, g), chemin, None)


def test_u4_nist_impulsion_choisie_apres_coup_dans_la_fenetre_refusee(tmp_path):
    dossier, chemin, balise, imp = _tirage_nist(tmp_path)
    assert tp.verifier(dossier, chemin) == [] and tp.verifier(dossier, chemin, lire=balise, maintenant=TTP.APRES) == []
    autre = next(p for p in balise.impulsions
                 if tp.lire_iso(p["timeStamp"]) == tp.lire_iso(imp["heure_impulsion"]) + timedelta(minutes=5))
    _reecrire(dossier, chemin, dict(imp, url=autre["uri"], heure_impulsion=autre["timeStamp"],
                                    brut=json.dumps({"pulse": autre})))
    assert any("première minute" in e for e in tp.verifier(dossier, chemin))
    assert any("archive publique" in e for e in tp.verifier(dossier, chemin, lire=balise, maintenant=TTP.APRES))


def test_u4_nist_heure_declaree_differente_de_l_impulsion_brute_refusee(tmp_path):
    dossier, chemin, balise, imp = _tirage_nist(tmp_path)
    hors = next(p for p in balise.impulsions
                if tp.lire_iso(p["timeStamp"]) == tp.lire_iso(imp["heure_impulsion"]) + timedelta(minutes=90))
    _reecrire(dossier, chemin, dict(imp, brut=json.dumps({"pulse": hors})))  # heure déclarée inchangée
    ecarts = tp.verifier(dossier, chemin)
    assert any("heure de l'impulsion brute" in e for e in ecarts) and any("hors de l'heure" in e for e in ecarts)


def test_u4_nist_premiere_minute_manquante_confirmee_en_ligne(tmp_path):
    """NIST n'a rien publié à la première minute : l'impulsion suivante est la bonne, mais hors ligne on ne peut pas
    le prouver ; en ligne, la sélection refaite dans l'archive la confirme."""
    premiere = tp._plafond_minute(TTP.HEURE)
    dossier, chemin, balise, imp = _tirage_nist(tmp_path, manquantes={premiere})
    assert tp.lire_iso(imp["heure_impulsion"]) == premiere + timedelta(minutes=1)
    assert any("verifier --en-ligne" in e for e in tp.verifier(dossier, chemin))
    assert tp.verifier(dossier, chemin, lire=balise, maintenant=TTP.APRES) == []


def test_u4_drand_tour_choisi_apres_coup_refuse(tmp_path):
    trou = {datetime(2026, 12, 2, 10, 0, tzinfo=timezone.utc) + timedelta(minutes=k) for k in range(1, 62)}
    nist = TTP.FausseBalise(datetime(2026, 12, 2, 9, 0, tzinfo=timezone.utc), 240, manquantes=trou)

    def brut_drand(tour, signature="ab" * 48):
        return json.dumps({"round": tour, "signature": signature,
                           "randomness": hashlib.sha256(bytes.fromhex(signature)).hexdigest()}).encode()

    def lire(url):
        return brut_drand(int(url.rsplit("/", 1)[1])) if "drand" in url else nist(url)

    chemin = TTP._reserve_sur_disque(tmp_path)
    imp, g, part = tp.tirer(TTP.MANIFESTE, TTP.HEURE - tp.DELAI, TTP.RESERVE_ESSAI, lire=lire,
                            maintenant=TTP.APRES)
    dossier = tmp_path / "t"
    tp.ecrire(dossier, TTP.MANIFESTE, imp, g, part, chemin, None)
    assert tp.verifier(dossier, chemin) == [] and tp.verifier(dossier, chemin, lire=lire, maintenant=TTP.APRES) == []
    tour = tp.tour_drand(TTP.HEURE)
    _reecrire(dossier, chemin, dict(imp, brut=brut_drand(tour + 10, "cd" * 48).decode()))
    ecarts = tp.verifier(dossier, chemin)
    assert any("tour désigné" in e for e in ecarts)
    _reecrire(dossier, chemin, dict(imp, brut=json.dumps({"round": tour, "signature": "cd" * 48,
                                                           "randomness": "ef" * 32})))
    assert any("SHA-256 de la signature" in e for e in tp.verifier(dossier, chemin))


def test_u4_ligne_de_commande_verifier_en_ligne(tmp_path, monkeypatch, capsys):
    """La ligne de commande vérifie en ligne un tirage fait avec la réserve et les paires figées (C13, P4 : la
    ligne de commande n'accepte plus d'autres fichiers que ceux du manifeste du gel du plan)."""
    debut = datetime(2026, 10, 30, 9, 0, tzinfo=timezone.utc)
    heure = datetime(2026, 10, 30, 10, 0, 20, tzinfo=timezone.utc)
    balise = TTP.FausseBalise(debut, 240)
    reserve, paires = TTP.REEL / "reserve.json", TTP.REEL / "paires.json"
    imp, g, part = tp.tirer(TTP.MANIFESTE, heure - tp.DELAI, json.loads(reserve.read_text(encoding="utf-8")),
                            json.loads(paires.read_text(encoding="utf-8")), lire=balise,
                            maintenant=heure + timedelta(hours=2))
    dossier = tmp_path / "t"
    tp.ecrire(dossier, TTP.MANIFESTE, imp, g, part, reserve, paires)
    gel = TTP._manifeste_gel(tmp_path, [reserve, paires])
    monkeypatch.setattr(tp, "lire_url", balise)
    monkeypatch.setattr(tp, "_maintenant", lambda: heure + timedelta(hours=2))
    assert tp.main(["verifier", "--dossier", str(dossier), "--en-ligne", "--manifeste-gel", str(gel)]) == 0
    assert "tirage vérifié" in capsys.readouterr().out


# ======================================================================== #5 : tâche WorkBench retrouvée par son texte
import verdicts  # noqa: E402


def test_u5_consigne_partagee_refusee_plutot_qu_un_identifiant_devine():
    """Le lanceur écrit une seule tâche par fichier : la ligne 0 ne désigne rien. Deux tâches au même texte dans le
    domaine : refus explicite, jamais un identifiant deviné (qui serait faux dans actions.csv)."""
    textes = {"email:3": "Même texte", "email:7": "Même texte", "calendar:1": "Même texte", "calendar:2": "Autre"}
    with pytest.raises(ValueError, match="ambigu"):
        verdicts._resoudre_tache("Même texte", 0, textes, "email", n_lignes=1)
    assert verdicts._resoudre_tache("Même texte", 7, textes, "email", n_lignes=40) == "email:7"  # fichier complet
    assert verdicts._resoudre_tache("Même texte", 0, {"email:3": "Même texte", "calendar:1": "Même texte"}, "email",
                                    n_lignes=1) == "email:3"  # un seul candidat dans le domaine
    assert verdicts._resoudre_tache("Autre", 0, textes, "calendar", n_lignes=1) == "calendar:2"


def test_u5_aucune_consigne_partagee_entre_taches_workbench_de_la_reserve():
    """Hypothèse dont dépend l'identifiant des parties WorkBench : aucun texte de consigne n'est partagé (vérifié le
    06/11 sur les 690 tâches)."""
    racine = Path(__file__).resolve().parents[2] / "externe" / "WorkBench"
    if not (racine / "data" / "processed" / "tasks_and_outcomes").is_dir():
        pytest.skip("banc WorkBench absent")
    textes = verdicts.charger_textes_workbench(racine)
    reserve = json.loads((Path(__file__).resolve().parents[1] / "tirage" / "reserve.json").read_text())
    vus = {}
    for k, t in textes.items():
        vus.setdefault(t, []).append(k)
    assert not [k for k in reserve["WorkBench"] if len(vus[textes[k]]) > 1]


# ======================================================================== #8 : en-tête de decisions.csv avec espaces
import decisions  # noqa: E402


def test_u8_entete_avec_espaces_lu_correctement(tmp_path):
    """L'en-tête « alerte_id, decision, … » passe le contrôle : les lignes doivent alors être lues, pas vides."""
    f = tmp_path / "decisions.csv"
    f.write_text("alerte_id, decision, motif, justification, preuve\n"
                 "x1,confirmée,,erreur réelle de l'agent,\n"
                 "x2,levée,b,consigne ambiguë,énoncé ligne 3\n", encoding="utf-8")
    reg = decisions.lire(f, ["x1", "x2"])
    assert reg["x1"]["decision"] == decisions.CONFIRMEE and reg["x1"]["justification"] == "erreur réelle de l'agent"
    assert reg["x2"]["decision"] == decisions.LEVEE and reg["x2"]["motif"] == "b" and reg["x2"]["preuve"]
