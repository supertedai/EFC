#!/usr/bin/env python3
"""
Sanity checks for nested sampling configs.

Verifies that EFC and ΛCDM configs share identical priors (for shared
parameters), identical likelihoods, and identical theory settings —
which is REQUIRED for valid Bayes factor computation.
"""

import sys
from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).parent.parent / "config"

PAIRS = [
    ("efc_polychord.yaml", "lcdm_polychord.yaml"),
    ("efc_polychord_reduced.yaml", "lcdm_polychord_reduced.yaml"),
]

SHARED_PARAMS = ["logA", "ns", "theta_MC_100", "ombh2", "omch2", "tau"]
EFC_ONLY_PARAMS = ["K0", "m_sq"]


def load(name):
    with open(CONFIG_DIR / name) as f:
        return yaml.safe_load(f)


def test_likelihood_match():
    """EFC and ΛCDM must use identical likelihoods."""
    for efc_file, lcdm_file in PAIRS:
        efc = load(efc_file)
        lcdm = load(lcdm_file)
        efc_lk = set(efc["likelihood"].keys())
        lcdm_lk = set(lcdm["likelihood"].keys())
        assert efc_lk == lcdm_lk, (
            f"{efc_file} vs {lcdm_file}: likelihoods differ: "
            f"{efc_lk.symmetric_difference(lcdm_lk)}"
        )


def test_shared_prior_match():
    """Shared ΛCDM params must have identical priors in both configs."""
    for efc_file, lcdm_file in PAIRS:
        efc = load(efc_file)
        lcdm = load(lcdm_file)
        for p in SHARED_PARAMS:
            efc_prior = efc["params"][p].get("prior")
            lcdm_prior = lcdm["params"][p].get("prior")
            assert efc_prior == lcdm_prior, (
                f"{efc_file} vs {lcdm_file}: prior mismatch for {p}: "
                f"{efc_prior} vs {lcdm_prior}"
            )


def test_theory_match():
    """Theory blocks must be identical."""
    for efc_file, lcdm_file in PAIRS:
        efc = load(efc_file)
        lcdm = load(lcdm_file)
        # LCDM may drop MG flags — check CAMB extra_args that exist in both
        efc_args = efc["theory"]["camb"].get("extra_args", {})
        lcdm_args = lcdm["theory"]["camb"].get("extra_args", {})
        for key in ["lmax", "lens_potential_accuracy", "AccuracyBoost",
                    "lAccuracyBoost", "w", "mnu", "nnu"]:
            if key in efc_args and key in lcdm_args:
                assert efc_args[key] == lcdm_args[key], (
                    f"Theory mismatch: {key}: {efc_args[key]} vs {lcdm_args[key]}"
                )


def test_efc_has_K0_msq():
    """EFC configs must sample K0 and m_sq."""
    for efc_file, _ in PAIRS:
        efc = load(efc_file)
        for p in EFC_ONLY_PARAMS:
            assert p in efc["params"], f"{efc_file} missing {p}"
            assert "prior" in efc["params"][p], f"{efc_file}: {p} has no prior"


def test_lcdm_no_K0_msq():
    """ΛCDM configs must NOT have K0 or m_sq."""
    for _, lcdm_file in PAIRS:
        lcdm = load(lcdm_file)
        for p in EFC_ONLY_PARAMS:
            assert p not in lcdm["params"], (
                f"{lcdm_file} should not have {p}"
            )


def test_bridge_constants():
    """Bridge constants in YAML must match bridge_theory.py reference."""
    efc = load("efc_polychord.yaml")
    # K0 prior should bracket K0_ref = 1.66
    k0_prior = efc["params"]["K0"]["prior"]
    assert k0_prior["min"] <= 1.66 <= k0_prior["max"]
    # m_sq prior should bracket msq_ref = 0.0035
    msq_prior = efc["params"]["m_sq"]["prior"]
    assert msq_prior["min"] <= 0.0035 <= msq_prior["max"]


if __name__ == "__main__":
    tests = [test_likelihood_match, test_shared_prior_match,
             test_theory_match, test_efc_has_K0_msq,
             test_lcdm_no_K0_msq, test_bridge_constants]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {t.__name__}: {e}")
            failed += 1
    sys.exit(failed)
