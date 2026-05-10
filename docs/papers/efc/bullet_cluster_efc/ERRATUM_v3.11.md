# Erratum to v3.11 — A_sig PIEMD Baseline Recalibration

**Document:** Bullet Cluster Under EFC (DOI: 10.6084/m9.figshare.31963668)
**Affected version:** v3.11 (2026-04-01)
**Erratum date:** 2026-05-10
**Discovered in:** branch `claude/jwst-efc-killtest-setup-4wHkn`, commit b45f026

## What was wrong

§3.2.3 of v3.11 reports

> A_sig = −6.9 × 10⁻⁴, p = 0.98

as the PIEMD baseline and claims:

> "the parametric gravitational model produces no directional asymmetry at
> the shock front (A_sig ≈ 0, p = 0.98). This result establishes the null
> hypothesis…"

Both quantities were computed with the **placeholder halo geometry** in
`src/asig_2d_piemd.py::default_halos()` (Main-NW at x=350 kpc, Main-SE at
x=380 kpc, Subcluster at x=580 kpc, Group-NE at x=600 kpc, with the shock
at x=480 kpc). In that geometry main and subcluster halos sit roughly
symmetric around the shock front by accident, so their contributions to
the front and back strips cancel within ~10⁻⁴.

When the actual best-fit PIEMD halos from Rihtaršič et al. (2026)
Table C.2 (now integrated in `src/asig_2d_piemd.py::rihtarsic2026_halos`)
are inserted in the BCG1-centred frame, the geometric A_sig is

| Quantity | Calibrated (Rihtaršič 2026 Table C.2) | Placeholder (v3.11) |
|---|---|---|
| ⟨κ⟩_front | 0.1090 | 0.1824 |
| ⟨κ⟩_back  | 0.1911 | 0.1831 |
| **A_sig** | **−8.21 × 10⁻²** | −6.9 × 10⁻⁴ |
| Bootstrap p-value | < 10⁻⁴ | 0.98 |
| A_sig / σ_null | **−5.9** | −0.01 |

The calibrated baseline differs from the placeholder by **~120σ**.

## Cause

H3 (subcluster halo) sits ~100 kpc behind the shock front; H1 (main
halo) sits ~700 kpc in front of it. With realistic σ_lt and r_cut = 2 Mpc
(both fixed in Rihtaršič+2026 fiducial model), the back strip is dominated
by H3's mass while the front strip sees only the falling outer profile
of H1. The asymmetry is purely geometric — there is no physics in PIEMD
itself that produces directional residuals.

## Why P2 is unaffected

The A_sig operator is a linear functional of κ. The δκ residual test
that constitutes P2 is therefore invariant under any additive baseline
correction:

```
A_sig(δκ) = A_sig(κ_obs − κ_PIEMD) = A_sig(κ_obs) − A_sig(κ_PIEMD)
```

The calibrated baseline value is simply the correct number to subtract.
The sealed prediction P2 — "entropy-gradient lensing produces a non-zero
A_sig aligned with the Chandra shock front after subtracting a
density-only mass model" — is unchanged. What changes is the reporting
form: the test claim is no longer "A_sig(δκ) ≠ 0" but
"A_sig(δκ) ≠ −0.082 (calibrated geometric null)".

## What changes in the paper

1. §3.2.3 baseline values must be re-reported as **placeholder geometry
   diagnostic** rather than "null hypothesis validated".
2. The phrase "the parametric gravitational model produces no directional
   asymmetry at the shock front" must be removed — it is false in
   general; it is only true for symmetric placeholder geometries.
3. Table 1 should be replaced or supplemented with the calibrated
   baseline (`data/asig_baseline_rihtarsic2026.json`).
4. P1 (regime transition) is not affected by this correction.
5. Sealed prediction P2 in README.md is unchanged.

## What is unaffected

- All EFC predictions (P1, P2, growth-sector tests, regime-transition
  parameters µ, Σ) are unaffected by this correction.
- The A_sig operator definition is unaffected.
- The pre-registration locked-geometry parameters (shock_x_kpc=480 in
  paper-frame, equivalent to 720 kpc in BCG1-centred frame; strip
  width 200 kpc; strip length 400 kpc) are unaffected.
- The δκ residual test logic is unaffected.

## Provenance

- Calibrated halos: `src/asig_2d_piemd.py::rihtarsic2026_halos` (commit
  b45f026)
- Calibrated baseline JSON: `data/asig_baseline_rihtarsic2026.json`
- Placeholder coincidence flagged in:
  - `data/asig_baseline_result.json::caveats[0]` (existing)
  - `docs/validation-ledger/data/tests.json::quantitative_result.placeholder_coincidence_note` (commit 28b455d)

The next paper version (v3.12 or higher) should incorporate this
erratum. The branch `claude/jwst-efc-killtest-setup-4wHkn` (PR #292)
ships the calibrated pipeline ready to run on Cha+2025 free-form κ-map
when that FITS file is available.
