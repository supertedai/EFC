# The Bullet Cluster Under EFC — AI-friendly package

**Report:** EFC-VAL-2026-004
**DOI:** [10.6084/m9.figshare.31963668](https://doi.org/10.6084/m9.figshare.31963668)
**Author:** Morten Magnusson (ORCID 0009-0002-4860-5095)
**Date:** 2026-04 · **License:** CC-BY-4.0
**Ledger version:** v3.11

Analytical confrontation of the Energy-Flow Cosmology (EFC) framework with
three JWST-era Bullet Cluster (1E 0657−56) mass reconstructions:

1. **Cha et al. 2025** (ApJ 987, L15; arXiv:2503.21870) — 146 strong-lensing
   constraints + 398 arcmin⁻² weak-lensing sources → highest-resolution mass
   map to date, σ/m < 0.5 cm² g⁻¹, ICL–mass Hausdorff = 19.80 ± 12.46 kpc.
2. **Rihtaršič et al. 2026** (arXiv:2601.22245) — first spectroscopically
   anchored parametric lens model (135 secure multiple images from 27 systems
   with z_spec = 0.9–6.7).
3. **Cho et al. 2025** (arXiv:2512.03150) — JWST/NIRCam + DECam virial masses
   M_200c^main = 15.1×10¹⁴ M☉, M_200c^sub = 1.5×10¹⁴ M☉ → confirmed **~10:1
   minor merger**.

**No new parameters, simulations, or data reductions are introduced.** All
EFC parameters remain frozen at their Ledger v3.11 values.

## Four axes of confrontation

| # | Axis | EFC status |
|---|------|-----------|
| 1 | Cluster merger geometry under revised 10:1 mass ratio | Structural exclusion test (DOI 31173850) **tightened**, not weakened |
| 2 | A_sig directional lensing residual baseline (PIEMD null) | Validated: A_sig = −6.9×10⁻⁴, p = 0.98 (null hypothesis established) |
| 3 | SIDM constraint σ/m < 0.5 cm² g⁻¹ (Cha et al.) | Consistent: EFC predicts σ/m = 0 by construction (no DM particle) |
| 4 | Regime-transition prediction P1 (μ ≈ 1.1, Σ ≈ 1.2 at cluster scales) | Qualitative consistency check against Cho et al. virial masses |

## Main conclusions

- **None of the three JWST-era studies falsifies EFC.**
- None provides **positive** support for EFC over ΛCDM either; the Bullet
  Cluster remains a **consistency check** (L2 regime), not a detection site.
- The pre-registered **A_sig shock-front test on δκ = κ_obs − κ_PIEMD**
  (requires Cha et al. free-form κ-map) is the only pre-registered observable
  that can *discriminate* EFC from ΛCDM at this scale. It is **pending**.
- Given the v3.11 multi-epoch fσ8 null result (EFC-VAL-2026-003), the
  perturbation-sector coupling μ(a) is not detected in growth data (B = 0
  within 1σ). This makes the A_sig test on the lensing sector Σ even more
  important: the survival valley (μ ≈ 0.94, Σ ≈ 1.05) requires lensing and
  growth modifications to decouple, with Σ > 1 carrying the observable signal
  at L2 scales.

## A_sig 2D baseline result (PIEMD model)

| Quantity | Value |
|---|---|
| ⟨κ⟩_front | 0.1824 |
| ⟨κ⟩_back | 0.1831 |
| A_sig (baseline) | −6.9 × 10⁻⁴ |
| Bootstrap p-value (5000 random rotations) | 0.98 |
| A_sig / σ_null | −0.01 σ |
| Sensitivity (±20 % in σ₀^Main-NW) | ΔA_sig ≈ ±0.01 |

The parametric gravitational model produces **no directional asymmetry** at
the shock front. This validates the null hypothesis of the test operator (not
the physical hypothesis): any A_sig ≠ 0 observed in the full δκ residual
cannot be attributed to halo geometry within this PIEMD model class.

## Files

- `bullet_cluster_efc.pdf` — paper
- `index.json`, `metadata.json`, `schema.json`, `*.jsonld` — machine-readable metadata
- `data/asig_baseline_result.json` — PIEMD baseline A_sig result + halo parameters
- `data/external_studies.json` — machine-readable record of the three confronted externals
- `src/asig_2d_piemd.py` — PIEMD A_sig 2D pipeline (NumPy)
- `examples/reproduce_baseline.py` — minimal reproducer for the baseline
- `citations.bib` — references

## Reproduce

```bash
python examples/reproduce_baseline.py
```

## Related EFC artifacts (Ledger v3.11)

- Cluster merger geometry / triangulation: 10.6084/m9.figshare.31173850
- Directional lensing residuals (A_sig methodology): 10.6084/m9.figshare.31222900
- Regime Transition Test: 10.6084/m9.figshare.31941543
- EFC Screening Model (Track 1): 10.6084/m9.figshare.31940469
- EFC Relativistic Action: 10.6084/m9.figshare.31876324
- Empirical validation — cluster lensing + rotation curves: 10.6084/m9.figshare.31190233
- WP4 BOSS Transfer Validation: 10.6084/m9.figshare.31954125
- Multi-epoch fσ8 Growth Test: 10.6084/m9.figshare.31955871

## Language discipline

This package follows EFC's standing language discipline. Wording such as
"EFC is consistent with" / "overlaps with" / "survives the constraint" is
used. Claim-inflating phrases ("confirms EFC", "proves EFC", "validates EFC")
are **not** used: the Bullet Cluster remains a consistency check, not a
positive detection, until the pre-registered A_sig shock-front test on the
free-form δκ residual is executed.
