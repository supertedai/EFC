# EFC Nested Sampling Pipeline

Full Bayesian posterior and evidence computation for Energy-Flow Cosmology.

## Purpose

Addresses the critical inference gap: all existing cobaya runs use `minimize`
only, producing best-fit parameters without marginalized posteriors or Bayesian
evidence. The emcee daemon reports `DEGENERACY_LIMITED` and the NUTS daemon
shows `N1: COLLAPSED` — both indicate posterior structure that standard MCMC
cannot resolve. Nested sampling integrates the full volume.

## Architecture

This pipeline reuses the existing cobaya bridge from `tools/cobaya_bridge/`:

```
(K0, m_sq)  →  bridge_theory.py  →  (mu0, Sigma0) / Alens  →  CAMB/MGCAMB  →  likelihoods
```

Two variants:
- **Full** (`efc_polychord.yaml`): MGCAMB with mu0/Sigma0 pushed to Fortran backend. Full Planck plik_lite TTTEEE.
- **Reduced** (`efc_polychord_reduced.yaml`): Vanilla CAMB with Alens = Sigma0^2. Low-l + lensing.native + BAO + SNe. Sandbox-compatible.

Both EFC and ΛCDM configs share identical priors, likelihoods, and theory settings — only the EFC parameters (K0, m_sq) differ.

## Files

```
config/
  efc_polychord.yaml           # Full MGCAMB PolyChord (8 params)
  efc_polychord_reduced.yaml   # Vanilla CAMB PolyChord (8 params, reduced data)
  lcdm_polychord.yaml          # ΛCDM reference (6 params)
  lcdm_polychord_reduced.yaml  # ΛCDM reference (6 params, reduced data)
src/
  launch_polychord.py          # PolyChord pipeline: run → evidence → corners → ledger
  launch_dynesty.py            # dynesty pipeline (cobaya-backed, no placeholder)
tests/
  (sanity checks)
setup_environment.sh           # Install all deps on Symbiose machine
```

## Quick Start

```bash
# 1. Setup (once)
chmod +x setup_environment.sh && ./setup_environment.sh

# 2a. PolyChord (recommended, requires MPI):
source ~/efc_nested_venv/bin/activate
export COBAYA_PACKAGES_PATH=~/cobaya_packages
cd pipelines/efc/nested_sampling
mpirun -n 32 python src/launch_polychord.py          # full MGCAMB
mpirun -n 32 python src/launch_polychord.py --reduced # vanilla CAMB

# 2b. dynesty (no MPI needed):
python src/launch_dynesty.py --ncpu 16 --model both
python src/launch_dynesty.py --ncpu 16 --model both --reduced

# Or directly via cobaya:
cobaya-run config/efc_polychord.yaml
cobaya-run config/lcdm_polychord.yaml
```

## Parameter Space

Sampled (8 parameters, matching `tools/cobaya_bridge/efc_bridge_K0m2.yaml`):

| Parameter | Prior | Ref | Description |
|-----------|-------|-----|-------------|
| logA | [2.6, 3.5] | 3.044 | Scalar amplitude |
| ns | [0.9, 1.05] | 0.9649 | Spectral index |
| theta_MC_100 | [1.03, 1.05] | 1.04109 | Sound horizon angle |
| ombh2 | [0.019, 0.025] | 0.02237 | Baryon density |
| omch2 | [0.095, 0.145] | 0.1200 | CDM density |
| tau | Gaussian(0.0544, 0.0073) | 0.0544 | Reionization optical depth |
| **K0** | **[0.5, 3.0]** | **1.66** | **EFC stiffness amplitude** |
| **m_sq** | **[0.001, 0.010]** | **0.0035** | **EFC slip mass** |

Bridge calibration anchor: (K0=1.66, m_sq=0.0035) → (mu0=0.94, Sigma0=1.05).

## Outputs

- `polychord_output/` or `dynesty_output/`:
  - `ledger_entry_*.json` — Validation ledger entry
  - `parameter_summary.json` — Marginalized statistics
  - `bayes_factor_*.json` — ln(B) with uncertainty
  - `*_corner.pdf` — Triangle plots
  - `*_runplot.pdf` — Evidence accumulation (dynesty)
  - `*_traceplot.pdf` — Sampling diagnostics

## Interpretation

| ln(B) | Verdict |
|-------|---------|
| > 5 | Strong evidence for EFC |
| 2.5 to 5 | Moderate evidence for EFC |
| 1 to 2.5 | Weak evidence for EFC |
| -1 to 1 | Inconclusive |
| < -1 | Evidence for ΛCDM |

Scale: Kass & Raftery (1995).

## Compute

| Sampler | Cores | RAM | Wall Time |
|---------|-------|-----|-----------|
| PolyChord | 32 | 32 GB | 48-96h |
| dynesty | 16 | 8 GB | 72-120h |
