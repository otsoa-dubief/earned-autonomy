"""Rejeu, phase 2 : dépassement établi par le max-T de Westfall et Young (PLAN_EXPERIENCE.md, 5.14, point 2 ;
test sur cellules synthétiques corrélées : 5.16, point 8).
"""
import numpy as np
import pytest

from rejeu import maxt as MX


def _c_etoile(boot, colonnes):
    """c* de la formule retenue (relecture C13, C1 ; `controle3/maxt_niveau`) : T* recentré sur la moyenne des
    répétitions de chaque cellule, centile `MX.CENTILE` du maximum, au moins 0. Ce calcul recopie celui du moteur ;
    `test_c_etoile_contre_une_valeur_exacte` vérifie c* sans le recopier."""
    b = boot[:, colonnes]
    T = (b - b.mean(axis=0)) / b.std(axis=0, ddof=1)
    return max(float(np.quantile(T.max(axis=1), MX.CENTILE)), 0.0)


def test_max_t_mecanique():
    rng = np.random.default_rng(1)
    boot = rng.normal(size=(2000, 3)) * np.array([1.0, 2.0, 0.0]) + np.array([5.0, 5.0, 7.0])
    est = np.array([5.0, 5.0, 7.0])
    r = MX.depassement_etabli(est, boot, budgets=np.array([1.0, 4.0, 6.0]))
    sd = boot.std(axis=0, ddof=1)
    assert r["c_etoile"] == pytest.approx(_c_etoile(boot, [0, 1]))
    # écart type nul : non testable (plan, 5.14, point 2, amendé le 07/11), rien d'établi même au-dessus du budget
    assert r["etabli"].tolist() == [True, False, False]
    assert r["testable"].tolist() == [True, True, False]
    assert r["motif"] == ["", "", MX.MOTIF_SANS_VARIATION]
    assert r["borne"][0] == pytest.approx(5.0 - r["c_etoile"] * sd[0]) and np.isnan(r["borne"][2])
    vide = MX.depassement_etabli([], np.zeros((10, 0)), [])
    assert vide["m"] == 0 and not vide["etabli"].size


def test_depassement_plante_detecte():
    budgets = [5.0] * 6
    taux = [0.05] * 5 + [0.15]           # la sixième cellule dépasse : 15 pour 100 au lieu de 5
    r = MX.taux_rejet_synthetique(150, G=60, budgets=budgets, taux=taux, B=400, graine=11)
    assert r["par_cellule"][5] >= 0.9
    assert r["par_cellule"][:5].max() <= 0.1


def test_sans_depassement_au_plus_environ_cinq_pour_cent():
    budgets = [5.0, 5.0, 2.0, 2.0, 8.0, 8.0]
    taux = [b / 100 for b in budgets]    # toutes les vraies valeurs au budget
    r = MX.taux_rejet_synthetique(400, G=60, budgets=budgets, taux=taux, B=400, graine=12)
    # erreur de Monte-Carlo d'environ 1,1 point sur 400 jeux
    assert r["au_moins_un"] <= 0.085


# --------------------------------------------------------------------------
# Cellule non testable (plan, 5.14, point 2, décidé par Otsoa le 07/11)
# --------------------------------------------------------------------------
def _famille(rng, B=2000):
    """Deux cellules qui varient franchement, et une troisième au-dessus de son budget qui ne varie que très peu."""
    boot = rng.normal(size=(B, 3)) * np.array([1.0, 1.0, 1e-3]) + np.array([5.0, 5.0, 9.0])
    return np.array([5.0, 5.0, 9.0]), boot, np.array([1.0, 4.0, 6.0])


def test_cellule_a_une_seule_tache_porteuse_non_testable():
    """Une seule tâche porteuse : écart type minuscule (ordres, validateur), estimation au-dessus du budget ; avant
    l'amendement, la borne valait presque l'estimation et le dépassement était établi."""
    est, boot, bud = _famille(np.random.default_rng(3))
    r = MX.depassement_etabli(est, boot, bud, porteuses=[30, 30, 1])
    assert r["etabli"].tolist() == [True, False, False]
    assert r["testable"].tolist() == [True, True, False]
    assert r["motif"][2] == MX.motif_porteuses(MX.PORTEUSES_MIN) and np.isnan(r["borne"][2])
    assert r["c_etoile"] == pytest.approx(_c_etoile(boot, [0, 1]))     # c* sur les seules cellules testables
    sans = MX.depassement_etabli(est, boot, bud)          # sans le nombre de tâches : la cellule entre dans le maximum
    assert sans["testable"].tolist() == [True, True, True] and sans["etabli"][2]


def test_ecart_type_non_defini_non_testable():
    """Une répétition sans écriture au dénominateur donne NaN (0/0) : écart type non défini, la cellule n'établit rien
    et ne touche pas c* (avant l'amendement, NaN > 0 était faux et la cellule était jugée sur son estimation)."""
    est, boot, bud = _famille(np.random.default_rng(4))
    boot[:, 2] = np.random.default_rng(5).normal(size=boot.shape[0]) + 9.0
    boot[::7, 2] = np.nan
    r = MX.depassement_etabli(est, boot, bud, porteuses=[30, 30, 2])
    assert r["etabli"].tolist() == [True, False, False] and r["motif"][2] == MX.MOTIF_NON_DEFINI
    assert r["c_etoile"] == pytest.approx(_c_etoile(boot, [0, 1]))


def test_variation_numerique_seule_vaut_ecart_type_nul():
    """Des répétitions égales à l'arrondi près : aucune variation, à la tolérance numérique près."""
    est = np.array([7.0])
    boot = np.full((500, 1), 7.0) + np.random.default_rng(6).normal(size=(500, 1)) * 1e-14
    r = MX.depassement_etabli(est, boot, [6.0], porteuses=[5])
    assert not r["testable"][0] and not r["etabli"][0] and r["motif"] == [MX.MOTIF_SANS_VARIATION]
    assert np.isnan(r["c_etoile"])


def test_priorite_des_motifs():
    """Moins de deux tâches porteuses prime sur l'estimation non définie, qui prime sur l'écart type non défini, qui prime
    sur l'écart type nul (relecture C13, C5 : le motif de l'estimation vient après celui des tâches porteuses)."""
    est = np.array([np.nan, np.nan, 3.0, 3.0])
    boot = np.full((100, 4), 3.0)
    boot[0, 1:3] = np.nan
    r = MX.depassement_etabli(est, boot, [1.0] * 4, porteuses=[1, 4, 4, 4])
    assert r["motif"] == [MX.motif_porteuses(2), MX.MOTIF_ESTIMATION_NON_DEFINIE, MX.MOTIF_NON_DEFINI,
                          MX.MOTIF_SANS_VARIATION]
    assert not r["etabli"].any()


def test_estimation_non_definie_non_testable():
    """Relecture C13, C5 : une estimation NaN sortait avec le motif « aucune variation bootstrap » alors que ses
    répétitions varient. Elle a son propre motif, n'entre pas dans le maximum et n'établit rien."""
    est, boot, bud = _famille(np.random.default_rng(8))
    boot[:, 2] = np.random.default_rng(9).normal(size=boot.shape[0]) + 9.0
    est[2] = np.nan
    r = MX.depassement_etabli(est, boot, bud, porteuses=[30, 30, 30])
    assert r["testable"].tolist() == [True, True, False] and r["motif"][2] == MX.MOTIF_ESTIMATION_NON_DEFINIE
    assert r["c_etoile"] == pytest.approx(_c_etoile(boot, [0, 1])) and not r["etabli"][2] and np.isnan(r["borne"][2])


def test_arrondi_float32_du_stockage_vaut_ecart_type_nul():
    """Relecture C13, C6 : le moteur range les répétitions en float32 (`analyse._Morceaux`). Des répétitions égales à
    l'arrondi float64 près, à cheval sur deux float32, prennent au stockage un écart type d'un demi-pas float32,
    au-dessus d'une tolérance pensée pour le float64 : la cellule redevenait testable et jugée sur son estimation."""
    from rejeu import analyse as AN
    a = np.float32(0.6)
    milieu = (float(a) + float(np.nextafter(a, np.float32(1)))) / 2      # à égale distance de deux float32
    bruit = np.random.default_rng(10).choice([-1e-15, 1e-15], size=500)
    q = AN.Quantite(centre=milieu, boot=milieu + bruit)
    b = q.boot.tableau()
    assert np.unique(b).size == 2                                        # le stockage a séparé les répétitions
    r = MX.depassement_etabli(np.array([q.centre]), b[:, None], np.array([0.5]), porteuses=[5])
    assert not r["testable"][0] and r["motif"] == [MX.MOTIF_SANS_VARIATION] and not r["etabli"][0]


# --------------------------------------------------------------------------
# Décentrage du bootstrap de B-tout (relecture C13, C1 ; mesure : `controle3/maxt_niveau`)
# --------------------------------------------------------------------------
def test_t_etoile_recentre_sur_la_moyenne_des_repetitions():
    """Le tirage des tâches avec remise décentre les répétitions de B-tout vers le bas. Centré sur l'estimation, T*
    glisse sous zéro, c* devient négatif et la borne passe au-dessus de l'estimation ; recentré sur la moyenne des
    répétitions, la borne reste à c* écarts types sous l'estimation."""
    from scipy.stats import norm
    boot = np.random.default_rng(7).normal(0.8, 0.1, size=(4000, 1))     # deux écarts types sous l'estimation
    r = MX.depassement_etabli(np.array([1.0]), boot, np.array([0.9]), porteuses=[10])
    assert r["c_etoile"] == pytest.approx(_c_etoile(boot, [0]))
    assert r["c_etoile"] == pytest.approx(norm.ppf(MX.CENTILE), abs=0.08)    # loi normale centrée, une cellule
    assert r["borne"][0] < 0.9 and not r["etabli"][0]


def _asymetrique():
    """Une cellule dont 98 % des répétitions sont sous leur moyenne (1) : le centile de T* retenu est négatif."""
    boot = np.zeros((1000, 1))
    boot[:20, 0] = 50.0
    return boot


def test_c_etoile_jamais_negatif():
    """Loi bootstrap très asymétrique : c* est ramené à 0 et la borne ne dépasse jamais l'estimation (relecture C13,
    C1, preuve 5). Limite déclarée (plan, 5.14, point 2) : la cellule est alors jugée sur son estimation seule."""
    r = MX.depassement_etabli(np.array([1.0]), _asymetrique(), np.array([0.5]), porteuses=[10])
    assert r["c_etoile"] == 0.0 and r["borne"][0] == 1.0 and r["etabli"][0]


def test_borne_egale_au_budget_n_etablit_pas():
    r = MX.depassement_etabli(np.array([1.0]), _asymetrique(), np.array([1.0]), porteuses=[10])
    assert r["borne"][0] == 1.0 and not r["etabli"][0] and r["testable"][0]


def test_c_etoile_contre_une_valeur_exacte():
    """c* sans recopier le code (relecture du 08/11, constat 10) : pour deux cellules normales indépendantes, le
    centile q du maximum vaut Φ⁻¹(√q) ; pour deux cellules identiques, Φ⁻¹(q)."""
    from scipy.stats import norm
    rng = np.random.default_rng(11)
    budgets = np.array([100.0, 100.0])                                   # loin au-dessus : seul c* compte
    z = rng.standard_normal((400_000, 2))
    r = MX.depassement_etabli(np.zeros(2), z, budgets, porteuses=[10, 10])
    assert r["c_etoile"] == pytest.approx(norm.ppf(np.sqrt(MX.CENTILE)), abs=0.02)
    z1 = rng.standard_normal((400_000, 1))
    r = MX.depassement_etabli(np.zeros(2), np.hstack([z1, z1]), budgets, porteuses=[10, 10])
    assert r["c_etoile"] == pytest.approx(norm.ppf(MX.CENTILE), abs=0.02)


def test_estimation_infinie_non_definie():
    est, boot, bud = _famille(np.random.default_rng(12))
    boot[:, 2] = np.random.default_rng(13).normal(size=boot.shape[0]) + 9.0
    est[2] = np.inf
    r = MX.depassement_etabli(est, boot, bud, porteuses=[30, 30, 30])
    assert r["motif"][2] == MX.MOTIF_ESTIMATION_NON_DEFINIE and not r["etabli"][2] and r["testable"][:2].all()


@pytest.mark.parametrize("B", [0, 1])
def test_zero_ou_une_repetition_ecart_type_non_defini(B):
    r = MX.depassement_etabli(np.array([3.0]), np.full((B, 1), 2.0), np.array([1.0]), porteuses=[5])
    assert r["motif"] == [MX.MOTIF_NON_DEFINI] and not r["testable"][0] and np.isnan(r["c_etoile"])


def test_valeur_de_la_tolerance():
    """Quatre epsilon du float32, relatifs à la plus grande valeur absolue de l'estimation, du budget et des
    répétitions (relecture du 08/11, constats 9 et 10) : un écart type à 3,9 fois l'unité n'est pas une variation, à
    4,1 fois si."""
    assert MX.TOL_RELATIVE == pytest.approx(4 * np.finfo(np.float32).eps)
    for facteur, attendu in ((3.9, False), (4.1, True)):
        d = facteur / 4 * MX.TOL_RELATIVE * 2.0                          # échelle 2 : celle du budget
        boot = np.where(np.arange(1000) % 2 == 0, 1.0 - d, 1.0 + d)[:, None]
        r = MX.depassement_etabli(np.array([1.0]), boot, np.array([2.0]), porteuses=[5])
        assert bool(r["testable"][0]) is attendu


def test_arrondi_float32_a_l_echelle_des_repetitions():
    """Répétitions vers 40, égales à un pas float32 près, estimation 1 et budget 0,5 : l'arrondi suit la grandeur des
    répétitions ; la cellule ne varie pas et n'est pas testable (relecture du 08/11, constat 9)."""
    a = np.float32(40.0)
    boot = np.where(np.arange(500) % 2 == 0, float(a), float(np.nextafter(a, np.float32(100))))[:, None]
    r = MX.depassement_etabli(np.array([1.0]), boot, np.array([0.5]), porteuses=[5])
    assert not r["testable"][0] and r["motif"] == [MX.MOTIF_SANS_VARIATION] and not r["etabli"][0]
