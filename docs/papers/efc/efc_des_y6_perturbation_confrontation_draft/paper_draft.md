# EFC Perturbation Sector Confrontation with DES Y6 3×2pt and Cosmic Shear

**Morten Magnusson** — ORCID 0009-0002-4860-5095
Energy-Flow Cosmology Initiative, Bergen, Norway
Draft: 2026-04-17. DOI: pending.

---

## Abstract

We confront the Energy-Flow Cosmology (EFC) perturbation-sector engine — consisting of `efc_perturbation_engine.py`, `horndeski_consistency.py`, `lensing.py`, and the σ_eff crossover diagram generated 2026-04-17 — with the DES Y6 3×2pt (arXiv:2601.14559; S₈ = 0.789 ± 0.012, Ωₘ = 0.333) and DES Y6 cosmic-shear (arXiv:2602.10065; S₈ = 0.798 NLA) covariances. The parametrisation (B₀, M₀) = (0.02, 0.06) is frozen from the sealed Euclid-DR1 pre-registration (DOI 10.6084/m9.figshare.31990053). The Bellini–Sawicki α-mapping (DOI 10.6084/m9.figshare.32011407, CLOSED gap) identifies α_T = 0, α_M ∝ S(a), α_B ∝ dS/d ln a. Prior to confrontation we resolve a known χ²_red = 10.39 excursion on KiDS-1000 (logged as a learning insight 2026-04-17T19:23:45 by the EFC inference pipeline).

## 1. Engine Architecture

The perturbation-sector package contains:

| File | Purpose | Size (B) |
|---|---|---|
| `efc_perturbation_engine.py` | Core scalar-tensor perturbation solver | 17 571 |
| `horndeski_consistency.py` | Bellini–Sawicki α-consistency check | 9 932 |
| `lensing.py` | μ, Σ, η mapping onto lensing and clustering | 14 658 |
| `valley_robustness_test.py` | Posterior-valley robustness | 6 033 |
| `sigma_eff_crossover.pdf` | σ_eff(z) crossover plot | 29 260 |

The engine is provider-neutral (no hard-coded Planck/ACT dependency) and consumes any 3×2pt covariance in the standard CosmoSIS format.

## 2. Frozen Parametrisation

Inherited from DOI 31990053 (sealed Euclid-DR1 pre-registration):
- B₀ = 0.02
- M₀ = 0.06

Inherited from DOI 32011407 (Bellini–Sawicki α-mapping):
- α_T = 0 (gravitational-wave-speed-locked)
- α_M = f(S(a))
- α_B = g(dS/d ln a)

These are the only parameters; no new free parameters are introduced in the DES Y6 confrontation.

## 3. Known Pre-condition

The Symbiose inference pipeline logged a learning insight on 2026-04-17T19:23:45 (knowledge_id `efc_theory_7f036cc1`):
- Module: `inference_shear_kids1000`
- χ²_red = 10.39 (fails engine quality gate χ²_red < 5.0)
- Confidence: 0.7
- Recommendation: "1 EFC modules need attention"

This must be resolved before the DES Y6 confrontation, otherwise any disagreement between engine and DES Y6 could be attributed to the same bug rather than a genuine tension. Two resolution paths are open:
1. **Bug path:** numerical issue in `efc_perturbation_engine.py` at the KiDS-1000 redshift distribution
2. **Model path:** EFC genuinely disagrees with KiDS-1000 at the σ_8 level

If the bug path is correct, the engine is recalibrated and DES Y6 proceeds. If the model path is correct, this paper reports a first model-level tension that must be disclosed.

## 4. Confrontation Procedure

1. Freeze (B₀, M₀) = (0.02, 0.06)
2. Load DES Y6 3×2pt covariance (public release)
3. Evaluate μ(z), Σ(z), η(z) on DES Y6 z-bins (0.2 < z < 1.2)
4. Compute engine χ²_red on DES Y6 covariance
5. Cross-check with DES Y6 cosmic shear (NLA) on the same covariance
6. Report posterior on Ωₘ, σ₈, S₈

## 5. Pre-registered Kill Criteria

| # | Threshold | Outcome |
|---|---|---|
| K1 | χ²_red > 5.0 on DES Y6 after KiDS-1000 bug resolution | Engine not fit for publication |
| K2 | μ(z=0.5) ≥ 1 on DES Y6 at 3σ | Sealed prediction P1 falsified; scalar-tensor ansatz abandoned |
| K3 | Σ(z=0.5) < 1 on DES Y6 cosmic shear at 3σ | Sealed P2 falsified |
| K4 | |η(z=0.5) − 1| > 0.3 at 3σ | Sealed P3 falsified |
| K5 | S₈(EFC) differs from DES Y6 by > 3σ | First model-level tension |

## 6. Relation to KiDS-Legacy

KiDS-Legacy (arXiv:2503.19441, arXiv:2503.19442) reports S₈ = 0.81 ± 0.02, within 0.73σ of Planck. This is the external baseline against which DES Y6 vs EFC must be cross-checked. If EFC-μ < 1 predicts S₈_eff < 0.836 (Planck+ACT+SPT; arXiv:2602.12238), DES Y6 at 0.789 and KiDS-Legacy at 0.81 both fall in the EFC-preferred window.

## 7. Outlook and DR1 Arbitration

Euclid DR1 (ESA 2026-10-21) arbitrates the DES Y6 vs KiDS-Legacy disagreement on an independent covariance. The present paper seals its predictions before DR1 and stages them for DR1 confrontation in the successor paper.

## 8. Publication Pre-conditions

This draft becomes publication-ready when:
1. KiDS-1000 χ²_red excursion is resolved (bug fix or model disclosure)
2. DES Y6 public covariance is loaded in the engine
3. μ, Σ, η z-profiles and χ²_red on DES Y6 are populated

## Acknowledgements

Uses DOI-anchored sealed predictions (31990053) and closed-gap resolutions (32011407) only.
