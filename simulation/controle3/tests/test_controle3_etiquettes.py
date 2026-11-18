"""Les tableaux du contrôle 3 comptent les étiquettes du moteur (amendement R4, Otsoa, 07/11 : « preuves insuffisantes »
remplace « volume insuffisant », au même rang). Les résultats des passages précédents gardent l'ancien nom : il est lu
comme le nouveau."""
from controle3 import lancer as LA
from controle3 import rapport_tableaux as RT
from rejeu import decision as DE


def test_etiquettes_du_controle3_sont_celles_du_moteur():
    assert LA.ETIQUETTES == RT.ETIQ == DE.ORDRE_ETIQUETTES


def test_ancien_volume_insuffisant_lu_comme_preuves_insuffisantes():
    assert RT.etiquette_lue("volume insuffisant") == DE.PREUVES_INSUFFISANTES
    assert RT.etiquette_lue("R4") == "R4" and RT.etiquette_lue("confirmée") == "confirmée"


def _rep(monde, i, etiquette, mention="", r1=False):
    return dict(monde=monde, rep=i, etiquette=etiquette, mention=mention, duree=1.0, p0=dict(couverture=0.99),
                p1=dict(tenu=not r1, hors_hypothese=[], m=3), p4=dict(delegables=[]),
                p2=dict(liste_fixe=dict(battu=False, battu_partout=False),
                        tri_risque=dict(battu=False, battu_partout=False)))


def test_frequences_comptent_l_attendue_et_les_motifs():
    """Cinquième passage : l'attendue peut compter plusieurs étiquettes (C : « R4 ou preuves insuffisantes ») ou exiger
    un motif (V : « aucun type jugeable ») ; les motifs de « preuves insuffisantes » sont comptés."""
    reps = [_rep("C", 0, "R4"), _rep("C", 1, DE.PREUVES_INSUFFISANTES, DE.MOTIF_NON_ETABLI),
            _rep("C", 2, "R2", "délégation inférieure à un témoin"),
            _rep("V", 0, DE.PREUVES_INSUFFISANTES, DE.MOTIF_AUCUN_JUGEABLE),
            _rep("V", 1, DE.PREUVES_INSUFFISANTES, DE.MOTIF_NON_ETABLI)]
    lig = {l["monde"]: l for l in LA.lignes_frequences(reps)}
    assert (lig["C"]["attendue"], lig["C"]["part attendue"]) == (2, 0.667)
    assert lig["V"]["attendue"] == 1
    assert (lig["V"]["pi aucun type jugeable"], lig["V"]["pi dépassement non établi"],
            lig["V"]["pi établi sous rho propre"]) == (1, 1, 0)


def test_rapport_compte_l_attendue_comme_le_lanceur():
    reps = [_rep("C", 0, "R4"), _rep("C", 1, DE.PREUVES_INSUFFISANTES, DE.MOTIF_NON_ETABLI),
            _rep("C", 2, "R2", "délégation inférieure à un témoin"), _rep("C", 3, "volume insuffisant")]
    assert RT.compte_attendu(reps, "R4 ou preuves insuffisantes") == 3     # l'ancien nom est lu comme le nouveau
    assert RT.compte_attendu(reps, "R2 (délégation inférieure à un témoin)") == 1
    assert RT.compte_attendu(reps, "R2 (aucune délégation établie)") == 0
