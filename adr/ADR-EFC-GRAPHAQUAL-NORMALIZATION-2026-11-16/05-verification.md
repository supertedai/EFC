# Verification plan

## RED/GREEN numerical tests

- Constant potential: zero gradient and zero flux.
- Axis-linear `Φ=x`: central gradient has the analytic signed component; face `mu` uses the full norm.
- Diagonal-linear `Φ=x+y+z`: each component and full norm are exact; face constitutive weights match axis-rotated fields, proving the `mu` argument is not a single directional component.
- Quadratic `Φ=r²`: verify the `L=D-A` stencil and its `-h²∇²` conversion over several `h` values.
- Source sphere: explicit support rule and `sum rho_i h³=M` for multiple `h` and radii.
- Face flux: symmetric edge weights, antisymmetric paired flux and conservative closed-shell flux.
- Newton point source: slope and absolute amplitude at multiple radii, same bins for all resolutions, compare with `GM/r²` under the declared boundary convention.
- Nonlinear AQUAL: convergence and raw `C(r)` for each A/B/C/D variant; test full-vector face `mu` with non-axis-aligned linear fields.

## Run matrix

- Fixed physical side length 20; `N=21,31,41`; verify coordinates span 20 and use `h=20/(N-1)`.
- Fixed target physical mass, `G`, `a0`, source center/radius, boundary convention, and common physical radial bins.
- A=current sampled source/current observable; B=normalized source/current observable; C=current source/corrected observable; D=normalized source/corrected observable. The nonlinear solver is recomputed for every variant.
- At least two extra `h` or source-radius settings. Record exact parameters and mask inclusion rule.

## Required reporting

For each run: solver/model; commit; N/h/physical box; source support and discrete mass; G/a0/units; potential sign and boundary condition; flux and observable gradient conventions; raw per-bin C(r), radial window, counts and bin spread; Newton slope and amplitude; Gauss shell flux; solver convergence/iterations/time. Bin spread is not uncertainty on `C_infinity`.

## Repository gates

- Focused new test: exact command and exit status.
- Existing Native v2 KT tests relevant to the changed operator.
- Canonical interpreter `/opt/venvs/t_123ed6d9/bin/python`; sanitize `PYTHONPATH`, `PYTHONHOME`, `PYTHONUSERBASE`.
- Full repository suite according to `efc-test-validation`, with fresh baseline failures named.
- `scripts/maintenance/efc_schema_check.py`, `scripts/maintenance/efc_verify.py`, `scripts/maintenance/efc_spraakvakt.py --referanse origin/main`, and `git diff --check`.
- Exact branch/PR head and checks read back. No merge.

## Observed results to date (canonical venv)

- RED on baseline commit `origin/main` e2e5a6c7: fixed-box Newton amplitude test failed the 12% gate on the expected amplitude assertion (N=21 bins reached ratios about 1.64–1.69). The corrected branch passes after the explicit `rho`/RHS API split (see focused test below).
- Focused regression command after the explicit `rho`/RHS API split: `env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE /opt/venvs/t_123ed6d9/bin/python -m pytest -q pipelines/efc/native_v2_graph/tests/test_physical_normalization.py -k 'not newton_point_source_has_correct_amplitude_and_slope_at_fixed_box'` → **14 passed, 1 deselected**, 3 existing SciPy sparse-CSR assignment warnings, 9.04 s.
- The fixed-box Newton point-source amplitude/slope test reran after the `rho`/RHS API split: **1 passed**, one existing SciPy CSR assignment warning, 70.21 s. The complete 16-test normalization suite, after the KT2 and KT6 metadata changes, passes: **16 passed**, 4 existing SciPy sparse-CSR assignment warnings, 74.49 s.
- KT6 metadata contract followed RED/GREEN: the new metadata test first failed with the expected missing-import error, then passed. An N=11, one-iteration, high-tolerance smoke run wrote and read back code-unit, boundary, h, box, source-mask, run-id and calibration-only metadata; this smoke is not scientific evidence.
- Newton fixed-box check (side=20, h=20/(N-1), common bins r=4.5–8.5): N=21 amplitude mean 1.029599, slope −2.014775; N=31 mean 1.009317, slope −1.973470; N=41 mean 1.019292, slope −1.990700. All bins met the ±12% assertion; the combined test was rerun after the rho/RHS API-only refactor and passed. The source-density integral is tested at h=1,0.5,0.25; a discrete Gauss shell test passes at radii 2,3,4 for an N=11 AQUAL case.
- Legacy KT2 is now explicitly labelled a fixed-h domain-size trend. The updated N=21 smoke run records `continuum_limit_established=false`, `measurement_mask_comparison=same_cubic_graph_different_measurement_masks_only`, and `insufficient_data` for its one-point trend; it no longer reports a continuum or topology verdict.
- New fixed-box KT6 A/B/C/D run completed for N=21 and N=31. N=21 h=1, f_h=0.805722: A=2.029779, B=2.323376, C=1.014890, D=1.161688. N=31 h=2/3, f_h=0.928404: A=2.199407, B=2.305259, C=1.099703, D=1.152630. Both use common C bins [5.5,6.5,7.5,8.5]. Discrete AQUAL Gauss flux matches the represented source mass across shells 4,6,8,10. These are generic standard-AQUAL calibrations; they are not Lambda-locked EFC predictions.
- Source-radius sensitivity at N=21 for normalized source M: r_source=1.5 gives C=1.161868; r_source=2.5 gives C=1.161583 over the same window. This is a limited sensitivity check, not a convergence claim.
- N=41 KT6 A/B/C/D completed normally (exit 0). `h=0.5`, fixed side 20, `f_h=0.936279`; both AQUAL source cases converged in 13 iterations (under-sampled source 667.90 s, normalized source 677.99 s). On common bins [5.5,6.5,7.5,8.5], D has `C_by_bin=[1.235950,1.166215,1.125177,1.106312]`, mean `C=1.158414`, radial slope −1.257166; AQUAL shell flux for normalized source is 628.090817, 628.234521, 628.295680, 628.303823 at r=4,6,8,10. Newton slope is −1.967361; amplitude ratios by those bins are 1.016215, 1.012167, 1.012836, 1.033380, and Newton flux is 628.318531 across shells. The raw A/C and B/D profiles, counts, spreads, convergence and wall times are preserved in `pipelines/efc/native_v2_graph/outputs/runs/kt6_fixed_box_20261116/` with SHA-256 and run-context manifest. These are generic standard-AQUAL measurements, not a physical EFC prefactor.
- Full repository suite: `env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE /opt/venvs/t_123ed6d9/bin/python -m pytest tests/ -q` → **1327 passed**, exit 0, 122.04 s. One warning remains in `tests/test_maintenance_chain_fixpoint.py` (`SyntaxWarning: invalid escape sequence '\\d'`); no test failed.

- `py_compile` over all changed Python source/test files and `git diff --check`: exit 0.
- Repository gates: `efc_schema_check.py` → 4 schema/instance pairs, 2 instanceless schemas, 4 schema-only schemas valid/closed; `efc_verify.py` → 171 paper dirs, 0 errors, 0 warnings; `efc_spraakvakt.py --referanse origin/main` → 0 new findings; `git diff --check` → 0.

## Review round 2 (fixing researcher findings 1–3)

- **Boundary documentation (finding 1).** `experiment_metadata()` now emits a `boundary_condition` stating the pin is the spherical margin shell `r > r_max - boundary_margin*h` and a `boundary_treatment` stating outer cube faces are graph-truncated (fewer neighbours) and not Dirichlet-pinned, marked pre-existing solver behaviour. Mirrored in `03-decision.md` item 7 and the KT6 output `params`.
- **Source-mass guard (finding 2).** `kernel/fields.py` gains `active_source_mass(rho, boundary, spacing)` and `reject_source_on_boundary(rho, boundary)`; both solvers call the guard and return `active_source_mass`. KT6 records `represented_mass` from the measured `active_source_mass`. RED→GREEN: `test_aqual_rejects_source_support_overlapping_boundary_mask`, `test_aqual_accepts_central_source_and_reports_full_active_mass`, `test_linear_solver_reports_active_source_mass_equal_to_total`, and the updated `test_kt6_metadata_records_code_units_and_dirichlet_boundary` (asserts the new boundary strings).
- **Charter scope (finding 3).** `00-charter.md` scope now includes `pipelines/README.md`.
- Focused suite after round-2 fixes: `env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE /opt/venvs/t_123ed6d9/bin/python -m pytest -q pipelines/efc/native_v2_graph/tests/test_physical_normalization.py` → **19 passed**, 6 existing SciPy sparse-CSR assignment warnings, ~75 s.

## Run 862 verification (current worktree, before push)

- Canonical environment: `/opt/venvs/t_123ed6d9/bin/python`, Python 3.12.13, pytest 8.4.2; `PYTHONPATH`, `PYTHONHOME` and `PYTHONUSERBASE` unset.
- Focused suite: `.../python -m pytest -q pipelines/efc/native_v2_graph/tests/test_physical_normalization.py` → **23 passed**, 8 SciPy `SparseEfficiencyWarning` instances, exit 0, 75.73 s.
- Full suite: `.../python -m pytest tests/ -q` → **1327 passed**, exit 0, 112.26 s; one non-failing `SyntaxWarning` for `\\d` in `tests/test_maintenance_chain_fixpoint.py`.
- `py_compile` on the changed solver and both relevant test/probe files, schema check, paper verification, `spraakvakt --referanse origin/main`, and `git diff --check` all exited 0. Schema: 4 paired, 2 instanceless and 4 schema-only schemas valid; paper verifier: 171 dirs, 0 errors/warnings; language delta: 0 new findings.
- Re-ran the bounded acceptance probe from this worktree in run 862. It reproduced the archived C(r), mean-C and slope values; only wall times differed. The three boundary-margin runs (1.0/1.5/2.0) converged with mean C 1.160020/1.160807/1.160680 and radial slopes −1.239119/−1.240536/−1.241410. The farther window [9,13] gives C(r)=[1.092369,1.109629,1.398265,1.617244] and acceleration slope +0.524303; Deep-MOND status remains **Unresolved**.
- Pre-push remote readback: PR #657 is OPEN/DRAFT and branch/PR head are `76a0c4e6299b633f5bc65362c12913388675ec1d`; the run-862 acceptance diff is not yet included in that remote head. `mergeState=CLEAN`, `mergedAt=null` at that readback. No merge.

## Remaining gates

- KT1/KT3/KT4/KT5 compatibility smoke checks have not been run; they remain residual checks outside this bounded normalization acceptance. The run-862 implementation/data commit `6960e31d3ba82e096acedb553438fb2d3bbd2fb3` was pushed to the existing branch and PR #657. Its immediate remote readback showed OPEN/DRAFT, `verify=SUCCESS`, `mergeState=CLEAN`, `mergedAt=null`. Obtain a fresh independent review on the final exact PR head, read back that head and checks after the ADR closeout update, then complete the Kanban/ADR handoff. `C_physical`, Lambda coupling, LambdaCDM limit, GR limit, EBE/RCMP operation and astrophysical validation remain outside what these results establish.

## Acceptance clarification measurements (round 3)

- **Source positions — Pass.** The actual `solve_aqual` path now has behavior-level coverage for a centered source, an interior offset source, and a near-shell source. Centered and offset cases report `active_source_mass=M`; the near-shell case is rejected before solving because its strict-radius support intersects the pinned shell. The solver result carries `source_centers` as provenance.
- **Boundary semantics and symmetry — Pass.** The boundary mask remains a spherical margin shell; outer cube faces are graph-truncated and not Dirichlet-pinned. A regression test checks invariance under axis permutations and sign flips for N=9, h=1, margin=1.5.
- **Fixed-box margin sensitivity — Pass (numerical calibration only).** The preserved probe `pipelines/efc/native_v2_graph/outputs/runs/kt6_acceptance_probes_20261116/kt6_acceptance_probes.json` uses N=21, box side 20, h=1, M=50, a0=2 and common bins [5.5, 6.5, 7.5, 8.5]. For margins 1.0/1.5/2.0, mean C is 1.160020/1.160807/1.160680 and radial slopes are -1.239119/-1.240536/-1.241410. Each run converged; C(r) and bin spread are recorded separately, and spread is not treated as uncertainty on C_infinity.
- **Farther-radius probe — Unresolved.** The same preserved probe records C(r) on [9.5, 10.5, 11.5, 12.5] and acceleration slope +0.524303 over [9,13]. The finite box, bounded iteration and non-asymptotic/unstable profile do not establish the Deep-MOND asymptote; no parameter was tuned.
- **Current PR state — pre-push measurement.** The remote PR/branch remain at `76a0c4e6299b633f5bc65362c12913388675ec1d`; the acceptance changes verified in run 862 are still local and uncommitted. Re-read PR head/checks after pushing. `mergedAt` was null; no merge or landing is authorized by this ADR.
