# Closeout

**Status:** Implementation and validation in progress; not closed. Task `t_bfded048` is running on `energy-flow-cosmology`. Source changes are present only in the isolated worktree; no commit/PR or production effect yet.

## Baseline findings

- Baseline commit: `e2e5a6c7fa244b6ec6182a3a4da7e46e45305c12`.
- Prior linear A/B/C/D Newton control supports the source-quadrature × observable-normalization hypothesis under an `h³` node measure; it does not prove the graph's physical measure.
- Prior nonlinear AQUAL A/B/C/D produced 1.392983 at N=21 and 1.329724 at N=31 with different windows; these are not converged or physical C estimates.
- The old N=41 KT2 archive was not substituted. A new fixed-box KT6 N=41 run completed on the same 20-unit box/common bins as N=21,31; raw outputs are preserved under `pipelines/efc/native_v2_graph/outputs/runs/kt6_fixed_box_20261116/`.

## Implementation, tests, review, PR

The Native v2 source/field/observable chain has been changed and tested. The focused normalization suite passes 16/16; the full repository suite passes 1327 tests with one SyntaxWarning; the schema, paper-integrity, language-delta, compile and diff gates pass. Matched-window `D` results are 1.161688, 1.152630, 1.158414 for N=21,31,41, respectively. This is a numerical trend in generic standard AQUAL under the declared code-unit/node-volume convention, not a physical EFC `C` or a demonstrated continuum limit. Commit created on `wt/t_bfded048`; branch push, PR, independent exact-head review and remote readback are pending. No merge/landing or production effect occurred.

## Residual questions

Pending: correctness of the declared graph node measure relative to fundamental EFC; relation between the corrected continuum-calibrated AQUAL solver and the DGS edge-graph model; physical `a0`/Lambda mapping; and cross-regime EFC validation. Existing downstream uses of historical `C=2.32` were not audited or changed by this task; treat them as frozen prior assumptions pending a separate evidence review, not as updated by KT6.
