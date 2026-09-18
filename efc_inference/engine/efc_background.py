"""The EFC background solver — the FIRST self-consistent FRW background (L-033).

Source — the action paper
(docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_
Theory_and_Extraction), DOI 10.6084/m9.figshare.31876324.

The action (the paper's eq. 1)::

    S = int d^4x sqrt(-g) [ 1/2 M_Pl^2 F(phi) R
                            - 1/2 K(rho) d_mu phi d^mu phi
                            - V(phi)
                            - lambda (box phi - Gamma(rho)) ]

    F(phi) = 1 + alpha phi                                    (eq. 1)
    K(rho) = K0 / (1 - rho/rho_crit)                          (eq. 2)
    Gamma(rho) = gamma0 (rho/rho_crit) / (1 + rho/rho_crit)   (eq. 47)
    Gamma'(rho) = gamma0 / (rho_crit (1 + rho/rho_crit)^2)    (eq. 48)

The background equations are the paper's own (section 4.1, FRW metric eq. 11)::

    3 M_Pl^2 F(phi) H^2 = rho_m + 1/2 K(rho) phi_dot^2 + V(phi)
                          + 3 M_Pl^2 H F_dot + lambda_dot phi_dot     (12)
    phi_ddot + 3 H phi_dot = Gamma(rho)                                (13)

and the response field lambda from eq. 10::

    box lambda = V'(phi) - 1/2 M_Pl^2 F'(phi) R
                 - nabla_mu (K(rho) nabla^mu phi)                      (10)

WHY (12) AND (13) ARE ENOUGH AS A REQUIREMENT: (13) is the flow condition — it
determines the phi dynamics, and lambda absorbs the rest (the paper's own
wording: lambda is a RESPONSE FIELD). (12) is the modified
Friedmann equation and is used here as the INITIAL CONDITION for H. The evolution
is driven by the acceleration equation — the (i,j) part of eq. 7 — and the residual
of (12) along the solution is reported as a measured internal consistency.

THREE CONVENTIONS MADE EXPLICIT (no silent choices):

1. THE SIGN OF THE NON-MINIMAL TERM. The paper's eq. (12) writes
   ``+ 3 M_Pl^2 H F_dot``. The direct variation of eq. (1) in the
   signature the paper itself states (eq. 11: ds^2 = -dt^2 + a^2 dx^2) gives
   ``- 3 M_Pl^2 H F_dot`` — that is also the standard form for
   F(phi)R gravity. Both can be chosen with ``nonminimal_sign``
   (NONMINIMAL_SIGN_PAPER = +1, NONMINIMAL_SIGN_STANDARD = -1), and
   the difference is measured in ``diagnostics``. The LCDM limit does NOT
   distinguish them (there F_dot = 0), so the choice is not hidden in the
   falsifier — it stands in the number.

2. V(phi). The paper does not specify the potential (framework.json lists
   ``V_phi: false`` only for the TENSOR sector, not as V = 0). We choose
   V = const, because the LCDM limit — the card's falsifier — requires a
   Lambda-like term. Then V/(3 M_Pl^2 H0^2) = Omega_Lambda when the
   normalisation below is used. The alternative V = 0 gives Einstein-de
   Sitter, not LCDM; that is documented, not hidden.

3. UNITS. Everything is dimensionless with ``H0 = M_Pl = 1``: time is measured in
   1/H0, density in 3 M_Pl^2 H0^2, ``k0 = K0/M_Pl^2`` (K has mass^2),
   ``lambda_tilde = lambda/M_Pl^2`` and ``V0 = V/(3 M_Pl^2 H0^2)``.
   ``omega_crit = rho_crit/(3 M_Pl^2 H0^2)``. E(z) = H/H0 is
   the unit surface out — it is the same in every unit.

HONESTY — THIS IS THE FIRST BACKGROUND, NOT A BOLTZMANN CODE:
    * No CMB, no PERTURBATIONS, no EFCLASS. The ``mu(k,z)`` module
      still takes the background as INPUT — but it now gets it FROM
      this solution (``mu_kz_inputs``) instead of from thin air.
    * The solver is defined only for ``rho_m < rho_crit``: K diverges
      (eq. 2), and the solver stops at the crossing and says so
      (``status = "rho_crit_reached"``). It does not fill in numbers.
    * Super-horizon and a full ADM/Hamilton analysis are open in the paper.
      We make no stability claim beyond what is measured here.
    * Radiation is omitted: E^2 contains Omega_m and Omega_Lambda, not
      Omega_r. That is fine for z <~ 3, not for the CMB epoch.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from .base_engine import EFCEngine

# ---------------------------------------------------------------------------
# Conventions (see the module docstring, point 1)
# ---------------------------------------------------------------------------

#: The paper's eq. (12) as printed: + 3 M_Pl^2 H F_dot.
NONMINIMAL_SIGN_PAPER = 1.0

#: Direct variation of eq. (1) in the paper's own signature (and the standard
#: scalar-tensor form): - 3 M_Pl^2 H F_dot.
NONMINIMAL_SIGN_STANDARD = -1.0

#: The default choice. The rationale is MEASURED, not tasted: see
#: ``BackgroundSolution.diagnostics["constraint_residual_max"]`` and the test
#: ``test_sign_konvensjonen_er_maalt_mot_constraint_residualen``.
NONMINIMAL_SIGN_DEFAULT = NONMINIMAL_SIGN_PAPER

#: Key names the solver requires. V0 can be None (flat closure).
PAKREVDE = ("alpha", "k0", "omega_crit", "gamma0", "Omega_m")
VALGFRIE_DEFAULTS = {
    "V0": None,
    "phi0": 0.0,
    "phi_dot0": 0.0,
    "lam0": 0.0,
    "lam_dot0": 0.0,
}

#: How T^(lambda) (eq. 6) is fed into the background equations.
#:
#: "paper_eq12": the paper's printed form. Eq. (12) has only ``lambda_dot phi_dot``
#:     — i.e. the second-derivative term ``lambda(nabla nabla phi - g box phi)``
#:     in eq. (6) is dropped (the paper's own note in section 2.1 says that
#:     variants differ by boundary terms and shift contributions between
#:     the Einstein and phi equations "without changing the physical content").
#: "full_eq6": the whole of eq. (6) with the metric d'Alembert operator:
#:     rho_lambda = lambda_dot phi_dot - 3 H lambda phi_dot,
#:     p_lambda   = lambda_dot phi_dot + lambda Gamma  (at eq. 13).
#:     The two are MEASURED against each other — the constraint residual is the
#:     verdict, not a claim in a comment. If they are not equivalent, that is a
#:     finding.
LAMBDA_STRESS_FORMS = ("paper_eq12", "full_eq6")
LAMBDA_STRESS_DEFAULT = "paper_eq12"

KONSTRAINT_RESIDUAL_DEF = (
    "max |F E^2 - [rho_m + K phi_dot^2/(6(1-x)) + V0 + sigma E alpha phi_dot "
    "+ lambda_dot phi_dot/3]| / E^2 along the solution; x = rho_m/omega_crit. "
    "E is integrated via the (i,j) equation (eq. 7), not set from (12) — "
    "the residual is therefore a real measurement, not a tautology."
)


# ---------------------------------------------------------------------------
# The action's response functions (eq. 2, 47, 48)
# ---------------------------------------------------------------------------

def kinetic_stiffness(k0: float, rho_over_crit: float) -> float:
    """Eq. 2 in units of M_Pl^2: K(rho)/M_Pl^2 = k0/(1 - rho/rho_crit).

    Diverges at rho -> rho_crit and is not defined for rho >= rho_crit
    (+inf), as in the reference code (efc_relativistic.py:26-29) and in
    mu_kz.k_rho. The stiffness is the model's domain wall, not a warning.
    """
    if rho_over_crit >= 1.0:
        return np.inf
    return k0 / (1.0 - rho_over_crit)


def gamma_of_rho(gamma0: float, rho_over_crit: float) -> float:
    """Eq. 47, dimensionless: Gamma/(H0^2) = gamma0 x/(1+x), x = rho/rho_crit."""
    x = rho_over_crit
    return gamma0 * x / (1.0 + x)


def gamma_prime_of_rho(gamma0: float, rho_over_crit: float) -> float:
    """Eq. 48, in units of rho_crit: dGamma/dx = gamma0/(1+x)^2.

    The same number as mu_kz.gamma_prime_rho when it is called with
    ``rho_crit = 1`` — the test ``test_gamma_og_gamma_prime_eq47_48``
    holds the two modules together, so they cannot slide apart.
    """
    x = rho_over_crit
    return gamma0 / (1.0 + x) ** 2


#: Numerical wall: K and the 1/(1-x) terms are clipped this distance inside
#: rho_crit. Without it the integrator would try a step past the domain and
#: crash in the invalid region instead of stopping at the wall.
#: The clipping is a numerical guard, not physics: the solver REPORTS that it
#: stopped at rho_crit (status + z_rho_crit), and the points after are NaN.
VEGG_EPS = 1e-9


def _x_num(rho_over_crit: float) -> float:
    """rho/rho_crit clipped to the wall (VEGG_EPS inside rho_crit)."""
    return min(rho_over_crit, 1.0 - VEGG_EPS)


def _normalise(params: dict) -> dict:
    """Fills in the defaults and checks that what must be there is there."""
    mangler = [k for k in PAKREVDE if k not in params]
    if mangler:
        raise KeyError(f"missing background parameters: {mangler}")
    p = {**VALGFRIE_DEFAULTS, **params}
    if p["omega_crit"] <= 0:
        raise ValueError("omega_crit must be > 0 (K diverges at rho_crit)")
    if p["Omega_m"] <= 0:
        raise ValueError("Omega_m must be > 0")
    return p


def _V0_fra_lukning(params: dict, nonminimal_sign: float,
                    lambda_stress: str = LAMBDA_STRESS_DEFAULT) -> float:
    """V0 = V/(3 M_Pl^2 H0^2) when it is to be set by the z=0 normalisation.

    E(0) = 1 (flat closure) gives, with eq. (12) evaluated at z = 0:

        V0 = F(phi0) - Omega_m - K(0) phi_dot0^2/6
             - sigma alpha phi_dot0 - rho_lambda0/3

    The same convention as the EFC hubble engine and the LCDM limit require; for a
    static phi at z=0, V0 = Omega_Lambda.
    """
    p = params
    if p["V0"] is not None:
        return float(p["V0"])
    x0 = p["Omega_m"] / p["omega_crit"]
    F0 = 1.0 + p["alpha"] * p["phi0"]
    kin = p["k0"] * p["phi_dot0"] ** 2 / (6.0 * (1.0 - x0))
    if lambda_stress == "full_eq6":
        rho_lam0 = p["lam_dot0"] * p["phi_dot0"] - 3.0 * p["lam0"] * p["phi_dot0"]
    else:
        rho_lam0 = p["lam_dot0"] * p["phi_dot0"]
    return float(F0 - p["Omega_m"] - kin
                 - nonminimal_sign * p["alpha"] * p["phi_dot0"]
                 - rho_lam0 / 3.0)


# ---------------------------------------------------------------------------
# The solution
# ---------------------------------------------------------------------------

@dataclass
class BackgroundSolution:
    """The background on a z-grid. NaN where the solver has no coverage."""

    z: np.ndarray
    a: np.ndarray
    E: np.ndarray              # H/H0
    rho_m: np.ndarray          # in units of 3 M_Pl^2 H0^2
    phi: np.ndarray
    phi_dot: np.ndarray        # d phi/d tau, tau = H0 t
    lam: np.ndarray            # lambda/M_Pl^2
    lam_dot: np.ndarray        # d lam/d tau
    status: str
    z_rho_crit: float | None
    diagnostics: dict
    honesty: dict
    params: dict
    nonminimal_sign: float

    # -- derived, named measures -------------------------------------------

    @property
    def lcdm_max_rel_error(self) -> float | None:
        """Max |E_solver/E_LCDM - 1| — only defined when the solution IS
        the LCDM limit: alpha = gamma0 = 0 AND phi_dot = lambda_dot = 0 at
        z = 0 (otherwise the stiff kinetic energy is not zero and the
        background is not LCDM). Otherwise None — not 0."""
        return self.diagnostics.get("lcdm_max_rel_error")

    @property
    def h_consistency_max_rel(self) -> float:
        """Max |E_integrated - E_from_eq12|/E along the solution."""
        return self.diagnostics["h_consistency_max_rel"]

    def mu_kz_inputs(self, z: float) -> dict:
        """The background inputs the mu(k,z) module needs, at redshift z.

        Units: the solver's own (H0 = M_Pl = 1) — phi_dot_bar and
        lambda_dot_bar are per tau = H0 t. The unit conversion to mu_kz's
        natural units is the caller's responsibility and is not done here.

        This is L-033's purpose: the inputs come from the solution, not
        from thin air. They are still only defined where the solution is.
        """
        def _at_z(arr):
            return float(np.interp(z, self.z, arr))

        valid = np.isfinite(self.E)
        keys = ("phi_bar", "phi_dot_bar", "rho_bar", "lambda_dot_bar")
        if not np.any(valid) or z > float(np.nanmax(self.z[valid])):
            return {k: float("nan") for k in keys}
        return {
            "phi_bar": _at_z(self.phi),
            "phi_dot_bar": _at_z(self.phi_dot),
            "rho_bar": _at_z(self.rho_m),
            "lambda_dot_bar": _at_z(self.lam_dot),
        }


# ---------------------------------------------------------------------------
# The solver
# ---------------------------------------------------------------------------

class EFCBackgroundSolver:
    """Integrates (12)-(13) + matter conservation + the response field (10).

    State: (a, E, rho_m, phi, phi_dot, lambda, lambda_dot) in
    z = redshift. E is H/H0 and is integrated via the
    acceleration equation (eq. 7, the (i,j) part); eq. (12) is set as the
    initial condition and measured along the whole solution.
    """

    def __init__(self, params: dict,
                 nonminimal_sign: float = NONMINIMAL_SIGN_DEFAULT,
                 lambda_stress: str = LAMBDA_STRESS_DEFAULT):
        self.params = _normalise(params)
        if nonminimal_sign not in (NONMINIMAL_SIGN_PAPER,
                                   NONMINIMAL_SIGN_STANDARD):
            raise ValueError(
                "nonminimal_sign must be NONMINIMAL_SIGN_PAPER or "
                "NONMINIMAL_SIGN_STANDARD")
        if lambda_stress not in LAMBDA_STRESS_FORMS:
            raise ValueError(
                f"lambda_stress must be one of {LAMBDA_STRESS_FORMS}")
        self.nonminimal_sign = float(nonminimal_sign)
        self.lambda_stress = str(lambda_stress)
        self._V0 = _V0_fra_lukning(self.params, self.nonminimal_sign,
                                   self.lambda_stress)

    # -- T^(lambda): energy density and pressure (eq. 6 vs eq. 12) ---------

    def _lambda_term(self, E, lam, u, w, G):
        """(rho_lambda, p_lambda), both in units of 3 M_Pl^2 H0^2.

        ``rho_lambda`` is the term that enters eq. (12); ``p_lambda`` is
        the one that enters the (i,j) equation (as pressure). Gamma enters
        via the flow condition (13), phi_ddot + 3 H phi_dot = Gamma.

        The difference between the forms is documented at LAMBDA_STRESS_FORMS;
        which one closes the system is a MEASURED question
        (the constraint residual), not a choice argued in prose.
        """
        if self.lambda_stress == "full_eq6":
            return (w * u - 3.0 * E * lam * u, w * u + lam * G)
        return (w * u, w * u)

    # -- E from the modified Friedmann equation (eq. 12) -------------------

    def _E_from_constraint(self, rho_m, phi, u, w, lam=0.0):
        """Eq. (12) solved for H/H0 — it is quadratic when alpha != 0.

        F E^2 - sigma alpha phi_dot E - X = 0,
        X = rho_m + K phi_dot^2/6 + V0 + rho_lambda/3.
        The physical root (E > 0) is chosen. No real root -> NaN.
        """
        p, pr = self.params, self.nonminimal_sign
        x = _x_num(rho_m / p["omega_crit"])
        if not np.isfinite(x):
            return np.nan
        F = 1.0 + p["alpha"] * phi
        if F <= 0.0:
            return np.nan
        K = kinetic_stiffness(p["k0"], x)
        G = gamma_of_rho(p["gamma0"], x)
        rho_lam, _ = self._lambda_term(1.0, lam, u, w, G)
        X = rho_m + K * u ** 2 / 6.0 + self._V0 + rho_lam / 3.0
        b = pr * p["alpha"] * u
        disk = b ** 2 + 4.0 * F * X
        if disk < 0.0:
            return np.nan
        return (b + np.sqrt(disk)) / (2.0 * F)

    # -- the integration ---------------------------------------------------

    def _dy_dz(self, z, y):
        """The right-hand side. y = (a, E, rho_m, phi, u, lam, w), ' = d/dtau."""
        p, pr = self.params, self.nonminimal_sign
        # the (i,j) term is the non-minimal term in eq. (7), which the paper
        # writes with a MINUS — the opposite of the plus in eq. (12). The two
        # are consistent with each other: sigma' = -sigma.
        sign7 = -pr
        a, E, rho_m, phi, u, lam, w = y
        x = _x_num(rho_m / p["omega_crit"])
        F = 1.0 + p["alpha"] * phi
        if F <= 0.0 or E <= 0.0:
            raise RuntimeError("the fields left their domain of validity")
        K = kinetic_stiffness(p["k0"], x)
        G = gamma_of_rho(p["gamma0"], x)
        _, p_lam = self._lambda_term(E, lam, u, w, G)

        # (i,j): -F(2E' + 3E^2) = K u^2/2 - 3 V0 + 3 p_lambda + sign7 alpha Gamma
        D = (-3.0 * F * E ** 2 - K * u ** 2 / 2.0 + 3.0 * self._V0
             - 3.0 * p_lam - sign7 * p["alpha"] * G) / (2.0 * F)

        # (10): lam'' + 3 E lam' = 3 V' - 3 alpha (E' + 2E^2)
        #                          - K Gamma + K' rho' phi'
        dVdphi = 0.0                      # V = const -> V' = 0
        rho_p = -3.0 * E * rho_m          # d rho_m/d tau
        Kprime_term = (p["k0"] * rho_p * u
                       / (p["omega_crit"] * (1.0 - x) ** 2))
        rhs_lam = (3.0 * dVdphi - 3.0 * p["alpha"] * (D + 2.0 * E ** 2)
                   - K * G + Kprime_term)

        dz = 1.0 / ((1.0 + z) * E)
        return np.array([
            -E * a * dz,                   # da/dtau = E a
            -D * dz,                       # dE/dtau = D  (eq. 7, (i,j))
            3.0 * E * rho_m * dz,          # d rho_m/dtau = -3 E rho_m
            -u * dz,
            -(G - 3.0 * E * u) * dz,
            -w * dz,
            -(rhs_lam - 3.0 * E * w) * dz,
        ])

    def solve(self, z_max: float = 3.0, n_points: int = 201,
              rtol: float = 1e-10, atol: float = 1e-12
              ) -> BackgroundSolution:
        """Solve the background from z=0 to z_max on a grid of n_points.

        Stops honestly at rho_m = rho_crit (K diverges): the points after
        the crossing are NaN and ``status`` says why.
        """
        if z_max <= 0:
            raise ValueError("z_max must be > 0")
        p = self.params
        n_points = max(int(n_points), 2)
        z_grid = np.linspace(0.0, float(z_max), n_points)

        honesty = {
            "status": "first_self_consistent_background",
            "boltzmann_cmb": "open — no Boltzmann/CMB implementation",
            "V_choice_note": (
                "V(phi) is unspecified in the action paper; V = const is "
                "chosen because the LCDM limit requires a Lambda-like term. "
                f"V0 = {self._V0:.6g} in units of 3 M_Pl^2 H0^2"
                + (" (set by the z=0 normalisation)" if p["V0"] is None
                   else " (given by the caller)")),
            "nonminimal_sign": self.nonminimal_sign,
            "nonminimal_sign_note": (
                "the paper's eq. 12 writes +3 M_Pl^2 H F_dot; direct "
                "variation of eq. 1 in the paper's own signature (eq. 11) "
                "gives -3 M_Pl^2 H F_dot. Both can be chosen explicitly. "
                "MEASURED: the paper's printed sign gives a smaller "
                "constraint residual than the direct variation "
                "(see diagnostics) — hence the default."),
            "lambda_stress": self.lambda_stress,
            "lambda_stress_note": (
                "T^(lambda) (eq. 6) can be fed in as the paper's eq. 12 "
                "(only lambda_dot phi_dot) or in the full eq. 6 form; "
                "the paper's own note in 2.1 says that the forms differ by "
                "boundary terms. MEASURED: neither of them closes exactly — "
                "both give a structural residual (~1e-7 for the reference "
                "parameters, cause in diagnostics); the full eq. 6 form "
                "gives the smallest."),
            "units": ("H0 = M_Pl = 1: time in 1/H0, density in 3 M_Pl^2 H0^2, "
                      "k0 = K0/M_Pl^2, lambda_tilde = lambda/M_Pl^2, "
                      "V0 = V/(3 M_Pl^2 H0^2)"),
            "not_valid_for": [
                "perturbations and CMB (Boltzmann requirements — its own card)",
                "rho_m >= rho_crit (K diverges, eq. 2)",
                "z where radiation matters (Omega_r is not included)",
                "super-horizon/ADM stability (open in the paper)",
            ],
        }

        # -- initial condition: eq. (12) is set at z = 0 -------------------
        x0 = p["Omega_m"] / p["omega_crit"]
        F0 = 1.0 + p["alpha"] * p["phi0"]
        E0 = self._E_from_constraint(p["Omega_m"], p["phi0"],
                                     p["phi_dot0"], p["lam_dot0"],
                                     p["lam0"])
        if not np.isfinite(E0) or x0 >= 1.0 or F0 <= 0.0:
            return self._empty_grid(z_grid, honesty, status="invalid_state",
                                    z_rho_crit=None)

        y0 = np.array([1.0, E0, p["Omega_m"], p["phi0"], p["phi_dot0"],
                       p["lam0"], p["lam_dot0"]])

        def _rho_crit_event(z, y):
            return p["omega_crit"] - y[2]

        _rho_crit_event.terminal = True
        _rho_crit_event.direction = -1.0

        try:
            res = solve_ivp(self._dy_dz, (0.0, float(z_max)), y0,
                            method="RK45", rtol=rtol, atol=atol,
                            events=[_rho_crit_event], dense_output=True)
        except (RuntimeError, ValueError, FloatingPointError) as exc:
            return self._empty_grid(z_grid, honesty,
                                    status=f"integration_failed: {exc}",
                                    z_rho_crit=None)

        z_rho_crit = None
        if res.t_events and len(res.t_events[0]) > 0:
            z_rho_crit = float(res.t_events[0][0])
        status = "rho_crit_reached" if z_rho_crit is not None else "ok"
        if not res.success and status == "ok":
            status = f"integration_failed: {res.message}"

        valid = z_grid <= (z_rho_crit if z_rho_crit is not None
                           else float(z_max) + 1e-12)
        out = self._empty_grid(z_grid, honesty, status=status,
                               z_rho_crit=z_rho_crit)
        if np.any(valid):
            Y = res.sol(z_grid[valid])
            out.a[valid] = Y[0]
            out.E[valid] = Y[1]
            out.rho_m[valid] = Y[2]
            out.phi[valid] = Y[3]
            out.phi_dot[valid] = Y[4]
            out.lam[valid] = Y[5]
            out.lam_dot[valid] = Y[6]

        out.diagnostics = self._diagnostics(out)
        return out

    def _empty_grid(self, z_grid, honesty, status, z_rho_crit
                   ) -> BackgroundSolution:
        nan = np.full_like(z_grid, np.nan, dtype=float)
        return BackgroundSolution(
            z=z_grid.copy(), a=nan.copy(), E=nan.copy(), rho_m=nan.copy(),
            phi=nan.copy(), phi_dot=nan.copy(), lam=nan.copy(),
            lam_dot=nan.copy(), status=status, z_rho_crit=z_rho_crit,
            diagnostics={}, honesty=honesty, params=dict(self.params),
            nonminimal_sign=self.nonminimal_sign)

    # -- the measurements --------------------------------------------------

    def _diagnostics(self, sol: BackgroundSolution) -> dict:
        """Residuals along the solution — the measured verdict on the solution."""
        p = self.params
        ok = np.isfinite(sol.E)
        d = {
            "constraint_residual_definition": KONSTRAINT_RESIDUAL_DEF,
            "constraint_residual_cause": (
                "MEASURED: the residual is structural (unchanged from rtol "
                "1e-8 to 1e-11) and scales as K'(rho) = "
                "k0/(omega_crit(1-x)^2) — i.e. as the paper's own neglect of "
                "delta K/delta g^mu_nu (section 2.1, 'Note on delta K'): "
                "it grows with k0, with phi_dot^2 and as 1/omega_crit, and "
                "is zero when phi_dot = 0. See the test "
                "test_constraint_residualen_skalerer_som_K_prime."),
            "h_consistency_definition": (
                "max |E_integrated - E_from_eq12| / E: (12) solved for E at "
                "each state in the solution and compared with the "
                "integrated E."),
            "rho_crit_reached": sol.status == "rho_crit_reached",
            "z_rho_crit": sol.z_rho_crit,
        }
        if not np.any(ok):
            d.update({"constraint_residual_max": np.nan,
                      "h_consistency_max_rel": np.nan,
                      "lcdm_max_rel_error": None})
            return d

        rho, phi, u, w = (sol.rho_m[ok], sol.phi[ok],
                          sol.phi_dot[ok], sol.lam_dot[ok])
        lam = sol.lam[ok]
        E = sol.E[ok]
        x = rho / p["omega_crit"]
        F = 1.0 + p["alpha"] * phi
        K = np.where(x < 1.0, p["k0"] / (1.0 - x), np.inf)
        G = gamma_of_rho(p["gamma0"], x)
        rho_lam = (w * u - 3.0 * E * lam * u
                   if self.lambda_stress == "full_eq6" else w * u)
        rhs = (rho + K * u ** 2 / 6.0 + self._V0 + rho_lam / 3.0
               + self.nonminimal_sign * E * p["alpha"] * u)
        d["constraint_residual_max"] = float(
            np.max(np.abs(F * E ** 2 - rhs) / E ** 2))
        E_c = np.array([self._E_from_constraint(r, f, uu, ww, ll)
                        for r, f, uu, ww, ll in zip(rho, phi, u, w, lam)])
        d["h_consistency_max_rel"] = float(
            np.max(np.abs(E - E_c) / E))
        d["rho_crit_rho"] = float(np.nanmax(sol.rho_m))
        d["rho_over_crit_max"] = float(np.nanmax(x))

        # The LCDM limit is measured only where it actually is the limit.
        p_er_grense = (p["alpha"] == 0.0 and p["gamma0"] == 0.0
                       and p["phi_dot0"] == 0.0 and p["lam_dot0"] == 0.0)
        if p_er_grense:
            z = sol.z[ok]
            E_lcdm = np.sqrt(p["Omega_m"] * (1.0 + z) ** 3 + self._V0)
            d["lcdm_max_rel_error"] = float(np.max(np.abs(E / E_lcdm - 1.0)))
        else:
            d["lcdm_max_rel_error"] = None
        return d


# ---------------------------------------------------------------------------
# The engine surface (the same pattern as mu_kz and hubble)
# ---------------------------------------------------------------------------

class EFCBackgroundEngine(EFCEngine):
    """H(z) from the self-consistent EFC background (eq. 12-13).

    The units are the solver's (H0 = M_Pl = 1); ``H0`` in params is used
    only as a unit conversion out to km/s/Mpc.
    """

    REQUIRED_PARAMS = ["H0", "alpha", "k0", "omega_crit", "gamma0", "Omega_m"]

    #: The engine owns its own publication surface (see base_engine). The node
    #: IS in the atlas (``efc.efc_background_engine``) and is generated to
    #: GitHub Pages — «intern» was true while the node did not exist, and it
    #: stayed after the node arrived. Corrected against the measured state
    #: 2026-09-18 (the bridge audit).
    SYNLIGHET = "offentlig"

    @property
    def name(self) -> str:
        return "efc_background"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """H(z) = H0 * E(z) in km/s/Mpc when H0 is given in km/s/Mpc."""
        if not self.validate_params(params_dict):
            return np.full_like(np.asarray(coordinates, dtype=float), np.nan)
        z = np.asarray(coordinates, dtype=float)
        solver = EFCBackgroundSolver(
            params_dict, nonminimal_sign=params_dict.get(
                "nonminimal_sign", NONMINIMAL_SIGN_DEFAULT))
        sol = solver.solve(z_max=float(np.max(z)), n_points=2001)
        ok = np.isfinite(sol.E)
        if not np.any(ok):
            return np.full_like(z, np.nan)
        E = np.interp(z, sol.z[ok], sol.E[ok], left=np.nan, right=np.nan)
        E = np.where(z <= np.nanmax(sol.z[ok]) + 1e-12, E, np.nan)
        return params_dict["H0"] * E

    # ------------------------------------------------------------------
    # regime_node(): the engine's self-description in the atlas
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        p = _normalise(params_dict)
        sign = float(params_dict.get("nonminimal_sign",
                                     NONMINIMAL_SIGN_DEFAULT))
        V0 = _V0_fra_lukning(p, sign)
        validity = (
            f"Background solver for FLAT FRW with the EFC action (eq. 1): "
            f"alpha={p['alpha']}, k0={p['k0']}, "
            f"omega_crit={p['omega_crit']}, gamma0={p['gamma0']}, "
            f"Omega_m={p['Omega_m']}, V0={V0:.4g}, "
            f"nonminimal_sign={sign:+.0f}. This is the FIRST "
            f"self-consistent EFC background: phi is driven by the "
            f"flow condition (13), H by (12) and lambda is a "
            f"response field (eq. 10). Boltzmann/CMB is OPEN — "
            f"no perturbations, no EFCLASS. Valid only for "
            f"rho_m < rho_crit (K diverges, eq. 2), for z where "
            f"radiation is negligible, and with V = const chosen because "
            f"the paper does not specify V(phi). Super-horizon and "
            f"ADM stability are open in the paper."
        )
        law_form = (
            "3 M_Pl^2 F(phi) H^2 = rho_m + K phi_dot^2/2 + V(phi) "
            "+ sigma 3 M_Pl^2 H F_dot + lambda_dot phi_dot (eq. 12); "
            "phi_ddot + 3 H phi_dot = Gamma(rho) (eq. 13); "
            "F = 1 + alpha phi; K = k0/(1 - rho/rho_crit) (eq. 2); "
            "Gamma per eq. 47 — sigma = +1 is the paper's printed form, "
            "-1 is the direct variation of eq. 1."
        )
        return {
            "id": "efc.efc_background_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {
                "stipulert_av_oss": True,
                "terskler": [
                    "rho >= rho_crit -> K diverges — the model is not "
                    "defined beyond (eq. 2), the solver stops there",
                    "V = const — our choice, not the paper's (V(phi) is "
                    "unspecified in the source)",
                    f"nonminimal_sign = {sign:+.0f} — chosen explicitly, "
                    "the difference is measured",
                ],
                "motor": "efc_background"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                # The evidence status is owned by the ATLAS: the background
                # solver is a hypothesis without measured evidence (SYSTEM.md:
                # «no evidence yet»). The engine said «proxy» about a
                # derivation that is not measured.
                "evidensstatus": "ingen",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, "
                                    "not by the field",
                "konsensus_er_ikke_sannhet": True,
            },
            "maale_paradigme": {
                "koordinater": ["rom", "tid", "masse"],
                "enheter": "dimensionless (H0 = M_Pl = 1); E = H/H0 out",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations",
                                 "a different normalisation of a(t)"],
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine is the SUBSTRATE beneath the other cosmology engines, and
            # the level stands in the atlas — not in a separate copy here.
            "nivaa": {
                "indeks": 0,
                "forelder": None,
                "tidsskala": "cosmic time",
                "lengdeskala": "Hubble scale",
            },
            "regime": {
                "name": "Self-consistent EFC background (FLAT FRW)",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "H(z) and the background fields phi, phi_dot, "
                          "rho_m, lambda_dot",
                "measurer": "numerical integration of (12)-(13) + eq. 10",
                "instrument": "EFCBackgroundSolver "
                              "(efc_inference/engine/efc_background.py)",
                "proxy_chain": [
                    "parameters (alpha, k0, omega_crit, gamma0, V0) -> "
                    "ODE system",
                    "ODE system -> state (a, E, rho_m, phi, phi_dot, "
                    "lambda, lambda_dot)",
                    "state -> mu_kz_inputs -> mu(k,z) (candidate coupling)",
                ],
                "placement": "the solution exists on a z-grid from 0 to "
                             "z_max, and stops at rho_crit",
                "compression": "the background -> seven state variables + "
                               "measured constraint residual",
            },
            "episenter": "the flow condition (13) is what makes this an "
                         "EFC background and not an arbitrary "
                         "scalar-tensor: phi has no free "
                         "starting motion without Gamma, and lambda pays "
                         "for the ledger",
            "buffer": {
                "role": "lambda is the buffer: the response field that keeps "
                        "the flow accounting when phi cannot move freely",
                "note": "the solver declares what it is not (Boltzmann, "
                        "radiation, super-horizon) instead of letting "
                        "E(z) look like a full solution.",
            },
            "ontology": {
                "assumes": [
                    "the action (eq. 1) and the background equations (12)-(13) "
                    "are correctly derived in the paper",
                    "V(phi) = const — our choice, because the paper does not "
                    "specify the potential and the LCDM limit requires a "
                    "Lambda-like term",
                    "matter is dust that is conserved separately (rho ~ a^-3)",
                ],
                "source": "DOI 10.6084/m9.figshare.31876324 (Magnusson, "
                          "2025/2026)",
            },
            "observer": {
                "bandwidth": "the solver sees the background — no "
                             "perturbations, no CMB",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "rho_m -> Gamma -> phi dynamics -> K phi_dot^2 and "
                        "H F_dot -> H -> rho_m",
                "properties": ["H(z)", "phi(z)", "lambda(z)"],
            },
            "fractal": {
                "pattern": "the same background equation holds along the whole "
                           "z axis — the solution is an instance of (12)",
                "note": "one law, every z.",
            },
            "coupling": {
                "local": "every z point is a state on the solution",
                "global": "feeds the mu(k,z) module with the background inputs "
                          "— COUPLED_TO efc.mu_kz_engine (candidate: "
                          "the injection into growth is not implemented)",
                "empathy_note": "the background knows what it is not: it is "
                                "no Boltzmann code.",
            },
        }
