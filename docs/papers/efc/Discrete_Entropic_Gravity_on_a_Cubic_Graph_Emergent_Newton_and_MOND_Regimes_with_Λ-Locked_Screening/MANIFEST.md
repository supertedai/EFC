# Discrete Entropic Gravity on a Cubic Graph — Package Manifest

## Package Information

| Field | Value |
|-------|-------|
| Package ID | `discrete-entropic-gravity-cubic-graph` |
| Version | 1.0 |
| DOI | 10.6084/m9.figshare.31348411 |
| License | CC-BY-4.0 |
| Status | Layer B (Technical construction with numerical tests) |

## File Structure

```
Discrete_Entropic_Gravity_.../
├── README.md                              # Package overview
├── QUICKSTART.md                          # 5-minute introduction
├── MANIFEST.md                            # This file
├── CITATION.cff                           # Citation metadata (CFF)
├── index.json                             # Machine-readable metadata
├── DiscreteEntropicGravity.jsonld          # Schema.org semantic data
├── schema.json                            # JSON Schema for validation
├── citations.bib                          # BibTeX references
├── *.pdf                                  # Original paper
│
├── data/
│   ├── parameters.json                    # Physical and lattice parameters
│   ├── kill_test_results.json             # All five kill-test outcomes
│   └── convergence_table.json             # Prefactor C vs grid size N
│
├── src/
│   ├── __init__.py                        # Package init
│   ├── cubic_graph.py                     # Cubic lattice construction
│   ├── aqual_operator.py                  # AQUAL weights and field equation
│   ├── lambda_screening.py                # Bulk entropic term and Λ-locking
│   ├── kill_tests.py                      # Kill-test evaluation suite
│   └── growth_check.py                    # Cosmological stability ODE
│
└── examples/
    ├── run_kill_tests.py                  # Reproduce all five kill tests
    └── prefactor_convergence.py           # Prefactor C vs N analysis
```

## Key Results Summary

| Quantity | Value | Notes |
|----------|-------|-------|
| Newton slope | −2.00 | Expected: −2.0 |
| MOND slope (a₀=2.0) | −0.99 | Expected: −1.0 |
| MOND slope (a₀=0.5) | −1.01 | Expected: −1.0 |
| Prefactor C (N→∞) | 2.32 | Binning-independent |
| a₀,eff / a₀ | 5.4 | = C² |
| Mass scaling exponent | 0.18 ± 0.03 | MOND expects 0.50 |
| Superposition violation | 13.7% | Smooth (not noise) |
| σ₈ suppression | 0.7% | vs ΛCDM |
| fσ₈(z=0.51) | 0.463 | ΛCDM: 0.473 |

## Source Code (`src/`)

| File | Exports | Description |
|------|---------|-------------|
| `cubic_graph.py` | `CubicGraph`, `build_lattice` | N³ cubic lattice with neighbour connectivity |
| `aqual_operator.py` | `mu_interpolation`, `aqual_weight`, `solve_field` | Discrete AQUAL weights and iterative solver |
| `lambda_screening.py` | `screening_length`, `acceleration_scale`, `bulk_entropic_term` | Λ-locked entropic coupling |
| `kill_tests.py` | `run_kt1` .. `run_kt5`, `run_all_kill_tests` | Five falsification tests |
| `growth_check.py` | `linear_growth_ode`, `compute_fsigma8` | Cosmological stability check |

## Data Files (`data/`)

| File | Content |
|------|---------|
| `parameters.json` | Lattice sizes, a₀ values, Λ, β, tolerances |
| `kill_test_results.json` | Structured results for all five kill tests |
| `convergence_table.json` | C_cubic and C_sphere for N = 21, 31, 41 |

## Dependencies

### Python Requirements
- Python >= 3.8
- numpy (for lattice operations)
- scipy (optional, for ODE integration in growth check)

### Related Packages
- `core-lock` — Mathematical foundation
- `ebe-core-principles` — Methodological framework
- `efc-h0-unification` — Entropic gravity modification

## Validation Checklist

- [x] KT1: Newton and MOND regime slopes recovered
- [x] KT2: Prefactor C converges under refinement
- [x] KT3: Mass scaling measured (structural departure documented)
- [x] KT4: Superposition violation measured (smooth, non-noise)
- [x] KT5: EFE monotonic behaviour confirmed
- [x] Cosmological stability: no runaway growth
- [ ] Calibration against observed rotation curves using a₀,eff
- [ ] Full perturbation-level cosmological integration
- [ ] Continuum limit of the prefactor C
