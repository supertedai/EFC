"""EFC mu(k,z)-modul — aksjonens avledede Poisson-kobling (L-029).

Porterer de lukkede uttrykkene fra aksjonspapiret
(docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_
Theory_and_Extraction, eq. 2, 24-31, 47-48) inn i motorlaget, saa
growth-motoren kan sammenlignes mot den AVREDEDE mu(k,z) — ikke bare
den fenomenologiske ansatzen mu(a) = 1 - B*g(a).

Aksjon (papirets eq. 1):
    S = ∫ d4x sqrt(-g) [ M_Pl^2/2 F(phi) R
                       - 1/2 K(rho) d_mu phi d^mu phi - V(phi)
                       - lambda (box phi - Gamma(rho)) ]

Kvasi-statisk sub-horisont-regime (papirets eq. 24-31):
    eps_F      = F' a^2 Gamma' / (F k^2)                       (24)
    eps_lambda = lambda_dot a^2 Gamma' / (M_Pl^2 F k^2)        (25)
    eps_K      = K phi_dot a^2 Gamma' / (M_Pl^2 F k^2)         (26)
    R          = K a^4 (Gamma')^2 phi_dot^2 / (M_Pl^2 F k^4)   (29)
    mu         = (1 + eps_F + eps_K) / (F (1 + R))             (28)
    eta        = 1 + 2 (eps_F + eps_lambda + eps_lambda_resp)  (27)
    Sigma      = mu (1 + eta) / 2                              (31)

AERLIGHET om bakgrunnen: phi_bar, phi_dot_bar, rho_bar og
lambda_dot_bar er INNGANGER til modulen. Modulen loser IKKE
bakgrunnsligningene — aksjonspapiret sier selv at en fullt
selvkonsistent EFC-bakgrunn ikke finnes ennaa (boltzmann-CMB og
forsteprinsipper mangler). Ansatzen mu(a) forblir derfor referansen i
growth-motoren inntil bakgrunnen er lost.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


# ---------------------------------------------------------------------------
# Aksjonens responsfunksjoner (eq. 2, 47-48)
# ---------------------------------------------------------------------------

def k_rho(params: dict, rho: float) -> float:
    """Eq. 2: K(rho) = K0 / (1 - rho/rho_crit).

    ENHETER (natural units, c = 1; aksjonspapirets konvensjon):
        M_Pl : masse (Planck-masse)
        k    : 1/lengde (komovende bølgetall)
        rho  : masse^4 (energitetthet)
        Gamma og Gamma' : dimensjoner bestemt av flyt-betingelsen
        phi_dot, lambda_dot : bakgrunns-derivater
    Alle eps-uttrykk (24-26, 29) er DIMENSJONSLOSE i denne
    konvensjonen — testene verifiserer skaleringen.

    Grenseoppforsel (som referansekoden efc_relativistic.py:26-29):
    for rho >= rho_crit returneres +inf — stivheten divergerer ved
    kritisk tetthet, og modellen er ikke definert utenfor.
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
    """F(phi) = 1 + alpha*phi (ikke-minimal kobling)."""
    return 1.0 + params["alpha"] * phi


# ---------------------------------------------------------------------------
# Perturbasjonsparametre (eq. 24-26, 29)
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
# Observabler (eq. 27, 28, 31)
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
# Motor
# ---------------------------------------------------------------------------

class MuKZEngine(EFCEngine):
    """Beregner mu(k,z) fra aksjonens lukkede uttrykk.

    Innganger: bakgrunns-kvantitetene (phi_bar, phi_dot_bar, rho_bar,
    lambda_dot_bar) er PARAMETRE — ikke avledet. En selvkonsistent
    bakgrunn finnes ikke ennaa (se aksjonspapirets egen begrensning).
    """

    REQUIRED_PARAMS = [
        "alpha",           # ikke-minimal kobling F = 1 + alpha*phi
        "K0",              # kinetisk stivhet K(rho) = K0/(1-rho/rho_crit)
        "rho_crit",        # kritisk tetthet i K og Gamma
        "gamma0",          # flyt-betingelsens amplitude
        "M_Pl",            # Planck-masse (skalerer eps-ene)
        "phi_bar",         # bakgrunns-phi — INNGANG, ikke avledet
        "phi_dot_bar",     # bakgrunns-phi_dot — INNGANG
        "lambda_dot_bar",  # bakgrunns-lambda_dot — INNGANG
        "rho_bar",         # bakgrunns-tetthet — INNGANG
    ]

    @property
    def name(self) -> str:
        return "mu_kz"

    def mu_at(self, params: dict, a: float, k: float) -> float:
        """mu(k,z) for ett (a, k)-punkt via eq. 24-29, 28."""
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
        """Gitt (a, k)-par (N x 2), returner mu per punkt."""
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
            "regime": {
                "name": "Aksjonens avledede Poisson-kobling mu(k,z)",
                "validity": (
                    "Kvasi-statisk sub-horisont-regime (eq. 24-31), "
                    "betingelse: k/a >> H — modusene ligger dypt "
                    "innenfor horisonten slik at tidsderiverte kan "
                    "neglisjeres. BAKGRUNNEN ER INNGANG, IKKE AVLEDET: "
                    "phi_bar, phi_dot_bar, rho_bar og lambda_dot_bar "
                    "er parametre — en selvkonsistent EFC-bakgrunn er "
                    "ikke lost (aksjonspapirets egen begrensning). "
                    "Ansatzen mu(a) forblir referansen i growth-"
                    "motoren inntil bakgrunnen finnes. mu < 1 gjelder "
                    "KUN i stivhetsdominert regime med F > 0, eps-ledd "
                    "små mot 1 og R > 0 — ikke universelt."
                ),
                "law_form": (
                    "mu = (1 + eps_F + eps_K) / (F (1 + R)) med "
                    "eps_F (24), eps_K (26), R (29); F = 1 + alpha*phi; "
                    "K = K0/(1-rho/rho_crit); Gamma' per eq. 48"
                ),
            },
            "phase": "computation_engine",
            "measure": {
                "target": "mu(k,z) — effektiv Poisson-kobling",
                "measurer": "lukkede kvasi-statiske uttrykk (eq. 24-31)",
                "instrument": "MuKZEngine (efc_inference/engine/mu_kz.py)",
                "proxy_chain": [
                    "bakgrunns-innganger -> eps_F, eps_K, R",
                    "eps_F, eps_K, R -> mu (eq. 28)",
                ],
                "placement": "ett (a, k)-punkt om gangen i kvasi-statisk regime",
                "compression": "bakgrunn + (a,k) -> mu",
            },
            "episenter": "stivhetens dominans: naar R dominerer nevneren (med F > 0, eps-ledd smaa mot 1, R > 0) er mu < 1 — papirets prediksjon, naa beregnbart i motorlaget",
            "buffer": {
                "role": "gyldighetsomraadet er modulens buffer: kvasi-statisk sub-horisont — utenfor det deklarerer den det ikke",
                "note": "modulen deklarerer bakgrunnen som inngang i stedet for aa late som den er avledet.",
            },
            "ontology": {
                "assumes": [
                    "aksjonen (eq. 1) og de kvasi-statiske uttrykkene (eq. 24-31) er korrekt avledet i papiret",
                    "bakgrunns-kvantitetene er gitt utenfra — modulen avleder dem ikke",
                ],
                "source": "EFC Relativistic Action (eq. 2, 24-31, 47-48) — portert fra papirets src/efc_relativistic.py",
            },
            "observer": {
                "bandwidth": "modulen ser bare bakgrunns-inngangene og (a,k) — ingen felt-dynamikk",
                "awareness": "instrument_window",
            },
            "emergence": {
                "loop": "bakgrunn -> eps-er -> mu -> growth-motorens fσ8 — koblingen L-029 ba om",
                "properties": ["mu", "eta", "Sigma"],
            },
            "fractal": {
                "pattern": "samme lov i hvert (a,k)-punkt — motoren er en instans av aksjonens kvasi-statiske regime",
                "note": "en lov, alle skalaer.",
            },
            "coupling": {
                "local": "hvert (a,k)-punkt beregnes lokalt",
                "global": "modulen mater growth-motoren med den avledede mu — COUPLED_TO efc.growth_engine",
                "empathy_note": "modulen vet hva den ikke vet: bakgrunnen.",
            },
        }
