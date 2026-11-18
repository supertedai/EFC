# Implementation plan

1. Maintain the Kanban lease and use only `/opt/agent-work/EFC/.worktrees/t_bfded048`, branch `wt/t_bfded048`, based on origin/main e2e5a6c7. The claim-time workspace was corrected and read back; no source edits preceded this ADR.
2. Add focused numerical tests first for gradient, source quadrature, `h` scaling, face `mu` isotropy, and Gauss flux. Run the smallest failing subset and preserve expected RED output.
3. Implement one vertical slice at a time: (a) physical central gradient; (b) node-cell source normalization and explicit `h²`; (c) symmetric face-gradient `mu` in the actual weighted AQUAL flux; (d) solver and observable integration.
4. Run tests after each slice; do not change model parameters or select a prefactor to match the old C value.
5. Run the linear Newton A/B/C/D matrix with target physical `M` fixed; compute source mass, radial slope, amplitude and shell flux.
6. Run nonlinear AQUAL A/B/C/D at `N=21,31,41` with box side 20, `h=20/(N-1)`, fixed physical source radius, same boundary rule, common physical radial bins, `G`, `a0`, and target mass. Save raw `C(r)`, counts, spread, slope, amplitude, flux, convergence, iterations and wall time. Run at least two additional `h`/source-radius settings. If `N=41` exceeds the bounded runtime, record timeout and leave that acceptance item open.
7. Complete focused tests, relevant Native v2 regressions, canonical-venv suite, then repository gates. Keep baseline failures distinct.
8. Fill actual verification and rollback state in the ADR; obtain an independent fresh-context review on the exact branch/PR. Fix and re-review as needed. Do not merge or land.
9. Read back exact branch head, remote PR head/checks/review state; close the Kanban task only with verified outcome and residual gaps.
