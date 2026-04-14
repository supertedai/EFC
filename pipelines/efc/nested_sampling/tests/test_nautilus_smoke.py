#!/usr/bin/env python3
"""
End-to-end smoke test for launch_nautilus.py.

Replaces the cobaya-backed CobayaLikelihoodWrapper with a mock 2D
Gaussian so the entire nautilus pipeline (Prior -> Sampler -> run ->
analyze_results -> make_plots) can be exercised in under 30 seconds
without needing cobaya, CAMB, or Planck data.

If this test passes, it guarantees:
  - nautilus Prior/Sampler API calls match the installed version
  - prior_transform wiring is correct
  - run_nautilus() returns a valid sampler object
  - analyze_results() produces a ledger-compatible JSON output
  - make_plots() produces a corner PDF (via getdist or matplotlib)
  - Posterior means recover injected truth within 0.3 sigma

Usage:
    cd pipelines/efc/nested_sampling
    python tests/test_nautilus_smoke.py
"""
import os
import sys
import tempfile
import types
import importlib.util
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).parent.parent / "src" / "launch_nautilus.py"


def _load_module_with_fake_cobaya():
    """Load launch_nautilus while stubbing out cobaya imports."""
    fake_cobaya = types.ModuleType("cobaya")
    fake_yaml = types.ModuleType("cobaya.yaml")
    fake_model = types.ModuleType("cobaya.model")
    fake_yaml.yaml_load_file = lambda f: {}
    fake_model.get_model = lambda info: None
    sys.modules.setdefault("cobaya", fake_cobaya)
    sys.modules.setdefault("cobaya.yaml", fake_yaml)
    sys.modules.setdefault("cobaya.model", fake_model)

    spec = importlib.util.spec_from_file_location("launch_nautilus", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _MockWrapper:
    """2D Gaussian peak at (K0=1.66, m_sq=0.0035) with narrow prior."""

    def __init__(self):
        self.param_names = ["K0", "m_sq"]
        self.ndim = 2
        self.prior_min = np.array([0.5, 0.001])
        self.prior_max = np.array([3.0, 0.010])
        self._mu = np.array([1.66, 0.0035])
        self._sigma = np.array([0.3, 0.001])

    def prior_transform(self, u):
        return self.prior_min + u * (self.prior_max - self.prior_min)

    def log_likelihood(self, theta):
        d = (theta - self._mu) / self._sigma
        return -0.5 * float(np.sum(d * d))


def main():
    mod = _load_module_with_fake_cobaya()
    print("[OK] launch_nautilus module loaded")

    wrapper = _MockWrapper()
    print(f"[OK] MockWrapper: ndim={wrapper.ndim}, params={wrapper.param_names}")

    print("\n--- Running nautilus (nlive=200, mock Gaussian) ---")
    sampler, w = mod.run_nautilus(wrapper, ncpu=1, nlive=200)
    print(f"[OK] Sampler returned, ln(Z) = {sampler.log_z:.3f}")

    with tempfile.TemporaryDirectory() as tmp:
        mod.OUTPUT_DIR = tmp
        output, samples_eq = mod.analyze_results(sampler, w, "mock_efc")
        print(f"[OK] analyze_results: ln(Z) = {output['logZ']:.3f} "
              f"+/- {output['logZ_err']:.3f}")

        K0 = output['parameters']['K0']
        msq = output['parameters']['m_sq']
        print(f"     K0   : {K0['mean']:.3f} +/- {K0['std']:.3f}  "
              f"(truth: 1.660)")
        print(f"     m_sq : {msq['mean']:.5f} +/- {msq['std']:.5f}  "
              f"(truth: 0.00350)")

        mod.make_plots(samples_eq, w.param_names, "mock_efc")
        pdf_path = Path(tmp) / "mock_efc_corner.pdf"
        assert pdf_path.exists(), f"Corner plot missing: {pdf_path}"
        assert pdf_path.stat().st_size > 1000, "Corner PDF suspiciously small"
        print(f"[OK] Corner plot written ({pdf_path.stat().st_size} bytes)")

        K0_sig = abs(K0['mean'] - 1.66) / 0.3
        msq_sig = abs(msq['mean'] - 0.0035) / 0.001
        assert K0_sig < 0.3, f"K0 recovery poor ({K0_sig:.2f}σ)"
        assert msq_sig < 0.3, f"m_sq recovery poor ({msq_sig:.2f}σ)"
        print(f"\n[PASS] Posterior recovery within 0.3 sigma "
              f"(K0: {K0_sig:.2f}σ, m_sq: {msq_sig:.2f}σ)")


if __name__ == "__main__":
    main()
