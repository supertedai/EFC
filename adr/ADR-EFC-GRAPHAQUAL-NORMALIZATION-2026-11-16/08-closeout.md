# Closeout

**Status:** Acceptance implementation and local verification are complete for run 862. Code/data commit `6960e31d3ba82e096acedb553438fb2d3bbd2fb3` is pushed to the existing branch/PR; its immediate readback was PR #657 OPEN/DRAFT with `verify=SUCCESS`, `mergeState=CLEAN`, `mergedAt=null`. A fresh independent review of the final exact PR head remains; no merge/landing or production effect.

## Baseline findings

- Baseline commit: `e2e5a6c7fa244b6ec6182a3a4da7e46e45305c12`.
- Prior linear A/B/C/D Newton control supports the source-quadrature × observable-normalization hypothesis under an `h³` node measure; it does not prove the graph's physical measure.
- Prior nonlinear AQUAL A/B/C/D produced 1.392983 at N=21 and 1.329724 at N=31 with different windows; these are not converged or physical C estimates.
- The old N=41 KT2 archive was not substituted. A new fixed-box KT6 N=41 run completed on the same 20-unit box/common bins as N=21,31; raw outputs are preserved under `pipelines/efc/native_v2_graph/outputs/runs/kt6_fixed_box_20261116/`.

## Implementation, tests, review, PR

The Native v2 source/field/observable chain has been changed and tested. In run 862, the focused normalization suite passes 23/23 (8 SciPy sparse-CSR efficiency warnings); the full repository suite passes 1327 tests with one non-failing SyntaxWarning; schema, paper-integrity, language-delta, compile and diff gates pass. The acceptance-probe rerun reproduces the saved boundary-sensitivity and farther-window numerical profiles. Matched-window `D` results are 1.161688, 1.152630, 1.158414 for N=21,31,41, respectively. This is a numerical trend in generic standard AQUAL under the declared code-unit/node-volume convention, not a physical EFC `C` or a demonstrated continuum limit.

Independent review (round 1, `researcher`) returned **request changes** with three robustness/documentation findings (boundary treatment under-documented; silent source-mass shortfall at the boundary; ADR charter scope omission). All three were fixed in round 2. The round-2 reviewer (`researcher`, run 858) then requested the owner-added source-position, symmetry/margin-sensitivity, farther-window and status-reporting acceptance evidence; those items are now addressed by the run-862 tests/probes and this ADR update. A fresh independent review of the pushed exact head is still required. No merge/landing or production effect occurred.

## Acceptance clarification results

- Source-position contract: **Pass** — centered and interior-offset actual solves preserve the declared mass; near-shell support is rejected by the boundary guard. The actual solver now returns source-center provenance.
- Boundary semantics/symmetry: **Pass** — spherical margin-shell pin and graph-truncated cube-face behavior are documented and symmetry is regression-tested.
- Fixed-box boundary-margin sensitivity: **Pass** as generic numerical calibration, with preserved C(r), mean C, radial slope, counts/spread and timing in `kt6_acceptance_probes_20261116/kt6_acceptance_probes.json`.
- Farther-radius Deep-MOND status: **Unresolved** — a real [9,13] probe was run and preserved, but its finite-box profile and positive acceleration slope do not establish an asymptote. No tuning was performed.
- Review: round-2 requested changes are implemented; a fresh independent exact-head review remains required. PR #657 remains open/draft and unmerged.

## Residual questions

Pending: correctness of the declared graph node measure relative to fundamental EFC; relation between the corrected continuum-calibrated AQUAL solver and the DGS edge-graph model; physical `a0`/Lambda mapping; and cross-regime EFC validation. Existing downstream uses of historical `C=2.32` were not audited or changed by this task; treat them as frozen prior assumptions pending a separate evidence review, not as updated by KT6.
