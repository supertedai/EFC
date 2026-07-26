#!/usr/bin/env python3
"""
Data Hygiene Gate — pre-flight validation before MCMC.

Runs schema checks, unit sanity, NaN/inf rejection, baseline LCDM
sanity fit, and SHA256 data hashing. Returns HygieneResult with
pass/fail and details.

Usage:
    result = run_data_hygiene(bao_path, growth_path, bao_mod, growth_mod, policy)
    if not result.passed:
        logger.error(f"Data hygiene failed: {result.failures}")
"""
import os
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("data_hygiene")


# ═══════════════════════════════════════════════════════════════
#  EXPECTED SCHEMAS
# ═══════════════════════════════════════════════════════════════

BAO_REQUIRED_COLUMNS = {"z", "observable", "value", "sigma"}
GROWTH_REQUIRED_COLUMNS = {"z", "fs8", "sigma"}


# ═══════════════════════════════════════════════════════════════
#  RESULT
# ═══════════════════════════════════════════════════════════════

@dataclass
class HygieneResult:
    """Result from pre-flight data validation."""
    passed: bool
    checks: dict = field(default_factory=dict)     # {"schema": True, "unit_sanity": True, ...}
    failures: list = field(default_factory=list)    # ["NaN found in column sigma", ...]
    data_hashes: dict = field(default_factory=dict) # {"bao": "sha256...", "growth": "sha256..."}
    lcdm_chi2_red: Optional[float] = None

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════
#  INDIVIDUAL CHECKS
# ═══════════════════════════════════════════════════════════════

def validate_schema(df: pd.DataFrame, expected_columns: set, label: str) -> tuple:
    """Check column names vs whitelist. Returns (passed, failures)."""
    actual = set(df.columns)
    missing = expected_columns - actual
    if missing:
        return False, [f"{label}: missing columns {missing}"]
    return True, []


def validate_unit_sanity(df: pd.DataFrame, label: str,
                         z_range: tuple = (0.0, 3.0),
                         check_error_positivity: bool = True,
                         check_nan_inf: bool = True) -> tuple:
    """Validate data values: NaN, inf, negative errors, z-range.
    Returns (passed, failures).
    """
    failures = []

    # NaN check
    if check_nan_inf:
        nan_counts = df.isna().sum()
        nan_cols = nan_counts[nan_counts > 0]
        if len(nan_cols) > 0:
            for col, cnt in nan_cols.items():
                failures.append(f"{label}: {cnt} NaN values in column '{col}'")

        # Inf check on numeric columns
        for col in df.select_dtypes(include=[np.number]).columns:
            inf_count = np.isinf(df[col]).sum()
            if inf_count > 0:
                failures.append(f"{label}: {inf_count} inf values in column '{col}'")

    # z-range check
    if "z" in df.columns:
        z_min, z_max = z_range
        z_vals = df["z"]
        out_of_range = ((z_vals < z_min) | (z_vals > z_max)).sum()
        if out_of_range > 0:
            failures.append(f"{label}: {out_of_range} redshifts outside [{z_min}, {z_max}]")

    # Error positivity
    if check_error_positivity and "sigma" in df.columns:
        neg_sigma = (df["sigma"] <= 0).sum()
        if neg_sigma > 0:
            failures.append(f"{label}: {neg_sigma} non-positive sigma values")

    passed = len(failures) == 0
    return passed, failures


def compute_data_hash(filepath: str) -> str:
    """SHA256 hash of a data file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def run_lcdm_sanity_fit(bao_mod, growth_mod, max_chi2_red: float = 10.0,
                         nsteps: int = 500) -> tuple:
    """Quick LCDM sanity fit to check data isn't corrupt.

    Uses a quick grid evaluation (no full MCMC) at fiducial params.
    Returns (passed, chi2_red, failures).
    """
    try:
        # Fiducial LCDM: Om=0.315, H0=67.4, s8=0.811, alpha=0 (LCDM)
        fiducial = {
            "Omega_m": 0.315,
            "H0": 67.4,
            "sigma8": 0.811,
            "alpha_cosmo": 0.0,
            "r_d": 147.09,
        }

        # Evaluate log-likelihood at fiducial point
        ll_bao = bao_mod.log_likelihood(fiducial)
        ll_gr = growth_mod.log_likelihood(fiducial)

        if not np.isfinite(ll_bao) or not np.isfinite(ll_gr):
            return False, None, ["LCDM sanity: log-likelihood is -inf at fiducial params"]

        total_ll = ll_bao + ll_gr

        # Approximate chi2 = -2 * log_likelihood
        chi2 = -2.0 * total_ll
        n_data = len(bao_mod.coordinates) + len(growth_mod.coordinates)
        n_params = 3  # Om, H0, s8
        dof = max(n_data - n_params, 1)
        chi2_red = chi2 / dof

        failures = []
        if chi2_red > max_chi2_red:
            failures.append(
                f"LCDM sanity: chi2_red={chi2_red:.2f} > {max_chi2_red} "
                f"(data may be corrupt or model severely wrong)"
            )

        passed = len(failures) == 0
        return passed, float(chi2_red), failures

    except Exception as e:
        return False, None, [f"LCDM sanity fit error: {e}"]


# ═══════════════════════════════════════════════════════════════
#  MAIN GATE
# ═══════════════════════════════════════════════════════════════

def run_data_hygiene(bao_path: str, growth_path: str,
                     bao_mod, growth_mod, policy,
                     extra_data_paths: dict = None) -> HygieneResult:
    """Run all pre-flight data validation checks.

    Args:
        bao_path: Path to BAO CSV
        growth_path: Path to growth CSV
        bao_mod: Loaded BAOModule
        growth_mod: Loaded GrowthModule
        policy: ResearchPolicy (uses data_hygiene_gate config)
        extra_data_paths: Optional dict of {label: path} for additional
                         data files to hash (e.g. {"hz": hz_path, "snia": snia_path}).
                         These are included in the combined data hash so that
                         adding new probes creates a new ResearchCase.

    Returns:
        HygieneResult with pass/fail and details
    """
    gate = policy.data_hygiene_gate
    checks = {}
    all_failures = []

    # 1. Schema check
    if gate.schema_check:
        try:
            # BAO can be CSV or JSON (DESI DR2 uses JSON with covariance)
            if bao_path.endswith(".json"):
                import json as _json
                with open(bao_path) as _f:
                    _bao_json = _json.load(_f)
                bao_df = pd.DataFrame(_bao_json.get("measurements", []))
                # JSON schema uses z_eff (DESI convention), not z
                bao_required = {"z_eff", "observable", "value"}
            else:
                bao_df = pd.read_csv(bao_path, comment="#")
                bao_required = BAO_REQUIRED_COLUMNS
            growth_df = pd.read_csv(growth_path, comment="#")

            ok_bao, f_bao = validate_schema(bao_df, bao_required, "BAO")
            ok_growth, f_growth = validate_schema(growth_df, GROWTH_REQUIRED_COLUMNS, "Growth")

            checks["schema_bao"] = ok_bao
            checks["schema_growth"] = ok_growth
            all_failures.extend(f_bao)
            all_failures.extend(f_growth)
        except Exception as e:
            checks["schema"] = False
            all_failures.append(f"Schema check error: {e}")
            bao_df = None
            growth_df = None
    else:
        checks["schema"] = True
        if bao_path.endswith(".json"):
            import json as _json
            with open(bao_path) as _f:
                _bao_json = _json.load(_f)
            bao_df = pd.DataFrame(_bao_json.get("measurements", []))
        else:
            bao_df = pd.read_csv(bao_path, comment="#")
        growth_df = pd.read_csv(growth_path, comment="#")

    # 2. Unit sanity
    if gate.unit_sanity and bao_df is not None and growth_df is not None:
        z_range = tuple(gate.z_range_check) if gate.z_range_check else (0.0, 3.0)

        ok_bao, f_bao = validate_unit_sanity(
            bao_df, "BAO", z_range=z_range,
            check_error_positivity=gate.error_positivity,
            check_nan_inf=gate.nan_inf_reject,
        )
        ok_growth, f_growth = validate_unit_sanity(
            growth_df, "Growth", z_range=z_range,
            check_error_positivity=gate.error_positivity,
            check_nan_inf=gate.nan_inf_reject,
        )

        checks["unit_sanity_bao"] = ok_bao
        checks["unit_sanity_growth"] = ok_growth
        all_failures.extend(f_bao)
        all_failures.extend(f_growth)
    else:
        checks["unit_sanity"] = True

    # 3. Data hashes (all active probes)
    data_hashes = {}
    if gate.compute_data_hash:
        try:
            data_hashes["bao"] = compute_data_hash(bao_path)
            data_hashes["growth"] = compute_data_hash(growth_path)
            # Hash any additional data files (Hz, SNIa, etc.)
            if extra_data_paths:
                for label, path in sorted(extra_data_paths.items()):
                    if path and os.path.exists(path):
                        data_hashes[label] = compute_data_hash(path)
            checks["data_hash"] = True
        except Exception as e:
            checks["data_hash"] = False
            all_failures.append(f"Data hash error: {e}")

    # 4. Baseline LCDM sanity fit
    lcdm_chi2_red = None
    if gate.baseline_sanity_fit:
        ok, chi2_red, f_sanity = run_lcdm_sanity_fit(
            bao_mod, growth_mod,
            max_chi2_red=gate.baseline_max_chi2_red,
            nsteps=gate.baseline_sanity_nsteps,
        )
        checks["lcdm_sanity"] = ok
        lcdm_chi2_red = chi2_red
        all_failures.extend(f_sanity)
    else:
        checks["lcdm_sanity"] = True

    passed = len(all_failures) == 0
    logger.info(f"Data hygiene: {'PASS' if passed else 'FAIL'} — "
                f"checks={checks}, failures={len(all_failures)}")

    return HygieneResult(
        passed=passed,
        checks=checks,
        failures=all_failures,
        data_hashes=data_hashes,
        lcdm_chi2_red=lcdm_chi2_red,
    )
