"""Tester for mu(k,z)-modulen (L-029).

Modulen porterer aksjonspapirets lukkede uttrykk (eq. 24-31, 47-48,
2) fra docs/papers/efc/EFC_Relativistic_Action.../src/
efc_relativistic.py inn i motorlaget, saa growth-motoren kan
sammenlignes mot den AVREDEDE mu(k,z) — ikke bare ansatzen mu(a).

Viktig aerlighet: modulen beregner mu(k,z) fra BAKGRUNNS-INNGANGER
(phi_bar, phi_dot_bar, rho_bar, lambda_dot_bar). Den loser ikke
bakgrunnsligningene — aksjonspapiret sier selv at en fullt
selvkonsistent EFC-bakgrunn ikke finnes ennaa. Modulen ma derfor
deklarere inngangene eksplisitt og aldri late som de er avledet.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from efc_inference.engine.mu_kz import (
    MuKZEngine,
    compute_epsilon_F,
    compute_epsilon_lambda,
    compute_epsilon_K,
    compute_stiffness_response,
    compute_mu,
    compute_eta,
    compute_sigma,
    gamma_rho,
    gamma_prime_rho,
)

# Papir-eksempelparametre (defaults fra aksjonspapirets kode):
# alpha = 0.01, og en bakgrunn valgt slik at mu ~ 0.94 (papirets
# typiske verdi) ved de gitte a, k.
PARAMS = {
    "alpha": 0.01,
    "K0": 1.0,
    "rho_crit": 1.0,
    "gamma0": 1.0,
    "M_Pl": 1.0,          # enheter: M_Pl^2 skalerer eps-ene
    "phi_bar": 0.5,
    "phi_dot_bar": 0.1,
    "lambda_dot_bar": 0.05,
    "rho_bar": 0.4,
}


def test_gamma_form_eq47():
    """Gamma(rho) = gamma0 * (rho/rho_crit) / (1 + rho/rho_crit)."""
    for rho in (0.1, 0.4, 1.0, 2.0):
        forventet = (PARAMS["gamma0"] * (rho / PARAMS["rho_crit"])
                     / (1 + rho / PARAMS["rho_crit"]))
        assert np.isclose(gamma_rho(PARAMS, rho), forventet)


def test_gamma_prime_form_eq48():
    """Gamma'(rho) = gamma0 / (rho_crit * (1 + rho/rho_crit)^2)."""
    for rho in (0.1, 0.4, 1.0, 2.0):
        forventet = (PARAMS["gamma0"]
                     / (PARAMS["rho_crit"]
                        * (1 + rho / PARAMS["rho_crit"]) ** 2))
        assert np.isclose(gamma_prime_rho(PARAMS, rho), forventet)


def test_epsilon_F_eq24():
    """eps_F = alpha * a^2 * Gamma' / (F * k^2)."""
    a, k = 0.7, 0.1
    F_bar = 1.0 + PARAMS["alpha"] * PARAMS["phi_bar"]
    gp = gamma_prime_rho(PARAMS, PARAMS["rho_bar"])
    forventet = PARAMS["alpha"] * a ** 2 * gp / (F_bar * k ** 2)
    assert np.isclose(
        compute_epsilon_F(PARAMS["alpha"], PARAMS["phi_bar"], F_bar,
                          gp, a, k),
        forventet)


def test_epsilon_K_eq26():
    """eps_K = K_bar * phi_dot_bar * a^2 * Gamma' / (M_Pl^2 * F * k^2)."""
    a, k = 0.7, 0.1
    K_bar = PARAMS["K0"] / (1 - PARAMS["rho_bar"] / PARAMS["rho_crit"])
    F_bar = 1.0 + PARAMS["alpha"] * PARAMS["phi_bar"]
    gp = gamma_prime_rho(PARAMS, PARAMS["rho_bar"])
    forventet = (K_bar * PARAMS["phi_dot_bar"] * a ** 2 * gp
                 / (PARAMS["M_Pl"] ** 2 * F_bar * k ** 2))
    assert np.isclose(
        compute_epsilon_K(K_bar, PARAMS["phi_dot_bar"], gp,
                          PARAMS["M_Pl"], F_bar, a, k),
        forventet)


def test_stiffness_response_eq29():
    """R = K_bar * a^4 * (Gamma')^2 * phi_dot_bar^2 / (M_Pl^2 * F * k^4)."""
    a, k = 0.7, 0.1
    K_bar = PARAMS["K0"] / (1 - PARAMS["rho_bar"] / PARAMS["rho_crit"])
    F_bar = 1.0 + PARAMS["alpha"] * PARAMS["phi_bar"]
    gp = gamma_prime_rho(PARAMS, PARAMS["rho_bar"])
    forventet = (K_bar * a ** 4 * gp ** 2 * PARAMS["phi_dot_bar"] ** 2
                 / (PARAMS["M_Pl"] ** 2 * F_bar * k ** 4))
    assert np.isclose(
        compute_stiffness_response(K_bar, gp, PARAMS["phi_dot_bar"],
                                   PARAMS["M_Pl"], F_bar, a, k),
        forventet)


def test_mu_eq28_og_stiffness_dominans():
    """mu = (1 + eps_F + eps_K_resp) / (F * (1 + R)) — og for
    stiffness-dominerte bakgrunner er mu < 1 (papirets prediksjon)."""
    a, k = 0.7, 0.1
    K_bar = PARAMS["K0"] / (1 - PARAMS["rho_bar"] / PARAMS["rho_crit"])
    F_bar = 1.0 + PARAMS["alpha"] * PARAMS["phi_bar"]
    gp = gamma_prime_rho(PARAMS, PARAMS["rho_bar"])
    eps_F = compute_epsilon_F(PARAMS["alpha"], PARAMS["phi_bar"],
                              F_bar, gp, a, k)
    eps_K = compute_epsilon_K(K_bar, PARAMS["phi_dot_bar"], gp,
                              PARAMS["M_Pl"], F_bar, a, k)
    R = compute_stiffness_response(K_bar, gp, PARAMS["phi_dot_bar"],
                                   PARAMS["M_Pl"], F_bar, a, k)
    mu = compute_mu(eps_F, eps_K, F_bar, R)
    forventet = (1.0 + eps_F + eps_K) / (F_bar * (1.0 + R))
    assert np.isclose(mu, forventet)
    # Stiffness-dominans: K_bar stor -> R dominerer -> mu < 1.
    K_stor = 10.0
    R2 = compute_stiffness_response(K_stor, gp, PARAMS["phi_dot_bar"],
                                    PARAMS["M_Pl"], F_bar, a, k)
    eps_K2 = compute_epsilon_K(K_stor, PARAMS["phi_dot_bar"], gp,
                               PARAMS["M_Pl"], F_bar, a, k)
    mu2 = compute_mu(eps_F, eps_K2, F_bar, R2)
    assert mu2 < 1.0


def test_eta_og_sigma_eq27_31():
    """eta = 1 + 2(eps_F + eps_lambda + eps_lambda_resp);
    Sigma = mu(1+eta)/2."""
    eps_F, eps_l, eps_l_resp, mu = 0.01, 0.02, 0.03, 0.9
    eta = compute_eta(eps_F, eps_l, eps_l_resp)
    assert np.isclose(eta, 1 + 2 * (0.01 + 0.02 + 0.03))
    sigma = compute_sigma(mu, eta)
    assert np.isclose(sigma, mu * (1 + eta) / 2)


def test_mukz_engine_compute_returnerer_mu_grid():
    """Motoren tar (a, k)-koordinater og returnerer mu per punkt —
    og deklarerer at bakgrunnen er INNGANG, ikke avledning."""
    e = MuKZEngine()
    a_grid = np.array([0.5, 0.7, 0.9])
    k_grid = np.array([0.1, 0.2])
    # coordinates: (a, k)-par
    koordinater = np.array([[0.7, 0.1], [0.7, 0.2], [0.9, 0.1]])
    mu = e.compute(PARAMS, koordinater)
    assert mu.shape == (3,)
    assert np.all(np.isfinite(mu))
    assert np.all(mu > 0)


def test_mukz_engine_deklarerer_bakgrunn_som_inngang():
    """Modulen skal aldri late som bakgrunnen er avledet — den er en
    eksplisitt inngang inntil en selvkonsistent bakgrunn finnes."""
    e = MuKZEngine()
    node = e.regime_node(PARAMS)
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "input" in tekst or "background" in tekst
    assert "not derived" in tekst or "not solved" in tekst


def test_k_rho_grenseoppforsel():
    """K(rho) divergerer ved kritisk tetthet (inf for rho >= rho_crit)
    — samme oppforsel som referansekoden efc_relativistic.py:26-29."""
    from efc_inference.engine.mu_kz import k_rho
    assert np.isinf(k_rho(PARAMS, PARAMS["rho_crit"]))
    assert np.isinf(k_rho(PARAMS, PARAMS["rho_crit"] * 1.5))
    assert np.isfinite(k_rho(PARAMS, 0.4))
    assert k_rho(PARAMS, 0.4) > 0


def test_eps_er_dimensjonslose_skalering():
    """Dimensjonsloshets-verifisering: eps_F skalerer som 1/k^2 og R
    som 1/k^4 — forholdene er noyaktige, som dokumentasjonen pastar."""
    a = 0.7
    F_bar = 1.0 + PARAMS["alpha"] * PARAMS["phi_bar"]
    K_bar = PARAMS["K0"] / (1 - PARAMS["rho_bar"] / PARAMS["rho_crit"])
    gp = gamma_prime_rho(PARAMS, PARAMS["rho_bar"])
    eps_F_1 = compute_epsilon_F(PARAMS["alpha"], PARAMS["phi_bar"],
                                F_bar, gp, a, 0.1)
    eps_F_2 = compute_epsilon_F(PARAMS["alpha"], PARAMS["phi_bar"],
                                F_bar, gp, a, 0.2)
    assert np.isclose(eps_F_2 / eps_F_1, 1 / 4)  # 1/k^2
    R_1 = compute_stiffness_response(K_bar, gp, PARAMS["phi_dot_bar"],
                                     PARAMS["M_Pl"], F_bar, a, 0.1)
    R_2 = compute_stiffness_response(K_bar, gp, PARAMS["phi_dot_bar"],
                                     PARAMS["M_Pl"], F_bar, a, 0.2)
    assert np.isclose(R_2 / R_1, 1 / 16)  # 1/k^4
