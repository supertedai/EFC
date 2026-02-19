# Systematic Localization of Late-Time Cosmological Signals in Modified Gravity

CMB Survival, the Lensing Barrier, and a Growth-Sector Sign Constraint.

**DOI:** 10.6084/m9.figshare.31368433

**Date:** February 2026

## Summary

A systematic five-phase localization study determining where late-time cosmological signals can reside within modified-gravity (MG) parameter space, using Energy-Flow Cosmology (EFC) as a concrete case study. The analysis tests EFC against Planck 2018 CMB likelihoods (TTTEEE, lowl, lensing), DESI 2024 BAO, SDSS DR12 BAO, and Pantheon+ supernovae using CLASS v3.3.4, MGCAMB v1.5.2, and cobaya.

**Key finding:** The EFC background sector is observationally empty. The perturbation sector survives Planck within a narrow slip window (μ ∈ [0.93, 0.96], Σ ∈ [1.03, 1.07]), and a relativistic perturbation theory producing gravitational slip (η ≠ 1) is required.

## Five-Phase Results

| Phase | Test | Result | Significance |
|-------|------|--------|-------------|
| 1 | Background α (Planck) | Blind | corr(α, H₀) = 0.975 |
| 1 | Joint α (Planck+BAO+SN) | α → −0.045 | Background gate empty |
| 2 | Pure μ (Σ = 1) | Excluded | Lensing blocks S₈ relief |
| 2 | μ–Σ valley | Δχ² = −0.45 | Viable but degenerate with A_L |
| 3 | A_L diagnostic | cos = 0.93 | Same CMB modes as A_L |
| 4 | fσ₈ (B0) | Δχ² = −5.22 | μ < 1 at > 2σ, breaks A_L |
| 5 | GRAV → (μ, Σ) | Does not close | Wrong sign, no slip, screening |

## Phase 1: Background Gate

Joint-fit Δχ² (EFC α-free vs. ΛCDM, 1 extra DOF):

| Dataset | χ²_ΛCDM | χ²_EFC | α_bf | Δχ² |
|---------|---------|--------|------|-----|
| Planck only | 1010.35 | 1012.23 | +0.035 | +1.88 |
| Planck + SDSS DR12 | 1016.91 | 1015.60 | −0.111 | −1.31 |
| Planck + DESI 2024 | 1025.65 | 1028.63 | −0.045 | +2.98 |
| Planck + DESI + Pantheon+ | 2432.71 | 2430.61 | −0.045 | −2.10 |

No dataset combination exceeds 2σ significance. Background gate is observationally empty.

## Phase 2: Perturbation Sector

### Pure μ scan (Σ = 1 fixed)

| μ | Δσ₈ | Δχ²_TT | Δχ²_lens | Δχ²_full | Verdict |
|---|-----|--------|----------|----------|---------|
| 0.90 | −10.3% | +18.5 | +14.7 | +33.2 | Excluded |
| 0.93 | −7.3% | +11.5 | +7.5 | +19.0 | Excluded |
| 0.95 | −5.3% | +7.6 | +3.9 | +11.5 | Excluded |
| 0.97 | −3.2% | +4.1 | +1.4 | +5.6 | Marginal |
| 0.99 | −1.1% | +1.2 | +0.2 | +1.4 | Viable |

### μ–Σ degeneracy valley (profiled)

| μ | Σ* | Δχ²_full | Δσ₈ | S₈ relief |
|---|-----|----------|-----|-----------|
| 0.92 | 1.060 | +4.56 | −8.4% | 100% |
| 0.93 | 1.050 | +3.45 | −7.4% | 93% |
| 0.94 | 1.050 | +2.49 | −6.4% | 81% |
| 0.95 | 1.040 | +1.61 | −5.3% | 67% |

Sweet spot at (μ = 0.94, Σ = 1.05): Δχ² = −0.45 for 2 extra parameters.

## Phase 3: A_L Degeneracy

| Model | χ²_min | Δχ² | A_L^bf | DOF |
|-------|--------|-----|--------|-----|
| GR reference | 1014.78 | 0 | 1.00 | 0 |
| GR + A_L free | 1010.36 | −4.42 | 1.042 | 1 |
| (μ, Σ) + A_L = 1 | 1014.33 | −0.45 | 1.00 | 2 |
| (μ, Σ) + A_L free | 1016.37 | +1.59 | 0.976 | 3 |

Three diagnostics confirm: the (μ, Σ) valley is the A_L anomaly expressed through physical metric potentials.

## Phase 4: Growth-Sector Sign Constraint (B0)

| Filter | Direction | Δσ₈ | χ² | Δχ² | Verdict |
|--------|-----------|-----|-----|-----|---------|
| ΛCDM | — | — | 66.62 | — | Reference |
| F3 tanh | Weaken | −0.54% | 61.40 | −5.22 | > 2σ impr. |
| F2 gauss | Weaken | −0.25% | 63.62 | −3.00 | Improves |
| F1 raised | Weaken | −0.18% | 64.45 | −2.17 | Improves |
| F0 original | Weaken | −0.00% | 66.61 | −0.01 | Neutral |
| F1 raised | Strengthen | +16.8% | 561.4 | +494.7 | Killed |

Sign constraint: μ < 1 (weakened gravity) at > 2σ, independent of A_L.

## Surviving Signal Specification

- **Sign:** μ < 1 (weakened matter-potential coupling). Locked by fσ₈ independently of CMB.
- **Magnitude:** ~6% effective weakening (μ ≈ 0.94).
- **Lensing:** Σ ≈ 1.05 to compensate CMB lensing penalty. Gravitational slip (η ≠ 1) essential.
- **Scales:** Effect must reach k ≈ 0.05–0.1 h/Mpc.
- **Epoch:** Late-time (z < 1), consistent with dark-energy–dominated era.

## Theory–Observation Gap

Three structural incompatibilities between galactic-scale EFC (Grid-AQUAL) and cosmological constraints:

1. **Wrong sign:** Grid-AQUAL gives μ_GRAV > 1 (MOND strengthens gravity), CMB+fσ₈ require μ < 1
2. **No gravitational slip:** Single potential implies Φ = Ψ (η = 1), CMB requires η ≈ 1.12
3. **Fourier screening:** At k_Λ = 0.0014 h/Mpc, modification is < 0.1% at CMB-relevant scales

## Contents

| File | Description |
|------|-------------|
| `Systematic_Localization_...pdf` | Authoritative PDF (11 pages) |
| `index.json` | Machine-readable metadata, all scan data, phase results |
| `schema.json` | JSON Schema validation |
| `metadata.json` | Package metadata |
| `EFC-CMB-Localization.jsonld` | JSON-LD semantic metadata |
| `citations.bib` | BibTeX references |
| `src/cmb_localization.py` | Reference implementation (μ–Σ valley, B0 filters) |
| `data/localization_results.json` | Full numerical results for all phases |
| `examples/localization_demo.py` | Runnable demo of key results |
| `README.md` | This file |

## Quick Start

```python
from src.cmb_localization import MuSigmaValley, GrowthSignTest, BackgroundGate

# Phase 1: Background gate
gate = BackgroundGate()
print(gate.joint_fit_summary())

# Phase 2: μ–Σ valley
valley = MuSigmaValley()
delta_chi2 = valley.delta_chi2(mu=0.94, sigma_mg=1.05)
print(f"Δχ² at sweet spot: {delta_chi2:.2f}")

# Phase 4: Growth sign constraint
b0 = GrowthSignTest()
print(b0.sign_constraint_summary())
```

## Citation

```bibtex
@misc{magnusson2026localization,
  author = {Magnusson, Morten},
  title  = {Systematic Localization of Late-Time Cosmological Signals in Modified Gravity},
  year   = {2026},
  doi    = {10.6084/m9.figshare.31368433}
}
```

Version: 1.0
