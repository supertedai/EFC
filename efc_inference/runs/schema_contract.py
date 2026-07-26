#!/usr/bin/env python3
"""
ResearchCycleResult Schema Contract v1.0

Defines the REQUIRED and OPTIONAL fields that both samplers (emcee, NUTS)
must write to Neo4j. A validator function blocks publishing on mismatch.

Both samplers MUST write all REQUIRED fields. OPTIONAL fields are sampler-
or diagnostic-specific and may be null.

Usage:
    from efc_inference.runs.schema_contract import (
        SCHEMA_VERSION, validate_cycle_data, compute_dataset_hash,
        compute_assumptions_hash, get_code_commit,
    )
"""
import hashlib
import json
import logging
import os
import subprocess
from typing import Any

logger = logging.getLogger("schema_contract")

# ── Schema version ──────────────────────────────────────────────────
# Bump this when adding/removing REQUIRED fields. Both samplers must match.
SCHEMA_VERSION = "1.0"

# ── REQUIRED fields (both samplers MUST write these) ────────────────
REQUIRED_BASELINE = {
    "cycle_id",           # str: unique cycle identifier
    "timestamp",          # str: ISO 8601
    "sampler_type",       # str: 'emcee' or 'nuts'
    "schema_version",     # str: must match SCHEMA_VERSION
    "code_commit",        # str: git short hash
    "dataset_hash",       # str: SHA256 of input data
    "assumptions_hash",   # str: SHA256 of assumptions.yaml
    "cosmology_model",    # str: model name (e.g. 'efc_variant_a')
    "verdict",            # str: ROBUST/PARTIAL/MARGINAL/NO_SIGNAL/...
    "alpha_mean",         # float
    "alpha_std",          # float
    "alpha_significance", # float
    "p_alpha_negative",   # float: P(alpha < 0)
    "daic",               # float: Delta AIC vs LCDM
    "dbic",               # float: Delta BIC vs LCDM
    "om_mean",            # float: Omega_m posterior mean
    "om_std",             # float
    "h0_mean",            # float: H0 posterior mean
    "h0_std",             # float
    "s8_mean",            # float: sigma8 posterior mean
    "s8_std",             # float
    "n_eff_min",          # int/float: minimum effective sample size
    "r_hat_max",          # float: maximum Gelman-Rubin R-hat
    "n_data",             # int: total data points
    "signal_detected",    # bool
    "convergence_pass",   # bool
    "manifest_json",      # str: JSON metadata
}

# ── OPTIONAL fields (diagnostic results, sampler-specific) ─────────
OPTIONAL_DIAGNOSTICS = {
    # N1 rd-control
    "n1_verdict", "n1a_alpha_sig", "n1b_alpha_sig",
    # N2 sigma8-sweep
    "n2_verdict", "n2_stram_sig",
    # T7 leave-one-out (v2 sign-consistency)
    "t7_verdict", "t7_pass_count", "t7_n_total", "t7_robustness",
    "t7_criterion", "t7_strength_counts",
    # N3 gate freedom (A_eff reparameterized)
    "n3_verdict", "n3_reparameterized",
    "n3_aeff_sig", "n3_aeff_mean", "n3_aeff_std", "n3_aeff_p_negative",
    "n3_alpha_derived_mean", "n3_alpha_derived_std",
    "n3_a_t_mean", "n3_delta_a_mean",
    "n3_corr_aeff_at", "n3_corr_aeff_da", "n3_sweep_stable",
    # N4 modified Poisson
    "n4_verdict", "n4_free_alpha_sig",
    "n4_mu0_mean", "n4_mu0_std", "n4_mu0_deviation_from_gr",
    "n4_corr_alpha_mu0", "n4_sweep_stable", "n4_alpha_survives",
    # N5 sound horizon prior sweep (D2a)
    "n5_verdict", "n5_sweep_stable", "n5_max_corr_alpha_rd",
    "n5_alpha_survives_flat", "n5_high_degeneracy", "n5_sig_range",
    "n5_tight_alpha_sig", "n5_broad_alpha_sig", "n5_flat_alpha_sig",
    "n5_flat_rd_mean", "n5_flat_rd_std",
    # N6 EFC sound horizon (D2b)
    "n6_verdict", "n6_rd_efc_mean", "n6_rd_efc_std",
    "n6_rd_gr_mean", "n6_delta_rd_pct", "n6_safety_pass",
    "n6_R_max", "n6_R_at_drag_mean", "n6_c_eff_at_drag",
    # N7-GRAV: GRAV-locked cross-probe ("Domstolen")
    "n7_grav_verdict", "n7_grav_alpha_mean", "n7_grav_alpha_std",
    "n7_grav_alpha_sig", "n7_grav_alpha_p_negative",
    "n7_grav_daic", "n7_grav_dbic",
    # D2 self-consistent sound horizon
    "d2_verdict", "d2_alpha_mean", "d2_alpha_std", "d2_alpha_sig",
    "d2_delta_alpha_sig", "d2_rd_mean", "d2_rd_std",
    "d2_daic", "d2_dbic",
    # VariantG constitutive law — 3 pre-registered k_eff scenarios
    # Per-scenario fields: vg_{scenario}_{field} where scenario ∈ {g10, g02, g01}
    *[f"vg_{sc}_{f}" for sc in ("g10", "g02", "g01")
      for f in ("verdict", "dll_total", "daic_same_k",
                "s8_vg_mean", "s8_vg_std", "s8_lcdm_mean", "s8_lcdm_std", "s8_shift",
                "om_vg_mean", "h0_vg_mean",
                "mu_amp", "mu_span", "k_eff", "epsilon_eff", "screen_k_eff",
                "n_eff_min", "r_hat_max")],
    # Timing
    "diag_time_seconds", "wall_time_seconds", "total_mcmc_time",
}

# ── Sampler-specific optional fields ────────────────────────────────
OPTIONAL_SAMPLER = {
    # emcee-only
    "verdict_reasoning", "diagnostics_triggered", "artifact_path",
    "assumptions_json",
    # NUTS-only
    "has_posterior_chain", "chain_artifact_path",
}


def validate_cycle_data(data: dict[str, Any], strict: bool = True) -> tuple[bool, list[str]]:
    """
    Validate that cycle data contains all REQUIRED fields.

    Returns (is_valid, list_of_errors).
    If strict=True, raises ValueError on failure.
    """
    errors = []

    # Check schema version
    sv = data.get("schema_version")
    if sv is None:
        errors.append("Missing schema_version")
    elif sv != SCHEMA_VERSION:
        errors.append(f"Schema version mismatch: got '{sv}', expected '{SCHEMA_VERSION}'")

    # Check required fields
    for field in REQUIRED_BASELINE:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif data[field] is None:
            errors.append(f"Required field is None: {field}")

    # Check code_commit is not empty
    cc = data.get("code_commit", "")
    if not cc or cc == "unknown":
        errors.append("code_commit is empty or 'unknown' — git hash required")

    # Check dataset_hash is not empty
    dh = data.get("dataset_hash", "")
    if not dh:
        errors.append("dataset_hash is empty — data integrity cannot be verified")

    is_valid = len(errors) == 0

    if not is_valid:
        msg = f"Schema validation FAILED ({len(errors)} errors):\n  " + "\n  ".join(errors)
        logger.error(msg)
        if strict:
            raise ValueError(msg)

    return is_valid, errors


def compute_dataset_hash(data_files: list[str] | None = None, data_dict: dict | None = None) -> str:
    """
    Compute SHA256 hash of dataset.

    Can accept either file paths (for file-based data loading) or
    a dict of arrays (for in-memory data).
    """
    h = hashlib.sha256()

    if data_files:
        for fp in sorted(data_files):
            if os.path.exists(fp):
                with open(fp, "rb") as f:
                    h.update(f.read())
            else:
                h.update(fp.encode())

    if data_dict:
        # Sort keys for determinism
        import numpy as np
        for k in sorted(data_dict.keys()):
            h.update(k.encode())
            v = data_dict[k]
            if hasattr(v, "tobytes"):  # numpy array
                h.update(v.tobytes())
            else:
                h.update(str(v).encode())

    return h.hexdigest()[:16]


def compute_assumptions_hash(assumptions_path: str | None = None, assumptions_dict: dict | None = None) -> str:
    """Compute SHA256 hash of assumptions (YAML or dict)."""
    h = hashlib.sha256()

    if assumptions_path and os.path.exists(assumptions_path):
        with open(assumptions_path, "rb") as f:
            h.update(f.read())
    elif assumptions_dict:
        h.update(json.dumps(assumptions_dict, sort_keys=True, default=str).encode())
    else:
        h.update(b"no_assumptions")

    return h.hexdigest()[:16]


def get_code_commit(repo_path: str | None = None) -> str:
    """Get current git short hash."""
    try:
        if repo_path:
            result = subprocess.run(
                ["git", "-C", repo_path, "rev-parse", "--short=8", "HEAD"],
                capture_output=True, text=True, timeout=5,
            )
        else:
            result = subprocess.run(
                ["git", "rev-parse", "--short=8", "HEAD"],
                capture_output=True, text=True, timeout=5,
            )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"
