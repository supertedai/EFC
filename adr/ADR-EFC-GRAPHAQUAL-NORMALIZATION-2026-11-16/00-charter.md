# ADR-EFC-GRAPHAQUAL-NORMALIZATION-2026-11-16 — Charter

**Status:** Implementation and validation in progress; independent review pending. **Owner:** Morten. **Implementer:** default. **Task:** `t_bfded048`. **Baseline:** `origin/main` `e2e5a6c7fa244b6ec6182a3a4da7e46e45305c12`.

## Request

Make the Native v2 Graph-AQUAL numerical chain consistent before interpreting the measured prefactor `C`: source quadrature, continuum/grid scaling, nonlinear AQUAL flux, and acceleration extraction. Do not tune `a0`, `C`, or other physical parameters to restore the earlier `C≈2.32` result.

## Scope

Modify only `pipelines/efc/native_v2_graph`, the `pipelines/README.md` documentation of the Native v2 solver/tests, and this ADR package. Treat it as a generic continuum-calibrated AQUAL discretization on a cubic mesh, not as a demonstration of the separate Lambda-locked DGS mechanism, GR, cosmological limits, EBE/RCMP integration, or astrophysical fits. Preserve the historical DGS package/operator unless a separate decision is approved; document any remaining semantic difference rather than silently treating the two as identical.

No merge, landing, or production action is authorized by this task. Deliver a reviewed branch/PR for Morten's decision.

## Exit criteria

Local value: stop a numerical normalization defect from being mistaken for physical evidence. Local-to-global coupling: keep an auditable source-to-flux-to-observable bridge, while preventing a generic lattice calibration from being promoted into EFC's Lambda-locked or cosmological claims without a separate derivation and tests.

1. An ex-ante discrete derivation fixes signs, gradient/face-flux convention, source measure, `h` scaling, and boundary treatment.
2. Numerical regression tests fail on the current code for the observed defects, then pass on the implementation.
3. Newton amplitude and Gauss-flux checks accompany slope checks; nonlinear AQUAL is re-solved for each source/observable variant.
4. `N=21,31,41` use a fixed 20-unit physical box, common radial bins, the same boundary rule, and `h=20/(N-1)`. Raw profiles, bin counts, runtime, convergence and any timeout are preserved.
5. Sensitivity to at least two source/grid settings is measured. Numerical calibration is not promoted to physical `C`.
6. Focused tests and required EFC gates are recorded; independent review is complete; PR exact-head state is read back. Stop before merge/landing.
