# EFC Native v2 Graph — Specification

**Author**: Morten Magnusson
**Date**: 2026-02-16
**Status**: Active development

---

## 1. Primitive Objects

| Object | Symbol | Domain | Description |
|--------|--------|--------|-------------|
| Graph | (V, E) | Discrete | Cubic lattice N^3 with 6-connectivity |
| Entropy field | S_i | [0, 1] per node | Structural order parameter |
| Density field | rho_i | R+ per node | Source mass density |
| Potential field | Phi_i | R per node | Gravitational potential (AQUAL target) |
| Bulk reservoir | S_V | R+ global | Total entropy capacity (sets Lambda) |

## 2. Energy Functional

```
F[Phi] = F_grad + F_source + F_bulk + F_AQUAL

F_grad   = (1/2) sum_{<ij>} (Phi_i - Phi_j)^2
F_source = -sum_i rho_i * Phi_i
F_bulk   = Lambda * S_V                              (global constraint)
F_AQUAL  = a0^2 * sum_{<ij>} f(|dPhi_ij| / (a0*h))  (nonlinear flux)
```

where `f(x) = integral_0^x mu(t)*t dt` and `mu(x) = x/sqrt(1+x^2)` (standard MOND).

## 3. Field Equation

Variation of F w.r.t. Phi gives the discrete AQUAL equation:

```
sum_{j~i} mu(|Phi_i - Phi_j| / (a0*h)) * (Phi_i - Phi_j) = 4*pi*G*rho_i * h^2
```

This is the **nonlinear Poisson equation on a graph**.

KEY DESIGN CHOICE: Nonlinearity is on Phi (potential), NOT on S (source).

## 4. Emergent Limits

| Regime | Condition | Emergent behaviour |
|--------|-----------|-------------------|
| Newton (UV) | \|grad Phi\| >> a0 | mu -> 1, standard Poisson, g ~ 1/r^2 |
| MOND (IR) | \|grad Phi\| << a0 | mu -> x, g ~ sqrt(a0*g_N) ~ 1/r |
| Area law | S_0 = alpha * k_i | Capacity from local topology |
| Bulk scale | a0 ~ sqrt(Lambda) | Acceleration scale from bulk reservoir |

## 5. What This Is NOT

- NOT GR with a modification (no metric, no Einstein equations)
- NOT phenomenological mu(a) fitted to data
- NOT importing Friedmann equations for background
- NOT a continuum theory discretized — it IS discrete from the start

## 6. Test Suite (KT1–KT5)

| Test | Question | Pass criterion |
|------|----------|---------------|
| KT1 | Newton + MOND limits? | slope -2 (UV) and -1 (IR) |
| KT2 | Prefactor C stable? | C converges or stabilizes with N |
| KT3 | r_trans ~ sqrt(M)? | beta ~ 0.5 in power law |
| KT4 | Superposition broken? | delta_Phi smooth, nonzero |
| KT5 | EFE restores Newton? | enhancement drops with g_ext |

### Current Status (2026-02-16, v0.1)

| Test | Result | Note |
|------|--------|------|
| KT1 | **PASS** | slope -0.99 (MOND) to -2.00 (Newton) |
| KT2 | C ~ 2.32 | Converging slowly, may be grid signature |
| KT3 | **FAIL** | r_trans Lambda-locked, beta ~ 0.0 |
| KT4 | **PASS** | 13.7% violation, smooth (noise=0.23) |
| KT5 | TBD | v0.1 had measurement bug; v2 subtracts g_ext |

### Structural Diagnosis

The Lambda-locked transition (KT3 failure) means:
- Transition is at r ~ L_Lambda, not at g_N ~ a0
- Bulk reservoir sets a hard cutoff length
- This is "screened MOND" or "Yukawa-regulated AQUAL", not pure MOND

For sqrt(M) scaling, the transition must be determined by local
acceleration balance (g_N vs a0), not by global L_Lambda.

## 7. File Layout

```
pipelines/efc/native_v2_graph/
  kernel/
    graph.py         # nodes, edges, geometry
    fields.py        # Phi, S, rho, boundary
    operators.py     # Laplacian, gradient on graph
    energy.py        # F_grad + F_source + F_bulk + F_AQUAL
    aqual.py         # mu functions, conductivity
    solver.py        # linear + nonlinear Picard solver
    observables.py   # g(r), slopes, C, EFE, beta
  tests/
    kt1_limits.py
    kt2_C_convergence.py
    kt3_mass_scaling.py
    kt4_superposition.py
    kt5_EFE.py
  configs/
    base.yaml
    sweeps.yaml
  run_efc_graph.py   # orchestrator
```
