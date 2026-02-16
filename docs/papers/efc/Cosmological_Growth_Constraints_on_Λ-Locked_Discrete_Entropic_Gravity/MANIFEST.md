# Cosmological Growth Constraints — Package Manifest

## Package Information

| Field | Value |
|-------|-------|
| Package ID | `cosmological-growth-constraints-lambda-locked` |
| Version | 1.0 |
| License | CC-BY-4.0 |
| Status | Layer B (Stress test / necessary condition) |

## File Structure

```
Cosmological_Growth_Constraints_.../
├── README.md                              # Package overview
├── QUICKSTART.md                          # 5-minute introduction
├── MANIFEST.md                            # This file
├── CITATION.cff                           # Citation metadata (CFF)
├── index.json                             # Machine-readable metadata
├── CosmologicalGrowthConstraints.jsonld    # Schema.org semantic data
├── schema.json                            # JSON Schema for validation
├── citations.bib                          # BibTeX references
├── *.pdf                                  # Original paper
│
├── data/
│   ├── parameters.json                    # Cosmological and model parameters
│   ├── scenario_results.json              # σ₈ results for all three scenarios
│   └── geff_profiles.json                 # G_eff(k)/G profiles per scenario
│
├── src/
│   ├── __init__.py                        # Package init
│   ├── geff_coupling.py                   # Scale-dependent G_eff(k) model
│   ├── growth_equation.py                 # Linear growth ODE
│   └── scenario_runner.py                 # Run and compare all scenarios
│
└── examples/
    ├── run_scenarios.py                   # Reproduce the σ₈ results table
    └── geff_profile.py                    # G_eff(k)/G profile analysis
```

## Key Results Summary

| Model | σ₈(z=0) | γ | σ₈ excess |
|-------|---------|---|-----------|
| ΛCDM | 0.811 | 0.554 | — |
| Graph-AQUAL (Λ-locked) | 0.814 | 0.554 | 0.4% |
| Graph-AQUAL (10 Mpc) | 367 | 0.541 | × 452 |
| Graph-AQUAL (1 Mpc) | 24 098 | 0.536 | × 29 714 |

## Source Code (`src/`)

| File | Exports | Description |
|------|---------|-------------|
| `geff_coupling.py` | `geff_ratio`, `lambda_locked_scale`, `GeffModel` | Lorentzian G_eff(k)/G model |
| `growth_equation.py` | `linear_growth_ode`, `compute_sigma8` | Linear perturbation growth |
| `scenario_runner.py` | `run_scenario`, `run_all_scenarios`, `compare_table` | Scenario comparison |

## Data Files (`data/`)

| File | Content |
|------|---------|
| `parameters.json` | Ω_m, H₀, σ₈(ΛCDM), C, Λ, scenario definitions |
| `scenario_results.json` | σ₈ and γ for all three scenarios + ΛCDM |
| `geff_profiles.json` | G_eff(k)/G sampled at k = 0.001..10 h/Mpc per scenario |

## Dependencies

### Python Requirements
- Python >= 3.8
- numpy (for ODE integration)
- scipy (optional, for `solve_ivp`)

### Related Packages
- `discrete-entropic-gravity-cubic-graph` — Companion operator paper

## Validation Checklist

- [x] Λ-locked scenario: σ₈ within observational bounds
- [x] Sub-Hubble scenarios: catastrophic overgrowth confirmed
- [x] Growth index γ unchanged across scenarios
- [ ] Full Boltzmann integration (CLASS/CAMB)
- [ ] CMB angular power spectrum
- [ ] Nonlinear / N-body verification
