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
  launch_nautilus.py           # nautilus pipeline (cobaya-backed, low-RAM, degeneracy-tolerant)
tests/
  test_nautilus_smoke.py       # End-to-end smoke test (mock likelihood, <30s)
  test_config_consistency.py   # Priors/likelihoods/theory parity EFC vs ΛCDM
setup.py                       # Cross-platform entrypoint (dispatches to .sh / .ps1)
setup_environment.sh           # Linux + macOS setup
setup_environment.ps1          # Windows PowerShell setup
```

## Quick Start

### One command, any platform

```bash
cd pipelines/efc/nested_sampling
python setup.py
```

`setup.py` autodetects Linux / macOS / Windows and runs the right
installer. It creates `~/efc_nested_venv`, installs the full cosmology
stack (CAMB, cobaya, dynesty, nautilus) and downloads Planck + BAO + SNe
data (~2 GB) into `~/cobaya_packages`.

### Platform-specific setup (if you prefer)

**Linux (Debian/Ubuntu or Fedora):**
```bash
chmod +x setup_environment.sh
./setup_environment.sh
source ~/efc_nested_venv/bin/activate
export COBAYA_PACKAGES_PATH=~/cobaya_packages
```
Requires: `gfortran`, `libopenmpi-dev` (for PolyChord). The script will
`sudo apt install` these if missing.

**macOS (Intel or Apple Silicon):**
```bash
# Prerequisite: Homebrew (https://brew.sh)
chmod +x setup_environment.sh
./setup_environment.sh
source ~/efc_nested_venv/bin/activate
export COBAYA_PACKAGES_PATH=~/cobaya_packages
```
Requires: `brew install gcc open-mpi pkg-config` (the script does this
for you). Works on both Intel and M1/M2/M3. PolyChord builds natively.

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_environment.ps1
& "$HOME\efc_nested_venv\Scripts\Activate.ps1"
$env:COBAYA_PACKAGES_PATH = "$HOME\cobaya_packages"
```
PolyChord + MPI do not run natively on Windows. Use **dynesty** or
**nautilus** on native Windows, or run the Linux setup inside **WSL2**
if you need PolyChord.

### Run the samplers (same on all platforms, once activated)

```bash
# PolyChord (Linux/macOS/WSL only — needs MPI):
mpirun -n 32 python src/launch_polychord.py          # full MGCAMB
mpirun -n 32 python src/launch_polychord.py --reduced # vanilla CAMB

# dynesty (any platform):
python src/launch_dynesty.py --ncpu 16 --model both
python src/launch_dynesty.py --ncpu 16 --model both --reduced

# nautilus (any platform, lowest RAM, degeneracy-tolerant):
python src/launch_nautilus.py --ncpu 8 --model both
python src/launch_nautilus.py --ncpu 8 --model both --reduced

# Or directly via cobaya:
cobaya-run config/efc_polychord.yaml
cobaya-run config/lcdm_polychord.yaml
```

### Smoke test (no Planck data needed, ~30 seconds)

Verify the pipeline wiring without downloading 2 GB of likelihood data:

```bash
python tests/test_nautilus_smoke.py
```

Expected output: `[PASS] Posterior recovery within 0.3 sigma`.

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

| Sampler | Cores | RAM | Wall Time | Notes |
|---------|-------|-----|-----------|-------|
| PolyChord | 32 | 32 GB | 48-96h | Best, needs MPI |
| dynesty | 16 | 8-16 GB | 72-120h | Pure Python |
| nautilus | 4-8 | 2-4 GB | 24-48h | Lowest RAM, best for degenerate posteriors (Lange & Tessore 2023) |

**Which sampler to pick?** If emcee has reported `DEGENERACY_LIMITED` or
dynesty has stalled on a curved likelihood ridge, use **nautilus** — its
flow-based proposals handle these geometries natively and it requires the
least RAM. Use PolyChord when MPI and ≥32 GB are available; use dynesty
as the middle-ground pure-Python option.
