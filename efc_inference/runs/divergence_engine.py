"""
Divergence Maximization Engine — find where EFC and LCDM differ most.

Purpose:
  Given best-fit parameters from MCMC (both EFC and LCDM), compute:
  1. Per-data-point Delta-logL (EFC minus LCDM)
  2. Per-probe aggregate Delta-logL
  3. Observable-prediction divergence over a fine z-grid
  4. Ranking: which (probe, z) region gives maximal discrimination
  5. Sensitivity: d(observable)/d(alpha) at each z

This module does NOT run MCMC. It post-processes existing results.

Design principle:
  "Where can I lose the most?" — optimize for falsification risk.

Usage:
  from divergence_engine import DivergenceEngine
  engine = DivergenceEngine()
  report = engine.run(params_efc, params_lcdm)
  # report contains ranked discriminators, sweet spots, and predictions

Author: Symbiose AGI / COO
"""

import logging
import json
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ─── Paths (same defaults as research_mcmc.py) ──────────────────
_BASE = Path(__file__).resolve().parent.parent
# Use same relative paths as research_mcmc.py (resolved from repo root)
BAO_PATH = "efc_inference/data/bao/bao_starter.csv"
GROWTH_PATH = "efc_inference/data/growth/fs8_extended.csv"
HZ_PATH = "efc_inference/data/hubble/hz_cosmic_chronometers.csv"
SNIA_PATH = "efc_inference/data/snia/pantheon_binned.csv"
SNIA_COV_PATH = None  # Not always present


# ─── Data classes ────────────────────────────────────────────────

@dataclass
class PointDivergence:
    """Divergence at a single data point."""
    probe: str
    z: float
    observable: str           # e.g. "DH/rd", "H(z)", "fsigma8", "mu"
    obs_value: float
    obs_error: float
    pred_efc: float
    pred_lcdm: float
    delta_pred: float         # pred_efc - pred_lcdm
    delta_pred_sigma: float   # delta_pred / obs_error (in units of sigma)
    chi2_efc: float           # (obs - pred_efc)^2 / err^2
    chi2_lcdm: float          # (obs - pred_lcdm)^2 / err^2
    delta_chi2: float         # chi2_lcdm - chi2_efc (positive = EFC fits better)


@dataclass
class ProbeDivergence:
    """Aggregate divergence for one probe."""
    probe: str
    n_data: int
    total_logL_efc: float
    total_logL_lcdm: float
    delta_logL: float          # logL_efc - logL_lcdm (positive = EFC better)
    delta_chi2_total: float    # sum of per-point delta_chi2
    mean_delta_sigma: float    # mean |delta_pred| in sigma units
    max_delta_sigma: float     # max |delta_pred| in sigma units
    z_of_max_divergence: float # z where EFC and LCDM differ most
    points: List[PointDivergence] = field(default_factory=list)


@dataclass
class ObservablePrediction:
    """Model prediction at a fine z-grid point (for divergence maps)."""
    z: float
    pred_efc: float
    pred_lcdm: float
    delta: float              # EFC - LCDM
    delta_pct: float          # 100 * (EFC - LCDM) / LCDM


@dataclass
class SensitivityPoint:
    """Sensitivity of observable to alpha at a given z."""
    z: float
    observable: str
    d_obs_d_alpha: float      # numerical derivative
    pred_at_alpha: float
    pred_at_zero: float


@dataclass
class DivergenceReport:
    """Full divergence analysis report."""
    timestamp: str
    params_efc: Dict
    params_lcdm: Dict

    # Per-probe aggregate
    probe_divergences: Dict[str, ProbeDivergence]

    # Ranked discriminators: (probe, z) sorted by |delta_chi2|
    top_discriminators: List[PointDivergence]

    # Observable predictions on fine z-grid
    prediction_maps: Dict[str, List[ObservablePrediction]]

    # Sensitivity to alpha
    alpha_sensitivity: Dict[str, List[SensitivityPoint]]

    # Summary metrics
    total_delta_logL: float    # sum over all probes
    total_delta_chi2: float
    best_probe: str            # probe with highest discrimination
    best_z: float              # z with highest discrimination
    best_delta_sigma: float    # corresponding sigma

    # Blind prediction targets (for DESI DR2 etc.)
    blind_predictions: Dict[str, Dict]


class DivergenceEngine:
    """Compute where EFC and LCDM diverge most."""

    # Fine z-grid for prediction maps
    Z_GRID = np.linspace(0.01, 2.5, 200)

    # Probes and their observable names
    PROBE_OBSERVABLES = {
        "bao": "BAO distance ratios",
        "hz": "H(z) [km/s/Mpc]",
        "growth": "fsigma8(z)",
        "snia": "distance modulus mu(z)",
    }

    def __init__(self, bao_path=BAO_PATH, growth_path=GROWTH_PATH,
                 hz_path=HZ_PATH, snia_path=SNIA_PATH, snia_cov_path=SNIA_COV_PATH):
        self.bao_path = bao_path
        self.growth_path = growth_path
        self.hz_path = hz_path
        self.snia_path = snia_path
        self.snia_cov_path = snia_cov_path
        self._modules_efc = None
        self._modules_lcdm = None

    def _load_modules(self):
        """Load data modules for EFC and LCDM cosmologies."""
        from .research_mcmc import load_modules
        from ..core.cosmology_model import EFCVariantA, EFCVariantF, FlatLCDM

        # EFC uses VariantF (GRAV-coupled) for Divergence analysis
        self._modules_efc = load_modules(
            bao_path=self.bao_path, growth_path=self.growth_path,
            hz_path=self.hz_path, snia_path=self.snia_path,
            snia_cov_path=self.snia_cov_path,
            cosmology=EFCVariantF(),
        )
        # LCDM uses FlatLCDM
        self._modules_lcdm = load_modules(
            bao_path=self.bao_path, growth_path=self.growth_path,
            hz_path=self.hz_path, snia_path=self.snia_path,
            snia_cov_path=self.snia_cov_path,
            cosmology=FlatLCDM(),
        )
        logger.info("DivergenceEngine: modules loaded (EFC=VariantF, LCDM=FlatLCDM)")

    def run(self, params_efc: Dict, params_lcdm: Dict,
            z_grid: Optional[np.ndarray] = None) -> DivergenceReport:
        """Run full divergence analysis.

        Args:
            params_efc: Best-fit EFC parameters {Omega_m, H0, sigma8, alpha_cosmo, r_d}
            params_lcdm: Best-fit LCDM parameters {Omega_m, H0, sigma8, r_d}
            z_grid: Optional custom z-grid for prediction maps

        Returns:
            DivergenceReport with full analysis
        """
        if self._modules_efc is None:
            self._load_modules()

        if z_grid is None:
            z_grid = self.Z_GRID

        logger.info("═══ DIVERGENCE MAXIMIZATION ENGINE ═══")
        logger.info(f"  EFC params: Om={params_efc['Omega_m']:.4f}, "
                     f"H0={params_efc['H0']:.2f}, "
                     f"s8={params_efc['sigma8']:.4f}, "
                     f"α={params_efc['alpha_cosmo']:.4f}")
        logger.info(f"  LCDM params: Om={params_lcdm['Omega_m']:.4f}, "
                     f"H0={params_lcdm['H0']:.2f}, "
                     f"s8={params_lcdm['sigma8']:.4f}")

        # 1. Per-point divergence at actual data points
        probe_divergences = {}
        all_points = []

        for probe_name in ["bao", "hz", "growth", "snia"]:
            mod_efc = self._modules_efc.get(probe_name)
            mod_lcdm = self._modules_lcdm.get(probe_name)
            if mod_efc is None or mod_lcdm is None:
                continue

            pd = self._compute_probe_divergence(probe_name, mod_efc, mod_lcdm,
                                                 params_efc, params_lcdm)
            probe_divergences[probe_name] = pd
            all_points.extend(pd.points)

        # 2. Rank all data points by discrimination power
        all_points.sort(key=lambda p: abs(p.delta_chi2), reverse=True)
        top_discriminators = all_points[:20]  # top 20

        # 3. Observable prediction maps on fine z-grid
        prediction_maps = self._compute_prediction_maps(params_efc, params_lcdm, z_grid)

        # 4. Sensitivity: d(observable)/d(alpha) at each z
        alpha_sensitivity = self._compute_alpha_sensitivity(params_efc, z_grid)

        # 5. Summary metrics
        total_delta_logL = sum(pd.delta_logL for pd in probe_divergences.values())
        total_delta_chi2 = sum(pd.delta_chi2_total for pd in probe_divergences.values())

        if all_points:
            best_pt = all_points[0]
            best_probe = best_pt.probe
            best_z = best_pt.z
            best_delta_sigma = best_pt.delta_pred_sigma
        else:
            best_probe, best_z, best_delta_sigma = "none", 0.0, 0.0

        # 6. Blind predictions for future data
        blind_predictions = self._compute_blind_predictions(params_efc, params_lcdm)

        logger.info(f"  Total ΔlogL (EFC−LCDM): {total_delta_logL:.3f}")
        logger.info(f"  Total Δχ²: {total_delta_chi2:.3f}")
        logger.info(f"  Best discriminator: {best_probe} at z={best_z:.3f} "
                     f"({best_delta_sigma:.2f}σ prediction gap)")

        for pname, pd in probe_divergences.items():
            logger.info(f"  {pname}: ΔlogL={pd.delta_logL:.3f}, "
                         f"max divergence at z={pd.z_of_max_divergence:.3f} "
                         f"({pd.max_delta_sigma:.2f}σ)")

        report = DivergenceReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            params_efc=params_efc,
            params_lcdm=params_lcdm,
            probe_divergences=probe_divergences,
            top_discriminators=top_discriminators,
            prediction_maps=prediction_maps,
            alpha_sensitivity=alpha_sensitivity,
            total_delta_logL=total_delta_logL,
            total_delta_chi2=total_delta_chi2,
            best_probe=best_probe,
            best_z=best_z,
            best_delta_sigma=best_delta_sigma,
            blind_predictions=blind_predictions,
        )
        return report

    def _compute_probe_divergence(self, probe_name: str,
                                    mod_efc, mod_lcdm,
                                    params_efc: Dict, params_lcdm: Dict) -> ProbeDivergence:
        """Compute per-point and aggregate divergence for one probe."""
        pred_efc = mod_efc.predict(params_efc)
        pred_lcdm = mod_lcdm.predict(params_lcdm)

        obs = mod_efc.observed
        err = mod_efc.errors
        z_values = mod_efc.coordinates

        # Per-point
        points = []
        for i in range(len(obs)):
            chi2_efc_i = ((obs[i] - pred_efc[i]) / err[i]) ** 2
            chi2_lcdm_i = ((obs[i] - pred_lcdm[i]) / err[i]) ** 2
            delta_pred = pred_efc[i] - pred_lcdm[i]
            delta_pred_sigma = delta_pred / err[i] if err[i] > 0 else 0.0

            z_i = float(z_values[i]) if hasattr(z_values, '__getitem__') else float(z_values)

            pt = PointDivergence(
                probe=probe_name,
                z=z_i,
                observable=self.PROBE_OBSERVABLES.get(probe_name, probe_name),
                obs_value=float(obs[i]),
                obs_error=float(err[i]),
                pred_efc=float(pred_efc[i]),
                pred_lcdm=float(pred_lcdm[i]),
                delta_pred=float(delta_pred),
                delta_pred_sigma=float(delta_pred_sigma),
                chi2_efc=float(chi2_efc_i),
                chi2_lcdm=float(chi2_lcdm_i),
                delta_chi2=float(chi2_lcdm_i - chi2_efc_i),
            )
            points.append(pt)

        # Aggregate
        total_logL_efc = mod_efc.log_likelihood(params_efc)
        total_logL_lcdm = mod_lcdm.log_likelihood(params_lcdm)
        delta_logL = total_logL_efc - total_logL_lcdm
        delta_chi2_total = sum(p.delta_chi2 for p in points)
        delta_sigmas = [abs(p.delta_pred_sigma) for p in points]
        mean_delta_sigma = float(np.mean(delta_sigmas)) if delta_sigmas else 0.0
        max_delta_sigma = float(np.max(delta_sigmas)) if delta_sigmas else 0.0
        z_max_idx = int(np.argmax(delta_sigmas)) if delta_sigmas else 0
        z_of_max = points[z_max_idx].z if points else 0.0

        return ProbeDivergence(
            probe=probe_name,
            n_data=len(obs),
            total_logL_efc=float(total_logL_efc),
            total_logL_lcdm=float(total_logL_lcdm),
            delta_logL=float(delta_logL),
            delta_chi2_total=float(delta_chi2_total),
            mean_delta_sigma=mean_delta_sigma,
            max_delta_sigma=max_delta_sigma,
            z_of_max_divergence=z_of_max,
            points=points,
        )

    def _compute_prediction_maps(self, params_efc: Dict, params_lcdm: Dict,
                                   z_grid: np.ndarray) -> Dict[str, List[ObservablePrediction]]:
        """Compute EFC vs LCDM observable predictions on fine z-grid.

        This shows WHERE in redshift space the two models diverge.
        """
        from ..engine.hubble import EFCHubble
        from ..engine.growth import EFCGrowth
        from ..core.cosmology_model import EFCVariantF, FlatLCDM

        maps = {}

        # H(z) predictions
        hubble_efc = EFCHubble(cosmology=EFCVariantF())
        hubble_lcdm = EFCHubble(cosmology=FlatLCDM())

        hz_efc = hubble_efc.compute(params_efc, z_grid)
        hz_lcdm = hubble_lcdm.compute(params_lcdm, z_grid)

        maps["Hz"] = [
            ObservablePrediction(
                z=float(z_grid[i]),
                pred_efc=float(hz_efc[i]),
                pred_lcdm=float(hz_lcdm[i]),
                delta=float(hz_efc[i] - hz_lcdm[i]),
                delta_pct=float(100 * (hz_efc[i] - hz_lcdm[i]) / hz_lcdm[i]) if hz_lcdm[i] != 0 else 0,
            )
            for i in range(len(z_grid))
        ]

        # fσ8(z) predictions
        growth_efc = EFCGrowth(cosmology=EFCVariantF())
        growth_lcdm = EFCGrowth(cosmology=FlatLCDM())

        fs8_efc = growth_efc.compute(params_efc, z_grid)
        fs8_lcdm = growth_lcdm.compute(params_lcdm, z_grid)

        maps["fsigma8"] = [
            ObservablePrediction(
                z=float(z_grid[i]),
                pred_efc=float(fs8_efc[i]),
                pred_lcdm=float(fs8_lcdm[i]),
                delta=float(fs8_efc[i] - fs8_lcdm[i]),
                delta_pct=float(100 * (fs8_efc[i] - fs8_lcdm[i]) / fs8_lcdm[i]) if fs8_lcdm[i] != 0 else 0,
            )
            for i in range(len(z_grid))
        ]

        # D_L(z) (luminosity distance) — for SNIa mu = 5*log10(D_L/10pc)
        # Compute comoving distance from H(z): D_C = c * integral(dz/H(z))
        c_km = 299792.458  # km/s
        dz = np.diff(z_grid, prepend=0)

        dc_efc = np.cumsum(c_km * dz / hz_efc)
        dc_lcdm = np.cumsum(c_km * dz / hz_lcdm)
        dl_efc = dc_efc * (1 + z_grid)  # luminosity distance in Mpc
        dl_lcdm = dc_lcdm * (1 + z_grid)

        # Distance modulus
        mu_efc = np.where(dl_efc > 0, 5 * np.log10(dl_efc) + 25, 0)
        mu_lcdm = np.where(dl_lcdm > 0, 5 * np.log10(dl_lcdm) + 25, 0)

        maps["mu"] = [
            ObservablePrediction(
                z=float(z_grid[i]),
                pred_efc=float(mu_efc[i]),
                pred_lcdm=float(mu_lcdm[i]),
                delta=float(mu_efc[i] - mu_lcdm[i]),
                delta_pct=float(100 * (mu_efc[i] - mu_lcdm[i]) / mu_lcdm[i]) if mu_lcdm[i] != 0 else 0,
            )
            for i in range(len(z_grid))
        ]

        # D_A(z) / r_d (angular diameter distance ratio — for BAO)
        r_d = params_efc.get("r_d", 147.09)
        da_efc = dc_efc / (1 + z_grid)  # angular diameter distance
        da_lcdm = dc_lcdm / (1 + z_grid)
        da_rd_efc = da_efc / r_d
        da_rd_lcdm = da_lcdm / r_d

        maps["DA_over_rd"] = [
            ObservablePrediction(
                z=float(z_grid[i]),
                pred_efc=float(da_rd_efc[i]),
                pred_lcdm=float(da_rd_lcdm[i]),
                delta=float(da_rd_efc[i] - da_rd_lcdm[i]),
                delta_pct=float(100 * (da_rd_efc[i] - da_rd_lcdm[i]) / da_rd_lcdm[i])
                if da_rd_lcdm[i] != 0 else 0,
            )
            for i in range(len(z_grid))
        ]

        # DH/rd = c / (H(z) * rd) — Hubble distance for BAO
        dh_rd_efc = c_km / (hz_efc * r_d)
        dh_rd_lcdm = c_km / (hz_lcdm * r_d)

        maps["DH_over_rd"] = [
            ObservablePrediction(
                z=float(z_grid[i]),
                pred_efc=float(dh_rd_efc[i]),
                pred_lcdm=float(dh_rd_lcdm[i]),
                delta=float(dh_rd_efc[i] - dh_rd_lcdm[i]),
                delta_pct=float(100 * (dh_rd_efc[i] - dh_rd_lcdm[i]) / dh_rd_lcdm[i])
                if dh_rd_lcdm[i] != 0 else 0,
            )
            for i in range(len(z_grid))
        ]

        return maps

    def _compute_alpha_sensitivity(self, params_efc: Dict,
                                     z_grid: np.ndarray) -> Dict[str, List[SensitivityPoint]]:
        """Compute d(observable)/d(alpha) numerically.

        This tells us: at each z, how much does each observable
        change per unit alpha? High sensitivity = high discrimination potential.
        """
        from ..engine.hubble import EFCHubble
        from ..engine.growth import EFCGrowth
        from ..core.cosmology_model import EFCVariantF

        alpha_0 = params_efc["alpha_cosmo"]
        d_alpha = 0.1  # finite difference step

        params_plus = dict(params_efc)
        params_plus["alpha_cosmo"] = alpha_0 + d_alpha
        params_minus = dict(params_efc)
        params_minus["alpha_cosmo"] = alpha_0 - d_alpha

        sensitivity = {}

        # H(z) sensitivity
        hub = EFCHubble(cosmology=EFCVariantF())
        hz_plus = hub.compute(params_plus, z_grid)
        hz_minus = hub.compute(params_minus, z_grid)
        hz_at_alpha = hub.compute(params_efc, z_grid)

        # Central params (alpha=0) for reference
        params_zero = dict(params_efc)
        params_zero["alpha_cosmo"] = 0.0
        hz_at_zero = hub.compute(params_zero, z_grid)

        d_hz_d_alpha = (hz_plus - hz_minus) / (2 * d_alpha)

        sensitivity["Hz"] = [
            SensitivityPoint(
                z=float(z_grid[i]),
                observable="H(z)",
                d_obs_d_alpha=float(d_hz_d_alpha[i]),
                pred_at_alpha=float(hz_at_alpha[i]),
                pred_at_zero=float(hz_at_zero[i]),
            )
            for i in range(len(z_grid))
        ]

        # fσ8(z) sensitivity
        gro = EFCGrowth(cosmology=EFCVariantF())
        fs8_plus = gro.compute(params_plus, z_grid)
        fs8_minus = gro.compute(params_minus, z_grid)
        fs8_at_alpha = gro.compute(params_efc, z_grid)
        fs8_at_zero = gro.compute(params_zero, z_grid)

        d_fs8_d_alpha = (fs8_plus - fs8_minus) / (2 * d_alpha)

        sensitivity["fsigma8"] = [
            SensitivityPoint(
                z=float(z_grid[i]),
                observable="fsigma8(z)",
                d_obs_d_alpha=float(d_fs8_d_alpha[i]),
                pred_at_alpha=float(fs8_at_alpha[i]),
                pred_at_zero=float(fs8_at_zero[i]),
            )
            for i in range(len(z_grid))
        ]

        return sensitivity

    def _compute_blind_predictions(self, params_efc: Dict,
                                     params_lcdm: Dict) -> Dict[str, Dict]:
        """Generate blind predictions for upcoming data releases.

        These are frozen predictions that can be published BEFORE data is released.
        DESI DR2 expected z-bins for BAO: 0.1-0.5, 0.5-1.0, 1.0-1.5, 1.5-2.0
        """
        from ..engine.hubble import EFCHubble
        from ..engine.growth import EFCGrowth
        from ..core.cosmology_model import EFCVariantF, FlatLCDM

        # Target redshifts for DESI DR2
        z_targets = np.array([0.3, 0.5, 0.7, 1.0, 1.3, 1.5, 2.0, 2.5])
        r_d = params_efc.get("r_d", 147.09)
        c_km = 299792.458

        hub_efc = EFCHubble(cosmology=EFCVariantF())
        hub_lcdm = EFCHubble(cosmology=FlatLCDM())
        gro_efc = EFCGrowth(cosmology=EFCVariantF())
        gro_lcdm = EFCGrowth(cosmology=FlatLCDM())

        hz_efc = hub_efc.compute(params_efc, z_targets)
        hz_lcdm = hub_lcdm.compute(params_lcdm, z_targets)
        fs8_efc = gro_efc.compute(params_efc, z_targets)
        fs8_lcdm = gro_lcdm.compute(params_lcdm, z_targets)

        # DH/rd and DM/rd (for BAO predictions)
        dh_rd_efc = c_km / (hz_efc * r_d)
        dh_rd_lcdm = c_km / (hz_lcdm * r_d)

        predictions = {}
        for i, z in enumerate(z_targets):
            z_key = f"z={z:.1f}"
            predictions[z_key] = {
                "z": float(z),
                "Hz_efc": float(hz_efc[i]),
                "Hz_lcdm": float(hz_lcdm[i]),
                "Hz_delta_pct": float(100 * (hz_efc[i] - hz_lcdm[i]) / hz_lcdm[i]),
                "DH_rd_efc": float(dh_rd_efc[i]),
                "DH_rd_lcdm": float(dh_rd_lcdm[i]),
                "DH_rd_delta_pct": float(100 * (dh_rd_efc[i] - dh_rd_lcdm[i]) / dh_rd_lcdm[i]),
                "fsigma8_efc": float(fs8_efc[i]),
                "fsigma8_lcdm": float(fs8_lcdm[i]),
                "fsigma8_delta_pct": float(
                    100 * (fs8_efc[i] - fs8_lcdm[i]) / fs8_lcdm[i]
                ) if fs8_lcdm[i] != 0 else 0,
            }

        return predictions

    def save_report(self, report: DivergenceReport, output_dir: str = None) -> Path:
        """Save report as JSON."""
        if output_dir is None:
            output_dir = str(_BASE / "outputs" / "divergence")
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = out / f"divergence_{ts}.json"

        # Convert to serializable dict
        data = {
            "timestamp": report.timestamp,
            "params_efc": report.params_efc,
            "params_lcdm": report.params_lcdm,
            "total_delta_logL": report.total_delta_logL,
            "total_delta_chi2": report.total_delta_chi2,
            "best_probe": report.best_probe,
            "best_z": report.best_z,
            "best_delta_sigma": report.best_delta_sigma,

            "probe_divergences": {
                name: {
                    "probe": pd.probe,
                    "n_data": pd.n_data,
                    "total_logL_efc": pd.total_logL_efc,
                    "total_logL_lcdm": pd.total_logL_lcdm,
                    "delta_logL": pd.delta_logL,
                    "delta_chi2_total": pd.delta_chi2_total,
                    "mean_delta_sigma": pd.mean_delta_sigma,
                    "max_delta_sigma": pd.max_delta_sigma,
                    "z_of_max_divergence": pd.z_of_max_divergence,
                    "points": [asdict(p) for p in pd.points],
                }
                for name, pd in report.probe_divergences.items()
            },

            "top_discriminators": [asdict(p) for p in report.top_discriminators],

            "prediction_maps": {
                name: [asdict(p) for p in preds]
                for name, preds in report.prediction_maps.items()
            },

            "alpha_sensitivity": {
                name: [asdict(s) for s in sens]
                for name, sens in report.alpha_sensitivity.items()
            },

            "blind_predictions": report.blind_predictions,
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Divergence report saved: {path}")
        return path

    def summary_table(self, report: DivergenceReport) -> str:
        """Generate a human-readable summary table."""
        lines = []
        lines.append("╔═══════════════════════════════════════════════════════════════╗")
        lines.append("║         DIVERGENCE MAXIMIZATION REPORT                       ║")
        lines.append("╠═══════════════════════════════════════════════════════════════╣")
        lines.append(f"║  Total ΔlogL (EFC−ΛCDM): {report.total_delta_logL:+.3f}          ")
        lines.append(f"║  Total Δχ²:              {report.total_delta_chi2:+.3f}          ")
        lines.append(f"║  Best probe:             {report.best_probe} at z={report.best_z:.3f}")
        lines.append(f"║  Max prediction gap:     {report.best_delta_sigma:.2f}σ          ")
        lines.append("╠═══════════════════════════════════════════════════════════════╣")
        lines.append("║  PROBE RANKING (by |ΔlogL|):                                ║")
        lines.append("║  ─────────────────────────────────────────────────────────── ║")

        ranked = sorted(report.probe_divergences.values(),
                        key=lambda p: abs(p.delta_logL), reverse=True)
        for pd in ranked:
            sign = "+" if pd.delta_logL > 0 else ""
            lines.append(f"║  {pd.probe:8s}  ΔlogL={sign}{pd.delta_logL:.3f}  "
                         f"max_div@z={pd.z_of_max_divergence:.2f}  "
                         f"({pd.max_delta_sigma:.2f}σ gap)")

        lines.append("╠═══════════════════════════════════════════════════════════════╣")
        lines.append("║  TOP 10 DATA POINTS (by |Δχ²| EFC vs LCDM):                ║")
        lines.append("║  ─────────────────────────────────────────────────────────── ║")

        for pt in report.top_discriminators[:10]:
            sign = "+" if pt.delta_chi2 > 0 else ""
            lines.append(f"║  {pt.probe:8s} z={pt.z:.3f}  Δχ²={sign}{pt.delta_chi2:.3f}  "
                         f"gap={pt.delta_pred_sigma:+.2f}σ")

        lines.append("╠═══════════════════════════════════════════════════════════════╣")
        lines.append("║  BLIND PREDICTIONS (freeze & publish before data):          ║")
        lines.append("║  ─────────────────────────────────────────────────────────── ║")

        for z_key, pred in report.blind_predictions.items():
            lines.append(f"║  {z_key}: Hz Δ={pred['Hz_delta_pct']:+.2f}%  "
                         f"DH/rd Δ={pred['DH_rd_delta_pct']:+.2f}%  "
                         f"fσ8 Δ={pred['fsigma8_delta_pct']:+.2f}%")

        lines.append("╚═══════════════════════════════════════════════════════════════╝")
        return "\n".join(lines)


    def posterior_robustness(self, chain_efc: np.ndarray, chain_lcdm: np.ndarray,
                               n_draws: int = 100, seed: int = 42) -> Dict:
        """Recompute ΔlogL over N posterior draws to assess robustness.

        Instead of using a single median point, sample N random draws
        from the posterior and compute per-probe ΔlogL for each.
        Returns mean ± std for each probe.

        This answers: "Is the divergence real, or a single-point artifact?"
        """
        if self._modules_efc is None:
            self._load_modules()

        rng = np.random.default_rng(seed)
        n_efc = len(chain_efc)
        n_lcdm = len(chain_lcdm)

        # Sample random indices
        idx_efc = rng.choice(n_efc, size=n_draws, replace=True)
        idx_lcdm = rng.choice(n_lcdm, size=n_draws, replace=True)

        results = {name: [] for name in ["bao", "hz", "growth", "snia"]}

        logger.info(f"Posterior robustness: {n_draws} draws from {n_efc}/{n_lcdm} samples")

        for i in range(n_draws):
            p_efc = {
                "Omega_m": float(chain_efc[idx_efc[i], 0]),
                "H0": float(chain_efc[idx_efc[i], 1]),
                "sigma8": float(chain_efc[idx_efc[i], 2]),
                "alpha_cosmo": float(chain_efc[idx_efc[i], 3]),
                "r_d": 147.09,
            }
            p_lcdm = {
                "Omega_m": float(chain_lcdm[idx_lcdm[i], 0]),
                "H0": float(chain_lcdm[idx_lcdm[i], 1]),
                "sigma8": float(chain_lcdm[idx_lcdm[i], 2]),
                "alpha_cosmo": 0.0,
                "r_d": 147.09,
            }

            for probe_name in results:
                mod_efc = self._modules_efc.get(probe_name)
                mod_lcdm = self._modules_lcdm.get(probe_name)
                if mod_efc is None or mod_lcdm is None:
                    continue
                ll_efc = mod_efc.log_likelihood(p_efc)
                ll_lcdm = mod_lcdm.log_likelihood(p_lcdm)
                results[probe_name].append(ll_efc - ll_lcdm)

        # Compute statistics
        summary = {}
        total_mean = 0
        total_std = 0
        for probe_name, delta_lls in results.items():
            if not delta_lls:
                continue
            arr = np.array(delta_lls)
            mean = float(np.mean(arr))
            std = float(np.std(arr))
            pct_positive = float(np.mean(arr > 0) * 100)
            summary[probe_name] = {
                "mean_delta_logL": mean,
                "std_delta_logL": std,
                "pct_efc_better": pct_positive,
                "n_draws": len(arr),
            }
            total_mean += mean
            total_std += std ** 2
            logger.info(f"  {probe_name}: ΔlogL = {mean:+.3f} ± {std:.3f} "
                         f"(EFC better in {pct_positive:.0f}% of draws)")

        total_std = float(np.sqrt(total_std))
        summary["total"] = {
            "mean_delta_logL": total_mean,
            "std_delta_logL": total_std,
            "significance": abs(total_mean / total_std) if total_std > 0 else 0,
        }
        logger.info(f"  TOTAL: ΔlogL = {total_mean:+.3f} ± {total_std:.3f}")

        return summary

    def null_test(self, chain_lcdm: np.ndarray, n_draws: int = 100, seed: int = 42) -> Dict:
        """ΛCDM vs ΛCDM null test — measures noise floor.

        Splits the LCDM posterior chain into two halves and computes
        ΔlogL between them. The resulting distribution is the noise floor:
        any real signal must exceed this.

        This answers: "How much ΔlogL arises from parameter scatter alone?"
        """
        if self._modules_efc is None:
            self._load_modules()

        rng = np.random.default_rng(seed)
        n = len(chain_lcdm)
        half = n // 2

        # Use first half as "model A", second half as "model B"
        chain_a = chain_lcdm[:half]
        chain_b = chain_lcdm[half:]

        results = {name: [] for name in ["bao", "hz", "growth", "snia"]}

        logger.info(f"Null test (ΛCDM vs ΛCDM): {n_draws} draws from {half}/{n-half} samples")

        for i in range(n_draws):
            idx_a = rng.choice(len(chain_a))
            idx_b = rng.choice(len(chain_b))

            p_a = {
                "Omega_m": float(chain_a[idx_a, 0]),
                "H0": float(chain_a[idx_a, 1]),
                "sigma8": float(chain_a[idx_a, 2]),
                "alpha_cosmo": 0.0,
                "r_d": 147.09,
            }
            p_b = {
                "Omega_m": float(chain_b[idx_b, 0]),
                "H0": float(chain_b[idx_b, 1]),
                "sigma8": float(chain_b[idx_b, 2]),
                "alpha_cosmo": 0.0,
                "r_d": 147.09,
            }

            for probe_name in results:
                mod = self._modules_lcdm.get(probe_name)
                if mod is None:
                    continue
                ll_a = mod.log_likelihood(p_a)
                ll_b = mod.log_likelihood(p_b)
                results[probe_name].append(ll_a - ll_b)

        summary = {}
        for probe_name, delta_lls in results.items():
            if not delta_lls:
                continue
            arr = np.array(delta_lls)
            summary[probe_name] = {
                "noise_mean": float(np.mean(arr)),
                "noise_std": float(np.std(arr)),
                "noise_95pct": float(np.percentile(np.abs(arr), 95)),
                "n_draws": len(arr),
            }
            logger.info(f"  {probe_name} noise floor: ΔlogL = {np.mean(arr):+.3f} ± {np.std(arr):.3f} "
                         f"(95th pct = {np.percentile(np.abs(arr), 95):.3f})")

        return summary

    def forecast_discrimination(self, params_efc: Dict, params_lcdm: Dict,
                                  future_errors: Dict[str, Dict[str, float]] = None) -> Dict:
        """Forecast future discrimination power given expected measurement errors.

        For each probe and z, compute:
          separation_sigma = |pred_EFC - pred_LCDM| / future_error

        Default future errors based on DESI DR2 + Euclid projections.

        This answers: "Given future data, how many sigma will we separate?"
        """
        if self._modules_efc is None:
            self._load_modules()

        from ..engine.hubble import EFCHubble
        from ..engine.growth import EFCGrowth
        from ..core.cosmology_model import EFCVariantF, FlatLCDM

        # Default future error projections (1σ)
        if future_errors is None:
            future_errors = {
                "DH_rd": {  # BAO DH/rd errors (DESI DR2 + DESI Y5)
                    0.3: 0.8, 0.5: 0.5, 0.7: 0.4, 1.0: 0.3,
                    1.3: 0.5, 1.5: 0.7, 2.0: 1.0,
                },
                "fsigma8": {  # fσ8 errors (DESI DR2 + Euclid)
                    0.3: 0.015, 0.5: 0.012, 0.7: 0.010, 1.0: 0.015,
                    1.3: 0.020, 1.5: 0.025,
                },
                "Hz": {  # H(z) errors (cosmic chronometers improved)
                    0.3: 3.0, 0.5: 3.0, 0.7: 3.5, 1.0: 5.0,
                    1.3: 8.0, 1.5: 10.0,
                },
            }

        hub_efc = EFCHubble(cosmology=EFCVariantF())
        hub_lcdm = EFCHubble(cosmology=FlatLCDM())
        gro_efc = EFCGrowth(cosmology=EFCVariantF())
        gro_lcdm = EFCGrowth(cosmology=FlatLCDM())

        forecasts = {}
        r_d = params_efc.get("r_d", 147.09)
        c_km = 299792.458

        for probe_name, z_errors in future_errors.items():
            z_vals = np.array(sorted(z_errors.keys()))

            if probe_name == "Hz":
                pred_efc = hub_efc.compute(params_efc, z_vals)
                pred_lcdm = hub_lcdm.compute(params_lcdm, z_vals)
            elif probe_name == "fsigma8":
                pred_efc = gro_efc.compute(params_efc, z_vals)
                pred_lcdm = gro_lcdm.compute(params_lcdm, z_vals)
            elif probe_name == "DH_rd":
                hz_efc = hub_efc.compute(params_efc, z_vals)
                hz_lcdm = hub_lcdm.compute(params_lcdm, z_vals)
                pred_efc = c_km / (hz_efc * r_d)
                pred_lcdm = c_km / (hz_lcdm * r_d)
            else:
                continue

            probe_forecast = {}
            for i, z in enumerate(z_vals):
                error = z_errors[z]
                delta = abs(pred_efc[i] - pred_lcdm[i])
                sigma = delta / error if error > 0 else 0
                probe_forecast[f"z={z:.1f}"] = {
                    "z": float(z),
                    "pred_efc": float(pred_efc[i]),
                    "pred_lcdm": float(pred_lcdm[i]),
                    "delta": float(pred_efc[i] - pred_lcdm[i]),
                    "future_error": error,
                    "separation_sigma": float(sigma),
                }
                logger.info(f"  Forecast {probe_name} z={z:.1f}: "
                             f"Δ={pred_efc[i]-pred_lcdm[i]:+.4f}, "
                             f"σ_future={error:.4f} → {sigma:.1f}σ separation")
            forecasts[probe_name] = probe_forecast

        return forecasts


def run_divergence_from_neo4j() -> Optional[DivergenceReport]:
    """Load latest best-fit parameters from Neo4j and run divergence analysis.

    This is the main entry point for daemon/automated use.
    """
    try:
        import requests

        # Query Neo4j for latest research cycle with best-fit params
        api_url = "http://localhost:8000"
        resp = requests.get(f"{api_url}/api/v1/research/overview", timeout=30)
        if resp.status_code != 200:
            logger.error(f"Research API returned {resp.status_code}")
            return None

        overview = resp.json()
        cycles = overview.get("cycles", [])
        if not cycles:
            logger.warning("No research cycles found")
            return None

        # Find most recent cycle with best-fit params
        # Use emcee results (they have richer per-probe data from N7)
        latest = None
        for c in cycles:
            if c.get("sampler_type") == "emcee" and c.get("alpha_mean") is not None:
                latest = c
                break
        if latest is None:
            # Fallback to any sampler
            latest = cycles[0] if cycles else None

        if latest is None:
            logger.warning("No suitable cycle found")
            return None

        # Reconstruct params (best-fit are MAP estimates from MCMC)
        # Note: we use the cycle's reported values as approximate best-fit
        params_efc = {
            "Omega_m": latest.get("om_mean", 0.30),
            "H0": latest.get("h0_mean", 67.5),
            "sigma8": latest.get("s8_mean", 0.81),
            "alpha_cosmo": latest.get("alpha_mean", -0.7),
            "r_d": 147.09,
        }
        params_lcdm = {
            "Omega_m": latest.get("om_mean", 0.30),  # LCDM uses similar Om/H0
            "H0": latest.get("h0_mean", 67.5),
            "sigma8": latest.get("s8_mean", 0.81),
            "alpha_cosmo": 0.0,
            "r_d": 147.09,
        }

        engine = DivergenceEngine()
        report = engine.run(params_efc, params_lcdm)
        engine.save_report(report)
        return report

    except Exception as e:
        logger.error(f"Divergence from Neo4j failed: {type(e).__name__}: {e}")
        return None


# ─── CLI ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    # Default: use approximate best-fit from recent MCMC
    params_efc = {
        "Omega_m": 0.2735,
        "H0": 68.43,
        "sigma8": 0.8034,
        "alpha_cosmo": -0.673,
        "r_d": 147.09,
    }
    params_lcdm = {
        "Omega_m": 0.298,
        "H0": 67.8,
        "sigma8": 0.811,
        "alpha_cosmo": 0.0,
        "r_d": 147.09,
    }

    engine = DivergenceEngine()
    report = engine.run(params_efc, params_lcdm)
    print(engine.summary_table(report))
    engine.save_report(report)
