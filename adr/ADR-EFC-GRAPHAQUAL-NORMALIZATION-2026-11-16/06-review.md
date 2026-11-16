# Independent review record

**Reviewer:** `researcher` (kanban independent review, run 855, round 1 — artifact lens). **Route/model:** independent card review; reviewer independently re-verified numerics and gates. **Model verified:** not applicable (separate profile/session, not a same-model self-review).

Review must receive this ADR, the exact diff and test outputs. It must independently inspect the discrete derivation and answer:

1. Is the face reconstruction for `mu(|∇Φ|/a0)` consistent with a conservative cubic finite-volume discretization, including diagonal linear fields?
2. Are signs, `h²` scaling, source mass measure, boundary treatment and Gauss-flux accounting internally consistent?
3. Do the tests detect the original defects and fail under mutants (missing source normalization, missing `h²`, edge-component `mu`, unnormalized gradient)?
4. Are A/B/C/D runs genuinely one-factor/combined comparisons with common physical bins and target mass?
5. Are generic AQUAL, the historical DGS edge model and Lambda-locked EFC kept separate in all claims?
6. Is rollback and exact-head readback adequate?

**Round 1 verdict (run 855): request changes — no merge/landing.** Core numerics and gates accepted (not in dispute): the source→RHS sign/h² chain, centered-difference gradient with 2h divisor, symmetric full-vector face norm, `g=-∇Φ`, `sum rho h³=M`, and the Gauss-flux helper; focused suite 16/16, `git diff --check` 0, schema/verify/spraakvakt gates green.

Three findings, each independently reproduced against the code:

1. **Boundary treatment under-documented (KT6 metadata + ADR).** `boundary_mask` pins the spherical shell `r > r_max − 1.5h`, not the outer cube faces (measured N=9/h=1: 116 pinned, 386 outer-face nodes, 270 face nodes graph-truncated and unpinned). KT6 metadata claimed only "Dirichlet Phi=0 on boundary_mask".
2. **"sum rho h³ = M" silently violated for boundary-overlapping sources.** `solve_aqual`/`solve_linear_poisson` clamp boundary RHS rows to `phi_bc`, so the solved mass is less than the declared mass (measured 0.6296 active at `[3,3,3]`, 0.125 at `[4,4,4]`; 1.0 only for the central default).
3. **ADR charter scope mismatch.** `00-charter.md` limited edits to `pipelines/efc/native_v2_graph` + this ADR package, but `pipelines/README.md` also changes.

**Disposition (implementer, round 2):** all three fixed.

1. `experiment_metadata()` now states the Dirichlet pin applies to the spherical margin shell only, that outer cube faces are graph-truncated (fewer neighbours) and not Dirichlet-pinned, and that this is pre-existing solver behaviour; mirrored in `03-decision.md` item 7.
2. Added `reject_source_on_boundary` (raises `ValueError` on source/boundary overlap) and `active_source_mass` (measured mass on non-boundary rows), applied in both solvers and returned in the result dict; KT6 now records `represented_mass` from the measured `active_source_mass`. Regression tests: `test_aqual_rejects_source_support_overlapping_boundary_mask`, `test_aqual_accepts_central_source_and_reports_full_active_mass`, `test_linear_solver_reports_active_source_mass_equal_to_total` (RED→GREEN).
3. Widened `00-charter.md` scope to include `pipelines/README.md`.

Re-review pending on the new exact head; no self-approval.
