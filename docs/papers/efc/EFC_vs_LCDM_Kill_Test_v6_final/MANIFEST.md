# EFC vs ΛCDM Kill-Test v6 — Package Manifest

## Package Information

| Field | Value |
|-------|-------|
| Package ID | `efc-vs-lcdm-kill-test-v6` |
| Version | 6.0 (final) |
| DOI | 10.6084/m9.figshare.31964847 |
| License | CC-BY-4.0 |
| Date | 2026-04-08 |
| Status | Layer B→C (numerical kill-test; awaiting full MCMC) |

## File Structure

```
EFC_vs_LCDM_Kill_Test_v6_final/
├── README.md                              # Package overview
├── QUICKSTART.md                          # 5-minute introduction
├── MANIFEST.md                            # This file
├── CITATION.cff                           # Citation metadata (CFF)
├── index.json                             # Machine-readable metadata
├── EFCvsLCDMKillTest.jsonld               # Schema.org semantic data
├── schema.json                            # JSON Schema for validation
├── citations.bib                          # BibTeX references
├── EFC_vs_LCDM_Kill_Test_v6_final.pdf     # Original paper
│
├── data/
│   ├── parameters.json                    # K0, m², sweet spot, ρ*, priors
│   ├── cobaya_runs.json                   # Four cobaya minimize runs
│   ├── sector_decomposition.json          # Per-sector Δχ² breakdown
│   ├── probe_results.json                 # 6 probes with verdicts
│   └── mu_k_table.json                    # μ(k) at K0 = 1.66
│
├── src/
│   ├── __init__.py                        # Package init
│   ├── k_rho_bridge.py                    # K(ρ) bridge, Θ(ρ), μ(k)
│   ├── gravitational_slip.py              # f, η, Σ from δλ counter-term
│   ├── kill_test_suite.py                 # Six-probe kill-test runner
│   └── cobaya_minimize.py                 # Δχ² aggregator for all runs
│
└── examples/
    ├── run_kill_tests.py                  # Reproduce six-probe verdict
    └── slip_window_scan.py                # Reproduce slip sweet spot
```

## Key Results Summary

| Quantity | Value | Notes |
|----------|-------|-------|
| K0 (EFC minimum) | 1.552 | Ref v5: 1.66 (−6%) |
| m² (EFC minimum) | 0.00318 | Ref v5: 0.0035 (−9%) |
| μ₀ | 0.9437 | Sweet-spot window [0.93, 0.96] |
| Σ₀ | 1.069 | Sweet-spot window [1.03, 1.07] |
| η | 1.23 | f = 0.15 sweet spot |
| A_lens (EFC) | 1.143 | GR: 1.000 |
| H₀ (EFC) | 68.79 km/s/Mpc | ΛCDM: 67.89 (ΔH₀ = +0.90) |
| σ₈ (EFC) | 0.797 | ΛCDM: 0.811 (Δσ₈ = −0.014) |
| Ω_m (EFC) | 0.299 | ΛCDM: 0.302 (ΔΩ_m = −0.003) |
| Total Δχ² (all sectors) | **−0.300** | Lensing + BAO favour EFC |
| Cobaya runs | 4 / 4 | All return Δχ² ≤ 0 |
| DDO 154 ΔAIC | +35.4 | Decisive for EFC |
| SPARC multi-component success | 5% → 100% | On 5 tested galaxies |

## Source Code (`src/`)

| File | Exports | Description |
|------|---------|-------------|
| `k_rho_bridge.py` | `KRhoBridge`, `theta_rho`, `R_k` | K(ρ) bridge and μ(k) with density suppression |
| `gravitational_slip.py` | `GravSlip`, `slip_scan` | Slip calibration from δλ counter-term |
| `kill_test_suite.py` | `run_all_probes`, `probe_result` | Six-probe verdict runner |
| `cobaya_minimize.py` | `aggregate_runs`, `delta_chi2` | Δχ² aggregator for cobaya runs |

## Data Files (`data/`)

| File | Content |
|------|---------|
| `parameters.json` | Calibration parameters (K0, m², ρ*, sweet-spot window, datasets) |
| `cobaya_runs.json` | Four cobaya minimize runs with parameters and Δχ² |
| `sector_decomposition.json` | Per-sector χ² breakdown (lowl, EE, lensing, BAO, Pantheon+) |
| `probe_results.json` | Six probes with regime, metric, EFC, GR, verdict |
| `mu_k_table.json` | μ(k) at K0 = 1.66 from super-horizon to Solar System |

## Dependencies

### Python Requirements
- Python ≥ 3.8
- No third-party requirements (pure stdlib for the package code)
- (Optional) numpy + scipy for the full cobaya reproduction pipeline

### Related Packages
- `efc-relativistic-action` — Action, field equations, perturbation theory
- `systematic-localization` — Source of μ₀/Σ₀ MGCAMB run
- `discrete-entropic-gravity-cubic-graph` — Graph-AQUAL operator
- `efc-h0-s8-tensions` — Upstream tensions framework
- `bullet-cluster-efc` — Probe #3

## Validation Checklist

- [x] All four cobaya runs return Δχ² ≤ 0
- [x] K0 converges to sweet spot from BAO + lensing without high-ℓ CMB
- [x] Parameter shifts (H₀ ↑, Ω_m ↓, σ₈ ↓) follow analytic μ < 1 prediction
- [x] μ(k = 5 h/Mpc) = 1 → Solar System GR recovered
- [x] f ∈ [0.12, 0.18] sweet-spot width = 25% (not fine-tuned)
- [x] c_T = c (GW170817 safe)
- [x] σ₈ suppression −1.4% verified in CAMB
- [ ] Full MCMC posterior (≥ 16 GB RAM required; yaml ready)
- [ ] 175-galaxy universality (only 5 refitted)
- [ ] Physical origin of m² from inflation / stability
- [ ] A_lens / Σ₀ degeneracy disentanglement via MGCAMB primary MG run

## Epistemic Status

**Layer B (technical construction)** → **Layer C** (empirically testable via full MCMC).
The paper is explicit: *"What EFC is not: proven correct; decisively better than ΛCDM
by Bayesian standards; tested with a full posterior."*
