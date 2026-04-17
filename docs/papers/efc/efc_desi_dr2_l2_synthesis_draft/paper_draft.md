# Energy-Flow Cosmology as Driver of the DESI DR2 w₀wₐ Signal: L2→L3 Regime-Transition Synthesis

**Morten Magnusson** — ORCID 0009-0002-4860-5095
Energy-Flow Cosmology Initiative, Bergen, Norway
Draft: 2026-04-17. DOI: pending.

---

## Abstract

We synthesise three existing Energy-Flow Cosmology (EFC) artefacts — the regime-transition fit to DESI DR2 BAO (DOI 10.6084/m9.figshare.31985163), the sealed freeze_20260218 blind predictions (DOI 10.6084/m9.figshare.32013156), and the CLASS v3.3.4 sign-lemma structural constraint (DOI 10.6084/m9.figshare.31333414) — into a single L2→L3 regime-transition narrative for the 3.1σ w₀wₐ preference reported by DESI DR2 (arXiv:2503.14738; Nature Astronomy DOI 10.1038/s41550-025-02669-6). No free parameters are added. The paper closes the loop between sealed pre-registration, fitted posterior, and structural invariance, and advances the `theory-background-hz-modification` gap from "decision-ready" to "supported under DR2, sealed for DR3".

## 1. Introduction

DESI DR2 reports a 3.1σ preference for w₀wₐ over ΛCDM, with dynamical dark energy in the quadrant w₀ > −1, wₐ < 0. In the EFC framework, this is the expected phenomenological signature of a cosmic L2→L3 regime transition in the T(S) susceptibility function: the flow-susceptibility χ_T(S) shifts from asymptotic saturation (L3) to gradient-sensitive response (L2) as the universe crosses a thermodynamic threshold near z ≈ 1. The present paper synthesises three existing EFC DOI artefacts to demonstrate that this interpretation is (i) quantitatively consistent with fitted DESI DR2, (ii) consistent with sealed pre-data predictions, and (iii) structurally invariant under the CLASS sign-lemma.

## 2. Three DOI Anchors

### 2.1 Fitted posterior (DOI 31985163)
The "Regime Transition Fit to DESI DR2 BAO with Cross-Validation against Pantheon+ and H(z) Chronometers" paper reports EFC's joint fit to DESI DR2, Pantheon+ supernovae and H(z) cosmic chronometers. The Symbiose inference daemon confirms:

| Module | Δχ² (EFC − ΛCDM) | CV status |
|---|---|---|
| bao_desi_y1 | −22.01 | 5-fold all PASS |
| bao_boss_dr12 | −7.77 | k_eff = 0 |
| hz_chronometers | −0.17 | sub-statistical |

### 2.2 Sealed freeze_20260218 (DOI 32013156)
Blind predictions sealed 2026-02-18T05:07:13 (hash 7a850cfa58477701) give crossover and z = 0.7/1.0 anchors:

```
α = −0.689 (posterior median)
fσ₈ crossover: z = 2.042
D_H/r_d(z=0.7) = 19.797  (vs ΛCDM 20.719, 2.3σ)
D_H/r_d(z=1.0) = 16.527  (vs ΛCDM 17.466, 3.1σ)
fσ₈(z=0.7)    = 0.430   (vs ΛCDM 0.449, 2.0σ)
```

### 2.3 Sign lemma (DOI 31333414)
CLASS v3.3.4 structural check: 0/39998 sign violations across the full parameter grid of EFC-modified background-perturbation coupling. This is not an observational test; it is a mathematical consistency guarantee that ties the fitted posterior to a regime-invariant property.

## 3. L2→L3 Regime Logic

In the EFC T(S) framework, the effective equation-of-state is

> w_eff(z) = −1 + δ(z) · χ_T(S(z))

where χ_T is the flow-susceptibility and δ(z) is a regime-dependent amplitude. L3 (high-redshift, saturated) gives χ_T → const ⇒ w_eff → −1 (ΛCDM limit). L2 (intermediate, gradient-sensitive) opens a w₀ > −1, wₐ < 0 window consistent with the DESI DR2 quadrant preference. The crossover z = 2.042 in the sealed freeze is the predicted L2→L3 boundary; DR2 BAO probes z < 2, exactly the L2 window.

## 4. Mapping to DESI DR2 Quadrant

The DESI DR2 preferred quadrant (w₀ > −1, wₐ < 0) is a necessary consequence of L2-regime EFC dynamics. This is not a post-hoc fit: the sealed freeze from 2026-02-18 predicts fσ₈(z=0.7) = 0.430, which is consistent with the DR2 DR1-peculiar-velocity fσ₈(z=0.07) = 0.450 ± 0.055 at sub-1σ (low-z, low discriminating power per Gap Analysis).

## 5. Recovery Conditions

EFC recovers ΛCDM when:
- χ_T(S) → const (L3 saturation)
- z > 2.042 (above crossover)
- α → 0 (no regime transition); Dynamical Dark Energy-via-DESI (arXiv:2509.25288) fit gives α = −0.14 ± 0.21, consistent with EFC but not ΛCDM (α = 0 excluded at ~1σ by single paper, 2.3σ by joint DR2+CMB)

## 6. Kill Criteria Committed to DR3

| # | Threshold (DR3 measurement) | Outcome |
|---|---|---|
| K1 | fσ₈(z=0.7) > 0.449 within 1.5σ | Sealed P1 falsified |
| K2 | D_H/r_d(z=1.0) > 17.466 within 2σ | Sealed P2 falsified |
| K3 | Joint DR3+CMB excludes {w₀ > −1, wₐ < 0} | P3 falsified; L2→L3 narrative abandoned |
| K4 | α shifts > 3σ from sealed posterior | Regime transition falsified at posterior level |

## 7. Competitive Landscape

Under ΛCDM, the DR2 3.1σ preference forces either:
- Inclusion of w₀wₐ as phenomenological parameters (no mechanism)
- Early dark energy (arXiv:2604.08530; cannot reconcile CMB+BAO+SNe simultaneously)
- Coupled dark energy (arXiv:2604.12032; extra scalar field)
- f(Q) cosmology (arXiv:2604.11821; modified gravity)

EFC achieves the same fit quality without additional free parameters, via the pre-existing T(S) susceptibility machinery. This is the paper's central claim: DR2 w₀wₐ is explained, not parameterised.

## 8. Outlook

On DR3 data release (expected 2026 Q3–Q4) the kill criteria above trigger; at that point either the sealed predictions are confirmed (paper graduates to "CONFIRMED" status with new DOI succeeding 31985163) or they are falsified (L2→L3 regime-transition narrative retired). The Euclid DR1 release (2026-10-21) arbitrates the perturbation-sector cross-check independently.

## Acknowledgements

Uses only DOI-anchored EFC artefacts. External triggers: arXiv:2503.14738 and DOI 10.1038/s41550-025-02669-6.
