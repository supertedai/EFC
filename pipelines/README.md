# EFC Computational Pipelines

Computational validation pipelines for Energy-Flow Cosmology (EFC). This directory contains the numerical solvers, test suites, and analysis tools that translate EFC theoretical predictions into quantitative, falsifiable results. The three pipeline systems are the Native v2 Graph solver for galactic-scale AQUAL/MOND predictions, the HCP Bridge B1 pipeline for neural connectome validation, and the Euclid DR1 pipeline for Stage-IV cosmological survey pre-registration.

**Author:** Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)), Symbiose Research, Sandnes, Norway
**License:** CC-BY-4.0

## Directory Structure

```
pipelines/
└── efc/
    ├── hcp_bridge_b1/              # Human Connectome Project neural bridge
    │   ├── README.md               # Detailed HCP pipeline documentation
    │   ├── run_hcp_pipeline.py     # Main pipeline orchestrator
    │   ├── run_revised_b1.py       # Revised Bridge B1* implementation
    │   ├── run_feature_test.py     # Feature extraction tests
    │   ├── run_multiscale_test.py  # Multi-scale entropy analysis
    │   ├── run_real_hcp_test.py    # Real HCP data validation
    │   ├── run_sensitivity.py      # Sensitivity analysis
    │   ├── literature_connectome.py # Literature-based connectome construction
    │   └── .gitignore              # Ignores large data files
    │
    ├── native_v2_graph/            # Graph-based AQUAL solver
    │   ├── run_efc_graph.py        # Main entry point
    │   ├── configs/
    │   │   ├── base.yaml           # Default simulation parameters
    │   │   └── sweeps.yaml         # Parameter sweep definitions
    │   ├── kernel/                 # Core computational kernel
    │   │   ├── __init__.py         # Package init (documents primitives)
    │   │   ├── aqual.py            # AQUAL equation solver
    │   │   ├── energy.py           # Energy field computations
    │   │   ├── fields.py           # Field initialization and management
    │   │   ├── graph.py            # Graph construction (V, E)
    │   │   ├── observables.py      # Observable extraction (profiles, slopes)
    │   │   ├── operators.py        # Discrete differential operators
    │   │   └── solver.py           # Iterative AQUAL solver
    │   ├── tests/                  # Key-test suite (KT1-KT5)
    │   │   ├── kt1_limits.py       # Newton/MOND limit recovery
    │   │   ├── kt2_C_convergence.py # C-parameter convergence
    │   │   ├── kt3_mass_scaling.py  # Mass scaling relations
    │   │   ├── kt4_superposition.py # Field superposition tests
    │   │   └── kt5_EFE.py          # External Field Effect
    │   └── outputs/
    │       └── runs/               # Timestamped run results (JSON)
    │
    └── euclid_dr1/                 # Euclid DR1 pre-registration pipeline
        ├── README.md               # Pipeline overview + critical path
        ├── RUN_CHECKLIST.sh        # 7-step execution checklist
        ├── config/
        │   ├── efc_cobaya.yaml     # Cobaya + PolyChord sampler config
        │   └── efc_hiclass.ini     # hi_class input file
        ├── data/
        │   └── efc_hiclass_alphas.dat  # Tabulated Horndeski alpha-functions
        ├── docs/
        │   └── RCMP_COMPLIANCE_MATRIX.md  # RCMP compliance per kill criterion
        ├── src/
        │   ├── __init__.py
        │   ├── efc_mg_functions.py     # Canonical mu/eta/Sigma (verified)
        │   ├── efc_hiclass_bridge.py   # EFC -> Horndeski alpha mapping
        │   └── euclid_mock_likelihood.py  # Simplified Euclid mock
        └── tests/
            └── test_sanity.py      # 6 automated sanity checks (A-F)
```

## Pipeline 1: Native v2 Graph Solver

The graph-based AQUAL solver discretizes the modified Poisson equation on a 3D lattice and tests whether EFC-predicted gravitational dynamics recover known Newtonian and MOND limits.

**Kernel primitives:** Graph (V, E), entropy field S_i, density rho_i, potential Phi_i, bulk entropy S_V.

**Emergent predictions:** Poisson limit recovery, area-law entropy scaling, a0 proportional to sqrt(Lambda), MOND-limit behavior.

### Running the Graph Solver

```bash
cd pipelines/efc/native_v2_graph
python run_efc_graph.py
```

Configuration is read from `configs/base.yaml`. Key parameters include:

- `domain.N` -- Grid resolution (default: 31)
- `physics.a0` -- MOND acceleration scale (default: 2.0)
- `physics.mu_func` -- Interpolating function (`standard` or `simple`)
- `solver.tol` -- Convergence tolerance (default: 1e-4)

### Running Tests (KT1-KT5)

The five key tests validate distinct physical predictions:

| Test | What It Validates | Pass Criteria |
|------|-------------------|---------------|
| KT1 | Newton/MOND limit recovery | Slope approaches -2 (Newton) and -1 (MOND) |
| KT2 | C-parameter convergence | Convergence with increasing resolution |
| KT3 | Mass scaling relations | Correct M-dependence of rotation curves |
| KT4 | Field superposition | Linearity in the Newtonian regime |
| KT5 | External Field Effect (EFE) | MOND-regime sensitivity to external fields |

```bash
cd pipelines/efc/native_v2_graph
python -m tests.kt1_limits
python -m tests.kt2_C_convergence
python -m tests.kt3_mass_scaling
python -m tests.kt4_superposition
python -m tests.kt5_EFE
```

Each test produces a JSON output file in `outputs/runs/<timestamp>/` containing numerical results, pass/fail status, and diagnostic data.

## Pipeline 2: HCP Bridge B1*

Tests the cross-domain prediction that the cosmological parameter C = 4.4 (derived from SPARC galaxy rotation curves) also predicts neural entropy distributions in Human Connectome Project data, via the Bridge B1* formula:

```
eta = C / (1 + lambda_2 * tau_c)
```

where lambda_2 is the Fiedler eigenvalue of the structural connectome and tau_c is the entropy redistribution timescale.

### Running the HCP Pipeline

```bash
cd pipelines/efc/hcp_bridge_b1

# With real HCP data:
python run_hcp_pipeline.py --hcp-dir /path/to/HCP --n-subjects 50

# Sensitivity analysis:
python run_sensitivity.py

# Multi-scale entropy test:
python run_multiscale_test.py
```

### Pipeline Steps

1. Build structural connectome W (360 x 360) from tractography
2. Compute Fiedler eigenvalue lambda_2 from the normalized Laplacian
3. Extract BOLD time series per parcel (MMP1.0 atlas)
4. Compute multi-scale entropy (MSE) at scales 4-6
5. Classify hub (top 10%) vs peripheral (bottom 30%) parcels
6. Compute kappa = mean(S_hub) / mean(S_periph)
7. Run model comparison: EFC vs power-law vs linear (AIC/BIC)

### Decision Criteria

| Outcome | Interpretation |
|---------|---------------|
| EFC wins BIC, tau_c in 3-4 range, r > 0.4 | Strong support: C=4.4 from galaxies predicts brains |
| EFC approximately equals Linear | Structure correct but not uniquely EFC |
| Power-law wins | Generic network scaling; B1* fails |
| r < 0.2 | Hypothesis falsified |

### Expected Outputs

```
output/
├── lambda2.npy       # Fiedler eigenvalue per subject
├── eta.npy           # Kappa (entropy ratio) per subject
├── subjects.json     # Subject metadata
├── per_subject/      # Individual subject results
└── results.json      # Model comparison (AIC, BIC, r-values)
```

## Pipeline 3: Euclid DR1 Pre-Registration

Tests EFC modified gravity predictions (mu, eta, Sigma) against Euclid Stage-IV survey data via the hi_class Boltzmann solver. The primary falsification channel is E_G (gravitational slip statistic), ranked first by RCMP compliance.

**Core modules:** Canonical mu(k,z)/eta(k,z)/Sigma(k,z) functions, EFC-to-Horndeski alpha mapping, Euclid mock likelihood, and 6 automated sanity checks.

**Kill criteria covered:** KC1 (P(k)), KC3 (S8), KC4 (E_G, primary), KC5 (BAO). KC2 (fsigma8) is already covered by Kill-Test v6.

### Running the Pipeline

```bash
cd pipelines/efc/euclid_dr1

# Run sanity checks (must pass before anything else)
PYTHONPATH=. python tests/test_sanity.py

# Generate hi_class config
PYTHONPATH=. python src/efc_hiclass_bridge.py --write-ini --write-yaml

# Full checklist
bash RUN_CHECKLIST.sh
```

### Sanity Checks (A-F)

| Check | What It Validates | Pass Criteria |
|-------|-------------------|---------------|
| A | Early-time GR recovery | mu -> 1/F, eta -> 1 for z > 50 |
| B | Stability (no-ghost) | Q_S > 0 for all a |
| C | k-unit consistency | k[h/Mpc] = k[1/Mpc] / h end-to-end |
| D | Finiteness + positivity | All functions finite, positive |
| E | Smoothness | Gradients << 100 (Boltzmann-safe) |
| F | Neutrino discriminant | EFC slip is scale-localized |

See `docs/RCMP_COMPLIANCE_MATRIX.md` for the full regime-consistency analysis.

## Dependencies

- Python 3.10+
- NumPy, SciPy
- PyYAML (for config parsing)
- Matplotlib (optional, for figure generation)
- NiBabel, dipy (for HCP pipeline neuroimaging I/O)
- hi_class (for Euclid pipeline Boltzmann integration)
- cobaya, PolyChord (for Euclid pipeline MCMC sampling)

## Related Directories

- `/scripts/` -- Analysis and visualization scripts that operate on pipeline outputs
- `/meta/meta-process/validation-plan/` -- Validation planning documents
- `/jsonld/` -- Metadata for published pipeline results
