"""
EFC Grav-Cosmo Bridge — Self-contained pipeline module.

Combines cosmology models, engines, and observation modules needed to reproduce
the Phase 1-4 structural closure analysis. Extracted from the EFC inference
codebase so the pipeline can be run standalone from this repository.

Contents:
    Likelihoods:     log_likelihood_chi2, log_likelihood_covariance
    Cosmology:       CosmologyModel (ABC), FlatLCDM, EFCVariantI/J/K
    Engines:         EFCEngine (ABC), EFCHubble, EFCGrowth
    Modules:         BaseModule (ABC), BAOModule, HzModule, GrowthModule
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np
from scipy.integrate import solve_ivp


logger = logging.getLogger(__name__)

Params = Mapping[str, float]

# Speed of light in km/s
C_KM_S = 299792.458

# Planck 2018 sound horizon at drag epoch [Mpc]
DEFAULT_RD = 147.09


def _as_array(a: Any) -> np.ndarray:
    return np.asarray(a, dtype=float)


# =====================================================================
#  LIKELIHOODS
# =====================================================================

def log_likelihood_chi2(observed: np.ndarray, predicted: np.ndarray,
                         errors: np.ndarray) -> float:
    """Chi-squared log-likelihood for diagonal errors."""
    if np.any(errors <= 0):
        return -np.inf
    residuals = observed - predicted
    chi2 = float(np.sum((residuals / errors) ** 2))
    log_det = float(np.sum(np.log(2 * np.pi * errors ** 2)))
    return -0.5 * (chi2 + log_det)


def log_likelihood_covariance(observed: np.ndarray, predicted: np.ndarray,
                               cov: np.ndarray) -> float:
    """Full-covariance Gaussian log-likelihood."""
    n = len(observed)
    residuals = observed - predicted
    try:
        L = np.linalg.cholesky(cov)
    except np.linalg.LinAlgError:
        return -np.inf
    y = np.linalg.solve(L, residuals)
    chi2 = float(np.dot(y, y))
    log_det = 2.0 * float(np.sum(np.log(np.diag(L))))
    return -0.5 * (chi2 + log_det + n * np.log(2 * np.pi))


# =====================================================================
#  COSMOLOGY MODELS
# =====================================================================

class CosmologyModel(ABC):
    """Abstract cosmological model — ontology carrier + forward model."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {}

    @abstractmethod
    def e_squared(self, a: Any, params: Params) -> np.ndarray: ...

    @abstractmethod
    def de_squared_da(self, a: Any, params: Params) -> np.ndarray: ...

    @abstractmethod
    def growth_source(self, a: Any, params: Params) -> np.ndarray: ...

    def friction_extra(self, a: Any, params: Params) -> np.ndarray:
        """Extra friction coefficient for growth ODE. Default 0."""
        a = _as_array(a)
        return np.zeros_like(a)


class FlatLCDM(CosmologyModel):
    """Standard flat FLRW ΛCDM with unmodified Poisson growth."""

    @property
    def name(self) -> str:
        return "flat_lcdm"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {"geometry": "flat_FLRW", "dark_energy": "cosmological_constant",
                "poisson": "unmodified", "gate": "none"}

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return Om * a**(-3.0) + (1.0 - Om)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return -3.0 * Om * a**(-4.0)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        return np.where(E2 > 0, 1.5 * Om / (a**5.0 * E2), 0.0)


class EFCVariantI(CosmologyModel):
    """
    EFC Variant I — Phase 1 multiplicative G_eff coupling (Vei Z projection).

    Background: Pure ΛCDM.
    Growth source: (3/2) · G_eff(k_eff, a)/G · Ω_m / (a^5 · E²).

    G_eff/G = 1 + (C² − 1) · gate(a) · screen(k)
        gate(a)    = 1 / (1 + exp(−(a − a_t) / δ_a))      [logistic]
        screen(k)  = 1 / (1 + (k / k_Λ)²)                 [low-pass, MOND-consistent]

    Defaults: k_Λ = 0.05 h/Mpc, k_eff = 0.1 h/Mpc, a_t = 0.5, δ_a = 0.1.
    C is free via params_dict["C"] (default 2.32 from KT2 Grid-AQUAL prior).
    """

    K_LAMBDA = 0.05
    K_EFF = 0.1
    A_T = 0.5
    DELTA_A = 0.1
    RCMP_GR_THRESHOLD = 0.01
    RCMP_MODIFIED_THRESHOLD = 0.10

    def __init__(self, C_default: float = 2.32,
                 k_lambda: Optional[float] = None,
                 k_eff: Optional[float] = None,
                 a_t: Optional[float] = None,
                 delta_a: Optional[float] = None):
        self._C_default = float(C_default)
        self._a_t = float(a_t) if a_t is not None else self.A_T
        self._delta_a = float(delta_a) if delta_a is not None else self.DELTA_A
        self._k_lambda = float(k_lambda) if k_lambda is not None else self.K_LAMBDA
        self._k_eff = float(k_eff) if k_eff is not None else self.K_EFF
        self._screen_k_eff = 1.0 / (1.0 + (self._k_eff / self._k_lambda) ** 2)

    @property
    def name(self) -> str:
        return "efc_variant_i"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {"background": "pure_lcdm", "coupling": "multiplicative_G_eff",
                "k_lambda": self._k_lambda, "k_eff": self._k_eff,
                "screen_at_k_eff": round(self._screen_k_eff, 6),
                "gate": {"a_t": self._a_t, "delta_a": self._delta_a}}

    def _gate(self, a: Any) -> np.ndarray:
        a = _as_array(a)
        x = (a - self._a_t) / self._delta_a
        x = np.clip(x, -50, 50)
        return 1.0 / (1.0 + np.exp(-x))

    def g_eff_over_G(self, a: Any, C: float) -> np.ndarray:
        gate_a = self._gate(a)
        return 1.0 + (float(C) ** 2 - 1.0) * gate_a * self._screen_k_eff

    def classify_regime(self, a: float, C: float) -> str:
        geff = float(self.g_eff_over_G(np.array([a]), C)[0])
        dev = abs(geff - 1.0)
        if dev < self.RCMP_GR_THRESHOLD:
            return "GR"
        if dev < self.RCMP_MODIFIED_THRESHOLD:
            return "TRANSITION"
        return "MODIFIED"

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return Om * a**(-3.0) + (1.0 - Om)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return -3.0 * Om * a**(-4.0)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        C = float(params.get("C", self._C_default))
        E2 = self.e_squared(a, params)
        g_eff = self.g_eff_over_G(a, C)
        g_eff = np.clip(g_eff, 0.1, 100.0)
        return np.where(E2 > 0, 1.5 * g_eff * Om / (a**5.0 * E2), 0.0)


class EFCVariantJ(CosmologyModel):
    """
    EFC Variant J — Phase 2 local friction coupling.

    Background: Pure ΛCDM (unmodified Poisson source).
    Friction: standard + β · gate(a) / a.

    β = 0 recovers FlatLCDM exactly. β enters params_dict.
    """

    A_T = 0.5
    DELTA_A = 0.1

    def __init__(self, a_t: Optional[float] = None,
                 delta_a: Optional[float] = None,
                 beta_default: float = 0.0):
        self._a_t = float(a_t) if a_t is not None else self.A_T
        self._delta_a = float(delta_a) if delta_a is not None else self.DELTA_A
        self._beta_default = float(beta_default)

    @property
    def name(self) -> str:
        return "efc_variant_j"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {"background": "pure_lcdm", "coupling": "friction_local_gate",
                "gate": {"a_t": self._a_t, "delta_a": self._delta_a}}

    def _gate(self, a: Any) -> np.ndarray:
        a = _as_array(a)
        x = (a - self._a_t) / self._delta_a
        x = np.clip(x, -50, 50)
        return 1.0 / (1.0 + np.exp(-x))

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return Om * a**(-3.0) + (1.0 - Om)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return -3.0 * Om * a**(-4.0)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        return np.where(E2 > 0, 1.5 * Om / (a**5.0 * E2), 0.0)

    def friction_extra(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        beta = float(params.get("beta", self._beta_default))
        if beta == 0.0:
            return np.zeros_like(a)
        gate_a = self._gate(a)
        return beta * gate_a / np.maximum(a, 1e-10)


class EFCVariantK(CosmologyModel):
    """
    EFC Variant K — Phase 3 non-local memory friction.

    Background: Pure ΛCDM.
    Friction: standard + β · G(a) / a,  with G(a) = ∫_0^a gate(a') da'.

    Analytic form of the logistic-gate integral:
        G(a) = δ_a · [ln(1 + e^((a−a_t)/δ_a)) − ln(1 + e^(−a_t/δ_a))]

    With a_t=0.5, δ_a=0.1:  G(1) ≈ 0.493, G(0.5) ≈ 0.069, G(0.1) ≈ 0.002.
    """

    A_T = 0.5
    DELTA_A = 0.1

    def __init__(self, a_t: Optional[float] = None,
                 delta_a: Optional[float] = None,
                 beta_default: float = 0.0):
        self._a_t = float(a_t) if a_t is not None else self.A_T
        self._delta_a = float(delta_a) if delta_a is not None else self.DELTA_A
        self._beta_default = float(beta_default)
        self._G_offset = self._delta_a * float(np.logaddexp(0, -self._a_t / self._delta_a))
        self._G_at_1 = float(self._G_integral(np.array([1.0]))[0])

    @property
    def name(self) -> str:
        return "efc_variant_k"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {"background": "pure_lcdm", "coupling": "friction_non_local_memory",
                "memory_kernel": "integrated_logistic_gate",
                "G_at_1": round(self._G_at_1, 6),
                "markov": False}

    def _G_integral(self, a: np.ndarray) -> np.ndarray:
        a = _as_array(a)
        x = (a - self._a_t) / self._delta_a
        x = np.clip(x, -50, 50)
        return self._delta_a * np.logaddexp(0, x) - self._G_offset

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return Om * a**(-3.0) + (1.0 - Om)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return -3.0 * Om * a**(-4.0)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        return np.where(E2 > 0, 1.5 * Om / (a**5.0 * E2), 0.0)

    def friction_extra(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        beta = float(params.get("beta", self._beta_default))
        if beta == 0.0:
            return np.zeros_like(a)
        G_a = self._G_integral(a)
        return beta * G_a / np.maximum(a, 1e-10)


# =====================================================================
#  ENGINES
# =====================================================================

class EFCEngine(ABC):
    """Abstract base for physics engines."""

    REQUIRED_PARAMS: List[str] = []

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray: ...

    def validate_params(self, params_dict: dict) -> bool:
        for key in self.REQUIRED_PARAMS:
            if key not in params_dict or not np.isfinite(params_dict[key]):
                return False
        return True


class EFCHubble(EFCEngine):
    """H(z) from a CosmologyModel: H(z) = H0 * sqrt(E²(a(z)))."""

    REQUIRED_PARAMS = ["H0", "Omega_m"]

    def __init__(self, cosmology: Optional[CosmologyModel] = None):
        self.cosmology = cosmology if cosmology is not None else FlatLCDM()

    @property
    def name(self) -> str:
        return f"hubble-{self.cosmology.name}"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        if not self.validate_params(params_dict):
            return np.full_like(coordinates, np.nan, dtype=float)
        H0 = float(params_dict["H0"])
        a = 1.0 / (1.0 + _as_array(coordinates))
        E2 = self.cosmology.e_squared(a, params_dict)
        return np.where(E2 > 0, H0 * np.sqrt(E2), np.nan)


class EFCGrowth(EFCEngine):
    """
    f·σ8(z) via growth ODE with CosmologyModel-provided source + friction.

    Growth equation:
        δ'' + [3/a + E'/E + friction_extra(a)] · δ' − source(a) · δ = 0

    where friction_extra is 0 for standard variants, and β·g(a)/a or β·G(a)/a
    for VariantJ/VariantK respectively.
    """

    REQUIRED_PARAMS = ["Omega_m", "sigma8"]
    _A_INI = 1e-3
    _RTOL = 1e-8
    _ATOL = 1e-10

    def __init__(self, cosmology: Optional[CosmologyModel] = None):
        self.cosmology = cosmology if cosmology is not None else FlatLCDM()

    @property
    def name(self) -> str:
        return f"growth-{self.cosmology.name}"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        if not self.validate_params(params_dict):
            return np.full_like(coordinates, np.nan, dtype=float)
        return self._compute(params_dict, _as_array(coordinates))

    def _compute(self, params_dict: dict, z: np.ndarray) -> np.ndarray:
        z = np.atleast_1d(np.asarray(z, dtype=float))
        s8 = float(params_dict["sigma8"])
        a_data = 1.0 / (1.0 + z)
        cosmo = self.cosmology

        E2_ini = cosmo.e_squared(np.array([self._A_INI]), params_dict)
        if E2_ini[0] <= 0:
            return np.full_like(z, np.nan, dtype=float)

        def growth_ode(a: float, y: np.ndarray) -> list:
            D, Dp = y
            a_arr = np.array([a])
            E2 = cosmo.e_squared(a_arr, params_dict).item()
            if E2 <= 0:
                return [0.0, 0.0]
            E_a = np.sqrt(E2)
            dE2_da = cosmo.de_squared_da(a_arr, params_dict).item()
            dE_da = dE2_da / (2.0 * E_a)
            friction_base = 3.0 / a + dE_da / E_a
            friction_extra = cosmo.friction_extra(a_arr, params_dict).item()
            friction = friction_base + friction_extra
            source = cosmo.growth_source(a_arr, params_dict).item()
            return [Dp, -friction * Dp + source * D]

        y0 = [self._A_INI, 1.0]
        sol = solve_ivp(growth_ode, (self._A_INI, 1.0), y0, method="RK45",
                        rtol=self._RTOL, atol=self._ATOL, dense_output=True)
        if not sol.success:
            return np.full_like(z, np.nan, dtype=float)

        D_at_1 = float(sol.sol(1.0)[0])
        if D_at_1 <= 0:
            return np.full_like(z, np.nan, dtype=float)

        fs8 = np.zeros_like(z, dtype=float)
        for i, ai in enumerate(a_data):
            if ai < self._A_INI or ai > 1.0:
                fs8[i] = np.nan
                continue
            D_i, Dp_i = sol.sol(ai)
            D_i, Dp_i = float(D_i), float(Dp_i)
            if D_i <= 0:
                fs8[i] = np.nan
                continue
            f_i = ai * Dp_i / D_i
            sigma8_z = s8 * D_i / D_at_1
            fs8[i] = f_i * sigma8_z
        return fs8


# =====================================================================
#  MODULES — data loading + likelihood
# =====================================================================

class BaseModule(ABC):
    def __init__(self, engine: EFCEngine):
        self.engine = engine
        self.observed: Optional[np.ndarray] = None
        self.errors: Optional[np.ndarray] = None
        self.coordinates: Optional[np.ndarray] = None
        self._loaded = False

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def load_data(self, **kwargs): ...

    def predict(self, params_dict: dict) -> np.ndarray:
        if not self._loaded:
            raise RuntimeError(f"Module '{self.name}': call load_data() first")
        return self.engine.compute(params_dict, self.coordinates)

    def log_likelihood(self, params_dict: dict) -> float:
        if not self._loaded:
            raise RuntimeError(f"Module '{self.name}': call load_data() first")
        pred = self.predict(params_dict)
        if np.any(~np.isfinite(pred)):
            return -np.inf
        return log_likelihood_chi2(self.observed, pred, self.errors)

    @property
    def n_data(self) -> int:
        return 0 if self.observed is None else len(self.observed)


class HzModule(BaseModule):
    """Cosmic-chronometer H(z) direct measurements."""

    @property
    def name(self) -> str:
        return "hz"

    def load_data(self, data_path: str = None, **kwargs):
        if data_path is None:
            raise ValueError("data_path is required")
        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"H(z) data not found: {path}")
        lines = []
        header_skipped = False
        with open(str(path)) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if not header_skipped:
                    header_skipped = True
                    continue
                lines.append([float(x) for x in line.split(",")])
        raw = np.array(lines)
        if raw.ndim == 1:
            raw = raw.reshape(1, -1)
        self.coordinates = raw[:, 0]
        self.observed = raw[:, 1]
        self.errors = raw[:, 2]
        self._loaded = True
        logger.info("Loaded H(z) data: %d points", len(self.coordinates))


class BAOModule(BaseModule):
    """BAO distance observables (D_H/r_d, D_M/r_d, D_V/r_d)."""

    def __init__(self, engine: EFCEngine):
        super().__init__(engine)
        self._covariance: Optional[np.ndarray] = None
        self._observables: Optional[List[str]] = None

    @property
    def name(self) -> str:
        return "bao"

    def load_data(self, data_path: str = None, **kwargs):
        if data_path is None:
            raise ValueError("data_path is required")
        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"BAO data not found: {path}")
        if path.suffix == ".csv":
            self._load_csv(path)
        else:
            self._load_json(path)
        self._loaded = True

    def _load_csv(self, path: Path):
        z_list, obs_list, val_list, sig_list = [], [], [], []
        with open(path) as f:
            f.readline()  # header
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) < 4:
                    continue
                z_list.append(float(parts[0]))
                obs_list.append(parts[1].strip())
                val_list.append(float(parts[2]))
                sig_list.append(float(parts[3]))
        self.coordinates = np.array(z_list)
        self.observed = np.array(val_list)
        self.errors = np.array(sig_list)
        self._observables = obs_list

    def _load_json(self, path: Path):
        with open(path) as f:
            data = json.load(f)
        ms = data["measurements"]
        self._observables = [m["observable"] for m in ms]
        self.coordinates = np.array([m["z_eff"] for m in ms])
        self.observed = np.array([m["value"] for m in ms])
        self.errors = np.array([m["error"] for m in ms])
        if "covariance" in data:
            self._covariance = np.array(data["covariance"])

    def predict(self, params_dict: dict) -> np.ndarray:
        if not self._loaded:
            raise RuntimeError("Call load_data() first")
        r_d = params_dict.get("r_d", DEFAULT_RD)
        predictions = np.zeros(len(self.coordinates))
        _trapz = getattr(np, "trapezoid", None) or np.trapz
        for i, obs_type in enumerate(self._observables):
            z_i = float(self.coordinates[i])
            if obs_type == "DH_over_rd":
                Hz_i = self.engine.compute(params_dict, np.array([z_i]))[0]
                predictions[i] = C_KM_S / (Hz_i * r_d)
            elif obs_type == "DM_over_rd":
                predictions[i] = self._DM(params_dict, z_i, _trapz) / r_d
            elif obs_type == "DV_over_rd":
                Hz_i = self.engine.compute(params_dict, np.array([z_i]))[0]
                DH_i = C_KM_S / Hz_i
                DM_i = self._DM(params_dict, z_i, _trapz)
                DV_i = (z_i * DH_i * DM_i ** 2) ** (1.0 / 3.0)
                predictions[i] = DV_i / r_d
            else:
                raise ValueError(f"Unknown BAO observable: {obs_type}")
        return predictions

    def _DM(self, params_dict: dict, z: float, trapz) -> float:
        n = 201
        z_grid = np.linspace(0.0, z, n)
        Hz_grid = self.engine.compute(params_dict, z_grid)
        integrand = C_KM_S / Hz_grid
        return float(trapz(integrand, z_grid))

    def log_likelihood(self, params_dict: dict) -> float:
        if not self._loaded:
            raise RuntimeError("Call load_data() first")
        pred = self.predict(params_dict)
        if np.any(~np.isfinite(pred)):
            return -np.inf
        if self._covariance is not None:
            return log_likelihood_covariance(self.observed, pred, self._covariance)
        return log_likelihood_chi2(self.observed, pred, self.errors)


# BOSS DR12 fσ8 covariance — from SDSS DR16 BAOplus (Gil-Marín+2020)
BOSS_FS8_COV_3x3 = np.array([
    [0.00203355, 0.00081183, 0.0],
    [0.00081183, 0.00142289, 0.0],
    [0.0,        0.0,        0.00196162],
])
BOSS_FS8_Z = np.array([0.38, 0.51, 0.61])


def build_fs8_covariance(z_data: np.ndarray, sigma_data: np.ndarray,
                          boss_cov: Optional[np.ndarray] = None,
                          z_tol: float = 0.005) -> np.ndarray:
    """Build full fσ8 covariance. BOSS DR12 points replaced by Gil-Marín 3x3 sub-block."""
    if boss_cov is None:
        boss_cov = BOSS_FS8_COV_3x3
    cov = np.diag(sigma_data ** 2)
    boss_idx = []
    for z_boss in BOSS_FS8_Z:
        matches = np.where(np.abs(z_data - z_boss) < z_tol)[0]
        if len(matches) == 1:
            boss_idx.append(matches[0])
    if len(boss_idx) == 3:
        for i, bi in enumerate(boss_idx):
            for j, bj in enumerate(boss_idx):
                cov[bi, bj] = boss_cov[i, j]
    return cov


class GrowthModule(BaseModule):
    """fσ8(z) module with automatic BOSS DR12 3x3 covariance."""

    def __init__(self, engine: Optional[EFCGrowth] = None):
        if engine is None:
            engine = EFCGrowth()
        super().__init__(engine)
        self._covariance: Optional[np.ndarray] = None
        self._cov_inv: Optional[np.ndarray] = None
        self._cov_logdet: Optional[float] = None

    @property
    def name(self) -> str:
        return "growth"

    def load_data(self, data_path: str = None, use_boss_cov: bool = True,
                  cov_matrix: Optional[np.ndarray] = None, **kwargs):
        if data_path is None:
            raise ValueError("data_path is required")
        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"fσ8 data not found: {path}")

        lines, header_skipped = [], False
        with open(str(path)) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if not header_skipped:
                    header_skipped = True
                    continue
                lines.append([float(x) for x in line.split(",")])
        raw = np.array(lines)
        if raw.ndim == 1:
            raw = raw.reshape(1, -1)
        self.coordinates = raw[:, 0]
        self.observed = raw[:, 1]
        self.errors = raw[:, 2]

        if cov_matrix is not None:
            self._covariance = np.array(cov_matrix)
        elif use_boss_cov:
            self._covariance = build_fs8_covariance(self.coordinates, self.errors)

        if self._covariance is not None:
            try:
                L = np.linalg.cholesky(self._covariance)
                self._cov_inv = np.linalg.solve(
                    self._covariance, np.eye(len(self.observed))
                )
                self._cov_logdet = 2.0 * float(np.sum(np.log(np.diag(L))))
            except np.linalg.LinAlgError:
                logger.warning("Covariance not positive definite; using diagonal.")
                self._covariance = None
                self._cov_inv = None
                self._cov_logdet = None

        self._loaded = True
        logger.info("Loaded fσ8 data: %d points", len(self.coordinates))

    def log_likelihood(self, params_dict: dict) -> float:
        pred = self.predict(params_dict)
        if pred is None or np.any(np.isnan(pred)):
            return -np.inf
        if self._cov_inv is not None:
            residuals = self.observed - pred
            chi2 = float(residuals @ self._cov_inv @ residuals)
            n = len(self.observed)
            return -0.5 * (chi2 + self._cov_logdet + n * np.log(2 * np.pi))
        return log_likelihood_chi2(self.observed, pred, self.errors)


__all__ = [
    "C_KM_S", "DEFAULT_RD",
    "log_likelihood_chi2", "log_likelihood_covariance",
    "CosmologyModel", "FlatLCDM", "EFCVariantI", "EFCVariantJ", "EFCVariantK",
    "EFCEngine", "EFCHubble", "EFCGrowth",
    "BaseModule", "BAOModule", "HzModule", "GrowthModule",
    "BOSS_FS8_COV_3x3", "build_fs8_covariance",
]
