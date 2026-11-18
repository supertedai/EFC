# Context and evidence

## Repository/task/workspace

- Repository: `/opt/agent-work/EFC`; remote `origin` is `supertedai/EFC`.
- Baseline: `origin/main` = `e2e5a6c7fa244b6ec6182a3a4da7e46e45305c12`.
- Task: `t_bfded048`, board `energy-flow-cosmology`.
- Active worktree: `/opt/agent-work/EFC/.worktrees/t_bfded048`, branch `wt/t_bfded048`; current run 853. Verified `HEAD == origin/main`, merge-base equals baseline, and clean before edits.

## Measured prior results

All numbers below are exploratory generic Native v2 solver outputs, not physical EFC measurements.

- Linear point-source Poisson at `h=1`, `r_source=2`, `M=50`, `G=1`: 27 nodes satisfy strict `r<2`. Under equal node-cell volume `h^3`, `f=27h^3/(4πr_source^3/3)=0.80572190`. Raw `g_graph/(GM_target/r^2)` was approximately 1.66 for `N=21,31,41`, with log slope near -2.03.
- Actual linear A/B/C/D runs gave combined source normalization plus postprocessed gradient `/2` ratios approximately 1.0300, 1.0304, 1.0304 for `N=21,31,41` over common bins. This is numerical support for the hypothesis, not proof of the graph's physical node measure.
- Nonlinear standard-AQUAL A/B/C/D runs used `G=1`, target `M=50`, `a0=2`, `h=1`, `r_source=2`. Combined variant D gave `C=1.392983` at `N=21` (two bins, `r=5..7`) and `1.329724` at `N=31` (seven bins, `r=5..12`). Different windows make these non-comparable; `N=41` was not run.
- The AQUAL `/2` variant changed only the postprocessed observable; the internal edge conductivity remained unchanged. Thus it was not a fully corrected field law.

## Source inspection at baseline

- `kernel/operators.py`: `L=D-A`; `discrete_gradient` sums all six neighbor differences without the central-gradient normalization. `weighted_laplacian` passes a scalar edge `|ΔΦ|` to conductivity.
- `kernel/fields.py`: point and multi-source RHS use continuous sphere volume while populating node samples; no discrete `h^3` normalization or explicit `h^2` conversion is present.
- `kernel/aqual.py`: `mu` is evaluated on a single edge difference divided by `a0*h`, not a reconstructed full local vector-gradient norm.
- `kernel/graph.py`: coordinates are centered and span `(N-1)h` per side; for a 20-unit box, use `h=20/(N-1)`.
- `docs/papers/efc/Discrete_Entropic_Gravity.../src/aqual_operator.py` separately specifies a graph edge-weight rule. This ADR does not silently rewrite that historical model claim.

## Ranked hypotheses

1. Source quadrature and missing continuum scaling contribute to Newton amplitude error; test by exact discrete mass integration and `h` refinement.
2. The vector acceleration estimator has a factor/sign convention error; test axis-linear and diagonal-linear fields against analytic gradients.
3. Edgewise `mu(|ΔΦ|/(a0h))` is not the standard continuum AQUAL constitutive argument `mu(|∇Φ|/a0)`; test a symmetric full-vector face reconstruction on axis and diagonal fields.
4. Remaining amplitude residual may arise from finite-box boundary conditions, lattice Green function and radial estimator; isolate only after 1–3.

## Unknowns / limits

- Whether equal node-volume `h^3` is the intended physical measure of the fundamental graph is not established. The implementation may use it only as the declared continuum-calibration convention, with that limitation explicit.
- No source commit or independently reviewed physical derivation currently establishes a universal `C` or the Lambda-locked mechanism.
