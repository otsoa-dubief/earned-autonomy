"""Le test séquentiel de Wald classique, sans borne (deux seuils ln A et ln B).

Sert seulement aux tests : retrouver les nombres de la fiche de lecture
(`lectures/wald_test_sequentiel.md`, vérifiés dans `_verification.md`).
La règle elle-même n'utilise que le seuil d'acceptation ln B.
"""
import math

import numpy as np


def increments(p0, p1):
    """a : poids d'une erreur ; b : poids d'une réussite (en valeur absolue)."""
    return math.log(p1 / p0), -math.log((1 - p1) / (1 - p0))


def seuils(alpha, beta):
    return math.log((1 - beta) / alpha), math.log(beta / (1 - alpha))


def reussites_pour_monter(p0, p1, alpha, beta, s=0):
    """Nombre de réussites d'affilée pour passer sous ln B depuis LLR = s·a."""
    a, b = increments(p0, p1)
    _, lnB = seuils(alpha, beta)
    return math.ceil((s * a - lnB) / b - 1e-12)


def sprt_exact(p, p0, p1, alpha, beta, n_max=20000):
    """Probabilités exactes d'accepter et de rejeter, et taille moyenne d'échantillon,
    par programmation dynamique sur le nombre d'erreurs."""
    a, b = increments(p0, p1)
    lnA, lnB = seuils(alpha, beta)
    dist = np.array([1.0])
    p_acc = p_rej = asn = 0.0
    for n in range(1, n_max + 1):
        new = np.zeros(n + 1)
        new[1:] += dist * p
        new[:-1] += dist * (1 - p)
        k = np.arange(n + 1)
        llr = k * a - (n - k) * b
        acc = llr <= lnB
        rej = llr >= lnA
        pa, pr = new[acc].sum(), new[rej].sum()
        p_acc += pa
        p_rej += pr
        asn += n * (pa + pr)
        new[acc | rej] = 0.0
        dist = new
        if dist.sum() < 1e-15:
            break
    return p_acc, p_rej, asn


def sprt_monte_carlo(p, p0, p1, alpha, beta, n_runs, rng, n_max=100000):
    """Mêmes quantités par Monte-Carlo (vectorisé sur les essais)."""
    a, b = increments(p0, p1)
    lnA, lnB = seuils(alpha, beta)
    llr = np.zeros(n_runs)
    actif = np.ones(n_runs, dtype=bool)
    issue = np.zeros(n_runs, dtype=np.int8)  # 1 accepté, -1 rejeté
    taille = np.zeros(n_runs, dtype=np.int64)
    for n in range(1, n_max + 1):
        ia = np.nonzero(actif)[0]
        if ia.size == 0:
            break
        u = rng.random(ia.size)
        llr[ia] += np.where(u < p, a, -b)
        acc = llr[ia] <= lnB
        rej = llr[ia] >= lnA
        issue[ia[acc]] = 1
        issue[ia[rej]] = -1
        fin = ia[acc | rej]
        taille[fin] = n
        actif[fin] = False
    return float((issue == 1).mean()), float((issue == -1).mean()), float(taille.mean())
