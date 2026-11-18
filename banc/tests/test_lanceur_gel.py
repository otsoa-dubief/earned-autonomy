"""Lanceur, vague réelle : le dépôt doit être conforme au manifeste du gel du plan, au lancement comme à la reprise ;
le commit, l'étiquette et l'empreinte du manifeste sont notés dans le plan de jeu (relecture C13, P3). Aucun appel réel."""
import json

import pytest

import lanceur as L
import test_lanceur as T


def test_verifier_gel_refuse_un_depot_different(monkeypatch):
    class Gel:
        @staticmethod
        def verifier(racine):
            return ["banc/lanceur.py : empreinte différente"]
    monkeypatch.setattr(L, "_module_gel", lambda: Gel)
    with pytest.raises(L.ErreurPilote, match="gel du plan"):
        L.verifier_gel()


def test_verifier_gel_rend_le_commit_et_l_empreinte(monkeypatch):
    class Gel:
        @staticmethod
        def verifier(racine):
            return []
    monkeypatch.setattr(L, "_module_gel", lambda: Gel)
    g = L.verifier_gel()
    assert set(g) == {"commit", "etiquette", "manifeste_gel"} and len(g["commit"]) == 40


def test_vague_reelle_refusee_si_le_depot_differe_du_gel(tmp_path, monkeypatch, capsys):
    T.neutraliser(monkeypatch, tmp_path)

    def refuse():
        raise L.ErreurPilote("le dépôt diffère du manifeste du gel du plan : essai")
    monkeypatch.setattr(L, "verifier_gel", refuse)
    trace = []
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    rc = L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE, graine=None),
                executeur=T.executeur_factice(trace), base_env={}, chemin_cle=T.fichier_cle(tmp_path),
                extracteur=T.extracteur_ok)
    assert rc == 2 and not trace and "gel du plan" in capsys.readouterr().err


def test_vague_reelle_note_le_gel_dans_le_plan_de_jeu(tmp_path, monkeypatch):
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE, graine=None),
           executeur=T.executeur_factice([]), base_env={}, chemin_cle=T.fichier_cle(tmp_path),
           extracteur=T.extracteur_ok)
    plan = json.loads((T.dossier_unique(tmp_path) / "plan_de_jeu.json").read_text(encoding="utf-8"))
    assert plan["gel_plan"]["commit"] == "essai"
