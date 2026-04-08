# KT3b Cross-Regime Measurement Failure — AI-friendly package

**Report:** EFC-VAL-2026-005 (methodological diagnosis)
**DOI:** [10.6084/m9.figshare.31963821](https://doi.org/10.6084/m9.figshare.31963821)
**Author:** Morten Magnusson (ORCID 0009-0002-4860-5095), Independent Researcher, Sola, Norway
**Date:** 2026-04 · v1.0 · **License:** CC-BY-4.0
**Ledger version at publication:** v3.12

Structural diagnosis of the KT3b environmental test null result. Argues
that the observed monotonic signal collapse across four runs of increasing
methodological rigour is not a physical null but a **cross-regime
measurement failure**: the test architecture violates the Regime-Consistent
Measurement Principle (RCMP, DOI 31222900).

## TL;DR

| Run | Env. proxy | N | Slope | Diagnosis |
|---|---|---:|---:|---|
| 1 | log(L/D²) | ~60 | −0.21 | Mass artefact |
| 2 | Karachentsev Θ₁ | 17 | +0.01 | N too small |
| 3 | Tully N_mem (raw) | 70 | −0.07 | Mass bias |
| 4 | Tully (mass-matched pairs) | 23 | ≈ 0 | **Null** |

Pattern: as confounders are removed, the signal vanishes. Standard
interpretation is "effect too small for SPARC". This paper argues for a
deeper structural diagnosis.

## The regime mismatch

The KT3b measurement chain spans **three different EFC regimes**:

| Component | Regime | Why |
|---|---|---|
| D_eff(ρ) (theory) | L2 | Non-linear galactic dynamics; grid-mode activation at g ≲ a₀ |
| ρ_env (driver) | L1 | Large-scale structure; Mpc-scale density field |
| ℛ at a₀ (observable) | **L1/L2 boundary** | Transition point; maximally unstable |
| Rotation curve (data) | L2 | kpc-scale circular velocities |
| Υ⋆ (mass model) | L1 assumption | Stellar population synthesis assumes universal IMF |

The test attempts to measure an L2 effect using an L1 driver, observed
**at the L1/L2 boundary**. This is precisely where:

- stiffness response R(k) transitions from R ≫ 1 (L1) to R ≪ 1 (L2)
- entropy production Γ(ρ) crosses its inflection point
- effective Poisson coupling μ(k) swings from < 1 to > 1
- observational scatter in the RAR is maximal

Measuring at a₀ is analogous to measuring a phase transition **at** the
critical temperature: fluctuations diverge and signal-to-noise collapses.

## Three RCMP violations

| ID | Violation | Why |
|---|---|---|
| V1 | Driver–response mismatch | ρ_env (L1) drives D_eff (L2) through an *underived* α operator |
| V2 | Boundary observation | ℛ at a₀ sits on the L1/L2 boundary where both regimes contribute and neither dominates |
| V3 | Implicit regime mixing in mass model | Υ⋆ = 0.5 M☉/L☉ assumes L1-regime stellar physics applied to L2-regime gravitational dynamics |

Any one of these is sufficient to degrade the measurement. Together,
they explain the **systematic collapse of the signal across all four runs**.

## Three valid test architectures

| Architecture | Regime | Observable | Free params | Data now? | Discriminates EFC/MOND? |
|---|---|---|---:|---|---|
| **A** (pure L2) | L2 | RAR slope at 10⁻² ≲ g_bar/a₀ ≲ 10⁻¹ | 0 | Yes (SPARC) | Yes (shape) |
| **B** (pure L1) | L1 | fσ₈(z) from RSD or void–cluster growth | 1 (α_L1) | Partial (fσ₈) | Yes (growth) |
| **C** (derived L1→L2) | both | Same as KT3b but with *derived* α(k, z) | 0 | No | Yes (amplitude) |

**Architecture A is the recommended next step**: uses existing SPARC data,
zero free parameters, stays entirely within the L2 regime.

## Files

- `KT3b_CrossRegime_Measurement_Failure_DOI.pdf` — paper
- `index.json`, `metadata.json`, `schema.json`, `*.jsonld` — machine-readable metadata
- `data/kt3b_run_history.json` — the four-run signal collapse table
- `data/test_architectures.json` — comparison of the three valid architectures
- `src/rcmp_check.py` — RCMP compliance checker (evaluates test architectures against the three violation classes)
- `examples/check_kt3b_and_alternatives.py` — runs the RCMP check on KT3b + A/B/C
- `citations.bib` — references

## Reproduce the RCMP diagnosis

```bash
python examples/check_kt3b_and_alternatives.py
```

Expected output: KT3b flagged with V1+V2+V3; architectures A, B, C all pass.

## Related EFC artifacts

- Scale-dependent gravitational response (R(k), Γ(ρ)): [10.6084/m9.figshare.31941543](https://doi.org/10.6084/m9.figshare.31941543)
- Regime-Consistent Measurement Principle (RCMP): [10.6084/m9.figshare.31222900](https://doi.org/10.6084/m9.figshare.31222900)
- Multi-epoch fσ₈ growth test (Architecture B candidate): [10.6084/m9.figshare.31955871](https://doi.org/10.6084/m9.figshare.31955871)

## Language discipline

KT3b is a **null result with a methodological diagnosis**. This package
follows EFC's standing language discipline: the diagnosis is stated as a
structural constraint on cross-regime tests, not as a "confirmation" or
"validation" of EFC. The diagnosis is in fact *stronger* than the null
result itself, because it applies to MOND's External Field Effect,
Verlinde's emergent gravity, and any framework in which the transition
scale a₀ marks a regime boundary.
