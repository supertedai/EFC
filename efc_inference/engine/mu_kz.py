"""EFC mu(k,z) module — the action's derived Poisson coupling (L-029).

Ports the closed expressions from the action paper
(docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_
Theory_and_Extraction, eq. 2, 24-31, 47-48) into the engine layer, so
the growth engine can be compared against the DERIVED mu(k,z) — not just
the phenomenological ansatz mu(a) = 1 - B*g(a).

Action (the paper's eq. 1):
    S = ∫ d4x sqrt(-g) [ M_Pl^2/2 F(phi) R
                       - 1/2 K(rho) d_mu phi d^mu phi - V(phi)
                       - lambda (box phi - Gamma(rho)) ]

Quasi-static sub-horizon regime (the paper's eq. 24-31):
    eps_F      = F' a^2 Gamma' / (F k^2)                       (24)
    eps_lambda = lambda_dot a^2 Gamma' / (M_Pl^2 F k^2)        (25)
    eps_K      = K phi_dot a^2 Gamma' / (M_Pl^2 F k^2)         (26)
    R          = K a^4 (Gamma')^2 phi_dot^2 / (M_Pl^2 F k^4)   (29)
    mu         = (1 + eps_F + eps_K) / (F (1 + R))             (28)
    eta        = 1 + 2 (eps_F + eps_lambda + eps_lambda_resp)  (27)
    Sigma      = mu (1 + eta) / 2                              (31)

HONESTY about the background: phi_bar, phi_dot_bar, rho_bar and
lambda_dot_bar are INPUTS to the module. The module does NOT solve
the background equations — the action paper itself says that a fully
self-consistent EFC background does not exist yet (Boltzmann-CMB and
first principles are missing). The ansatz mu(a) therefore remains the
reference in the growth engine until the background is solved.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


# ---------------------------------------------------------------------------
# The action's response functions (eq. 2, 47-48)
# ---------------------------------------------------------------------------

def k_rho(params: dict, rho: float) -> float:
    """Eq. 2: K(rho) = K0 / (1 - rho/rho_crit).

    UNITS (natural units, c = 1; the action paper's convention):
        M_Pl : mass (Planck mass)
        k    : 1/length (comoving wavenumber)
        rho  : mass^4 (energy density)
        Gamma and Gamma' : dimensions fixed by the flow condition
        phi_dot, lambda_dot : background derivatives
    All eps expressions (24-26, 29) are DIMENSIONLESS in this
    convention — the tests verify the scaling.

    Boundary behaviour (as in the reference code efc_relativistic.py:26-29):
    for rho >= rho_crit +inf is returned — the stiffness diverges at
    critical density, and the model is not defined beyond it.
    """
    if rho >= params["rho_crit"]:
        return np.inf
    return params["K0"] / (1.0 - rho / params["rho_crit"])


def gamma_rho(params: dict, rho: float) -> float:
    """Eq. 47: Gamma(rho) = gamma0 (rho/rho_crit) / (1 + rho/rho_crit)."""
    x = rho / params["rho_crit"]
    return params["gamma0"] * x / (1.0 + x)


def gamma_prime_rho(params: dict, rho: float) -> float:
    """Eq. 48: Gamma'(rho) = gamma0 / (rho_crit (1 + rho/rho_crit)^2)."""
    x = rho / params["rho_crit"]
    return params["gamma0"] / (params["rho_crit"] * (1.0 + x) ** 2)


def f_phi(params: dict, phi: float) -> float:
    """F(phi) = 1 + alpha*phi (non-minimal coupling)."""
    return 1.0 + params["alpha"] * phi


# ---------------------------------------------------------------------------
# Perturbation parameters (eq. 24-26, 29)
# ---------------------------------------------------------------------------

def compute_epsilon_F(alpha: float, phi_bar: float, F_bar: float,
                      Gamma_prime: float, a: float, k: float) -> float:
    """Eq. 24: eps_F = F'(phi_bar) a^2 Gamma' / (F k^2)."""
    return alpha * a ** 2 * Gamma_prime / (F_bar * k ** 2)


def compute_epsilon_lambda(lambda_dot_bar: float, Gamma_prime: float,
                           M_Pl: float, F_bar: float, a: float,
                           k: float) -> float:
    """Eq. 25: eps_lambda = lambda_dot a^2 Gamma' / (M_Pl^2 F k^2)."""
    return lambda_dot_bar * a ** 2 * Gamma_prime / (M_Pl ** 2 * F_bar * k ** 2)


def compute_epsilon_K(K_bar: float, phi_dot_bar: float,
                      Gamma_prime: float, M_Pl: float, F_bar: float,
                      a: float, k: float) -> float:
    """Eq. 26: eps_K = K phi_dot a^2 Gamma' / (M_Pl^2 F k^2)."""
    return K_bar * phi_dot_bar * a ** 2 * Gamma_prime / (M_Pl ** 2 * F_bar * k ** 2)


def compute_stiffness_response(K_bar: float, Gamma_prime: float,
                               phi_dot_bar: float, M_Pl: float,
                               F_bar: float, a: float, k: float) -> float:
    """Eq. 29: R = K a^4 (Gamma')^2 phi_dot^2 / (M_Pl^2 F k^4)."""
    return (K_bar * a ** 4 * Gamma_prime ** 2 * phi_dot_bar ** 2
            / (M_Pl ** 2 * F_bar * k ** 4))


# ---------------------------------------------------------------------------
# Observables (eq. 27, 28, 31)
# ---------------------------------------------------------------------------

def compute_mu(eps_F: float, eps_K_resp: float, F_bar: float,
               R: float) -> float:
    """Eq. 28: mu = (1 + eps_F + eps_K_resp) / (F (1 + R))."""
    return (1.0 + eps_F + eps_K_resp) / (F_bar * (1.0 + R))


def compute_eta(eps_F: float, eps_lambda: float,
                eps_lambda_resp: float) -> float:
    """Eq. 27: eta = 1 + 2 (eps_F + eps_lambda + eps_lambda_resp)."""
    return 1.0 + 2.0 * (eps_F + eps_lambda + eps_lambda_resp)


def compute_sigma(mu: float, eta: float) -> float:
    """Eq. 31: Sigma = mu (1 + eta) / 2."""
    return mu * (1.0 + eta) / 2.0


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class MuKZEngine(EFCEngine):
    """Computes mu(k,z) from the action's closed expressions.

    Inputs: the background quantities (phi_bar, phi_dot_bar, rho_bar,
    lambda_dot_bar) are PARAMETERS — not derived. A self-consistent
    background does not exist yet (see the action paper's own limitation).
    """

    REQUIRED_PARAMS = [
        "alpha",           # non-minimal coupling F = 1 + alpha*phi
        "K0",              # kinetic stiffness K(rho) = K0/(1-rho/rho_crit)
        "rho_crit",        # critical density in K and Gamma
        "gamma0",          # the flow condition's amplitude
        "M_Pl",            # Planck mass (scales the eps terms)
        "phi_bar",         # background phi — INPUT, not derived
        "phi_dot_bar",     # background phi_dot — INPUT
        "lambda_dot_bar",  # background lambda_dot — INPUT
        "rho_bar",         # background density — INPUT
    ]

    @property
    def name(self) -> str:
        return "mu_kz"

    def mu_at(self, params: dict, a: float, k: float) -> float:
        """mu(k,z) for one (a, k) point via eq. 24-29, 28."""
        F_bar = f_phi(params, params["phi_bar"])
        K_bar = k_rho(params, params["rho_bar"])
        gp = gamma_prime_rho(params, params["rho_bar"])
        eps_F = compute_epsilon_F(params["alpha"], params["phi_bar"],
                                  F_bar, gp, a, k)
        eps_K = compute_epsilon_K(K_bar, params["phi_dot_bar"], gp,
                                  params["M_Pl"], F_bar, a, k)
        R = compute_stiffness_response(K_bar, gp, params["phi_dot_bar"],
                                       params["M_Pl"], F_bar, a, k)
        return compute_mu(eps_F, eps_K, F_bar, R)

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Given (a, k) pairs (N x 2), return mu per point."""
        koord = np.asarray(coordinates, dtype=float)
        if koord.ndim == 1:
            koord = koord.reshape(1, -1)
        ut = np.array([
            self.mu_at(params_dict, float(rad[0]), float(rad[1]))
            for rad in koord
        ])
        return ut

    def regime_node(self, params: dict) -> dict:
        return {
            "id": "efc.mu_kz_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["rho >= rho_crit -> K diverges — stiffness boundary", "regime condition: k/a >> H — validity boundary", "mu < 1 -> stiffness-dominated — regime condition"],
            "motor": "mu_kz"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["rom", "masse", "tid"],
                "enheter": "engine-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the staircase its node belongs. The field must
            # nevertheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": None,
                "tidsskala": "motor time",
                "lengdeskala": "domain"
            },            "regime": {
                "name": "The action's derived Poisson coupling mu(k,z)",
                "validity": (
                    "Quasi-static sub-horizon regime (eq. 24-31), "
                    "condition: k/a >> H — the modes lie deep "
                    "inside the horizon so that time derivatives can "
                    "be neglected. THE BACKGROUND IS INPUT, NOT DERIVED: "
                    "phi_bar, phi_dot_bar, rho_bar and lambda_dot_bar "
                    "are parameters — a self-consistent EFC background is "
                    "not solved (the action paper's own limitation). "
                    "The ansatz mu(a) remains the reference in the growth "
                    "engine until the background is found. mu < 1 applies "
                    "ONLY in the stiffness-dominated regime with F > 0, eps "
                    "terms small against 1 and R > 0 — not universally."
                ),
                "law_form": (
                    "mu = (1 + eps_F + eps_K) / (F (1 + R)) with "
                    "eps_F (24), eps_K (26), R (29); F = 1 + alpha*phi; "
                    "K = K0/(1-rho/rho_crit); Gamma' per eq. 48"
                ),
            },
            "phase": "computation_engine",
            "measure": {
                "target": "mu(k,z) — the effective Poisson coupling",
                "measurer": "closed quasi-static expressions (eq. 24-31)",
                "instrument": "MuKZEngine (efc_inference/engine/mu_kz.py)",
                "proxy_chain": [
                    "background inputs -> eps_F, eps_K, R",
                    "eps_F, eps_K, R -> mu (eq. 28)",
                ],
                "placement": "one (a, k) point at a time in the quasi-static regime",
                "compression": "background + (a,k) -> mu",
            },
            "episenter": "the dominance of stiffness: when R dominates the denominator (with F > 0, eps terms small against 1, R > 0) mu < 1 — the paper's prediction, now computable in the engine layer",
            "buffer": {
                "role": "the validity range is the module's buffer: quasi-static sub-horizon — outside it the module declares nothing",
                "note": "the module declares the background as input instead of pretending it is derived.",
            },
            "ontology": {
                "assumes": [
                    "the action (eq. 1) and the quasi-static expressions (eq. 24-31) are correctly derived in the paper",
                    "the background quantities are given from outside — the module does not derive them",
                ],
                "source": "EFC Relativistic Action (eq. 2, 24-31, 47-48) — ported from the paper's src/efc_relativistic.py",
            },
            "observer": {
                "bandwidth": "the module sees only the background inputs and (a,k) — no field dynamics",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "background -> eps terms -> mu -> the growth engine's fσ8 — the coupling L-029 asked for",
                "properties": ["mu", "eta", "Sigma"],
            },
            "fractal": {
                "pattern": "the same law at every (a,k) point — the engine is an instance of the action's quasi-static regime",
                "note": "one law, all scales.",
            },
            "coupling": {
                "local": "each (a,k) point is computed locally",
                "global": "the module feeds the growth engine with the derived mu — COUPLED_TO efc.growth_engine",
                "empathy_note": "the module knows what it does not know: the background.",
            },
        }
