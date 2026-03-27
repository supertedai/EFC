"""
Reference implementation: EFC Relativistic Action
Field Equations, Perturbation Theory, and Extraction of mu, Sigma, eta

Paper: Magnusson (2026), DOI: 10.6084/m9.figshare.31876324
This is a pedagogical implementation, not production-ready.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np


# ---------------------------------------------------------------------------
# Action components
# ---------------------------------------------------------------------------

@dataclass
class KineticStiffness:
    """Eq. 2: K(rho) = K0 / (1 - rho/rho_crit)
    Diverges as rho -> rho_crit, enforcing GR recovery at high densities."""

    K0: float = 1.0
    rho_crit: float = 1e15  # critical density (arbitrary units)

    def K(self, rho: float) -> float:
        if rho >= self.rho_crit:
            return np.inf
        return self.K0 / (1.0 - rho / self.rho_crit)

    def dK_drho(self, rho: float) -> float:
        denom = 1.0 - rho / self.rho_crit
        return self.K0 / (self.rho_crit * denom ** 2)


@dataclass
class EntropyProduction:
    """Eq. 47: Gamma(rho) = gamma0 * (rho/rho_crit) / (1 + rho/rho_crit)
    Vanishes in vacuum, grows with density, saturates at rho_crit."""

    gamma0: float = 1.0     # entropy production rate scale [1/time]
    rho_crit: float = 1e15

    def Gamma(self, rho: float) -> float:
        x = rho / self.rho_crit
        return self.gamma0 * x / (1.0 + x)

    def Gamma_prime(self, rho: float) -> float:
        """Eq. 48: Gamma'(rho) = gamma0 / (rho_crit * (1 + rho/rho_crit)^2)"""
        x = rho / self.rho_crit
        return self.gamma0 / (self.rho_crit * (1.0 + x) ** 2)


@dataclass
class EFCAction:
    """The EFC relativistic action (Eq. 1).
    S = int d^4x sqrt(-g) [
        (1/2) M_Pl^2 F(phi) R
      - (1/2) K(rho) (nabla phi)^2
      - V(phi)
      - lambda (box phi - Gamma(rho))
    ]
    """

    alpha: float = 0.01      # non-minimal coupling: F(phi) = 1 + alpha*phi
    stiffness: KineticStiffness = field(default_factory=KineticStiffness)
    entropy_prod: EntropyProduction = field(default_factory=EntropyProduction)

    def F(self, phi: float) -> float:
        """Non-minimal coupling F(phi) = 1 + alpha*phi"""
        return 1.0 + self.alpha * phi

    def F_prime(self, phi: float) -> float:
        return self.alpha

    def departures_from_GR(self) -> List[str]:
        return [
            "Geometry-information coupling F(phi)R",
            "Kinetic stiffness K(rho) = K0/(1 - rho/rho_crit)",
            "Flow constraint lambda(box phi - Gamma(rho))",
        ]


# ---------------------------------------------------------------------------
# Perturbation theory: dimensionless parameters
# ---------------------------------------------------------------------------

def compute_epsilon_F(alpha: float, phi_bar: float, F_bar: float,
                      Gamma_prime: float, a: float, k: float) -> float:
    """Eq. 24: eps_F = F'(phi_bar) * a^2 * Gamma' / (F * k^2)"""
    return alpha * a ** 2 * Gamma_prime / (F_bar * k ** 2)


def compute_epsilon_lambda(lambda_dot_bar: float, Gamma_prime: float,
                           M_Pl: float, F_bar: float, a: float, k: float) -> float:
    """Eq. 25: eps_lambda = lambda_dot_bar * a^2 * Gamma' / (M_Pl^2 * F * k^2)"""
    return lambda_dot_bar * a ** 2 * Gamma_prime / (M_Pl ** 2 * F_bar * k ** 2)


def compute_epsilon_K(K_bar: float, phi_dot_bar: float, Gamma_prime: float,
                      M_Pl: float, F_bar: float, a: float, k: float) -> float:
    """Eq. 26: eps_K = K(rho_bar) * phi_dot_bar * a^2 * Gamma' / (M_Pl^2 * F * k^2)"""
    return K_bar * phi_dot_bar * a ** 2 * Gamma_prime / (M_Pl ** 2 * F_bar * k ** 2)


def compute_stiffness_response(K_bar: float, Gamma_prime: float, phi_dot_bar: float,
                                M_Pl: float, F_bar: float, a: float, k: float) -> float:
    """Eq. 29: R = K(rho_bar) * a^4 * (Gamma')^2 * phi_dot_bar^2 / (M_Pl^2 * F * k^4)"""
    return K_bar * a ** 4 * Gamma_prime ** 2 * phi_dot_bar ** 2 / (M_Pl ** 2 * F_bar * k ** 4)


# ---------------------------------------------------------------------------
# Observables: mu, eta, Sigma
# ---------------------------------------------------------------------------

def compute_mu(eps_F: float, eps_K_resp: float, F_bar: float, R: float) -> float:
    """Eq. 28: mu = (1 + eps_F + eps_K_resp) / (F * (1 + R))"""
    return (1.0 + eps_F + eps_K_resp) / (F_bar * (1.0 + R))


def compute_eta(eps_F: float, eps_lambda: float, eps_lambda_resp: float) -> float:
    """Eq. 27: eta = 1 + 2*(eps_F + eps_lambda + eps_lambda_resp)"""
    return 1.0 + 2.0 * (eps_F + eps_lambda + eps_lambda_resp)


def compute_sigma(mu: float, eta: float) -> float:
    """Eq. 31: Sigma = mu * (1 + eta) / 2"""
    return mu * (1.0 + eta) / 2.0


# ---------------------------------------------------------------------------
# Tensor sector
# ---------------------------------------------------------------------------

@dataclass
class TensorSector:
    """Gravitational wave propagation in EFC.
    Only F(phi)R couples to tensor modes at linear order."""

    alpha: float = 0.01
    phi_bar: float = 0.05

    @property
    def c_T(self) -> float:
        """Eq. 37-38: c_T = c = 1 exactly."""
        return 1.0

    def gw_luminosity_ratio(self, phi_z: float, phi_0: float) -> float:
        """Eq. 40: d_L^GW / d_L^EM = sqrt(F(phi_0) / F(phi_z))"""
        F_0 = 1.0 + self.alpha * phi_0
        F_z = 1.0 + self.alpha * phi_z
        return np.sqrt(F_0 / F_z)

    def gw_luminosity_ratio_approx(self, phi_z: float, phi_0: float) -> float:
        """Eq. 41: d_L^GW/d_L^EM ≈ 1 - (alpha/2)(phi_z - phi_0)"""
        return 1.0 - (self.alpha / 2.0) * (phi_z - phi_0)

    def friction_constraint_satisfied(self, alpha_phi_dot: float, H: float) -> bool:
        """Eq. 42: |alpha * phi_dot_bar| << H"""
        return abs(alpha_phi_dot) < 0.1 * H


# ---------------------------------------------------------------------------
# Perturbation system container
# ---------------------------------------------------------------------------

@dataclass
class EFCPerturbations:
    """Full perturbation system evaluated at given background."""

    # Background
    phi_bar: float = 0.05
    phi_dot_bar: float = 1e-3
    lambda_dot_bar: float = 1e-4
    rho_bar: float = 1e10
    a: float = 1.0          # scale factor
    H: float = 70.0         # Hubble parameter (km/s/Mpc, illustrative)
    M_Pl: float = 1.0       # reduced Planck mass (natural units)

    # Model
    alpha: float = 0.01
    K0: float = 1.0
    rho_crit: float = 1e15
    gamma0: float = 1.0

    def _stiffness(self) -> KineticStiffness:
        return KineticStiffness(K0=self.K0, rho_crit=self.rho_crit)

    def _entropy(self) -> EntropyProduction:
        return EntropyProduction(gamma0=self.gamma0, rho_crit=self.rho_crit)

    def F_bar(self) -> float:
        return 1.0 + self.alpha * self.phi_bar

    def evaluate(self, k: float) -> dict:
        """Evaluate mu, eta, Sigma at wavenumber k."""
        stiff = self._stiffness()
        ent = self._entropy()

        K_bar = stiff.K(self.rho_bar)
        Gp = ent.Gamma_prime(self.rho_bar)
        F = self.F_bar()

        eps_F = compute_epsilon_F(self.alpha, self.phi_bar, F, Gp, self.a, k)
        eps_lam = compute_epsilon_lambda(self.lambda_dot_bar, Gp, self.M_Pl, F, self.a, k)
        eps_K = compute_epsilon_K(K_bar, self.phi_dot_bar, Gp, self.M_Pl, F, self.a, k)
        R = compute_stiffness_response(K_bar, Gp, self.phi_dot_bar, self.M_Pl, F, self.a, k)

        # Response-field contribution (Eq. 46): eps_lambda_resp ~ -eps_K
        eps_lam_resp = -eps_K

        mu = compute_mu(eps_F, eps_K, F, R)
        eta = compute_eta(eps_F, eps_lam, eps_lam_resp)
        sigma = compute_sigma(mu, eta)

        return {
            "k": k,
            "eps_F": eps_F,
            "eps_lambda": eps_lam,
            "eps_K": eps_K,
            "eps_lambda_resp": eps_lam_resp,
            "R": R,
            "mu": mu,
            "eta": eta,
            "Sigma": sigma,
            "F_bar": F,
            "K_bar": K_bar,
            "Gamma_prime": Gp,
        }

    def check_survival_valley(self, k: float) -> dict:
        """Check if parameters fall within the survival valley."""
        r = self.evaluate(k)
        return {
            "mu_in_range": 0.93 <= r["mu"] <= 0.96,
            "Sigma_in_range": 1.03 <= r["Sigma"] <= 1.07,
            "mu": r["mu"],
            "Sigma": r["Sigma"],
            "eta": r["eta"],
        }


# ---------------------------------------------------------------------------
# Falsification conditions
# ---------------------------------------------------------------------------

@dataclass
class FalsificationCondition:
    id: str
    condition: str
    consequence: str
    status: str = "open"


FALSIFICATION_CONDITIONS = [
    FalsificationCondition("FA1", "R(k,z) < 0 for any k,z",
                           "Stiffness mechanism fails; mu > 1 generically"),
    FalsificationCondition("FA2", "Ghost in (delta_phi, delta_lambda) sector",
                           "Theory UV-unstable; action must be modified"),
    FalsificationCondition("FA3", "c_T != c",
                           "GW170817 violated", status="PASSED"),
    FalsificationCondition("FA4", "eta = 1 identically",
                           "Flow constraint does not generate anisotropic stress"),
    FalsificationCondition("FA5", "No parameter region gives mu in [0.93,0.96], Sigma in [1.03,1.07]",
                           "Action doesn't reproduce observed signatures"),
    FalsificationCondition("FA6", "|F_dot/F| >= H at any z < 2",
                           "GW friction too large; violates LIGO/Virgo constraints"),
]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def run_perturbation_demo():
    """Demonstrate the full EFC perturbation framework."""
    print("=" * 65)
    print("EFC Relativistic Action: Perturbation Theory Demo")
    print("=" * 65)

    # --- Action components ---
    print("\n--- 1. EFC Action Components ---")
    action = EFCAction(alpha=0.01)
    print(f"  F(phi=0.05) = {action.F(0.05):.4f}")
    print(f"  F'(phi)     = {action.F_prime(0.05):.4f}")

    stiff = KineticStiffness(K0=1.0, rho_crit=1e15)
    print(f"  K(rho=1e10)   = {stiff.K(1e10):.6f}")
    print(f"  K(rho=0.9e15) = {stiff.K(0.9e15):.2f}  (approaching screening)")

    ent = EntropyProduction(gamma0=1.0, rho_crit=1e15)
    print(f"  Gamma(rho=1e10)  = {ent.Gamma(1e10):.6e}")
    print(f"  Gamma'(rho=1e10) = {ent.Gamma_prime(1e10):.6e}")

    print("\n  Departures from GR:")
    for d in action.departures_from_GR():
        print(f"    - {d}")

    # --- Perturbation evaluation at single k ---
    print("\n--- 2. Perturbation Parameters (single k) ---")
    pert = EFCPerturbations(
        phi_bar=0.05, phi_dot_bar=1e-3, lambda_dot_bar=1e-4,
        rho_bar=1e10, a=1.0, M_Pl=1.0,
        alpha=0.01, K0=1.0, rho_crit=1e15, gamma0=1.0
    )

    k_ref = 0.1  # reference wavenumber
    r = pert.evaluate(k_ref)
    print(f"  k = {k_ref}")
    print(f"  eps_F           = {r['eps_F']:.6e}")
    print(f"  eps_lambda      = {r['eps_lambda']:.6e}")
    print(f"  eps_K           = {r['eps_K']:.6e}")
    print(f"  eps_lambda_resp = {r['eps_lambda_resp']:.6e}")
    print(f"  R (stiffness)   = {r['R']:.6e}")
    print(f"  mu              = {r['mu']:.6f}")
    print(f"  eta             = {r['eta']:.6f}")
    print(f"  Sigma           = {r['Sigma']:.6f}")

    # --- Scale dependence ---
    print("\n--- 3. Scale Dependence mu(k) ---")
    k_values = np.logspace(-3, 0, 8)
    print(f"  {'k':>10s}  {'mu':>10s}  {'eta':>10s}  {'Sigma':>10s}  {'R':>12s}")
    for k in k_values:
        res = pert.evaluate(k)
        print(f"  {k:10.4f}  {res['mu']:10.6f}  {res['eta']:10.6f}  {res['Sigma']:10.6f}  {res['R']:12.4e}")

    # --- Stiffness-dominated regime ---
    print("\n--- 4. Entropy-Stiffness Mechanism ---")
    print("  Increasing K0 (stiffness strength):")
    for K0 in [0.1, 1.0, 10.0, 100.0]:
        pert_test = EFCPerturbations(
            phi_bar=0.05, phi_dot_bar=1e-3, lambda_dot_bar=1e-4,
            rho_bar=1e10, a=1.0, M_Pl=1.0,
            alpha=0.01, K0=K0, rho_crit=1e15, gamma0=1.0
        )
        res = pert_test.evaluate(0.05)
        print(f"    K0={K0:6.1f}  ->  mu={res['mu']:.6f}  R={res['R']:.4e}")

    # --- Screening ---
    print("\n--- 5. Automatic Screening (K -> inf as rho -> rho_crit) ---")
    for rho_frac in [1e-5, 1e-3, 0.1, 0.5, 0.9, 0.99]:
        rho = rho_frac * 1e15
        K = stiff.K(rho)
        if K > 1e10:
            print(f"    rho/rho_crit = {rho_frac:.0e}  K = {K:.2e}  (GR recovered)")
        else:
            print(f"    rho/rho_crit = {rho_frac:.0e}  K = {K:.4f}")

    # --- Tensor sector ---
    print("\n--- 6. Tensor Sector (Gravitational Waves) ---")
    tensor = TensorSector(alpha=0.01, phi_bar=0.05)
    print(f"  c_T = {tensor.c_T} (exactly c; GW170817 PASSED)")

    phi_0 = 0.05
    for z, phi_z in [(0.5, 0.04), (1.0, 0.03), (2.0, 0.01)]:
        ratio = tensor.gw_luminosity_ratio(phi_z, phi_0)
        approx = tensor.gw_luminosity_ratio_approx(phi_z, phi_0)
        print(f"  z={z:.1f}: d_L^GW/d_L^EM = {ratio:.6f}  (approx: {approx:.6f})")

    # --- Falsification conditions ---
    print("\n--- 7. Falsification Conditions ---")
    for fc in FALSIFICATION_CONDITIONS:
        status_str = f"[{fc.status}]"
        print(f"  {fc.id} {status_str:>10s}: {fc.condition}")

    # --- Cross-sector summary ---
    print("\n--- 8. Cross-Sector Summary ---")
    summary = [
        ("Growth",       "mu(k,z)",          "< 1", "K(rho) stiffness"),
        ("Lensing",      "Sigma(k,z)",       "> 1", "lambda-anisotropy"),
        ("Slip",         "eta(k,z)",         "!= 1", "F' + lambda + phi"),
        ("GW speed",     "c_T",             "= c", "No Weyl coupling"),
        ("GW amplitude", "d_L^GW/d_L^EM",  "!= 1", "F(phi) friction"),
    ]
    print(f"  {'Sector':<14s} {'Observable':<18s} {'Prediction':<10s} {'Source'}")
    for s in summary:
        print(f"  {s[0]:<14s} {s[1]:<18s} {s[2]:<10s} {s[3]}")

    print("\n" + "=" * 65)
    print("Demo complete.")


if __name__ == "__main__":
    run_perturbation_demo()
