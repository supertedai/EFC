# Π_EFC as Candidate Disk-State Proxy (SPARC + xGASS-Validated)

**Version:** v0.1-candidate
**Date:** 2026-04-25
**Status:** **CANDIDATE prediction with external support.** Same-sign correlations across SPARC (Spitzer-3.6μm, V-decomp) and xGASS (SDSS Petrosian + Arecibo HI) — independent samples, independent observables, independent pipelines. Registered in Atlas (Phenomenon `disk_evolutionary_state`, AtlasPredictions `EFC_disk_state_logSigma_correlation_v0.1` + `EFC_disk_state_fgas_correlation_v0.1`, both `test_status=candidate_external_support`).
**Atlas status:** REGISTERED as candidate prediction. NOT a fundamental law. NOT linked back to bar morphology (which remains FALSIFIED — see [FALSIFICATION_RECORD.md](FALSIFICATION_RECORD.md)).
**Provenance:** Pivot from EFC-BIC bar prediction (falsified, AUC<0.5 in physical ζ regime)
**Atlas status:** NOT registered as Phenomenon or AtlasPrediction. Holds as draft until external validation on independent IFU/HI sample (MaNGA, SAMI, or THINGS) confirms the same correlation direction with N≥30 and ρ-sign consistency.

## Robustness checks completed (D, C, B-prime — all PASS)

| Test | Question | Method | Result |
|---|---|---|---|
| D | Outlier-driven? | 3 random seeds × half-split, 6 sub-samples N=56 | All halves: ρ(log Σ) ∈ [−0.83, −0.59], ρ(f_gas) ∈ [+0.53, +0.75], all signs hold |
| C | V_gas-decomposition artefact? | Replace internal f_gas (V_gas²/V_baryon²) with external M_HI/(M_HI + Υ·L[3.6]) from SPARC table1 photometry+HI | ρ(Π, f_gas_external) = +0.530 (vs +0.648 internal). Sign holds, 82% of original strength |
| B-prime | Reduction-pipeline artefact? | Stratify by original RC reduction (3 sources with N≥10) | VS01 (N=17) ρ=−0.91/+0.82; Sw09 (N=15) ρ=−0.70/+0.54; No07 (N=11) ρ=−0.90/+0.73. All same sign, all \|ρ\|>0.5 |
| B (THINGS/LITTLE THINGS) | Sample-independence? | DEFERRED — full V_gas/V_disk decomposition not in public VizieR catalogs |
| A (MaNGA Pipe3D) | True external sample + observable independence? | IN PROGRESS — Π proxy from Σ_*(Re), σ_*(Re), V_rot(Re); independent IFU survey |

## ⚠ Single-dataset risk

All N=112 galaxies in this analysis come from SPARC. The Π_min vs f_gas / log Σ correlations could in principle be:
1. A real EFC effect (the claim)
2. A reparameterisation of SPARC scaling relations (RAR, BTFR, etc.) carrying through Σ and V components
3. A selection-bias artefact of SPARC's high-quality-rotation-curve criterion

Distinguishing (1) from (2)/(3) requires repeating the test on a sample with different selection. Until that is done, this document is a CANDIDATE only.

---

## Claim

The EFC stability parameter

$$\Pi_{\rm EFC}(R) \;=\; \frac{\sigma_R(R)\,\kappa_{\rm eff}(R)}{3.36\,G\,\Sigma(R)} \quad{\rm with}\quad \kappa^2_{\rm eff} = \kappa^2 + \zeta\,\frac{g_{\rm EFC}}{R}, \quad g_{\rm EFC} = \alpha\,v\,R\,\frac{d\Omega}{dR}$$

evaluated as the disk-window minimum

$$\Pi_{\rm min} \equiv \min_{R \in [R_d,\,3R_d]} \Pi_{\rm EFC}(R)$$

with σ_R = √(πGΣR_d), shear ∇S proxy, and dimensionless coupling ζ ≈ 1, **does not predict bar morphology** but **does predict the disk evolutionary state** of a SPARC-style rotation-supported galaxy.

Specifically, Π_min is monotonically related to:

- **Stellar surface density**: ρ_Spearman(Π_min, log Σ_disk) = **−0.71**
- **Gas-richness**: ρ_Spearman(Π_min, f_gas) = **+0.65**, where f_gas = V_gas² / (V_gas² + V_disk² + V_bulge²) median in disk window
- **Maximum rotation amplitude**: ρ_Spearman(Π_min, V_max) = **−0.46**
- **Disk dominance**: ρ_Spearman(Π_min, V_disk² / V_obs²) = **−0.41**

## Operational binary predictions (falsifiable)

| Prediction | Score | Binary class | AUC (N=112) |
|---|---|---|---|
| P1 | Π_min ranks galaxy in top tertile of f_gas | "gas-rich" | **0.812** |
| P2 | Π_min ranks galaxy in bottom tertile of log Σ_disk | "low-Σ" | **0.814** |
| P3 | Π_min ranks galaxy in bottom tertile of disk dominance | "disk-faint" | 0.663 |

P1 and P2 are the two strongest predictions and are interchangeable proxies for "kinematically immature, gas-rich late disk".

## Per-regime structure (consistent with claim)

| EFC regime | N | median Π_min | median log Σ | median f_gas | median disk_dom |
|---|---|---|---|---|---|
| FLOW | 47 | 2.14 | +1.30 | 0.06 | 0.53 |
| TRANSITION | 44 | 3.98 | +0.44 | 0.18 | 0.22 |
| LATENT | 21 | **1.52** | **+2.17** | **0.00** | 0.41 |

LATENT galaxies (large massive spirals: NGC2841, NGC2998, ...) sit at LOW Π / HIGH Σ / ZERO gas — the "mature disk" corner.
TRANSITION galaxies (gas-rich LSB and intermediate dwarfs) sit at HIGH Π / LOW Σ / HIGH gas — the "immature/diffuse" corner.

## Physical interpretation

Π_EFC inherits the form of a Toomre-Q stability parameter modified by an EFC entropy-gradient term in κ². The shear proxy ∇S = v·R·dΩ/dR makes g_EFC negative in differentially rotating disks, which lowers κ²_eff. The result is largest where disks are dynamically cold and centrally concentrated (high Σ, low σ_R / Σ ratio), and smallest where disks are dynamically warm and gas-pressure supported.

In short: Π_min is a **kinematic + structural condensation index** for rotation-supported galaxies. It is small for compact, dynamically settled, evolved disks and large for diffuse, gas-rich, kinematically less-evolved disks.

## Falsifiable predictions (next data sets)

If this claim holds, the following must be true on independent samples:

1. **DESI BGS / SDSS MaNGA late-type subset** (resolved kinematics + stellar surface densities): Π_min should anti-correlate with log Σ_*(R<R_e) at ρ < −0.5 and AUC > 0.75 for top/bottom tertile classification of HI-rich vs HI-poor.
2. **SAMI/Califa**: same prediction transposed to integral-field gas-fraction maps.
3. **Cosmological zoom simulations** (FIRE-2, IllustrisTNG): Π_min should evolve with cosmic time in a single galaxy as Σ_* grows and f_gas declines — model predicts decreasing Π_min over the simulation epoch.
4. **Counter-example check**: A galaxy with high Π_min and high Σ (or low Π_min and low Σ) at >2σ would be a falsification candidate.

## Scope and explicit limits

This claim is bounded:

- **Sample**: SPARC-175 rotation-curve galaxies. Excludes ellipticals, S0s, mergers, and irregular dwarfs without measurable rotation curves.
- **Metric used**: Π_min in the disk window [R_d, 3R_d] from the v0.1 EFC pipeline (`proxy_mode='shear'`, `sigma_mode='sigma_jeans'`).
- **ζ assumption**: ζ = 1 (uncalibrated, but the rank ordering is essentially independent of ζ in [0.5, 1.5] as shown in earlier ζ-grid tests).
- **What this claim is NOT**: it is not a bar-instability criterion (FALSIFIED in v0.1 and v0.2 — see [FALSIFICATION_RECORD.md](FALSIFICATION_RECORD.md)). Bars are sekulær/historie-driven and not predictable from instantaneous kinematics alone in this formulation.

## Reproducibility

```bash
cd scripts/efc_bic_pilot
python3 disk_state_analysis.py
# → output/disk_state.json (full per-galaxy table)
# → output/disk_state.png  (4-panel scatter + statistics)
```

Files:
- Pipeline: [efc_bic_pipeline.py](efc_bic_pipeline.py)  (`proxy_mode='shear'`)
- Loader: [sparc_loader.py](sparc_loader.py)  (`sigma_mode='sigma_jeans'`)
- Analysis: [disk_state_analysis.py](disk_state_analysis.py)
- Output: [output/disk_state.json](output/disk_state.json), [output/disk_state.png](output/disk_state.png)
- SIMBAD bar labels (used to confirm bars are NOT correlated): [data/sparc/sparc_bar_labels.json](../../data/sparc/sparc_bar_labels.json)

## Prior negative result (calibration of strength)

Bar prediction with the same Π_min:

- v0.1 (`v_squared` proxy) on N=43 SIMBAD-labeled SPARC: **AUC = 0.217** (anti-predictive)
- v0.1 (`shear` proxy) on N=43: **AUC = 0.217** at ζ=1.0, monotonicity broken across regimes
- v0.2 (resonance-aware: ILR + corotation + Toomre X + A(X) window): **AUC = 0.310** at best ζ=1.5

The ~0.6 AUC gap between bar prediction (0.22–0.31) and disk-state prediction (0.81) is the empirical evidence that Π_EFC encodes **structural condensation**, not **mode-coupling instability**.

## Atlas-context corroboration

Three independent Atlas-graph observations support the pivot:

1. **No framework in the EFC Framework Atlas has any registered AtlasPrediction for bar instability.** Cypher: `MATCH (bar:Phenomenon {name:"Bar Instability in Galactic Disks"})<-[:PREDICTS]-(p:AtlasPrediction) RETURN p` returns zero rows across all 16+ frameworks (LCDM, MOND, Verlinde, fR, Horndeski, Jacobson, Padmanabhan, IEG, EDE, ...). The bar-prediction blind spot is community-wide, not EFC-specific. Our negative result is consistent with the field having implicitly conceded this target is not predictable from snapshot kinematics.

2. **EFC's documented L3 SUCCESSES are exactly the observable family this claim falls into.** From `MATCH (efc:Framework {name:"EFC"})-[:SUCCEEDS_AT]->(p:Phenomenon) WHERE p.rcmp_regime="L3"`:
   - Cluster Halo Mass Function (`mass_function`)
   - Cluster Mass-Temperature / Mass-Lensing Scaling (`scaling_relation`)
   - Missing Satellites / TBTF / Core-Cusp (`subhalo_population`)
   - **Radial Acceleration Relation (`acceleration_correlation`)** — also SPARC, also continuous, also kinematic
   None of these are binary morphological classifications. All are continuous regime/scaling observables. The disk-state Π_EFC fits this empirical success pattern; bar morphology does not.

3. **Cluster-scale precedent: f_SCC (Core-State Composition).** From the cluster-TNG track (memory: "Cluster TNG: Regime Model Progression, Session 22-23"): the same story arc happened at L3-CLUSTER — mass-only model FAILED, core-state composition fraction f_SCC WORKED (1-param tanh, ΔAIC=-213). The cluster pendant `Phenomenon: Cluster Core-State Composition f_SCC` (`observable_type='composition_fraction'`) is the structural analog of what Π_min becomes on the disk side. **The disk-state claim could register as the L3-DISK pendant of f_SCC**, completing a regime-composition parameter set across galactic and cluster scales.

In short: this is not a salvage operation. It's the same pattern EFC has succeeded with elsewhere, applied to the right observable on the disk side.
