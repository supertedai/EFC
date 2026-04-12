#!/bin/bash
# ============================================================
# EFC Euclid DR1 Pipeline -- Execution Checklist
# Run this on local machine or Symbiose (not claude.ai)
# ============================================================
#
# Status: Design complete. All sanity checks pass.
# What remains: hi_class -> real Cl -> verify -> freeze.
#
# Estimated time: 2 months focused work (buffer to October 2026)
# ============================================================

set -e

PIPELINE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PIPELINE_DIR"

echo "=== STEP 0: Sanity checks (run first, every time) ==="
PYTHONPATH=. python tests/test_sanity.py
# Must show: ALL PASS (A through F)
# If any fail: DO NOT PROCEED

echo ""
echo "=== STEP 1: Install hi_class ==="
# Option A: pip (if available)
# pip install hi_class

# Option B: build from source
# git clone https://github.com/miguelzuma/hi_class_public.git
# cd hi_class_public && make class && pip install .

# Verify:
# python -c "from classy import Class; print('hi_class OK')"

echo ""
echo "=== STEP 2: Run EFC through hi_class ==="
# Generate config
PYTHONPATH=. python src/efc_hiclass_bridge.py --write-ini --write-yaml

# Run hi_class (produces Cl, P(k), transfer functions)
mkdir -p output

# Via Python:
# python3 << 'HICLASS'
# from classy import Class
# import numpy as np
#
# # LCDM baseline
# cosmo_lcdm = Class()
# cosmo_lcdm.set({
#     'output': 'tCl,pCl,lCl,mPk',
#     'lensing': 'yes',
#     'l_max_scalars': 5000,
#     'h': 0.6736,
#     'omega_b': 0.02237,
#     'omega_cdm': 0.1200,
#     'n_s': 0.9649,
#     'ln10^{10}A_s': 3.044,
#     'tau_reio': 0.0544,
#     'z_pk': '0,0.2,0.35,0.5,0.7,1.0,1.5,2.0',
# })
# cosmo_lcdm.compute()
#
# ell = np.arange(2, 5001)
# cl_tt_lcdm = [cosmo_lcdm.lensed_cl(l)['tt'] for l in ell]
# np.savez('output/cl_lcdm.npz', ell=ell, cl_tt=cl_tt_lcdm)
# print("LCDM Cl saved")
# cosmo_lcdm.struct_cleanup()
# HICLASS

echo ""
echo "=== STEP 3: Critical verification ==="
echo "--- 3a: Mapping consistency (TEST G) ---"
# Compare input mu(k,z) vs effective mu from hi_class growth
# mu_eff = D''(a) + 2H D'(a) / (4 pi G rho_m D(a))
# If |mu_eff - mu_input| > 2%: MAPPING LEAKS, STOP

echo "--- 3b: Limber vs non-Limber ---"
# Run CLASS with l_switch_limber = 10 (default) and 1000 (near-exact)
# Compare Cl^WL at ell = 30-100
# Report: "Limber error at ell=66: X%"

echo "--- 3c: Early-time verification ---"
# Extract Cl^TT from hi_class EFC run
# Compare with Planck 2018 LCDM at ell > 30
# Must match to < 0.1% (EFC = GR at z > 50)

echo ""
echo "=== STEP 4: Build E_G from real Cl ==="
# E_G(ell) = Cl^{g-kappa}(ell) / [Cl^{gg}(ell) * beta(z)]
# where:
#   Cl^{g-kappa} = galaxy-convergence cross-spectrum
#   Cl^{gg} = galaxy auto-spectrum
#   beta = f/b (growth rate / bias)
#
# For EFC: E_G propto Sigma / (f * mu) -> bump at ell ~ 66
#
# Compute BOTH:
#   - E_G(ell) unbinned (theoretical)
#   - E_G(ell-bin, z-bin) with Euclid window (observable)
#
# Compare: window smearing reduces 5.5% -> X%

echo ""
echo "=== STEP 5: Freeze predictions ==="
# For each prediction, generate RCMP-compliant block:
#
# PREDICTION: E_G(ell=50-80, z=0.3-0.5) = [value +/- sigma]
# REGIME: linear, k < 0.1 h/Mpc, ell > 30
# RCMP STATUS:
#   - galaxy bias: cancels in E_G ratio
#   - IA: < 1% at ell < 200
#   - nonlinear: excluded (k < 0.1)
#   - Limber: verified < X% error
#   - f(z): from hi_class (not GR approx)
# INTERPRETATION:
#   - If absent at > 3sigma: EFC mu-Sigma coupling falsified
#   - If present: model survives RCMP-clean test
#
# SHA-256 hash of the block
# Timestamp

echo ""
echo "=== STEP 6: Cobaya + PolyChord ==="
# Full posterior: cobaya-run config/efc_cobaya.yaml
# Requires: classy_hiclass theory module + Planck likelihoods
# Output: posterior on (B0, M0, h, omega_b, omega_cdm, n_s, A_s, tau)
# + Bayesian evidence ln Z

echo ""
echo "=== STEP 7: Wait for Euclid DR1 (October 21, 2026) ==="
# Swap mock data vector with real Euclid Cl
# Run cobaya
# Compare predictions vs data
# Report: which kill criteria pass/fail

echo ""
echo "============================================================"
echo "Pipeline ready. All design work is done."
echo "Next action: install hi_class and run Step 2."
echo "============================================================"
