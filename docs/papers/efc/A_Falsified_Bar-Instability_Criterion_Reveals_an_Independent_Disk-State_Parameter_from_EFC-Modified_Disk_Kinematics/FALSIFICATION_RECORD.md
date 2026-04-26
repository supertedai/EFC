# EFC-BIC v0.1 (shear proxy) — Falsification Record

**Date:** 2026-04-25
**Test:** Bar/no-bar classification on N=43 cleanly-labeled SPARC galaxies (15 bar SB + 28 no_bar SA, after dropping 31 SAB mixed + 14 not_disk + 79 unknown labels via SIMBAD).
**Model under test:** `efc_bic_pipeline_v0.1` with `proxy_mode='shear'`, σ_R = √(πGΣR_d) Jeans, ζ ∈ [1.0, 3.0].
**Outcome:** **FALSIFIED** as a bar predictor.

## Headline metrics (best ζ in physical regime)

| ζ | accuracy | precision | recall | F1 | AUC | unphysical (κ²_eff<0) |
|---|---|---|---|---|---|---|
| 1.0 | 0.641 | 0.000 | 0.000 | nan | **0.217** | 0/43 |
| 1.5 | 0.590 | 0.000 | 0.000 | nan | 0.197 | 0/43 |
| 2.0 | 0.359 | 0.000 | 0.000 | nan | 0.166 | 4/43 |
| 2.5 | 0.308 | 0.095 | 0.200 | 0.129 | 0.241 | 6/43 |
| 3.0 | 0.282 | 0.200 | 0.600 | 0.300 | 0.390 | 18/43 |

Null model (predict always no_bar): 28/43 = 65.1%.
Best physical-regime accuracy 64.1% — **below null**.
**AUC 0.217 < 0.5** → model ranks anti-correlated with bar truth.

## Hard constraint

ζ_max physical (worst-case κ²_eff ≥ 0): **1.52**
The ζ window where Π_min crosses 1.0 for any bar (≥3) lies above ζ_max.
Cannot push the model into "predicts bars" regime without violating κ²_eff ≥ 0.

## Monotonicity test FAILED

Per-regime medians at ζ=1: FLOW=1.81, TRANSITION=3.21, LATENT=1.14
Expected: FLOW > TRANSITION > LATENT (Π decreases toward bar-prone regime)
Got: TRANSITION > FLOW > LATENT (the N=21 ordering was small-sample artefact)

## Root cause (post-hoc analysis)

Π_EFC ∝ σ_R·κ_eff/(3.36·G·Σ) is a **modified local Toomre Q**.
Q tests local axisymmetric stability (m=0/1).
Bar formation is a **global m=2 resonant instability**.

Local stability criterion ≠ global mode coupling. Tuning ζ cannot fix this.

EBE (energy/shear coupling via g_EFC) is present and correctly signed.
RCMP (regime via α = 1−L) modulates strength.
But both act only as **local corrections**: no coupling between annuli, no pattern speed Ω_p, no resonance condition.

## What Π_EFC apparently DOES measure (preliminary — pivot test pending)

Disk-state / "structural maturity" parameter:
- Correlates with regime (FLOW vs LATENT)
- Correlates with surface density scale (low Σ → low Π)
- Does NOT correlate with bar status (AUC 0.22, anti-correlated)

## Status

- v0.1 (`proxy_mode='v_squared'`): **FALSIFIED on sign** — g_EFC > 0 in disk for all galaxies, never destabilizes
- v0.1 (`proxy_mode='shear'`): **FALSIFIED on prediction** — sign correct, magnitude OK, but local-only criterion cannot predict global m=2 mode (AUC=0.217 at ζ=1)
- v0.2 (`efc_bic_v02_resonance.py`): **FALSIFIED 2026-04-25** — resonance-aware (CR + ILR + Toomre X + A(X) window peaked at X=1.5 + Q_floor=0.01). AUC=0.310 at best ζ=1.5 (still <0.5). Recall=18% (2/11 bars). Score dominated by ILR-absent geometric artefact (79% of galaxies have no ILR in data window), not bar physics. Bars with high X (>3) are downweighted by A(X); bars with present ILR are damped to score≈0.

## Final verdict: bar prediction track CLOSED

Two independent formulations (local Toomre-style v0.1, global resonance v0.2) both fail on the same N=43 SIMBAD-labeled SPARC subset, in the same direction (AUC < 0.5), with correctly implemented physics.

This is an **information-limit result**, not a model-formulation bug. Bar morphology is a sekulær/evolutionary outcome that depends on history (gas accretion, tidal triggers, prior instabilities). Snapshot kinematics alone — even with EFC modification of the epicyclic frequency and a global m=2 resonance treatment — does not contain enough information to predict bar status.

**Hypothesis "bar can be derived from EFC-modified disk kinematics alone" is now empirically falsified.**

## Pivot: Π_EFC repurposed as disk-state parameter

Π_min is strongly predictive of structural / evolutionary observables:

| Prediction | AUC (N=112) |
|---|---|
| gas-rich (top tertile of f_gas) | **0.812** |
| low-Σ (bottom tertile of log Σ_disk) | **0.814** |
| disk-faint (bottom tertile of disk dominance) | 0.663 |

Spearman ρ(log Σ) = −0.71, ρ(f_gas) = +0.65, ρ(V_max) = −0.46 — all p ≪ 0.001 on N=112.

See [CLAIM_DISK_STATE.md](CLAIM_DISK_STATE.md) for the formal claim, falsifiable predictions on independent samples (DESI, SDSS MaNGA, SAMI, FIRE-2/TNG), and reproducibility.

## Atlas update applied 2026-04-25

Neo4j `Phenomenon {name: "Bar Instability in Galactic Disks"}` and linked `EFCValidation`:
- `pipeline_status` → "FALSIFIED 2026-04-25 — v0.1 (Π_min) AUC=0.22; v0.2 (resonance) AUC=0.31; pivot to disk-state."
- `EFCValidation.status` → "FALSIFIED"
- `atlas_note` → "Bar prediction track closed. Π_EFC repurposed as disk-state parameter — see CLAIM_DISK_STATE.md."

## Files

- Pipeline: `efc_bic_pipeline.py`
- Pilot data: `output/n20_shear.json`, `output/compare_proxies.json`
- Classification: `output/classify_fit.json`, `output/classify_fit.png`
- Diagnostic: `output/diag_efc_vs_kappa.png`, `output/diag_efc_vs_kappa_SHEAR.png`
- Labels: `data/sparc/sparc_bar_labels.json` (SIMBAD provenance, strict de Vaucouleurs classifier)

## Atlas update

Atlas node `bar_instability_L3` was NOT updated in this session — Neo4j ID lookup failed (no node with `id='bar_instability_L3'` or `name CONTAINS 'bar_instability'`). Likely lives under a different label/ID convention (e.g. AtlasPrediction with hashed key) or was created externally to this Neo4j instance. **Recommended atlas update** when reachable:

```
pipeline_status: "FALSIFIED at SPARC N=43, AUC=0.22 in physical ζ regime, monotonicity failed. v0.2 planned (resonance-aware)."
falsification_evidence: classify_fit.json
falsification_date: 2026-04-25
next_version: efc_bic_pipeline_v0.2 (pattern_speed + ILR + swing_X)
```
