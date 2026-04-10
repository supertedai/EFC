# EFC Solver — Grid-AQUAL Kill Tests

Numerical solver infrastructure for discrete entropic gravity on a cubic graph.

## Contents

| File | Purpose |
|------|---------|
| `grid_aqual_killtests.py` | KT1 (Newton/MOND limits), KT2 (prefactor convergence), KT3 (mass scaling) |
| `grid_aqual_extra_tests.py` | Extended convergence and diagnostic tests |
| `grid_aqual_convergence.png` | Reference convergence plot |
| `grid_aqual_extra_tests.png` | Reference diagnostic plot |

## Related

- Theory: `theory/formal/efc-r-model/` (regime sector)
- Validation ledger: KT1 PASSED, KT2 PASSED, KT3 MARGINAL (β = 0.29 vs target 0.50)
- Paper: [Discrete Entropic Gravity on a Cubic Graph](https://doi.org/10.6084/m9.figshare.31348411)
