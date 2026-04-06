# EFC Analysis and Visualization Scripts

Six Python scripts for analyzing, validating, and visualizing Energy-Flow Cosmology (EFC) predictions. These scripts operate on outputs from the EFC computational pipelines and provide statistical tests, model comparisons, and publication-ready plots.

**Author:** Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)), Symbiose Research, Sandnes, Norway
**License:** CC-BY-4.0

## Scripts Overview

| Script | Purpose | Key Output |
|--------|---------|------------|
| `efc_c_kappa_analysis.py` | Kappa entropy score and EFC-C predictions | JSON with kappa, alpha_AP, statistical tests |
| `efc_model_comparison.py` | EFC vs power-law vs linear model comparison | AIC/BIC scores, winner determination |
| `generate_efc_vs_lcdm_plot.py` | EFC vs Lambda-CDM Hubble parameter plot | PNG comparison figure |
| `p4_monte_carlo.py` | Monte Carlo robustness pre-screen for B1* | JSON with correlation distributions |
| `run_efc_baseline.py` | Baseline EFC run for development/debugging | Rotation curve JSON, run metadata |
| `validate_efc.py` | Validation against mock JWST/DESI/SPARC data | Comparison plots and residual analysis |

## Script Details

### 1. efc_c_kappa_analysis.py

Computes the centrifugal entropy score kappa and tests predictions Q1-Q3 from EFC-C v2.0. Provides five analysis stages: connectome lambda_2 computation, MSE-based entropy proxy estimation, kappa computation (hub/periphery ratio), anterior-posterior asymmetry (alpha_AP), and statistical tests against EFC-C predictions.

```bash
# Validation mode with synthetic data:
python scripts/efc_c_kappa_analysis.py --synthetic

# With real HCP data:
python scripts/efc_c_kappa_analysis.py --connectome path/to/W.npy --fmri path/to/ts.npy
```

**Dependencies:** numpy, scipy (eigh, pearsonr, spearmanr, ttest_ind)

### 2. efc_model_comparison.py

The decisive test: does the EFC Bridge B1* formula explain neural entropy-connectivity data better than generic alternatives? Three models compete on identical data:

- **EFC:** eta = C / (1 + lambda_2 * tau_c) with C=4.4 fixed from SPARC
- **Power-law:** eta = A * (1/lambda_2)^alpha + B (3 free parameters)
- **Linear:** eta = a + b * (1/lambda_2) (2 free parameters)

Two EFC variants are tested: tau_c fixed at 3.5s (zero free parameters, strongest claim) and tau_c fitted (one free parameter, best EFC fit). Winner is determined by AIC/BIC to penalize overfitting.

```bash
python scripts/efc_model_comparison.py \
    --data output/lambda2.npy output/eta.npy output/results.json
```

**Dependencies:** numpy, scipy (curve_fit, pearsonr)

### 3. generate_efc_vs_lcdm_plot.py

Generates a comparison plot of the Hubble parameter H as a function of entropy (EFC) versus redshift (Lambda-CDM). The EFC model uses a smooth tanh function H(S) = 70 * (1 + 0.25 * tanh(3*(S - 0.5))), while the Lambda-CDM baseline uses standard flat cosmology with Omega_m=0.3 and Omega_Lambda=0.7.

```bash
python scripts/generate_efc_vs_lcdm_plot.py
# Output: output/efc_vs_lcdm.png
```

**Dependencies:** numpy, matplotlib

### 4. p4_monte_carlo.py

Monte Carlo pre-screen testing the robustness of the Bridge B1* prediction. Answers the key question: is the correlation r(eta, 1/lambda_2) robust against realistic biological noise, or is it trivially built-in? Uses parameters from literature and SPARC galaxy data (C = 4.4 +/- 0.6, lambda_2 in 0.3-0.8 range, tau_c in 2-5s range).

```bash
python scripts/p4_monte_carlo.py
```

**Dependencies:** numpy, scipy (pearsonr, spearmanr)

### 5. run_efc_baseline.py

Baseline EFC run for development and debugging. Reads parameters from `output/parameters.json`, runs the core EFC model, and produces rotation curve predictions with git commit metadata for reproducibility. Text is in Norwegian as this is a development utility.

```bash
python scripts/run_efc_baseline.py
# Reads:   output/parameters.json
# Writes:  output/run_metadata.json
#          output/validation/rotation_curve.json
```

**Dependencies:** numpy, src.efc_core (EFCModel, load_parameters)

### 6. validate_efc.py

Validation of the EFC model against mock observational data from three datasets: JWST (early-galaxy luminosity-density trends), DESI (baryon acoustic oscillation measurements), and SPARC (galaxy rotation curves). Compares EFC predictions against a Lambda-CDM baseline using generated mock data.

```bash
# Validate against JWST mock data:
python scripts/validate_efc.py --dataset jwst

# Other datasets:
python scripts/validate_efc.py --dataset desi
python scripts/validate_efc.py --dataset sparc
```

**Dependencies:** numpy, pandas, matplotlib, src.efc.core.efc_core (EFCModel, EFCParameters)

## Quick Start

```bash
# Install common dependencies
pip install numpy scipy matplotlib pandas

# Run the Monte Carlo robustness check (no external data needed)
python scripts/p4_monte_carlo.py

# Generate the EFC vs Lambda-CDM comparison plot
python scripts/generate_efc_vs_lcdm_plot.py

# Run kappa analysis with synthetic data
python scripts/efc_c_kappa_analysis.py --synthetic
```

## Dependencies Summary

| Package | Required By | Purpose |
|---------|-------------|---------|
| numpy | All scripts | Array operations and linear algebra |
| scipy | 1, 2, 4 | Eigenvalue decomposition, optimization, statistics |
| matplotlib | 3, 6 | Plot generation |
| pandas | 6 | Data frame operations |

Note: Scripts 5 and 6 depend on the EFC core library (`src/efc_core.py` or `src/efc/core/efc_core.py`) located in the repository root. Ensure the repository root is on your Python path or run scripts from the repository root directory.

## Output Formats

All scripts produce JSON output for machine readability. Visualization scripts additionally produce PNG figures in the `output/` directory. JSON outputs include metadata such as parameter values, statistical test results, and pass/fail determinations to support automated validation pipelines.

## Related Directories

- `/pipelines/efc/` -- Computational pipelines that generate inputs for these scripts
- `/pipelines/efc/hcp_bridge_b1/` -- HCP pipeline whose outputs feed into model comparison
- `/src/` -- Core EFC model library used by baseline and validation scripts
